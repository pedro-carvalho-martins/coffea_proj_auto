"""Durable MDB vend state machine. Payment and dispense are distinct phases."""

import threading
from datetime import datetime

from mdb_protocol import (
    MessageKind,
    command_cancel,
    command_decision,
    command_session,
    command_status,
)
from mdb_state_store import MdbStateStore


MDB_SESSION_FUNDS_UNITS = 9900
VEND_SUCCESS_PENDING_FINALIZATION = "vend_success_pending_finalization"
BRIDGE_VEND_STATE = 4


def _now():
    return datetime.now().astimezone().isoformat(timespec="seconds")


class MdbSessionCoordinator:
    def __init__(
        self,
        send,
        notify=None,
        store=None,
        session_funds=MDB_SESSION_FUNDS_UNITS,
    ):
        self.send = send
        self.notify = notify or (lambda *_: None)
        self.store = store or MdbStateStore()
        self.session_funds = int(session_funds)
        self._lock = threading.RLock()
        self.boot_id = None
        self.reader_enabled = False
        self.session_open = False
        self.active = self.store.load()
        self._session_requested = False
        self.paused = False

    def start(self):
        self.send(command_status())
        if not self.active:
            return
        if self.active.get("state") == VEND_SUCCESS_PENDING_FINALIZATION:
            self.notify("vend_success", dict(self.active))
        else:
            self.notify("recovery", dict(self.active))

    def is_awaiting_payment(self):
        with self._lock:
            return bool(
                self.active
                and self.active.get("state") == "awaiting_payment"
            )

    def payment_started(self, provider):
        with self._lock:
            if not self.is_awaiting_payment():
                return False
            self.active["payment_provider"] = str(provider)
            self.active["payment_in_progress"] = True
            self.store.save(self.active)
            return True

    def update_payment_context(self, payment):
        with self._lock:
            if not self.active or not self.active.get("payment_in_progress"):
                return False
            self.active["payment"] = dict(payment or {})
            self.store.save(self.active)
            return True

    def payment_result(self, approved, payment=None, reason="payment_failed"):
        with self._lock:
            if not self.active:
                return False
            if self.active.get("state") != "awaiting_payment":
                if not self.active.get("payment_in_progress"):
                    return False
                self._store_payment_result(approved, payment)
                if approved:
                    self._mark_recovery("payment_completed_after_mdb_cancel")
                elif self.active.get("session_complete_seen"):
                    self._clear_active()
                    if self.reader_enabled:
                        self._request_session()
                    self.notify("cancelled_final", {"reason": reason})
                else:
                    self.store.save(self.active)
                return False

            self._store_payment_result(approved, payment)
            if approved:
                self.active["state"] = "waiting_vend_result"
                self.store.save(self.active)
                self.send(
                    command_decision(
                        True,
                        self.active["boot"],
                        self.active["vend"],
                    )
                )
                self.notify("awaiting_dispense", dict(self.active))
            else:
                self.active["state"] = "payment_failed"
                self.active["reason"] = reason
                self.store.save(self.active)
                self.send(
                    command_decision(
                        False,
                        self.active["boot"],
                        self.active["vend"],
                    )
                )
                self.send(
                    command_cancel(
                        self.active["boot"],
                        self.active["session"],
                    )
                )
                self.notify("payment_failed", dict(self.active))
            return True

    def complete_vend_success(self, boot_id, vend_id):
        """Clear durable state only after payment delivery is durably finalized."""
        with self._lock:
            if (
                not self.active
                or self.active.get("state") != VEND_SUCCESS_PENDING_FINALIZATION
                or self.active.get("boot") != str(boot_id)
                or self.active.get("vend") != int(vend_id)
            ):
                return False
            session_complete_seen = bool(
                self.active.get("session_complete_seen")
            )
            self._clear_active()
            if session_complete_seen and self.reader_enabled:
                self._request_session()
            return True

    def cancel_active(self, reason="customer_cancel"):
        with self._lock:
            if not self.is_awaiting_payment():
                return False
            if self.active.get("payment_in_progress"):
                self.active["state"] = "local_cancelled"
                self.active["reason"] = reason
                self.store.save(self.active)
                self.send(
                    command_decision(
                        False,
                        self.active["boot"],
                        self.active["vend"],
                    )
                )
                self.send(
                    command_cancel(
                        self.active["boot"],
                        self.active["session"],
                    )
                )
                self.notify("cancelled", dict(self.active))
                return True
            return self.payment_result(False, reason=reason)

    def pause(self, reason="local_control"):
        with self._lock:
            self.paused = True
            if self.is_awaiting_payment():
                self.payment_result(False, reason=reason)
            elif self.session_open:
                self.send(command_cancel())

    def resolve_recovery(self):
        """Operator action after checking any possibly charged payment."""
        with self._lock:
            if not self.active:
                return False
            self.send(command_cancel())
            self._clear_active()
            self.session_open = False
            self._session_requested = False
            if self.reader_enabled:
                self._request_session()
            self.notify("recovery_cleared", {})
            return True

    def transport_state(self, state, detail):
        self.notify("transport", {"state": state, "detail": detail})
        if state == "connected":
            self.send(command_status())

    def handle(self, message):
        with self._lock:
            handlers = {
                MessageKind.BOOT: self._boot,
                MessageKind.STATUS: self._status,
                MessageKind.READER_ENABLE: self._reader_enable,
                MessageKind.SESSION_BEGIN: self._session_begin,
                MessageKind.VEND_REQUEST: self._vend_request,
                MessageKind.VEND_CANCEL: self._vend_cancel,
                MessageKind.VEND_SUCCESS: self._vend_success,
                MessageKind.VEND_FAILURE: self._vend_failure,
                MessageKind.SESSION_COMPLETE: self._session_complete,
                MessageKind.RESET: self._reset,
            }
            handler = handlers.get(message.kind)
            if handler:
                handler(message)

    def _store_payment_result(self, approved, payment):
        self.active["payment"] = payment or {}
        self.active["payment_approved"] = bool(approved)
        self.active["payment_finished_at"] = _now()
        self.active["payment_in_progress"] = False

    def _boot(self, message):
        boot = message.text("boot")
        if (
            self.active
            and self.active.get("boot") != boot
            and self.active.get("state")
            != VEND_SUCCESS_PENDING_FINALIZATION
        ):
            self._mark_recovery("esp_rebooted_during_vend")
        self.boot_id = boot
        self.reader_enabled = False
        self.session_open = False
        self._session_requested = False

    def _status(self, message):
        boot = message.text("boot")
        if boot:
            if (
                self.active
                and self.active.get("boot") != boot
                and self.active.get("state")
                != VEND_SUCCESS_PENDING_FINALIZATION
            ):
                self._mark_recovery("esp_state_does_not_match_saved_vend")
            self.boot_id = boot
        self.reader_enabled = message.integer("reader", default=0) == 1
        self.session_open = message.integer("session_open", default=0) == 1
        self._reconcile_active_with_status(message)
        if (
            self.reader_enabled
            and not self.session_open
            and not self.active
            and not self.paused
        ):
            self._request_session()
        self.notify("status", dict(message.fields))

    def _reconcile_active_with_status(self, message):
        if not self.active or self.active.get("state") in (
            "recovery",
            VEND_SUCCESS_PENDING_FINALIZATION,
        ):
            return
        if self.active.get("state") not in (
            "awaiting_payment",
            "waiting_vend_result",
            "local_cancelled",
        ):
            return

        matching_vend = (
            message.integer("state", default=-1) == BRIDGE_VEND_STATE
            and self.session_open
            and message.text("boot") == self.active.get("boot")
            and message.integer("session", default=None)
            == self.active.get("session")
            and message.integer("vend", default=None)
            == self.active.get("vend")
        )
        if matching_vend:
            return

        self.active["bridge_status"] = dict(message.fields)
        self._mark_recovery("bridge_no_longer_reports_active_vend")

    def _reader_enable(self, message):
        self.boot_id = message.text("boot", self.boot_id)
        self.reader_enabled = True
        if not self.active and not self.paused:
            self._request_session()

    def _request_session(self):
        if self._session_requested or self.paused:
            return
        self._session_requested = True
        self.send(command_session(self.session_funds))

    def _session_begin(self, message):
        self.session_open = True
        self._session_requested = False
        self.notify(
            "ready",
            {"session": message.integer("session", default=0)},
        )

    def _vend_request(self, message):
        incoming = {
            "state": "awaiting_payment",
            "boot": message.text("boot"),
            "session": message.integer("session", required=True),
            "vend": message.integer("vend", required=True),
            "price_units": message.integer("price", required=True),
            "item": message.integer("item", required=True),
            "started_at": _now(),
        }
        if self.paused:
            self.send(
                command_decision(False, incoming["boot"], incoming["vend"])
            )
            return
        if self.active:
            same = (
                self.active.get("boot") == incoming["boot"]
                and self.active.get("vend") == incoming["vend"]
            )
            if same:
                return
            self.send(
                command_decision(False, incoming["boot"], incoming["vend"])
            )
            if (
                self.active.get("state")
                == VEND_SUCCESS_PENDING_FINALIZATION
            ):
                return
            self._mark_recovery("overlapping_vend_request")
            return
        self.active = incoming
        self.store.save(self.active)
        self.notify("vend_request", dict(self.active))

    def _matches_active(self, message):
        if not self.active:
            return False
        return (
            self.active.get("boot") == message.text("boot")
            and self.active.get("vend")
            == message.integer("vend", default=None)
        )

    def _vend_cancel(self, message):
        if not self._matches_active(message):
            return
        if self.active.get("state") == VEND_SUCCESS_PENDING_FINALIZATION:
            return
        if self.active.get("state") == "waiting_vend_result":
            self._mark_recovery("vmc_cancel_after_payment")
        else:
            self.active["state"] = "vmc_cancelled"
            self.active["reason"] = "vmc_cancel"
            self.store.save(self.active)
            self.notify("cancelled", dict(self.active))

    def _vend_success(self, message):
        if not self._matches_active(message):
            return
        if self.active.get("state") == VEND_SUCCESS_PENDING_FINALIZATION:
            return
        if self.active.get("state") != "waiting_vend_result":
            self._mark_recovery("vend_success_without_approved_payment")
            return
        self.active["state"] = VEND_SUCCESS_PENDING_FINALIZATION
        self.active["completed_at"] = _now()
        self.store.save(self.active)
        self.notify("vend_success", dict(self.active))

    def _vend_failure(self, message):
        if not self._matches_active(message):
            return
        if self.active.get("state") == VEND_SUCCESS_PENDING_FINALIZATION:
            return
        self.active["state"] = "vend_failed"
        self.active["reason"] = "vend_failure"
        self.store.save(self.active)
        self.notify("vend_failure", dict(self.active))

    def _session_complete(self, _message):
        self.session_open = False
        self._session_requested = False
        if self.active:
            if (
                self.active.get("payment_in_progress")
                or self.active.get("state")
                == VEND_SUCCESS_PENDING_FINALIZATION
            ):
                self.active["session_complete_seen"] = True
                self.store.save(self.active)
            elif self.active.get("state") not in (
                "payment_failed",
                "local_cancelled",
                "vmc_cancelled",
            ):
                self._mark_recovery("session_completed_with_unresolved_vend")
            else:
                self._clear_active()
        if self.reader_enabled and not self.active and not self.paused:
            self._request_session()
        self.notify("session_complete", {})

    def _reset(self, _message):
        self.reader_enabled = False
        self.session_open = False
        self._session_requested = False
        if (
            self.active
            and self.active.get("state")
            != VEND_SUCCESS_PENDING_FINALIZATION
        ):
            self._mark_recovery("vmc_reset_during_vend")

    def _mark_recovery(self, reason):
        already_reported = bool(
            self.active
            and self.active.get("state") == "recovery"
            and self.active.get("reason") == reason
        )
        if not self.active:
            self.active = {"state": "recovery", "started_at": _now()}
        self.active["state"] = "recovery"
        self.active["reason"] = reason
        self.active["recovery_at"] = _now()
        self.store.save(self.active)
        if not already_reported:
            self.notify("recovery", dict(self.active))

    def _clear_active(self):
        self.store.clear()
        self.active = None

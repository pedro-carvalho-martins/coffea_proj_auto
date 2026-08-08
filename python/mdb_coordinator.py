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


def _now():
    return datetime.now().astimezone().isoformat(timespec="seconds")


class MdbSessionCoordinator:
    def __init__(self, send, notify=None, store=None):
        self.send = send
        self.notify = notify or (lambda *_: None)
        self.store = store or MdbStateStore()
        self._lock = threading.RLock()
        self.boot_id = None
        self.reader_enabled = False
        self.session_open = False
        self.active = self.store.load()
        self._session_requested = False
        self.paused = False

    def start(self):
        self.send(command_status())
        if self.active:
            self.notify("recovery", dict(self.active))

    def is_awaiting_payment(self):
        with self._lock:
            return bool(self.active and self.active.get("state") == "awaiting_payment")

    def payment_started(self, provider):
        with self._lock:
            if not self.active or self.active.get("state") != "awaiting_payment":
                return False
            self.active["payment_provider"] = str(provider)
            self.active["payment_in_progress"] = True
            self.store.save(self.active)
            return True

    def pause(self, reason="local_control"):
        with self._lock:
            self.paused = True
            if self.active and self.active.get("state") == "awaiting_payment":
                self.payment_result(False, reason=reason)
            elif self.session_open:
                self.send(command_cancel())

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

    def payment_result(self, approved, payment=None, reason="payment_failed"):
        with self._lock:
            if not self.active:
                return False
            if self.active.get("state") != "awaiting_payment":
                if not self.active.get("payment_in_progress"):
                    return False
                self.active["payment_in_progress"] = False
                self.active["payment"] = payment or {}
                self.active["payment_finished_at"] = _now()
                if approved:
                    self._mark_recovery("payment_completed_after_mdb_cancel")
                elif self.active.get("session_complete_seen"):
                    self.store.clear()
                    self.active = None
                    if self.reader_enabled:
                        self._request_session()
                    self.notify("cancelled_final", {"reason": reason})
                else:
                    self.store.save(self.active)
                return False
            self.active["payment"] = payment or {}
            self.active["payment_finished_at"] = _now()
            self.active["payment_in_progress"] = False
            if approved:
                self.active["state"] = "waiting_vend_result"
                self.store.save(self.active)
                self.send(command_decision(True, self.active["boot"], self.active["vend"]))
                self.notify("awaiting_dispense", dict(self.active))
            else:
                self.active["state"] = "payment_failed"
                self.active["reason"] = reason
                self.store.save(self.active)
                self.send(command_decision(False, self.active["boot"], self.active["vend"]))
                self.send(command_cancel(self.active["boot"], self.active["session"]))
                self.notify("payment_failed", dict(self.active))
            return True

    def cancel_active(self, reason="timeout"):
        with self._lock:
            if not self.active or self.active.get("state") != "awaiting_payment":
                return False
            return self.payment_result(False, reason=reason)

    def resolve_recovery(self):
        """Operator action after checking any possibly charged payment."""
        with self._lock:
            if not self.active:
                return False
            self.send(command_cancel())
            self.store.clear()
            self.active = None
            self.session_open = False
            self._session_requested = False
            if self.reader_enabled:
                self._request_session()
            self.notify("recovery_cleared", {})
            return True

    def _boot(self, message):
        boot = message.text("boot")
        if self.active and self.active.get("boot") != boot:
            self._mark_recovery("esp_rebooted_during_vend")
        self.boot_id = boot
        self.reader_enabled = False
        self.session_open = False
        self._session_requested = False

    def _status(self, message):
        boot = message.text("boot")
        if boot:
            if self.active and self.active.get("boot") != boot:
                self._mark_recovery("esp_state_does_not_match_saved_vend")
            self.boot_id = boot
        self.reader_enabled = message.integer("reader", default=0) == 1
        self.session_open = message.integer("session_open", default=0) == 1
        if self.reader_enabled and not self.session_open and not self.active and not self.paused:
            self._request_session()
        self.notify("status", dict(message.fields))

    def _reader_enable(self, message):
        self.boot_id = message.text("boot", self.boot_id)
        self.reader_enabled = True
        if not self.active and not self.paused:
            self._request_session()

    def _request_session(self):
        if self._session_requested or self.paused:
            return
        self._session_requested = True
        self.send(command_session(65535))

    def _session_begin(self, message):
        self.session_open = True
        self._session_requested = False
        self.notify("ready", {"session": message.integer("session", default=0)})

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
            self.send(command_decision(False, incoming["boot"], incoming["vend"]))
            return
        if self.active:
            same = (
                self.active.get("boot") == incoming["boot"]
                and self.active.get("vend") == incoming["vend"]
            )
            if same:
                return
            self.send(command_decision(False, incoming["boot"], incoming["vend"]))
            self._mark_recovery("overlapping_vend_request")
            return
        self.active = incoming
        self.store.save(self.active)
        self.notify("vend_request", dict(self.active))

    def _matches_active(self, message):
        if not self.active:
            return False
        boot = message.text("boot")
        vend = message.integer("vend", default=None)
        return self.active.get("boot") == boot and self.active.get("vend") == vend

    def _vend_cancel(self, message):
        if not self._matches_active(message):
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
        if self.active.get("state") != "waiting_vend_result":
            self._mark_recovery("vend_success_without_approved_payment")
            return
        completed = dict(self.active)
        completed["state"] = "dispensed"
        completed["completed_at"] = _now()
        self.store.clear()
        self.active = None
        self.notify("vend_success", completed)

    def _vend_failure(self, message):
        if not self._matches_active(message):
            return
        self.active["state"] = "vend_failed"
        self.active["reason"] = "vend_failure"
        self.store.save(self.active)
        self.notify("vend_failure", dict(self.active))

    def _session_complete(self, message):
        self.session_open = False
        self._session_requested = False
        if self.active:
            if self.active.get("payment_in_progress"):
                self.active["session_complete_seen"] = True
                self.store.save(self.active)
            elif self.active.get("state") not in ("payment_failed", "vmc_cancelled"):
                self._mark_recovery("session_completed_with_unresolved_vend")
            else:
                self.store.clear()
                self.active = None
        if self.reader_enabled and not self.active and not self.paused:
            self._request_session()
        self.notify("session_complete", {})

    def _reset(self, message):
        self.reader_enabled = False
        self.session_open = False
        self._session_requested = False
        if self.active:
            self._mark_recovery("vmc_reset_during_vend")

    def _mark_recovery(self, reason):
        if not self.active:
            self.active = {"state": "recovery", "started_at": _now()}
        self.active["state"] = "recovery"
        self.active["reason"] = reason
        self.active["recovery_at"] = _now()
        self.store.save(self.active)
        self.notify("recovery", dict(self.active))

"""Background server pairing worker, independent from payment and GPIO code."""

import threading
import time
from datetime import datetime

import diagnosticLog
import paymentOutbox
import rwServerPairingSettings
import rwHelloSettingFile
import rwMACAddress
import rwPaymentMethodsList
import rwPulseCoinValue
import rwPricesList
import rwSystemId
import rwSystemName
import rwSystemVersion
import remoteCommandProcess
import shared_resource
from server_api_client import DeviceApiError, post_json


SYNC_INTERVAL_SECONDS = 300
REMOTE_DIAGNOSTIC_UPLOAD_ENABLED = False

_state_lock = threading.Lock()
_sync_lock = shared_resource.server_sync_lock
_worker_lock = threading.Lock()
_initial_sync_done = threading.Event()
_worker_started = False
_state = {
    "status": "not_checked",
    "last_contact": "Ainda não conectado",
    "last_error": "",
}


def get_pairing_state():
    with _state_lock:
        return dict(_state)


def _update_state(status, last_error="", contacted=False):
    with _state_lock:
        _state["status"] = status
        _state["last_error"] = last_error
        if contacted:
            _state["last_contact"] = datetime.now().strftime("%d/%m/%Y %H:%M")


def sync_once():
    """Send one pairing heartbeat unless offline operation is enabled."""
    with _sync_lock:
        try:
            if shared_resource.factory_reset_in_progress.is_set():
                _update_state("offline")
                return False
            if not rwServerPairingSettings.is_online_mode_enabled():
                _update_state("offline")
                return False

            pulse_value, pulse_duration_ms, pulse_interval_ms = (
                rwPulseCoinValue.readPulseCharacteristics()
            )
            pending_events = (
                []
                if (
                    not REMOTE_DIAGNOSTIC_UPLOAD_ENABLED
                    or shared_resource.customer_interaction_active.is_set()
                )
                else diagnosticLog.get_pending_events()
            )
            pending_transactions = (
                []
                if shared_resource.customer_interaction_active.is_set()
                else paymentOutbox.get_pending_transactions()
            )
            payload = {
                "sistema_pag_id": rwSystemId.readSystemId(),
                "sistema_pag_nome": rwSystemName.readSystemName(),
                "versao_sistema_pag": rwSystemVersion.readVersion(),
                "pairing_code": rwServerPairingSettings.get_pairing_code(),
                "settings": {
                    "prices": rwPricesList.readList(),
                    "payment_methods": {},
                    "moderninha_mac": rwMACAddress.readMACAddress(),
                    "pulse_value": pulse_value,
                    "pulse_duration_ms": pulse_duration_ms,
                    "pulse_interval_ms": pulse_interval_ms,
                    "hello_screen_enabled": bool(
                        rwHelloSettingFile.readListCheckHello()
                    ),
                },
                "command_results": [],
                "events": pending_events,
                "moderninha_transactions": pending_transactions,
            }
            current_methods = rwPaymentMethodsList.readListSettings()
            payload["settings"]["payment_methods"] = {
                method: current_methods.get(method) == "enabled"
                for method in remoteCommandProcess.SUPPORTED_PAYMENT_METHODS
            }
            pending_result = remoteCommandProcess.read_pending_result()
            if pending_result:
                payload["command_results"].append(pending_result)
            token = rwServerPairingSettings.read_pairing_token()
            response = post_json("/sync", payload, token)
        except DeviceApiError as exc:
            diagnosticLog.record_event(
                "warning",
                "server.sync_failed",
                "serverPairingProcess",
                str(exc),
                dedupe_key="server.sync_failed",
            )
            _update_state("connection_error", str(exc))
            return False
        except Exception as exc:
            diagnosticLog.record_exception(
                "server.sync_exception",
                "serverPairingProcess",
                exc,
                dedupe_key="server.sync_exception",
            )
            _update_state("connection_error", str(exc))
            return False
        finally:
            _initial_sync_done.set()

        status = response.get("status", "connection_error")
        _update_state(status, contacted=True)
        if status == "paired":
            acknowledged_event_ids = response.get("acknowledged_event_ids", [])
            diagnosticLog.acknowledge_events(acknowledged_event_ids)
            paymentOutbox.acknowledge_transactions(
                response.get("acknowledged_transaction_ids", [])
            )
            acknowledged_ids = {str(event_id) for event_id in acknowledged_event_ids}
            sync_failure = next(
                (
                    event
                    for event in pending_events
                    if event["code"] == "server.sync_failed"
                    and event["event_id"] in acknowledged_ids
                ),
                None,
            )
            if sync_failure:
                diagnosticLog.record_event(
                    "info",
                    "server.sync_restored",
                    "serverPairingProcess",
                    "Server connection restored",
                    context={
                        "failure_count": sync_failure["occurrence_count"],
                        "first_failure": sync_failure["first_seen"],
                        "last_failure": sync_failure["last_seen"],
                    },
                )
            if pending_result:
                remoteCommandProcess.clear_pending_result(pending_result["command_id"])
            for command in response.get("commands", []):
                remoteCommandProcess.process_command_if_safe(command)
        return status == "paired"


def wait_for_initial_sync(timeout=12):
    """Wait briefly for the startup heartbeat used by the connection screen."""
    _initial_sync_done.wait(timeout)
    return get_pairing_state()


def run_pairing_loop():
    """Synchronize immediately on startup, then every five minutes."""
    while True:
        try:
            sync_once()
        except Exception as exc:
            _update_state("connection_error", str(exc))
        time.sleep(SYNC_INTERVAL_SECONDS)


def start_pairing_worker():
    """Start a single daemon worker even if startup navigation is retried."""
    global _worker_started

    with _worker_lock:
        if _worker_started:
            return

        worker = threading.Thread(target=run_pairing_loop, daemon=True)
        worker.start()
        _worker_started = True

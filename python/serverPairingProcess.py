"""Background server pairing worker, independent from payment and GPIO code."""

import threading
import time
from datetime import datetime

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
import recordTransmissionProcess
import shared_resource
import localRecordQueue
import rwLogCSV
from server_api_client import DeviceApiError, post_json


SYNC_INTERVAL_SECONDS = 300

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
        transmit_records = True
        while True:
            paired, needs_confirmation = _sync_cycle(transmit_records)
            if not needs_confirmation:
                return paired
            transmit_records = False


def _sync_cycle(transmit_records):
    try:
        if shared_resource.factory_reset_in_progress.is_set():
            _update_state("offline")
            return False, False
        if not rwServerPairingSettings.is_online_mode_enabled():
            _update_state("offline")
            return False, False

        pulse_value, pulse_duration_ms, pulse_interval_ms = (
            rwPulseCoinValue.readPulseCharacteristics()
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
            "capabilities": ["command_batch_v1"],
        }
        current_methods = rwPaymentMethodsList.readListSettings()
        payload["settings"]["payment_methods"] = {
            method: current_methods.get(method) == "enabled"
            for method in remoteCommandProcess.SUPPORTED_PAYMENT_METHODS
        }
        pending_results = remoteCommandProcess.read_pending_results()
        payload["command_results"].extend(pending_results)
        token = rwServerPairingSettings.read_pairing_token()
        response = post_json("/sync", payload, token)
    except DeviceApiError as exc:
        _record_connection_failure(exc)
        return False, False
    except Exception as exc:
        _record_connection_failure(exc)
        return False, False
    finally:
        _initial_sync_done.set()

    status = response.get("status", "connection_error")
    _update_state(status, contacted=True)
    recovery = localRecordQueue.note_connection_restored()
    if recovery:
        rwLogCSV.writeCSV(
            "conexao_restaurada",
            "",
            "",
            "serverPairingProcess",
            "server_connection_restored",
            "duration_seconds={duration_seconds}; failed_attempts={failed_attempts}".format(
                **recovery
            ),
        )

    handled_commands = []
    if status == "paired":
        if pending_results:
            remoteCommandProcess.clear_pending_results(
                result["command_id"] for result in pending_results
            )
        if transmit_records and not shared_resource.customer_interaction_active.is_set():
            recordTransmissionProcess.transmit_pending_records()
        commands = response.get("commands", [])
        handled_count = remoteCommandProcess.process_commands_if_safe(commands)
        handled_commands = commands[:handled_count]

    needs_confirmation = _commands_need_confirmation(handled_commands)
    return status == "paired", needs_confirmation


def _commands_need_confirmation(handled_commands):
    if not handled_commands:
        return False
    return not any(
        command.get("type") == "reboot" for command in handled_commands
    )


def _record_connection_failure(error):
    _update_state("connection_error", str(error))
    if localRecordQueue.note_connection_failure():
        rwLogCSV.writeCSV(
            "erro_conexao",
            "",
            "",
            "serverPairingProcess",
            error.__class__.__name__,
            str(error),
        )


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

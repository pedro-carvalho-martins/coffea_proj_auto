"""Apply heartbeat-delivered commands only while the kiosk is safely idle."""

import json
import math
import os
import re
import subprocess
import threading

import rwPaymentMethodsList
import rwHelloSettingFile
import rwMACAddress
import rwPulseCoinValue
import rwPricesList
import rwSystemName
import shared_resource
from app_paths import REMOTE_COMMAND_RESULT_FILE, UPDATE_INPUT_FILE, ensure_parent_dir


SUPPORTED_PAYMENT_METHODS = ("Débito", "Crédito", "Voucher", "QR Code (Pix)")
UPDATE_TAG_PATTERN = re.compile(r"^[A-Za-z0-9._-]+$")
MAC_ADDRESS_PATTERN = re.compile(r"^(?:[0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$")
_result_lock = threading.Lock()


def read_pending_result():
    results = read_pending_results()
    return results[0] if results else None


def read_pending_results():
    with _result_lock:
        return _read_pending_results_unlocked()


def clear_pending_result(command_id):
    clear_pending_results([command_id])


def clear_pending_results(command_ids):
    acknowledged_ids = {str(command_id) for command_id in command_ids}
    with _result_lock:
        remaining = [
            result
            for result in _read_pending_results_unlocked()
            if str(result["command_id"]) not in acknowledged_ids
        ]
        if remaining:
            _write_json_atomic(REMOTE_COMMAND_RESULT_FILE, remaining)
        elif os.path.exists(REMOTE_COMMAND_RESULT_FILE):
            try:
                os.remove(REMOTE_COMMAND_RESULT_FILE)
            except OSError:
                return


def process_commands_if_safe(commands):
    handled_count = 0
    for command in commands:
        if not process_command_if_safe(command):
            break
        handled_count += 1
        if command.get("type") in {"reboot", "close_app"}:
            break
    return handled_count


def process_command_if_safe(command):
    with shared_resource.remote_command_gate_lock:
        if shared_resource.customer_interaction_active.is_set():
            return False

        command_id = str(command.get("command_id", ""))
        if not command_id:
            return False

        try:
            message, should_reboot = _apply_command(command)
            result = {
                "command_id": command_id,
                "status": "completed",
                "message": message,
            }
            _store_result(result)
            if should_reboot:
                _request_reboot()
        except Exception as exc:
            result = {
                "command_id": command_id,
                "status": "failed",
                "message": str(exc)[:500],
            }
            _store_result(result)
    return True


def _read_pending_results_unlocked():
    if not os.path.exists(REMOTE_COMMAND_RESULT_FILE):
        return []
    try:
        with open(REMOTE_COMMAND_RESULT_FILE, "r", encoding="utf-8") as file:
            stored = json.load(file)
    except (OSError, ValueError):
        return []

    # Releases before batching stored one result as a JSON object.
    if isinstance(stored, dict):
        stored = [stored]
    if not isinstance(stored, list):
        return []
    return [
        result
        for result in stored
        if isinstance(result, dict) and result.get("command_id")
    ]


def _store_result(result):
    with _result_lock:
        command_id = str(result["command_id"])
        results = [
            stored_result
            for stored_result in _read_pending_results_unlocked()
            if str(stored_result["command_id"]) != command_id
        ]
        results.append(result)
        _write_json_atomic(REMOTE_COMMAND_RESULT_FILE, results)


def _apply_command(command):
    command_type = command.get("type")
    payload = command.get("payload") or {}

    if command_type == "settings":
        mac_changed = _apply_settings(payload)
        if mac_changed:
            return (
                "Configurações aplicadas. O novo MAC será usado após reinicialização.",
                False,
            )
        return "Configurações aplicadas.", False
    if command_type == "update":
        tag = str(payload.get("tag", "")).strip()
        if not tag or len(tag) > 100 or not UPDATE_TAG_PATTERN.fullmatch(tag):
            raise ValueError("Tag de atualização inválida")
        _write_text_atomic(UPDATE_INPUT_FILE, f"True\n{tag}\n")
        return f"Atualização {tag} preparada para a próxima reinicialização.", False
    if command_type == "reboot":
        return "Reinicialização solicitada.", True
    if command_type == "close_app":
        return "Encerramento da aplicação solicitado.", False
    raise ValueError(f"Tipo de comando desconhecido: {command_type}")


def _apply_settings(payload):
    system_name = str(payload.get("system_name", "")).strip()
    prices = payload.get("prices")
    payment_methods = payload.get("payment_methods")
    moderninha_mac = str(payload.get("moderninha_mac", "")).strip().upper()
    pulse_value = payload.get("pulse_value")
    pulse_duration_ms = payload.get("pulse_duration_ms")
    pulse_interval_ms = payload.get("pulse_interval_ms")
    hello_screen_enabled = payload.get("hello_screen_enabled")

    if not system_name or len(system_name) > 120:
        raise ValueError("Nome do sistema inválido")
    if not isinstance(prices, list) or not 1 <= len(prices) <= 20:
        raise ValueError("Lista de preços inválida")
    normalized_prices = [float(price) for price in prices]
    if any(
        not math.isfinite(price) or price <= 0 or price > 100000
        for price in normalized_prices
    ):
        raise ValueError("Preço fora do intervalo permitido")
    if not isinstance(payment_methods, dict) or set(payment_methods) != set(SUPPORTED_PAYMENT_METHODS):
        raise ValueError("Métodos de pagamento inválidos")
    normalized_methods = {
        method: "enabled" if payment_methods[method] is True else "disabled"
        for method in SUPPORTED_PAYMENT_METHODS
    }
    if not MAC_ADDRESS_PATTERN.fullmatch(moderninha_mac):
        raise ValueError("Endereço MAC Moderninha inválido")
    normalized_pulse_value = float(pulse_value)
    if not math.isfinite(normalized_pulse_value) or normalized_pulse_value <= 0:
        raise ValueError("Valor do pulso inválido")
    normalized_pulse_duration = _positive_integer(
        pulse_duration_ms,
        "Duração do pulso",
    )
    normalized_pulse_interval = _positive_integer(
        pulse_interval_ms,
        "Intervalo entre pulsos",
    )
    if not isinstance(hello_screen_enabled, bool):
        raise ValueError("Configuração da tela inicial inválida")

    mac_changed = rwMACAddress.readMACAddress().upper() != moderninha_mac
    rwSystemName.writeSystemName(system_name)
    rwPricesList.writeListSettings(normalized_prices)
    rwPaymentMethodsList.writeListSettings(normalized_methods)
    rwMACAddress.writeMACAddress(moderninha_mac)
    rwPulseCoinValue.writePulseCharacteristics(
        [
            normalized_pulse_value,
            normalized_pulse_duration,
            normalized_pulse_interval,
        ]
    )
    rwHelloSettingFile.writeListSettings(
        {
            "Tela inicial": (
                "enabled" if hello_screen_enabled else "disabled"
            )
        }
    )
    return mac_changed


def _positive_integer(value, label):
    number = float(value)
    if not math.isfinite(number) or number <= 0 or not number.is_integer():
        raise ValueError(f"{label} inválido")
    return int(number)


def _request_reboot():
    subprocess.Popen(
        ["sudo", "-n", "/sbin/reboot"],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )


def _write_json_atomic(path, value):
    _write_text_atomic(path, json.dumps(value, ensure_ascii=False))


def _write_text_atomic(path, value):
    ensure_parent_dir(path)
    temporary_path = f"{path}.tmp"
    with open(temporary_path, "w", encoding="utf-8", newline="\n") as file:
        file.write(value)
        file.flush()
        os.fsync(file.fileno())
    os.replace(temporary_path, path)

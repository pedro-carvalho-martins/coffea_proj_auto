"""Apply heartbeat-delivered commands only while the kiosk is safely idle."""

import json
import math
import os
import re
import subprocess
import threading

import rwPaymentMethodsList
import rwPricesList
import rwSystemName
import shared_resource
from app_paths import REMOTE_COMMAND_RESULT_FILE, UPDATE_INPUT_FILE, ensure_parent_dir


SUPPORTED_PAYMENT_METHODS = ("Débito", "Crédito", "Voucher", "QR Code (Pix)")
UPDATE_TAG_PATTERN = re.compile(r"^[A-Za-z0-9._-]+$")
_result_lock = threading.Lock()


def read_pending_result():
    with _result_lock:
        if not os.path.exists(REMOTE_COMMAND_RESULT_FILE):
            return None
        try:
            with open(REMOTE_COMMAND_RESULT_FILE, "r", encoding="utf-8") as file:
                result = json.load(file)
        except (OSError, ValueError):
            return None
        if not isinstance(result, dict) or not result.get("command_id"):
            return None
        return result


def clear_pending_result(command_id):
    with _result_lock:
        if not os.path.exists(REMOTE_COMMAND_RESULT_FILE):
            return
        try:
            with open(REMOTE_COMMAND_RESULT_FILE, "r", encoding="utf-8") as file:
                current = json.load(file)
        except (OSError, ValueError):
            return
        if current.get("command_id") == command_id:
            try:
                os.remove(REMOTE_COMMAND_RESULT_FILE)
            except OSError:
                return


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
            _write_json_atomic(REMOTE_COMMAND_RESULT_FILE, result)
            if should_reboot:
                _request_reboot()
        except Exception as exc:
            result = {
                "command_id": command_id,
                "status": "failed",
                "message": str(exc)[:500],
            }
            _write_json_atomic(REMOTE_COMMAND_RESULT_FILE, result)
    return True


def _apply_command(command):
    command_type = command.get("type")
    payload = command.get("payload") or {}

    if command_type == "settings":
        _apply_settings(payload)
        return "Configurações aplicadas.", False
    if command_type == "update":
        tag = str(payload.get("tag", "")).strip()
        if not tag or len(tag) > 100 or not UPDATE_TAG_PATTERN.fullmatch(tag):
            raise ValueError("Tag de atualização inválida")
        _write_text_atomic(UPDATE_INPUT_FILE, f"True\n{tag}\n")
        return f"Atualização {tag} preparada para a próxima reinicialização.", False
    if command_type == "reboot":
        return "Reinicialização solicitada.", True
    raise ValueError(f"Tipo de comando desconhecido: {command_type}")


def _apply_settings(payload):
    system_name = str(payload.get("system_name", "")).strip()
    prices = payload.get("prices")
    payment_methods = payload.get("payment_methods")

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

    rwSystemName.writeSystemName(system_name)
    rwPricesList.writeListSettings(normalized_prices)
    rwPaymentMethodsList.writeListSettings(normalized_methods)


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

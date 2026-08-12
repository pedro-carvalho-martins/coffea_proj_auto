"""Durable, idempotent Pix delivery confirmation with immediate retries."""

import csv
import os
import time
from datetime import datetime

from app_paths import PENDING_PIX_DELIVERIES_FILE, ensure_parent_dir
import rwServerPairingSettings
import rwSystemId
from server_api_client import post_json
from shared_resource import file_lock


DELIVERY_FIELDS = (
    "txid",
    "outcome",
    "pulsos_esperados",
    "pulsos_concluidos",
    "pulsos_retentados",
    "erro_entrega",
    "datetime",
)
ACTIVE_RETRY_DELAYS_SECONDS = (0, 1, 2, 3)
CONFIRMATION_REQUEST_TIMEOUT_SECONDS = 3


def _now_iso():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _read_locked(file_path):
    if not os.path.isfile(file_path) or os.path.getsize(file_path) == 0:
        return []
    with open(file_path, "r", newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        if tuple(reader.fieldnames or ()) != DELIVERY_FIELDS:
            raise ValueError("Unexpected Pix delivery CSV header")
        return list(reader)


def _write_locked(file_path, records):
    ensure_parent_dir(file_path)
    temporary_path = file_path + ".tmp"
    with open(temporary_path, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=DELIVERY_FIELDS)
        writer.writeheader()
        writer.writerows(records)
        csv_file.flush()
        os.fsync(csv_file.fileno())
    os.replace(temporary_path, file_path)


def _build_record(
    txid,
    outcome,
    expected_pulses,
    completed_pulses,
    retried_pulses,
    error_message="",
):
    return {
        "txid": str(txid)[:100],
        "outcome": str(outcome)[:20],
        "pulsos_esperados": str(int(expected_pulses)),
        "pulsos_concluidos": str(int(completed_pulses)),
        "pulsos_retentados": str(int(retried_pulses)),
        "erro_entrega": str(error_message)[:500],
        "datetime": _now_iso(),
    }


def _persist_record(record, file_path):
    with file_lock:
        records = _read_locked(file_path)
        records = [item for item in records if item["txid"] != record["txid"]]
        records.append(record)
        _write_locked(file_path, records)


def queue_delivery_result(
    txid,
    outcome,
    expected_pulses,
    completed_pulses,
    retried_pulses,
    error_message="",
    file_path=None,
):
    file_path = file_path or PENDING_PIX_DELIVERIES_FILE
    record = _build_record(
        txid,
        outcome,
        expected_pulses,
        completed_pulses,
        retried_pulses,
        error_message,
    )
    _persist_record(record, file_path)
    return record


def read_pending(file_path=None):
    file_path = file_path or PENDING_PIX_DELIVERIES_FILE
    with file_lock:
        return _read_locked(file_path)


def acknowledge(txid, file_path=None):
    file_path = file_path or PENDING_PIX_DELIVERIES_FILE
    with file_lock:
        records = _read_locked(file_path)
        remaining = [record for record in records if record["txid"] != str(txid)]
        if len(remaining) == len(records):
            return False
        _write_locked(file_path, remaining)
        return True


def _payload(record):
    return {
        "sistema_pag_id": rwSystemId.readSystemId(),
        "outcome": record["outcome"],
        "pulsos_esperados": int(record["pulsos_esperados"]),
        "pulsos_concluidos": int(record["pulsos_concluidos"]),
        "pulsos_retentados": int(record["pulsos_retentados"]),
        "erro_entrega": record["erro_entrega"] or None,
    }


def _send(record):
    return post_json(
        f"/pix/charges/{record['txid']}/delivery",
        _payload(record),
        rwServerPairingSettings.read_pairing_token(),
        timeout=CONFIRMATION_REQUEST_TIMEOUT_SECONDS,
    )


def send_with_immediate_retries(record, file_path=None, sleep=None):
    file_path = file_path or PENDING_PIX_DELIVERIES_FILE
    sleep = sleep or time.sleep
    for delay in ACTIVE_RETRY_DELAYS_SECONDS:
        if delay:
            sleep(delay)
        try:
            _send(record)
        except Exception:
            continue
        try:
            acknowledge(record["txid"], file_path)
        except Exception:
            # The server confirmation succeeded; local cleanup can be retried later.
            pass
        return True
    return False


def report_delivery(
    txid,
    outcome,
    expected_pulses,
    completed_pulses,
    retried_pulses,
    error_message="",
    file_path=None,
):
    file_path = file_path or PENDING_PIX_DELIVERIES_FILE
    record = _build_record(
        txid,
        outcome,
        expected_pulses,
        completed_pulses,
        retried_pulses,
        error_message,
    )
    persistence_error = None
    try:
        _persist_record(record, file_path)
    except Exception as exc:
        persistence_error = exc

    confirmed = send_with_immediate_retries(record, file_path=file_path)
    if not confirmed and persistence_error is not None:
        raise persistence_error
    return confirmed


def transmit_pending(file_path=None, limit=10):
    file_path = file_path or PENDING_PIX_DELIVERIES_FILE
    transmitted = 0
    for record in read_pending(file_path)[:limit]:
        try:
            _send(record)
        except Exception:
            break
        acknowledge(record["txid"], file_path)
        transmitted += 1
    return transmitted

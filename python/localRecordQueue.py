"""Small durable CSV queues for records awaiting HTTPS ingestion."""

import csv
import os
import threading
import time
import uuid
from datetime import datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from app_paths import PENDING_EVENTS_FILE, PENDING_TRANSACTIONS_FILE, ensure_parent_dir
from shared_resource import file_lock


TRANSACTION_FIELDS = (
    "record_id",
    "datetime",
    "valor_centavos",
    "metodo_pag",
    "status",
)
EVENT_FIELDS = (
    "event_id",
    "datetime",
    "component",
    "error_code",
    "short_message",
    "version",
)
ERROR_COOLDOWN_SECONDS = 900

_error_state_lock = threading.Lock()
_last_error_times = {}
_connection_state_lock = threading.Lock()
_connection_offline_since = None
_connection_failed_attempts = 0


def _now_iso():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _append_row(file_path, fieldnames, row):
    ensure_parent_dir(file_path)
    with file_lock:
        file_exists = os.path.isfile(file_path) and os.path.getsize(file_path) > 0
        with open(file_path, "a", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow(row)


def _value_to_centavos(value):
    try:
        normalized = Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    except (InvalidOperation, ValueError) as exc:
        raise ValueError("Invalid transaction value") from exc
    if normalized < 0:
        raise ValueError("Transaction value cannot be negative")
    return int(normalized * 100)


def record_transaction(value, payment_method, status, file_path=None):
    record_id = str(uuid.uuid4())
    _append_row(
        file_path or PENDING_TRANSACTIONS_FILE,
        TRANSACTION_FIELDS,
        {
            "record_id": record_id,
            "datetime": _now_iso(),
            "valor_centavos": _value_to_centavos(value),
            "metodo_pag": str(payment_method)[:40],
            "status": str(status)[:20],
        },
    )
    return record_id


def should_record_error(component, error_code, message, now=None):
    current_time = time.monotonic() if now is None else now
    key = (str(component)[:100], str(error_code)[:100], str(message)[:300])
    with _error_state_lock:
        previous_time = _last_error_times.get(key)
        if previous_time is not None and current_time - previous_time < ERROR_COOLDOWN_SECONDS:
            return False
        _last_error_times[key] = current_time
    return True


def record_event(component, error_code, message, version, file_path=None):
    event_id = str(uuid.uuid4())
    _append_row(
        file_path or PENDING_EVENTS_FILE,
        EVENT_FIELDS,
        {
            "event_id": event_id,
            "datetime": _now_iso(),
            "component": str(component)[:100],
            "error_code": str(error_code)[:100],
            "short_message": str(message)[:500],
            "version": str(version)[:100],
        },
    )
    return event_id


def note_connection_failure(now=None):
    global _connection_offline_since, _connection_failed_attempts

    current_time = time.monotonic() if now is None else now
    with _connection_state_lock:
        first_failure = _connection_offline_since is None
        if first_failure:
            _connection_offline_since = current_time
        _connection_failed_attempts += 1
    return first_failure


def note_connection_restored(now=None):
    global _connection_offline_since, _connection_failed_attempts

    current_time = time.monotonic() if now is None else now
    with _connection_state_lock:
        if _connection_offline_since is None:
            return None
        duration_seconds = max(0, int(current_time - _connection_offline_since))
        failed_attempts = _connection_failed_attempts
        _connection_offline_since = None
        _connection_failed_attempts = 0
    return {
        "duration_seconds": duration_seconds,
        "failed_attempts": failed_attempts,
    }


def read_batch(file_path, fieldnames, limit=50):
    if limit <= 0:
        return []
    with file_lock:
        if not os.path.isfile(file_path) or os.path.getsize(file_path) == 0:
            return []
        with open(file_path, "r", newline="", encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file)
            if tuple(reader.fieldnames or ()) != tuple(fieldnames):
                raise ValueError("Unexpected pending CSV header")
            records = []
            for row in reader:
                records.append(row)
                if len(records) >= limit:
                    break
            return records


def acknowledge_records(file_path, fieldnames, id_field, accepted_ids):
    accepted = {str(record_id) for record_id in accepted_ids}
    if not accepted:
        return 0

    with file_lock:
        if not os.path.isfile(file_path) or os.path.getsize(file_path) == 0:
            return 0
        with open(file_path, "r", newline="", encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file)
            if tuple(reader.fieldnames or ()) != tuple(fieldnames):
                raise ValueError("Unexpected pending CSV header")
            rows = list(reader)

        remaining = [row for row in rows if row.get(id_field) not in accepted]
        removed = len(rows) - len(remaining)
        temporary_path = file_path + ".tmp"
        with open(temporary_path, "w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(remaining)
            csv_file.flush()
            os.fsync(csv_file.fileno())
        os.replace(temporary_path, file_path)
        return removed


def reset_runtime_state_for_tests():
    global _connection_offline_since, _connection_failed_attempts
    with _error_state_lock:
        _last_error_times.clear()
    with _connection_state_lock:
        _connection_offline_since = None
        _connection_failed_attempts = 0

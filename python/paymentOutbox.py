"""Durable Moderninha transaction outbox stored outside the application."""

import base64
import json
import sqlite3
import sys
import threading
import uuid
from contextlib import closing
from datetime import datetime, timezone

from app_paths import PAYMENT_OUTBOX_FILE, ensure_parent_dir


MAX_BATCH_TRANSACTIONS = 20
_database_lock = threading.Lock()


def _utc_now():
    return datetime.now(timezone.utc).isoformat()


def _connect():
    ensure_parent_dir(PAYMENT_OUTBOX_FILE)
    connection = sqlite3.connect(PAYMENT_OUTBOX_FILE, timeout=5)
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS payment_transactions (
            transaction_id TEXT PRIMARY KEY,
            created_at TEXT NOT NULL,
            completed_at TEXT,
            amount_centavos INTEGER NOT NULL,
            payment_method TEXT NOT NULL,
            status TEXT NOT NULL,
            details_json TEXT NOT NULL,
            user_reference TEXT NOT NULL UNIQUE
        )
        """
    )
    return connection


def begin_transaction(amount_centavos, payment_method):
    transaction_id = uuid.uuid4()
    user_reference = base64.b32encode(transaction_id.bytes).decode("ascii")[:10]

    try:
        with _database_lock:
            with closing(_connect()) as connection:
                with connection:
                    connection.execute(
                        """
                        INSERT INTO payment_transactions (
                            transaction_id,
                            created_at,
                            amount_centavos,
                            payment_method,
                            status,
                            details_json,
                            user_reference
                        ) VALUES (?, ?, ?, ?, 'pendente', '{}', ?)
                        """,
                        (
                            str(transaction_id),
                            _utc_now(),
                            int(amount_centavos),
                            payment_method,
                            user_reference,
                        ),
                    )
    except Exception as error:
        print(f"Could not create payment outbox record: {error}", file=sys.stderr)
        persisted = False
    else:
        persisted = True

    return {
        "transaction_id": str(transaction_id),
        "user_reference": user_reference,
        "persisted": persisted,
    }


def complete_transaction(transaction_id, status, details):
    try:
        with _database_lock:
            with closing(_connect()) as connection:
                with connection:
                    connection.execute(
                        """
                        UPDATE payment_transactions
                        SET completed_at = ?,
                            status = ?,
                            details_json = ?
                        WHERE transaction_id = ?
                        """,
                        (
                            _utc_now(),
                            status,
                            json.dumps(details or {}, ensure_ascii=False, default=str),
                            str(transaction_id),
                        ),
                    )
    except Exception as error:
        print(f"Could not complete payment outbox record: {error}", file=sys.stderr)


def mark_interrupted_transactions_unknown():
    """Finalize attempts left pending by a previous process interruption."""
    try:
        with _database_lock:
            with closing(_connect()) as connection:
                with connection:
                    connection.execute(
                        """
                        UPDATE payment_transactions
                        SET completed_at = ?,
                            status = 'resultado_desconhecido'
                        WHERE status = 'pendente'
                        """,
                        (_utc_now(),),
                    )
    except Exception as error:
        print(f"Could not recover interrupted payment records: {error}", file=sys.stderr)


def get_pending_transactions(limit=MAX_BATCH_TRANSACTIONS):
    try:
        with _database_lock:
            with closing(_connect()) as connection:
                rows = connection.execute(
                    """
                    SELECT
                        transaction_id,
                        created_at,
                        completed_at,
                        amount_centavos,
                        payment_method,
                        status,
                        details_json
                    FROM payment_transactions
                    WHERE status <> 'pendente'
                    ORDER BY created_at, transaction_id
                    LIMIT ?
                    """,
                    (min(int(limit), MAX_BATCH_TRANSACTIONS),),
                ).fetchall()
    except Exception as error:
        print(f"Could not read payment outbox: {error}", file=sys.stderr)
        return []

    return [
        {
            "transaction_id": row[0],
            "created_at": row[1],
            "completed_at": row[2],
            "amount_centavos": row[3],
            "payment_method": row[4],
            "status": row[5],
            "details": json.loads(row[6]),
        }
        for row in rows
    ]


def acknowledge_transactions(transaction_ids):
    normalized_ids = [str(transaction_id) for transaction_id in transaction_ids]
    if not normalized_ids:
        return

    placeholders = ", ".join("?" for _ in normalized_ids)
    try:
        with _database_lock:
            with closing(_connect()) as connection:
                with connection:
                    connection.execute(
                        f"DELETE FROM payment_transactions WHERE transaction_id IN ({placeholders})",
                        normalized_ids,
                    )
    except Exception as error:
        print(f"Could not acknowledge payment transactions: {error}", file=sys.stderr)

"""Small durable diagnostic outbox stored outside the replaceable application."""

import json
import sqlite3
import sys
import threading
import traceback as traceback_module
import uuid
from contextlib import closing
from datetime import datetime, timezone

from app_paths import DIAGNOSTIC_OUTBOX_FILE, ensure_parent_dir


MAX_PENDING_EVENTS = 2000
MAX_BATCH_EVENTS = 50
_database_lock = threading.Lock()
_hooks_installed = False


def _utc_now():
    return datetime.now(timezone.utc).isoformat()


def _connect():
    ensure_parent_dir(DIAGNOSTIC_OUTBOX_FILE)
    connection = sqlite3.connect(DIAGNOSTIC_OUTBOX_FILE, timeout=5)
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS diagnostic_events (
            event_id TEXT PRIMARY KEY,
            level TEXT NOT NULL,
            code TEXT NOT NULL,
            component TEXT NOT NULL,
            message TEXT NOT NULL,
            context_json TEXT NOT NULL,
            traceback TEXT NOT NULL,
            first_seen TEXT NOT NULL,
            last_seen TEXT NOT NULL,
            occurrence_count INTEGER NOT NULL,
            dedupe_key TEXT UNIQUE
        )
        """
    )
    return connection


def record_event(
    level,
    code,
    component,
    message,
    context=None,
    traceback_text="",
    dedupe_key=None,
):
    """Persist an event without allowing logging failures to interrupt the app."""
    event_id = str(uuid.uuid4())
    timestamp = _utc_now()
    normalized_context = json.dumps(context or {}, ensure_ascii=False, default=str)

    try:
        with _database_lock:
            with closing(_connect()) as connection:
                with connection:
                    if dedupe_key:
                        existing = connection.execute(
                            "SELECT event_id FROM diagnostic_events WHERE dedupe_key = ?",
                            (dedupe_key,),
                        ).fetchone()
                        if existing:
                            connection.execute(
                                """
                                UPDATE diagnostic_events
                                SET last_seen = ?,
                                    occurrence_count = occurrence_count + 1,
                                    message = ?,
                                    context_json = ?,
                                    traceback = ?
                                WHERE event_id = ?
                                """,
                                (
                                    timestamp,
                                    str(message)[:1000],
                                    normalized_context,
                                    str(traceback_text)[:8000],
                                    existing[0],
                                ),
                            )
                            return existing[0]

                    connection.execute(
                        """
                        INSERT INTO diagnostic_events (
                            event_id, level, code, component, message, context_json,
                            traceback, first_seen, last_seen, occurrence_count, dedupe_key
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?)
                        """,
                        (
                            event_id,
                            str(level)[:20],
                            str(code)[:100],
                            str(component)[:100],
                            str(message)[:1000],
                            normalized_context,
                            str(traceback_text)[:8000],
                            timestamp,
                            timestamp,
                            dedupe_key,
                        ),
                    )
                    _trim_outbox(connection)
        return event_id
    except Exception as error:
        print(f"Diagnostic logging failed: {type(error).__name__}: {error}", file=sys.stderr)
        return None


def record_exception(code, component, error, context=None, dedupe_key=None):
    return record_event(
        "error",
        code,
        component,
        str(error) or type(error).__name__,
        context=context,
        traceback_text="".join(
            traceback_module.format_exception(type(error), error, error.__traceback__)
        ),
        dedupe_key=dedupe_key,
    )


def get_pending_events(limit=MAX_BATCH_EVENTS):
    try:
        with _database_lock:
            with closing(_connect()) as connection:
                rows = connection.execute(
                    """
                    SELECT
                        event_id, level, code, component, message, context_json,
                        traceback, first_seen, last_seen, occurrence_count
                    FROM diagnostic_events
                    ORDER BY first_seen, event_id
                    LIMIT ?
                    """,
                    (min(int(limit), MAX_BATCH_EVENTS),),
                ).fetchall()
    except Exception as error:
        print(f"Could not read diagnostic outbox: {type(error).__name__}: {error}", file=sys.stderr)
        return []

    return [
        {
            "event_id": row[0],
            "level": row[1],
            "code": row[2],
            "component": row[3],
            "message": row[4],
            "context": json.loads(row[5]),
            "traceback": row[6],
            "first_seen": row[7],
            "last_seen": row[8],
            "occurrence_count": row[9],
        }
        for row in rows
    ]


def acknowledge_events(event_ids):
    normalized_ids = [str(event_id) for event_id in event_ids]
    if not normalized_ids:
        return

    placeholders = ", ".join("?" for _ in normalized_ids)
    try:
        with _database_lock:
            with closing(_connect()) as connection:
                with connection:
                    connection.execute(
                        f"DELETE FROM diagnostic_events WHERE event_id IN ({placeholders})",
                        normalized_ids,
                    )
    except Exception as error:
        print(f"Could not acknowledge diagnostic events: {type(error).__name__}: {error}", file=sys.stderr)


def _trim_outbox(connection):
    event_count = connection.execute(
        "SELECT COUNT(*) FROM diagnostic_events"
    ).fetchone()[0]
    excess = event_count - MAX_PENDING_EVENTS
    if excess <= 0:
        return

    connection.execute(
        """
        DELETE FROM diagnostic_events
        WHERE event_id IN (
            SELECT event_id
            FROM diagnostic_events
            ORDER BY
                CASE level
                    WHEN 'info' THEN 1
                    WHEN 'warning' THEN 2
                    WHEN 'error' THEN 3
                    ELSE 4
                END,
                first_seen
            LIMIT ?
        )
        """,
        (excess,),
    )


def report_tkinter_exception(exception_type, exception_value, exception_traceback):
    _record_exception_parts(
        "ui.tkinter_callback_exception",
        "tkinter",
        exception_type,
        exception_value,
        exception_traceback,
    )


def _record_exception_parts(
    code,
    component,
    exception_type,
    exception_value,
    exception_traceback,
):
    record_event(
        "error",
        code,
        component,
        str(exception_value) or exception_type.__name__,
        traceback_text="".join(
            traceback_module.format_exception(
                exception_type,
                exception_value,
                exception_traceback,
            )
        ),
    )


def install_exception_hooks():
    global _hooks_installed
    if _hooks_installed:
        return

    previous_sys_hook = sys.excepthook
    previous_thread_hook = getattr(threading, "excepthook", None)

    def handle_uncaught(exception_type, exception_value, exception_traceback):
        _record_exception_parts(
            "process.uncaught_exception",
            "main",
            exception_type,
            exception_value,
            exception_traceback,
        )
        previous_sys_hook(exception_type, exception_value, exception_traceback)

    def handle_thread_uncaught(arguments):
        record_event(
            "error",
            "thread.uncaught_exception",
            arguments.thread.name if arguments.thread else "unknown_thread",
            str(arguments.exc_value) or arguments.exc_type.__name__,
            traceback_text="".join(
                traceback_module.format_exception(
                    arguments.exc_type,
                    arguments.exc_value,
                    arguments.exc_traceback,
                )
            ),
        )
        if previous_thread_hook:
            previous_thread_hook(arguments)

    sys.excepthook = handle_uncaught
    if previous_thread_hook:
        threading.excepthook = handle_thread_uncaught
    _hooks_installed = True

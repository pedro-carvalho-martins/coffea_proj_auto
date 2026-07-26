"""Persistent settings used to pair this payment system with the server."""

import os
import secrets
import threading

from app_paths import (
    SERVER_PAIRING_MODE_FILE,
    SERVER_PAIRING_TOKEN_FILE,
    ensure_parent_dir,
)


_token_lock = threading.Lock()


def read_pairing_token():
    """Return the device token, creating it once for a fresh installation."""
    with _token_lock:
        if os.path.exists(SERVER_PAIRING_TOKEN_FILE):
            with open(SERVER_PAIRING_TOKEN_FILE, "r", encoding="utf-8") as file:
                token = file.readline().strip()
            if token:
                return token

        token = secrets.token_urlsafe(32)
        ensure_parent_dir(SERVER_PAIRING_TOKEN_FILE)
        with open(SERVER_PAIRING_TOKEN_FILE, "w", encoding="utf-8") as file:
            file.write(token)
        return token


def get_pairing_code():
    """Return a stable six-digit code used only for visual confirmation."""
    token = read_pairing_token()
    token_prefix = token.encode("utf-8")[:8]
    return f"{int.from_bytes(token_prefix, 'big') % 1_000_000:06d}"


def is_online_mode_enabled():
    if not os.path.exists(SERVER_PAIRING_MODE_FILE):
        return True

    with open(SERVER_PAIRING_MODE_FILE, "r", encoding="utf-8") as file:
        return file.readline().strip().lower() != "offline"


def set_online_mode_enabled(enabled):
    ensure_parent_dir(SERVER_PAIRING_MODE_FILE)
    mode = "online" if enabled else "offline"
    with open(SERVER_PAIRING_MODE_FILE, "w", encoding="utf-8") as file:
        file.write(mode)

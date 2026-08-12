"""Atomic persistence for the one in-flight MDB vend."""

import json
import os
import threading

from app_paths import MDB_ACTIVE_STATE_FILE, ensure_parent_dir


class MdbStateStore:
    def __init__(self, path=MDB_ACTIVE_STATE_FILE):
        self.path = path
        self._lock = threading.Lock()

    def load(self):
        with self._lock:
            try:
                with open(self.path, "r", encoding="utf-8") as state_file:
                    value = json.load(state_file)
            except FileNotFoundError:
                return None
            except (OSError, ValueError):
                return {"state": "recovery", "reason": "invalid_state_file"}
        if isinstance(value, dict):
            return value
        return {"state": "recovery", "reason": "invalid_state_file"}

    def save(self, state):
        ensure_parent_dir(self.path)
        temporary = self.path + ".tmp"
        with self._lock:
            with open(temporary, "w", encoding="utf-8", newline="\n") as state_file:
                json.dump(state, state_file, ensure_ascii=True, sort_keys=True)
                state_file.write("\n")
                state_file.flush()
                os.fsync(state_file.fileno())
            os.replace(temporary, self.path)

    def clear(self):
        with self._lock:
            try:
                os.remove(self.path)
            except FileNotFoundError:
                pass

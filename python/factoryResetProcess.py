"""Reset local kiosk settings without touching application data or logs."""

import os
import shutil
import subprocess

import shared_resource
from app_paths import SETTINGS_DIR


EXPECTED_SETTINGS_DIR = "/home/pi/coffeapag/settings"


def reset_settings_and_reboot():
    """Remove the validated settings directory, recreate it, and reboot."""
    shared_resource.factory_reset_in_progress.set()

    with shared_resource.server_sync_lock:
        _reset_settings_directory()

    _request_reboot()


def _reset_settings_directory():
    target = os.path.normcase(os.path.realpath(SETTINGS_DIR))
    expected = os.path.normcase(os.path.realpath(EXPECTED_SETTINGS_DIR))
    if target != expected:
        raise RuntimeError("Diretório de configurações inesperado; reset cancelado")

    if os.path.lexists(SETTINGS_DIR):
        if os.path.islink(SETTINGS_DIR) or not os.path.isdir(SETTINGS_DIR):
            raise RuntimeError("Diretório de configurações inválido; reset cancelado")
        shutil.rmtree(SETTINGS_DIR)

    os.makedirs(SETTINGS_DIR, exist_ok=True)


def _request_reboot():
    subprocess.Popen(
        ["sudo", "-n", "/sbin/reboot"],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )

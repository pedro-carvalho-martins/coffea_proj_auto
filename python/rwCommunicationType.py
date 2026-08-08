"""Read and write the local vending-machine communication mode."""

import os

from app_paths import COMMUNICATION_TYPE_FILE, ensure_parent_dir


PULSE = "pulso"
MDB = "mdb"
SUPPORTED_TYPES = (PULSE, MDB)


def readCommunicationType():
    if not os.path.exists(COMMUNICATION_TYPE_FILE):
        writeCommunicationType(PULSE)
        return PULSE

    try:
        with open(COMMUNICATION_TYPE_FILE, "r", encoding="utf-8") as file:
            value = file.readline().strip().casefold()
    except OSError:
        return PULSE
    return value if value in SUPPORTED_TYPES else PULSE


def writeCommunicationType(value):
    normalized = str(value).strip().casefold()
    if normalized not in SUPPORTED_TYPES:
        raise ValueError("Tipo de comunicação inválido")

    ensure_parent_dir(COMMUNICATION_TYPE_FILE)
    temporary_path = COMMUNICATION_TYPE_FILE + ".tmp"
    with open(temporary_path, "w", encoding="utf-8", newline="\n") as file:
        file.write(normalized + "\n")
        file.flush()
        os.fsync(file.fileno())
    os.replace(temporary_path, COMMUNICATION_TYPE_FILE)


def isMdbEnabled():
    return readCommunicationType() == MDB

import os
import uuid

from app_paths import SYSTEM_ID_FILE, ensure_parent_dir


system_id_filename = SYSTEM_ID_FILE


def createSystemIdFile():
    """Creates systemId.txt with a new UUID value."""
    system_id_str = str(uuid.uuid4())
    ensure_parent_dir(system_id_filename)

    with open(system_id_filename, "w", encoding="utf-8") as file:
        file.write(system_id_str)

    print(f"{system_id_filename} created with system ID: {system_id_str}")
    return system_id_str


def readSystemId():
    print("read System ID BEGINS")

    if not os.path.exists(system_id_filename):
        return createSystemIdFile()

    with open(system_id_filename, "r", encoding="utf-8") as systemIdFile:
        system_id_str = systemIdFile.readline().strip()

    if not system_id_str:
        return createSystemIdFile()

    return system_id_str


def writeSystemId(system_id_str):
    ensure_parent_dir(system_id_filename)

    with open(system_id_filename, "w", encoding="utf-8") as systemIdFile:
        systemIdFile.write(system_id_str)


if __name__ == "__main__":
    print(readSystemId())

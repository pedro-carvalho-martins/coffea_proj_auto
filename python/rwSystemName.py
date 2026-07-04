import os
from app_paths import SYSTEM_NAME_FILE, ensure_parent_dir

# Global file path and default content
system_name_filename = SYSTEM_NAME_FILE
DEFAULT_SYSTEM_NAME = "Coffea_Default_000"


def createSystemNameFile():
    """Creates systemName.txt with the default system name."""
    ensure_parent_dir(system_name_filename)
    with open(system_name_filename, "w", encoding="utf-8") as file:
        file.write(DEFAULT_SYSTEM_NAME)
    print(f"{system_name_filename} created with default system name: {DEFAULT_SYSTEM_NAME}")


def readSystemName():
    print("read System Name BEGINS")

    if not os.path.exists(system_name_filename):
        createSystemNameFile()

    with open(system_name_filename, "r", encoding="utf-8") as systemNameFile:
        system_name_str = systemNameFile.readline().strip()

    return system_name_str


def writeSystemName(system_name_str):
    ensure_parent_dir(system_name_filename)
    with open(system_name_filename, "w", encoding="utf-8") as systemNameFile:
        systemNameFile.write(system_name_str)


if __name__ == "__main__":
    print(readSystemName())

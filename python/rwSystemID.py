
import os

# Global file path and default content
system_id_filename = './settings_files/systemID.txt'
DEFAULT_SYSTEM_ID = "Coffea_Default_000"

def createSystemIDFile():
    """Creates systemID.txt with default system ID."""
    with open(system_id_filename, 'w', encoding='utf-8') as file:
        file.write(DEFAULT_SYSTEM_ID)
    print(f"{system_id_filename} created with default ID: {DEFAULT_SYSTEM_ID}")

def readSystemID():
    print("read System ID BEGINS")

    if not os.path.exists(system_id_filename):
        createSystemIDFile()

    with open(system_id_filename, "r", encoding='utf-8') as SystemIDFile:
        SystemID_str = SystemIDFile.readline().strip()

    return SystemID_str

def writeSystemID(SystemID_str):
    with open(system_id_filename, "w", encoding='utf-8') as SystemIDFile:
        SystemIDFile.write(SystemID_str)

if __name__ == "__main__":
    print(readSystemID())
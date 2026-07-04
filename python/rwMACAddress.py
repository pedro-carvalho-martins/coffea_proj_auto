import os
from app_paths import MAC_ADDRESS_FILE, ensure_parent_dir

# Global config
mac_filename = MAC_ADDRESS_FILE
DEFAULT_MAC_CONTENT = "00:00:00:00:00:00"

def createMACFile():
    """Creates the MAC address file with default content."""
    ensure_parent_dir(mac_filename)
    with open(mac_filename, 'w', encoding='utf-8') as file:
        file.write(DEFAULT_MAC_CONTENT)
    print(f"{mac_filename} created with default MAC address.")

def readMACAddress():
    print("read MAC BEGINS")

    if not os.path.exists(mac_filename):
        createMACFile()

    with open(mac_filename, "r", encoding='utf-8') as MACFile:
        MAC_address = MACFile.readline().strip()

    return MAC_address

def writeMACAddress(MAC_address):
    ensure_parent_dir(mac_filename)
    with open(mac_filename, "w", encoding='utf-8') as MACFile:
        MACFile.write(MAC_address)

if __name__ == "__main__":
    print(readMACAddress())

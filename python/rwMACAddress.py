import os

# Global config
mac_filename = './settings_files/enderecoMAC.txt'
DEFAULT_MAC_CONTENT = "00:00:00:00:00:00"

def createMACFile():
    """Creates the MAC address file with default content."""
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
    with open(mac_filename, "w", encoding='utf-8') as MACFile:
        MACFile.write(MAC_address)

if __name__ == "__main__":
    print(readMACAddress())
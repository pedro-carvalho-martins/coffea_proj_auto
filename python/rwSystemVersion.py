
import os

# Global file path
system_version_filename = './settings_files/version.txt'

def readVersion():
    print("read system version BEGINS")

    with open(system_version_filename, "r", encoding='utf-8') as SystemVersionFile:
        SystemVersion_str = SystemVersionFile.readline().strip()

    return SystemVersion_str

if __name__ == "__main__":
    print(readVersion())

import os

# Global file path and default content
pulse_coin_filename = './settings_files/pulseCoinValue.txt'
DEFAULT_PULSE_COIN_VALUE = "0.25"

def createPulseCoinFile():
    """Creates pulseCoinValue.txt with default coin value."""
    with open(pulse_coin_filename, 'w', encoding='utf-8') as file:
        file.write(DEFAULT_PULSE_COIN_VALUE)
    print(f"{pulse_coin_filename} created with default value {DEFAULT_PULSE_COIN_VALUE}.")

def readPulseCoinValue():
    print("read pulse coin value BEGINS")

    if not os.path.exists(pulse_coin_filename):
        createPulseCoinFile()

    with open(pulse_coin_filename, "r", encoding='utf-8') as pulseCoinValueFile:
        pulseCoinValue_float = float(pulseCoinValueFile.readline().strip())

    return pulseCoinValue_float

def writePulseCoinValue(pulseCoinValue):
    with open(pulse_coin_filename, "w", encoding='utf-8') as pulseCoinValueFile:
        pulseCoinValueFile.write(str(pulseCoinValue))

if __name__ == "__main__":
    print(readPulseCoinValue())

import os

# Global file path and default content
pulse_coin_filename = './settings_files/pulseCoinValue.txt'
DEFAULT_PULSE_COIN_VALUE = """0.25
100
400"""

def createPulseCoinFile():
    """Creates pulseCoinValue.txt with default coin value."""
    with open(pulse_coin_filename, 'w', encoding='utf-8') as file:
        file.write(DEFAULT_PULSE_COIN_VALUE)
    print(f"{pulse_coin_filename} created with default values.")

def readPulseCharacteristics():
    print("read pulse coin value BEGINS")

    if not os.path.exists(pulse_coin_filename):
        createPulseCoinFile()

    with open(pulse_coin_filename, "r", encoding='utf-8') as pulseCoinValueFile:
        pulseCharacteristicsList = pulseCoinValueFile.readlines()

    if len(pulseCharacteristicsList) < 3:
        createPulseCoinFile()
        with open(pulse_coin_filename, "r", encoding='utf-8') as pulseCoinValueFile:
            pulseCharacteristicsList = pulseCoinValueFile.readlines()

    pulseCoinValue_float = float(pulseCharacteristicsList[0].strip())
    pulse_duration_int = float(pulseCharacteristicsList[1].strip())
    pulse_sleep_interval_int = float(pulseCharacteristicsList[2].strip())

    return pulseCoinValue_float, pulse_duration_int, pulse_sleep_interval_int

def writePulseCharacteristics(pulseCharacteristicsList):
    outString = ""

    for item in pulseCharacteristicsList:
        outString += str(item) + '\n'

    print(outString)

    with open(pulse_coin_filename, "w", encoding='utf-8') as pulseFile:
        pulseFile.write(outString)

if __name__ == "__main__":
    print(readPulseCharacteristics())
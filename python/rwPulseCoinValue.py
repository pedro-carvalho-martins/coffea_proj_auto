
def readPulseCoinValue():

    print("read pulse coin value BEGINS")

    pulseCoinValueFile= open('./settings_files/pulseCoinValue.txt', "r", encoding='utf-8')
    pulseCoinValue_float = float(pulseCoinValueFile.readline())

    return pulseCoinValue_float


def writePulseCoinValue(pulseCoinValue):

    pulseCoinValueFile= open('./settings_files/pulseCoinValue.txt', "w", encoding='utf-8')

    pulseCoinValueFile.write(str(pulseCoinValue))

    pulseCoinValueFile.close()



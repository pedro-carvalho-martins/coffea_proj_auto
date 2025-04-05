import os

filename = './settings_files/paymentMethods.txt'

DEFAULT_FILE_CONTENT =\
    """Débito
    Crédito
    #Voucher
    QR Code (Pix)"""

def createNewFile(filename):
    # Creates the payment methods file with default content
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(DEFAULT_FILE_CONTENT)
    print(f"{filename} created with default content.")

def readListDisplay():
    print("readList BEGINS")

    if not os.path.exists(filename):
        createNewFile()

    with open(filename, "r", encoding='utf-8') as pMethodsFile:
        pMethods = pMethodsFile.readlines()

    for lineIndex in range(len(pMethods)-1, -1, -1):
        pMethods[lineIndex] = pMethods[lineIndex].strip()

        if pMethods[lineIndex][0] == '#':
            del pMethods[lineIndex]

    print(pMethods)
    print("readList ENDS")
    return pMethods

def readListSettings():
    print("readList BEGINS")

    if not os.path.exists(filename):
        createNewFile()

    with open(filename, "r", encoding='utf-8') as pMethodsFile:
        pMethods = pMethodsFile.readlines()

    pMethodsDict = {}

    for line in pMethods:
        line = line.strip()
        if line[0] == '#':
            pMethodsDict[line[1:]] = "disabled"
        else:
            pMethodsDict[line] = "enabled"

    print(pMethodsDict)
    print("readList ENDS")
    return pMethodsDict

def writeListSettings(pMethodsDict):
    outString = ""
    for item, status in pMethodsDict.items():
        if status == "enabled":
            outString += item + '\n'
        else:
            outString += "#" + item + '\n'

    print(outString)

    with open(filename, "w", encoding='utf-8') as pMethodsFile:
        pMethodsFile.write(outString)


if __name__ == "__main__":
    readListSettings()
    readListDisplay()

# #TESTES READ:
#
# readListSettings()
# readListDisplay()
#
# #TESTE WRITE:
#
# pMethodsDict = {'Crédito': 'enabled', 'Débito': 'disabled', 'Voucher': 'enabled', 'QR Code (Pix)': 'disabled'}
# writeListSettings(pMethodsDict)
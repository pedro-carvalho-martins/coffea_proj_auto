def readListDisplay():
    
    print("readList BEGINS")

    pMethodsFile = open('./settings_files/paymentMethods.txt', "r", encoding='utf-8')
    pMethods = pMethodsFile.readlines()
    for lineIndex in range(len(pMethods)-1,-1,-1):

        # Removes \n
        pMethods[lineIndex] = pMethods[lineIndex].split("\n")[0]

        # Removes items starting with '#'
        if pMethods[lineIndex][0] == '#':
            del pMethods[lineIndex]


    print(pMethods)

    print("readList ENDS")

    return pMethods


def readListSettings():

    print("readList BEGINS")

    pMethodsFile = open('./settings_files/paymentMethods.txt', "r", encoding='utf-8')
    pMethods = pMethodsFile.readlines()
    pMethodsDict = {}

    for lineIndex in range(len(pMethods)):

        # Removes \n
        pMethods[lineIndex] = pMethods[lineIndex].split("\n")[0]

        # Treats items starting with '#' and adds items to dictionary
        if pMethods[lineIndex][0] == '#':
            pMethodsDict[pMethods[lineIndex][1:]] = "disabled"
        else:
            pMethodsDict[pMethods[lineIndex]] = "enabled"


    print(pMethodsDict)

    print("readList ENDS")

    return pMethods

def writeListSettings(pMethodsDict):

    pMethods = pMethodsDict.items()

    outString=""

    for item in pMethods:
        if item[1] == "enabled":
            outString = outString + item[0] + '\n'
        else:
            outString = outString + "#" + item[0] + '\n'

    print(outString)

    pMethodsFile = open('./settings_files/paymentMethods.txt', "w", encoding='utf-8')

    pMethodsFile.write(outString)

    pMethodsFile.close()

#TESTES READ:

#readListSettings()
#readListDisplay()

#TESTE WRITE:

#pMethodsDict = {'Crédito': 'enabled', 'Débito': 'disabled', 'Voucher': 'enabled', 'QR Code (Pix)': 'disabled'}
#writeListSettings(pMethodsDict)
# Construir baseado no rwPaymentMethodsList

def readList():

    print("readList BEGINS")

    pricesFile = open('./settings_files/listaPrecos.txt', "r", encoding='utf-8')
    priceList = pricesFile.readlines()
    for lineIndex in range(len(priceList)):

        # Removes \n
        priceList[lineIndex] = priceList[lineIndex].split("\n")[0]

        priceList[lineIndex] = float(priceList[lineIndex])

    print(priceList)

    print("readList ENDS")

    return priceList


def writeListSettings(priceList):

    outString=""

    for item in priceList:
        outString = outString + str(item) + '\n'

    print(outString)

    pMethodsFile = open('./settings_files/listaPrecos.txt', "w", encoding='utf-8')

    pMethodsFile.write(outString)

    pMethodsFile.close()






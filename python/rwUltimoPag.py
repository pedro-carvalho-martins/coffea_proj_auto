
def readValue():

    print("readUltimoValor BEGINS")

    ultimoPagFile = open('./settings_files/ultimoPagamento.txt', "r", encoding='utf-8')
    ultimoValor = float(ultimoPagFile.readlines()[0])

    print(ultimoValor)

    # for lineIndex in range(len(priceList)):
    #
    #     # Removes \n
    #     priceList[lineIndex] = priceList[lineIndex].split("\n")[0]
    #
    #     priceList[lineIndex] = float(priceList[lineIndex])
    #
    # print(priceList)

    print("readUltimoValor ENDS")

    return ultimoValor


def writeValue(lastValue):

    outString=str(lastValue)

    print(outString)

    pMethodsFile = open('./settings_files/ultimoPagamento.txt', "w", encoding='utf-8')

    pMethodsFile.write(outString)

    pMethodsFile.close()



readValue()


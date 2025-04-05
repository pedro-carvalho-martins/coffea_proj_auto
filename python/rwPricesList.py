import os

# Global filename and default contents
price_list_filename = './settings_files/listaPrecos.txt'
DEFAULT_PRICE_LIST = """4.0
3.0
1.5"""

def createPriceListFile():
    """Creates listaPrecos.txt with default price values."""
    with open(price_list_filename, 'w', encoding='utf-8') as file:
        file.write(DEFAULT_PRICE_LIST)
    print(f"{price_list_filename} created with default price list.")

def readList():
    print("readList BEGINS")

    if not os.path.exists(price_list_filename):
        createPriceListFile()

    with open(price_list_filename, "r", encoding='utf-8') as pricesFile:
        priceList = pricesFile.readlines()

    for lineIndex in range(len(priceList)):
        priceList[lineIndex] = priceList[lineIndex].strip()
        priceList[lineIndex] = float(priceList[lineIndex])

    print(priceList)
    print("readList ENDS")

    return priceList

def writeListSettings(priceList):
    outString = ""

    for item in priceList:
        outString += str(item) + '\n'

    print(outString)

    with open(price_list_filename, "w", encoding='utf-8') as pricesFile:
        pricesFile.write(outString)

if __name__ == "__main__":
    print(readList())
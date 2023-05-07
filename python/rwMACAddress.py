
def readMACAddress():

    print("read MAC BEGINS")

    MACFile = open('./settings_files/enderecoMAC.txt', "r", encoding='utf-8')
    MAC_address = MACFile.readline()

    return MAC_address


def writeMACAddress(MAC_address):

    pass




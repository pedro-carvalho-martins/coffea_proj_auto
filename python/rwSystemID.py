
def readSystemID():

    print("read System ID BEGINS")

    SystemIDFile= open('./settings_files/systemID.txt', "r", encoding='utf-8')
    SystemID_str = SystemIDFile.readline()

    return SystemID_str


def writeSystemID(SystemID_str):

    SystemIDFile= open('./settings_files/systemID.txt', "w", encoding='utf-8')

    SystemIDFile.write(SystemID_str)

    SystemIDFile.close()



def readListCheckHello():
    
    print("readList BEGINS")

    helloSettingFile = open('./settings_files/helloScreenSetting.txt', "r", encoding='utf-8')
    helloSetting = helloSettingFile.readlines()
    for lineIndex in range(len(helloSetting)-1,-1,-1):

        # Removes \n
        helloSetting[lineIndex] = helloSetting[lineIndex].split("\n")[0]

        if helloSetting[lineIndex][0] == '#':
            return 0
        else:
            return 1



def readHelloSetting():

    print("readList BEGINS")

    helloSettingFile = open('./settings_files/helloScreenSetting.txt', "r", encoding='utf-8')
    helloSetting = helloSettingFile.readlines()
    helloSettingDict = {}

    for lineIndex in range(len(helloSetting)):

        # Removes \n
        helloSetting[lineIndex] = helloSetting[lineIndex].split("\n")[0]

        # Treats items starting with '#' and adds items to dictionary
        if helloSetting[lineIndex][0] == '#':
            helloSettingDict[helloSetting[lineIndex][1:]] = "disabled"
        else:
            helloSettingDict[helloSetting[lineIndex]] = "enabled"


    print(helloSettingDict)

    print("readList ENDS")

    return helloSettingDict

def writeListSettings(helloSettingDict):

    helloSetting = helloSettingDict.items()

    outString=""

    for item in helloSetting:
        if item[1] == "enabled":
            outString = outString + item[0] + '\n'
        else:
            outString = outString + "#" + item[0] + '\n'

    print(outString)

    helloSettingFile = open('./settings_files/helloScreenSetting.txt', "w", encoding='utf-8')

    helloSettingFile.write(outString)

    helloSettingFile.close()

# #TESTES READ:
#
# readListSettings()
# readListDisplay()
#

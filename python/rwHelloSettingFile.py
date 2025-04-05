import os

# Global file path and default content
hello_filename = './settings_files/helloScreenSetting.txt'
DEFAULT_HELLO_CONTENT = "Tela inicial"

def createHelloSettingFile():
    """Creates helloScreenSetting.txt with default content."""
    with open(hello_filename, 'w', encoding='utf-8') as file:
        file.write(DEFAULT_HELLO_CONTENT)
    print(f"{hello_filename} created with default content.")

def readListCheckHello():
    print("readList BEGINS")

    if not os.path.exists(hello_filename):
        createHelloSettingFile()

    with open(hello_filename, "r", encoding='utf-8') as helloSettingFile:
        helloSetting = helloSettingFile.readlines()

    for lineIndex in range(len(helloSetting)-1, -1, -1):
        helloSetting[lineIndex] = helloSetting[lineIndex].strip()

        if helloSetting[lineIndex][0] == '#':
            return 0
        else:
            return 1

def readHelloSetting():
    print("readList BEGINS")

    if not os.path.exists(hello_filename):
        createHelloSettingFile()

    with open(hello_filename, "r", encoding='utf-8') as helloSettingFile:
        helloSetting = helloSettingFile.readlines()

    helloSettingDict = {}

    for lineIndex in range(len(helloSetting)):
        helloSetting[lineIndex] = helloSetting[lineIndex].strip()

        if helloSetting[lineIndex][0] == '#':
            helloSettingDict[helloSetting[lineIndex][1:]] = "disabled"
        else:
            helloSettingDict[helloSetting[lineIndex]] = "enabled"

    print(helloSettingDict)
    print("readList ENDS")

    return helloSettingDict

def writeListSettings(helloSettingDict):
    outString = ""

    for item in helloSettingDict.items():
        if item[1] == "enabled":
            outString += item[0] + '\n'
        else:
            outString += "#" + item[0] + '\n'

    print(outString)

    with open(hello_filename, "w", encoding='utf-8') as helloSettingFile:
        helloSettingFile.write(outString)

if __name__ == "__main__":
    print(readListCheckHello())
    readHelloSetting()
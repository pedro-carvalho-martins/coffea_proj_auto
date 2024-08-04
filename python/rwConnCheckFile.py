def readConnCheckStatus():

    print("readList BEGINS")

    connCheckFile = open('./settings_files/connCheck.txt', "r", encoding='utf-8')
    connCheckList = connCheckFile.readlines()
    connCheckDict = {}

    for lineIndex in range(len(connCheckList)):

        # Removes \n
        connCheckList[lineIndex] = connCheckList[lineIndex].split("\n")[0]

        # Treats items according to status
        if connCheckList[lineIndex][0:2] == 'C-':
            connCheckDict[connCheckList[lineIndex][2:]] = "check"
        elif connCheckList[lineIndex][0:2] == 'D-':
            connCheckDict[connCheckList[lineIndex][2:]] = "disabled"
        else:
            connCheckDict[connCheckList[lineIndex][2:]] = "erro"


    print(connCheckDict)

    print("readList ENDS")

    return connCheckDict

def writeConnCheckStatus(connCheckDict):

    connCheckList = connCheckDict.items()

    outString=""

    for item in connCheckList:
        if item[1] == "check":
            outString = outString + "C-" + item[0] + '\n'
        elif item[1] == "disabled":
            outString = outString + "D-" + item[0] + '\n'
        else:
            outString = outString + "X-" + item[0] + '\n'

    print(outString)

    connCheckFile = open('./settings_files/connCheck.txt', "w", encoding='utf-8')

    connCheckFile.write(outString)

    connCheckFile.close()


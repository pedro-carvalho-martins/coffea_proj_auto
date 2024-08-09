# New implementation using file lock to avoid problems with threads accessing the same file at the same time

from shared_resource import file_lock

def readConnCheckStatus():
    with file_lock:  # Acquire the lock to ensure exclusive access
        print("readList BEGINS")

        # Open and read the file
        with open('./settings_files/connCheck.txt', "r", encoding='utf-8') as connCheckFile:
            connCheckList = connCheckFile.readlines()

        connCheckDict = {}

        # Process the file content
        for line in connCheckList:
            line = line.strip()  # Removes \n
            if line.startswith('C-'):
                connCheckDict[line[2:]] = "check"
            elif line.startswith('D-'):
                connCheckDict[line[2:]] = "disabled"
            else:
                connCheckDict[line[2:]] = "error"

        print(connCheckDict)
        print("readList ENDS")

        return connCheckDict

def writeConnCheckStatus(connCheckDict):
    outString = ""
    for item in connCheckDict.items():
        if item[1] == "check":
            outString += "C-" + item[0] + '\n'
        elif item[1] == "disabled":
            outString += "D-" + item[0] + '\n'
        else:
            outString += "X-" + item[0] + '\n'

    print(outString)

    with file_lock:  # Acquire the lock to ensure exclusive access
        # Write to file
        with open('./settings_files/connCheck.txt', "w", encoding='utf-8') as connCheckFile:
            connCheckFile.write(outString)


# Original implementation - was working fine but could eventually cause issues with simulatenous file access by multiple threads

# def readConnCheckStatus():
#
#     print("readList BEGINS")
#
#     connCheckFile = open('./settings_files/connCheck.txt', "r", encoding='utf-8')
#     connCheckList = connCheckFile.readlines()
#     connCheckDict = {}
#
#     for lineIndex in range(len(connCheckList)):
#
#         # Removes \n
#         connCheckList[lineIndex] = connCheckList[lineIndex].split("\n")[0]
#
#         # Treats items according to status
#         if connCheckList[lineIndex][0:2] == 'C-':
#             connCheckDict[connCheckList[lineIndex][2:]] = "check"
#         elif connCheckList[lineIndex][0:2] == 'D-':
#             connCheckDict[connCheckList[lineIndex][2:]] = "disabled"
#         else:
#             connCheckDict[connCheckList[lineIndex][2:]] = "erro"
#
#
#     print(connCheckDict)
#
#     print("readList ENDS")
#
#     return connCheckDict
#
# def writeConnCheckStatus(connCheckDict):
#
#     connCheckList = connCheckDict.items()
#
#     outString=""
#
#     for item in connCheckList:
#         if item[1] == "check":
#             outString = outString + "C-" + item[0] + '\n'
#         elif item[1] == "disabled":
#             outString = outString + "D-" + item[0] + '\n'
#         else:
#             outString = outString + "X-" + item[0] + '\n'
#
#     print(outString)
#
#     connCheckFile = open('./settings_files/connCheck.txt', "w", encoding='utf-8')
#
#     connCheckFile.write(outString)
#
#     connCheckFile.close()

if __name__ == "__main__":
    readConnCheckStatus()
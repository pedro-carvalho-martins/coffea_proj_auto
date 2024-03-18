import tkinter as tk

## TEMPORARY COMMENT TO TEST ON WINDOWS. UNCOMMENT ASAP
import navigation
import rwHelloSettingFile
## TEMPORARY COMMENT ENDS. UNCOMMENT ASAP.




def statemod_button_clicked(index_button, settingName, new_state):

    print("statemod button clicked")
    print(index_button)
    print(settingName)
    print(new_state)

    print(helloSettingDict[settingName])

    helloSettingDict[settingName]=new_state

    print(helloSettingDict[settingName])

    if new_state == "enabled":
        helloSettingLabelList[index_button].config(bg="#26f680")
        buttonEnableList[index_button].config(state="disabled")
        buttonDisableList[index_button].config(state="normal")
    else:
        helloSettingLabelList[index_button].config(bg="#cc0001")
        buttonEnableList[index_button].config(state="normal")
        buttonDisableList[index_button].config(state="disabled")


def appendSettingLabel(settingName, settingStatus):

    if settingStatus == "enabled":
        background_color_label = "#26f680"
    else:
        background_color_label = "#cc0001"

    helloSettingLabelList.append(
        tk.Label(
            options_frame,
            bg=background_color_label,
            text=settingName,
            font=('Ubuntu',14)
        )
    )

def appendEnableButton(settingLabel_index, settingName, settingStatus):

    if settingStatus == "enabled":
        enableButtonState = "disabled"
    else:
        enableButtonState = "normal"

    currentButton = tk.Button(options_frame,
                              #text="Habilitar",
                              text="ON",
                              font=('Ubuntu', 14),
                              command = lambda idx=settingLabel_index: statemod_button_clicked(idx, settingName, "enabled")
                              )
    currentButton["state"]=enableButtonState

    buttonEnableList.append(currentButton)

def appendDisableButton(settingLabel_index, settingName, settingStatus):

    if settingStatus == "disabled":
        disableButtonState = "disabled"
    else:
        disableButtonState = "normal"

    currentButton = tk.Button(options_frame,
                              #text="Desabilitar",
                              text="OFF",
                              font=('Ubuntu', 14),
                              command = lambda idx=settingLabel_index: statemod_button_clicked(idx, settingName, "disabled")
                              )
    currentButton["state"]=disableButtonState

    buttonDisableList.append(currentButton)


def saveQuit_button_clicked():

    # Não fazer nada se todos os métodos de pagamento estiverem disabled.
    helloSettingList = helloSettingDict.items()

    flag_all_disabled = True

    for item in helloSettingList:
        if item[1] == "enabled":
            flag_all_disabled = False
            break

    if flag_all_disabled:
        return

    rwHelloSettingFile.writeListSettings(helloSettingDict)
    navigation.quitProgramAfterSettings()


def onlyQuit_button_clicked():
    navigation.quitProgramAfterSettings()

## Função de criação do Frame de preços

def createHelloSettingFrame(settingsContainer):

    ### VER SE ESSA DECLARAÇÃO VAI FUNCIONAR NA IMPLEMENTAÇÃO FINAL
    global helloSettingDict
    global helloSetting
    global helloSettingLabelList
    global buttonEnableList
    global buttonDisableList
    global options_frame

    ### TEMPORARY COMMENT TO TEST IMPLEMENTATION. UNCOMMENT ASAP
    helloSettingDict = rwHelloSettingFile.readHelloSetting()
    ### TEMPORARY COMMENT TO TEST IMPLEMENTATION ENDS.


    #### TEMPORARY TO TEST IMPLEMENTATION: DELETE ASAP
    #helloSettingDict = {'Tela bem-vindo': 'enabled'}
    #### TEMPORARY ENDS. DELETE ASAP

    # Get items from pMethodsDict:
    helloSetting = helloSettingDict.items()


    helloSettingFrame = tk.Frame(settingsContainer, height=480, width=320)

    ## Configurando o Grid

    helloSettingFrame.rowconfigure(0, weight=3)
    helloSettingFrame.rowconfigure(1, weight=6)
    helloSettingFrame.rowconfigure(2, weight=1)
    helloSettingFrame.rowconfigure(3, weight=1)
    helloSettingFrame.rowconfigure(4, weight=1)
    helloSettingFrame.columnconfigure(0, weight=1)


    ## Adiciono o label principal

    titleLabel = tk.Label(
       helloSettingFrame,
       text="CONFIG \nTELA INICIAL",
       font=('SegoeUI', 16))
    titleLabel.grid(column=0, row=0, sticky=tk.S, pady=0, padx=20)


    ## Crio o Frame dos métodos e botões

    options_frame = tk.Frame(helloSettingFrame)
    options_frame.grid(column=0, row=1, pady=10, padx=20)


    helloSettingLabelList = []
    buttonEnableList = []
    buttonDisableList = []

    # add a set of 1) Label 2) Minus button 3) Plus button for each price on the price list

    helloSettingIndex = 0

    for helloSettingItem in helloSetting:

        # Append payment method label - send method label to function and whether the method is enabled or disabled
        appendSettingLabel(helloSettingItem[0], helloSettingItem[1])

        # Append enable button - send to function whether the method is enabled or disabled
        appendEnableButton(helloSettingIndex, helloSettingItem[0], helloSettingItem[1])

        # Append disable button - send to function whether the method is enabled or disabled
        appendDisableButton(helloSettingIndex, helloSettingItem[0], helloSettingItem[1])

        helloSettingIndex = helloSettingIndex + 1

    # place items on the grid

    for settingLabel_index in range(len(helloSettingLabelList)):
        helloSettingLabelList[settingLabel_index].grid(column=0, row=settingLabel_index+1, ipadx=0, ipady=10, padx=5, sticky=tk.EW)
        buttonEnableList[settingLabel_index].grid(column=1, row=settingLabel_index+1, ipadx=10, ipady=10, padx=5, sticky=tk.EW)
        buttonDisableList[settingLabel_index].grid(column=2, row=settingLabel_index+1, ipadx=0, ipady=10, padx=5, sticky=tk.EW)

    print("last settingLabel_index")
    print(settingLabel_index)

    ### ADD ONLYQUIT BUTTON

    onlyQuitButton = tk.Button(helloSettingFrame,
              text=" Sair sem salvar ",
              # font=('SegoeUI', 20, 'bold'),
              font=('Ubuntu', 16),
              # command=button_clicked(button_index),
              command= lambda: onlyQuit_button_clicked())

    onlyQuitButton.grid(column=0, row=2, sticky=tk.S, pady=0, padx=20)

    ### ADD SAVEANDQUIT BUTTON

    saveQuitButton = tk.Button(helloSettingFrame,
              text=" Salvar e sair ",
              # font=('SegoeUI', 20, 'bold'),
              font=('Ubuntu', 16),
              # command=button_clicked(button_index),
              command= lambda: saveQuit_button_clicked())

    saveQuitButton.grid(column=0, row=3, sticky=tk.S, pady=0, padx=20)




    return helloSettingFrame







##### TEMPORARY SCRIPT JUST TO TEST EXECUTION OF FRAME ######

# mainContainer = tk.Tk()
# mainContainer.title("teste")
#
# mainContainer.geometry('320x480')
# mainContainer.resizable(False, False)
# mainContainer.attributes('-fullscreen', False)
#
# helloFrame = createHelloSettingFrame(mainContainer)
# helloFrame.pack(side="top", fill="both", expand=True)
#
# mainContainer.mainloop()

####### TEMPORARY SCRIPT ENDS. DELETE ASAP.
#################################################
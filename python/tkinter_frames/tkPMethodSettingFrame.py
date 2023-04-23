import tkinter as tk

## TEMPORARY COMMENT TO TEST ON WINDOWS. UNCOMMENT ASAP
import navigation
import rwPaymentMethodsList
## TEMPORARY COMMENT ENDS. UNCOMMENT ASAP.




def statemod_button_clicked(index_button, pay_method_name, new_state):

    print("statemod button clicked")
    print(index_button)
    print(pay_method_name)
    print(new_state)

    print(payMethodsDict[pay_method_name])

    payMethodsDict[pay_method_name]=new_state

    print(payMethodsDict[pay_method_name])

    if new_state == "enabled":
        pMethodLabelList[index_button].config(bg="#26f680")
        buttonEnableList[index_button].config(state="disabled")
        buttonDisableList[index_button].config(state="normal")
    else:
        pMethodLabelList[index_button].config(bg="#cc0001")
        buttonEnableList[index_button].config(state="normal")
        buttonDisableList[index_button].config(state="disabled")


def appendPMethodLabel(payMethodName, payMethodStatus):

    if payMethodStatus == "enabled":
        background_color_label = "#26f680"
    else:
        background_color_label = "#cc0001"

    pMethodLabelList.append(
        tk.Label(
            pMethods_frame,
            bg=background_color_label,
            text=payMethodName,
            font=('Ubuntu',14)
        )
    )

def appendEnableButton(payMethodLabel_index, payMethodName, payMethodStatus):

    if payMethodStatus == "enabled":
        enableButtonState = "disabled"
    else:
        enableButtonState = "normal"

    currentButton = tk.Button(pMethods_frame,
                              #text="Habilitar",
                              text="ON",
                              font=('Ubuntu', 14),
                              command = lambda idx=payMethodLabel_index: statemod_button_clicked(idx, payMethodName, "enabled")
                              )
    currentButton["state"]=enableButtonState

    buttonEnableList.append(currentButton)

def appendDisableButton(payMethodLabel_index, payMethodName, payMethodStatus):

    if payMethodStatus == "disabled":
        disableButtonState = "disabled"
    else:
        disableButtonState = "normal"

    currentButton = tk.Button(pMethods_frame,
                              #text="Desabilitar",
                              text="OFF",
                              font=('Ubuntu', 14),
                              command = lambda idx=payMethodLabel_index: statemod_button_clicked(idx, payMethodName, "disabled")
                              )
    currentButton["state"]=disableButtonState

    buttonDisableList.append(currentButton)


def saveQuit_button_clicked():

    # Não fazer nada se todos os métodos de pagamento estiverem disabled.

    rwPaymentMethodsList.writeListSettings(payMethodsDict)



def onlyQuit_button_clicked():
    pass

## Função de criação do Frame de preços

def createPMethodSettingFrame(settingsContainer):

    ### VER SE ESSA DECLARAÇÃO VAI FUNCIONAR NA IMPLEMENTAÇÃO FINAL
    global payMethodsDict
    global payMethods
    global pMethodLabelList
    global buttonEnableList
    global buttonDisableList
    global pMethods_frame

    ### TEMPORARY COMMENT TO TEST IMPLEMENTATION. UNCOMMENT ASAP
    payMethodsDict = rwPaymentMethodsList.readListSettings()
    ### TEMPORARY COMMENT TO TEST IMPLEMENTATION ENDS.


    #### TEMPORARY TO TEST IMPLEMENTATION: DELETE ASAP
    # payMethodsDict = {'Crédito': 'enabled', 'Débito': 'disabled', 'Voucher': 'enabled', 'QR Code (Pix)': 'disabled'}
    #### TEMPORARY ENDS. DELETE ASAP

    # Get items from pMethodsDict:
    payMethods = payMethodsDict.items()


    pMethodSettingFrame = tk.Frame(settingsContainer, height=480, width=320)

    ## Configurando o Grid

    pMethodSettingFrame.rowconfigure(0, weight=3)
    pMethodSettingFrame.rowconfigure(1, weight=6)
    pMethodSettingFrame.rowconfigure(2, weight=1)
    pMethodSettingFrame.rowconfigure(3, weight=1)
    pMethodSettingFrame.rowconfigure(4, weight=1)
    pMethodSettingFrame.columnconfigure(0, weight=1)


    ## Adiciono o label principal

    titleLabel = tk.Label(
       pMethodSettingFrame,
       text="CONFIG \nMÉTODOS PAGAMENTO",
       font=('SegoeUI', 16))
    titleLabel.grid(column=0, row=0, sticky=tk.S, pady=0, padx=20)


    ## Crio o Frame dos métodos e botões

    pMethods_frame = tk.Frame(pMethodSettingFrame)
    pMethods_frame.grid(column=0, row=1, pady=10, padx=20)


    pMethodLabelList = []
    buttonEnableList = []
    buttonDisableList = []

    # add a set of 1) Label 2) Minus button 3) Plus button for each price on the price list

    pMethodIndex = 0

    for payMethodItem in payMethods:

        # Append payment method label - send method label to function and whether the method is enabled or disabled
        appendPMethodLabel(payMethodItem[0], payMethodItem[1])

        # Append enable button - send to function whether the method is enabled or disabled
        appendEnableButton(pMethodIndex, payMethodItem[0], payMethodItem[1])

        # Append disable button - send to function whether the method is enabled or disabled
        appendDisableButton(pMethodIndex, payMethodItem[0], payMethodItem[1])

        pMethodIndex = pMethodIndex + 1

    # place items on the grid

    for pMethodLabel_index in range(len(pMethodLabelList)):
        pMethodLabelList[pMethodLabel_index].grid(column=0, row=pMethodLabel_index+1, ipadx=0, ipady=10, padx=5, sticky=tk.EW)
        buttonEnableList[pMethodLabel_index].grid(column=1, row=pMethodLabel_index+1, ipadx=10, ipady=10, padx=5, sticky=tk.EW)
        buttonDisableList[pMethodLabel_index].grid(column=2, row=pMethodLabel_index+1, ipadx=0, ipady=10, padx=5, sticky=tk.EW)

    print("last pMethodLabel_index")
    print(pMethodLabel_index)

    ### ADD ONLYQUIT BUTTON

    onlyQuitButton = tk.Button(pMethodSettingFrame,
              text=" Sair sem salvar ",
              # font=('SegoeUI', 20, 'bold'),
              font=('Ubuntu', 16),
              # command=button_clicked(button_index),
              command= lambda: onlyQuit_button_clicked())

    onlyQuitButton.grid(column=0, row=2, sticky=tk.S, pady=0, padx=20)

    ### ADD SAVEANDQUIT BUTTON

    saveQuitButton = tk.Button(pMethodSettingFrame,
              text=" Save and quit (just save atm) ",
              # font=('SegoeUI', 20, 'bold'),
              font=('Ubuntu', 16),
              # command=button_clicked(button_index),
              command= lambda: saveQuit_button_clicked())

    saveQuitButton.grid(column=0, row=3, sticky=tk.S, pady=0, padx=20)




    return pMethodSettingFrame







##### TEMPORARY SCRIPT JUST TO TEST EXECUTION OF FRAME ######

# mainContainer = tk.Tk()
# mainContainer.title("teste")
#
# mainContainer.geometry('320x480')
# mainContainer.resizable(False, False)
# mainContainer.attributes('-fullscreen', False)
#
# helloFrame = createPMethodSettingFrame()
# helloFrame.pack(side="top", fill="both", expand=True)
#
# mainContainer.mainloop()

####### TEMPORARY SCRIPT ENDS. DELETE ASAP.
#################################################
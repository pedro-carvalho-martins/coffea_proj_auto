import tkinter as tk

## TEMPORARY COMMENT TO TEST ON WINDOWS. UNCOMMENT ASAP
#import navigation
#import rwPaymentMethodsList
## TEMPORARY COMMENT ENDS. UNCOMMENT ASAP.




def enable_button_clicked(index_button):
    pass

def disable_button_clicked(index_button):
    pass


def appendPMethodLabel(payMethodName):

    pMethodLabelList.append(
        tk.Label(
            pMethods_frame,
            text=payMethodName,
            font=('Ubuntu',18)
        )
    )

def appendEnableButton(payMethodLabel_index, payMethodStatus):

    if payMethodStatus == "enabled":
        enableButtonState = "disabled"
    else:
        enableButtonState = "normal"

    currentButton = tk.Button(pMethods_frame,
                              text="Habilitar",
                              font=('Ubuntu', 18),
                              command = lambda idx=payMethodLabel_index: enable_button_clicked(idx)
                              )
    currentButton["state"]=enableButtonState

    buttonEnableList.append(currentButton)

def appendDisableButton(payMethodLabel_index, payMethodStatus):

    if payMethodStatus == "disabled":
        disableButtonState = "disabled"
    else:
        disableButtonState = "normal"

    currentButton = tk.Button(pMethods_frame,
                              text="Desabilitar",
                              font=('Ubuntu', 18),
                              command = lambda idx=payMethodLabel_index: disable_button_clicked(idx)
                              )
    currentButton["state"]=disableButtonState

    buttonDisableList.append(currentButton)


def saveQuit_button_clicked():

    rwPaymentMethodsList.writeListSettings(payMethodsDict)



## Função de criação do Frame de preços

def createPMethodSettingFrame():

    ### VER SE ESSA DECLARAÇÃO VAI FUNCIONAR NA IMPLEMENTAÇÃO FINAL
    global payMethods
    global pMethodLabelList
    global buttonEnableList
    global buttonDisableList
    global pMethods_frame

    ### TEMPORARY COMMENT TO TEST IMPLEMENTATION. UNCOMMENT ASAP
    #pMethodsDict = rwPaymentMethodsList.readListSettings()
    ### TEMPORARY COMMENT TO TEST IMPLEMENTATION ENDS.


    #### TEMPORARY TO TEST IMPLEMENTATION: DELETE ASAP
    payMethodsDict = {'Crédito': 'enabled', 'Débito': 'disabled', 'Voucher': 'enabled', 'QR Code (Pix)': 'disabled'}
    #### TEMPORARY ENDS. DELETE ASAP

    # Get items from pMethodsDict:
    payMethods = payMethodsDict.items()


    pMethodSettingFrame = tk.Frame(height=480, width=320)

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
       text="CONFIG MÉTODOS PAGAMENTO",
       font=('SegoeUI', 18))
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

        # Append payment method label - send method label to function
        appendPMethodLabel(payMethods[pMethodIndex][0])

        # Append enable button - send to function whether the method is enabled or disabled
        appendEnableButton(pMethodIndex, payMethods[pMethodIndex][1])

        # Append disable button - send to function whether the method is enabled or disabled
        appendDisableButton(pMethodIndex, payMethods[pMethodIndex][1])

        pMethodIndex = pMethodIndex + 1

    # place items on the grid

    for pMethodLabel_index in range(len(pMethodLabelList)):
        pMethodLabelList[pMethodLabel_index].grid(column=0, row=pMethodLabel_index+1, ipadx=20, ipady=0, padx=5, sticky=tk.EW)
        buttonEnableList[pMethodLabel_index].grid(column=1, row=pMethodLabel_index+1, ipadx=0, ipady=0, padx=5, sticky=tk.EW)
        buttonDisableList[pMethodLabel_index].grid(column=2, row=pMethodLabel_index+1, ipadx=0, ipady=0, padx=5, sticky=tk.EW)

    print("last pMethodLabel_index")
    print(pMethodLabel_index)



    ### ADD SAVEANDQUIT BUTTON

    saveQuitButton = tk.Button(pMethodSettingFrame,
              text=" Save and quit (just save atm) ",
              # font=('SegoeUI', 20, 'bold'),
              font=('Ubuntu', 16),
              # command=button_clicked(button_index),
              command= lambda: saveQuit_button_clicked())

    saveQuitButton.grid(column=0, row=4, sticky=tk.S, pady=0, padx=20)




    return pMethodSettingFrame







##### TEMPORARY SCRIPT JUST TO TEST EXECUTION OF FRAME ######

mainContainer = tk.Tk()
mainContainer.title("teste")

mainContainer.geometry('320x480')
mainContainer.resizable(False, False)
mainContainer.attributes('-fullscreen', False)

helloFrame = createPMethodSettingFrame()
helloFrame.pack(side="top", fill="both", expand=True)

mainContainer.mainloop()

####### TEMPORARY SCRIPT ENDS. DELETE ASAP.
#################################################
import tkinter as tk

## TEMPORARY COMMENT TO TEST ON WINDOWS. UNCOMMENT ASAP
import navigation
import rwPulseCoinValue
## TEMPORARY COMMENT ENDS. UNCOMMENT ASAP.



def modvalue_button_clicked(index_button, sign_mod):
    print('Button clicked')
    print(index_button)
    print(sign_mod)

    global pulseValueList_singleValue
    global valueLabelList

    modValue = 0

    if sign_mod == "plus":
        modValue = +0.25
    elif sign_mod == "minus" and pulseValueList_singleValue[index_button] > 0.25:
        modValue = -0.25


    pulseValueList_singleValue[index_button] = pulseValueList_singleValue[index_button] + modValue

    valueLabelList[index_button].config(
        text=str(pulseValueList_singleValue[index_button]))

    print(pulseValueList_singleValue)


def appendValueLabel(pulseValueFloat):

    valueLabelList.append(
        tk.Label(
            values_frame,
            text=str(pulseValueFloat),
            font=('Ubuntu',18)
        )
    )


def appendMinusButton(valueLabel_index):

    buttonMinusList.append(
        tk.Button(values_frame,
                  text=" – ",
                  # font=('SegoeUI', 20, 'bold'),
                  font=('Ubuntu', 12, 'bold'),
                  # command=button_clicked(button_index),
                  command=lambda idx=valueLabel_index: modvalue_button_clicked(idx, "minus"))
        # height=1,
        # width=1)
    )


def appendPlusButton(valueLabel_index):

    buttonPlusList.append(
        tk.Button(values_frame,
                  text=" + ",
                  # font=('SegoeUI', 20, 'bold'),
                  font=('Ubuntu', 12, 'bold'),
                  # command=button_clicked(button_index),
                  command= lambda idx=valueLabel_index: modvalue_button_clicked(idx, "plus"))
        # height=1,
        # width=1)
    )






def saveQuit_button_clicked():

    rwPulseCoinValue.writePulseCoinValue(pulseValueList_singleValue[0])

    navigation.quitProgramAfterSettings()

def noSaveQuit_button_clicked():

    navigation.quitProgramAfterSettings()


## Função de criação do Frame de configuração de valor de pulso

def createPulseValueSettingFrame(settingsContainer):

    ### VER SE ESSA DECLARAÇÃO VAI FUNCIONAR NA IMPLEMENTAÇÃO FINAL
    global pulseValueList_singleValue
    global valueLabelList
    global values_frame

    global buttonMinusList
    global buttonPlusList


    pulse_value_float = rwPulseCoinValue.readPulseCoinValue()
    
    pulseValueList_singleValue = []
    pulseValueList_singleValue.append(pulse_value_float)

    #### TEMPORARY TO TEST IMPLEMENTATION: DELETE ASAP
    # pulseValueList_singleValue = [0.25]
    #### TEMPORARY ENDS. DELETE ASAP


    pulseValueSettingFrame = tk.Frame(settingsContainer, height=480, width=320)

    ## Configurando o Grid

    pulseValueSettingFrame.rowconfigure(0, weight=3)
    pulseValueSettingFrame.rowconfigure(1, weight=6)
    pulseValueSettingFrame.rowconfigure(2, weight=1)
    pulseValueSettingFrame.rowconfigure(3, weight=1)
    pulseValueSettingFrame.rowconfigure(4, weight=1)
    pulseValueSettingFrame.columnconfigure(0, weight=1)


    ## Adiciono o label principal

    titleLabel = tk.Label(
       pulseValueSettingFrame,
       text="Configurar valor do pulso\n\nAtenção: o valor do pulso também\ndeverá ser modificado\nna máquina vending!",
       font=('SegoeUI', 14))
    titleLabel.grid(column=0, row=0, sticky=tk.S, pady=0, padx=20)


    ## Crio o Frame do valor e botões

    values_frame = tk.Frame(pulseValueSettingFrame)
    values_frame.grid(column=0, row=1, pady=0, padx=20)


    valueLabelList = []
    buttonMinusList = []
    buttonPlusList = []

    # add a set of 1) Label 2) Minus button 3) Plus button for each value

    for valueLabel_index in range(len(pulseValueList_singleValue)):

        # Append price label
        appendValueLabel(pulseValueList_singleValue[valueLabel_index])

        # Append minus button
        appendMinusButton(valueLabel_index)

        # Append plus button
        appendPlusButton(valueLabel_index)

    # place items on the grid

    for valueLabel_index in range(len(valueLabelList)):
        valueLabelList[valueLabel_index].grid(column=1, row=valueLabel_index+1, ipadx=20, ipady=0, padx=5, sticky=tk.EW)
        buttonMinusList[valueLabel_index].grid(column=0, row=valueLabel_index+1, ipadx=0, ipady=0, padx=5, sticky=tk.EW)
        buttonPlusList[valueLabel_index].grid(column=2, row=valueLabel_index+1, ipadx=0, ipady=0, padx=5, sticky=tk.EW)

    print("last valueLabel_index")
    print(valueLabel_index)



    ### ADD SAVEANDQUIT BUTTON

    saveQuitButton = tk.Button(pulseValueSettingFrame,
              text=" Salvar e sair ",
              # font=('SegoeUI', 20, 'bold'),
              font=('Ubuntu', 16),
              # command=button_clicked(button_index),
              command= lambda: saveQuit_button_clicked())

    saveQuitButton.grid(column=0, row=4, sticky=tk.S, pady=0, padx=20)

    noSaveQuitButton = tk.Button(pulseValueSettingFrame,
              text=" Sair sem salvar ",
              # font=('SegoeUI', 20, 'bold'),
              font=('Ubuntu', 16),
              # command=button_clicked(button_index),
              command= lambda: noSaveQuit_button_clicked())

    noSaveQuitButton.grid(column=0, row=4, sticky=tk.S, pady=0, padx=20)


    return pulseValueSettingFrame







##### TEMPORARY SCRIPT JUST TO TEST EXECUTION OF FRAME ######

# mainContainer = tk.Tk()
# mainContainer.title("teste")
#
# mainContainer.geometry('320x480')
# mainContainer.resizable(False, False)
# mainContainer.attributes('-fullscreen', False)
#
# helloFrame = createPulseValueSettingFrame()
# helloFrame.pack(side="top", fill="both", expand=True)
#
# mainContainer.mainloop()

####### TEMPORARY SCRIPT ENDS. DELETE ASAP.
#################################################
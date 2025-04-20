import tkinter as tk

## TEMPORARY COMMENT TO TEST ON WINDOWS. UNCOMMENT ASAP
import navigation
import rwPulseCoinValue
## TEMPORARY COMMENT ENDS. UNCOMMENT ASAP.


def modvalue_button_clicked(index_button, sign_mod, step):
    print('Button clicked')
    print(index_button)
    print(sign_mod)

    global pulseValuesList
    global valueLabelList

    modValue = 0

    if sign_mod == "plus":
        modValue = step
    elif sign_mod == "minus" and pulseValuesList[index_button] > step:
        modValue = -1*step


    pulseValuesList[index_button] = pulseValuesList[index_button] + modValue

    valueLabelList[index_button].config(
        text=str(pulseValuesList[index_button]))

    print(pulseValuesList)


def appendValueLabel(pulseValueFloat):

    valueLabelList.append(
        tk.Label(
            values_frame,
            text=str(pulseValueFloat),
            font=('Ubuntu',18)
        )
    )


def appendPlusMinusButton(valueLabel_index, sign, display_text, increment_step):

    button_to_append = tk.Button(values_frame,
                  text=display_text,
                  # font=('SegoeUI', 20, 'bold'),
                  font=('Ubuntu', 12, 'bold'),
                  # command=button_clicked(button_index),
                  command=lambda idx=valueLabel_index: modvalue_button_clicked(idx, sign, increment_step))

    if sign == "minus":
        buttonMinusList.append(button_to_append)
    if sign == "plus":
        buttonPlusList.append(button_to_append)


def saveQuit_button_clicked():

    rwPulseCoinValue.writePulseCoinValue(pulseValuesList[0])

    navigation.quitProgramAfterSettings()

def noSaveQuit_button_clicked():

    navigation.quitProgramAfterSettings()


## Função de criação do Frame de configuração de valor de pulso

def createPulseValueSettingFrame(settingsContainer):

    ### VER SE ESSA DECLARAÇÃO VAI FUNCIONAR NA IMPLEMENTAÇÃO FINAL
    global pulseValuesList
    global valueLabelList
    global values_frame

    global buttonMinusList
    global buttonPlusList


    pulse_value_float = rwPulseCoinValue.readPulseCoinValue()
    pulse_duration_int = 100
    pulse_sleep_interval_int = 400
    
    pulseValuesList = [] # Index 0: coin value ; Index 1: pulse duration (ms) ; Index 2: interval between pulses (ms)

    pulseValuesList.append(pulse_value_float)
    pulseValuesList.append(pulse_duration_int)
    pulseValuesList.append(pulse_sleep_interval_int)

    #### TEMPORARY TO TEST IMPLEMENTATION: DELETE ASAP
    # pulseValueList_singleValue = [0.25]
    #### TEMPORARY ENDS. DELETE ASAP


    pulseValueSettingFrame = tk.Frame(settingsContainer, height=480, width=320)

    ## Configurando o Grid

    pulseValueSettingFrame.rowconfigure(0, weight=3)
    pulseValueSettingFrame.rowconfigure(1, weight=3)
    pulseValueSettingFrame.rowconfigure(2, weight=1)
    pulseValueSettingFrame.rowconfigure(3, weight=1)
    pulseValueSettingFrame.rowconfigure(4, weight=1)
    pulseValueSettingFrame.rowconfigure(5, weight=1)
    pulseValueSettingFrame.rowconfigure(6, weight=1)
    pulseValueSettingFrame.columnconfigure(0, weight=1)


    ## Adiciono o label principal

    titleLabel = tk.Label(
       pulseValueSettingFrame,
       text="Configurar valor do pulso\n\nAtenção:\nO valor do pulso também\ndeverá ser modificado\nna máquina vending!",
       font=('SegoeUI', 10))
    titleLabel.grid(column=0, row=0, sticky=tk.S, pady=0, padx=20)


    ## Crio o Frame do valor e botões

    values_frame = tk.Frame(pulseValueSettingFrame)
    values_frame.grid(column=0, row=1, pady=0, padx=20)
    values_frame.grid(column=0, row=2, pady=0, padx=20)
    values_frame.grid(column=0, row=3, pady=0, padx=20)
    values_frame.grid(column=0, row=4, pady=0, padx=20)
    values_frame.grid(column=0, row=5, pady=0, padx=20)
    values_frame.grid(column=0, row=6, pady=0, padx=20)

    valueLabelList = []
    buttonMinusList = []
    buttonPlusList = []

    # add a set of 1) Label 2) Minus button 3) Plus button for each value

    # Index 0: coin value ; Index 1: pulse duration (ms) ; Index 2: interval between pulses (ms)
    ## Append value label
    appendValueLabel(pulseValuesList[0])
    ## Append minus button
    appendPlusMinusButton(0, sign="minus", display_text=" – ", increment_step=0.25)
    ## Append plus button
    appendPlusMinusButton(0, sign="plus", display_text=" + ", increment_step=0.25)

    # Index 1: pulse duration (ms) ; Index 2: interval between pulses (ms)
    ## Append value label
    appendValueLabel(pulseValuesList[1])
    ## Append minus button
    appendPlusMinusButton(1, sign="minus", display_text=" – ", increment_step=20)
    ## Append plus button
    appendPlusMinusButton(1, sign="plus", display_text=" + ", increment_step=20)

    # Index 2: interval between pulses (ms)
    ## Append value label
    appendValueLabel(pulseValuesList[2])
    ## Append minus button
    appendPlusMinusButton(2, sign="minus", display_text=" – ", increment_step=20)
    ## Append plus button
    appendPlusMinusButton(2, sign="plus", display_text=" + ", increment_step=20)

    descriptionLabelList = [
        tk.Label(
            pulseValueSettingFrame,
            text="Valor ($) pulso",
            font=('SegoeUI', 10)),

        tk.Label(
            pulseValueSettingFrame,
            text="Duração pulso (ms) (padrão: 100ms)",
            font=('SegoeUI', 10)),

        tk.Label(
            pulseValueSettingFrame,
            text="Intervalo entre pulsos (ms) (padrão: 400ms)",
            font=('SegoeUI', 10))
    ]


    # place items on the grid

    for valueLabel_index in range(len(valueLabelList)):
        descriptionLabelList[valueLabel_index].grid(column=1, row=valueLabel_index * 2 + 1, ipadx=20, ipady=0, padx=5,sticky=tk.EW)

        valueLabelList[valueLabel_index].grid(column=1, row=valueLabel_index*2+2, ipadx=20, ipady=0, padx=5, sticky=tk.EW)
        buttonMinusList[valueLabel_index].grid(column=0, row=valueLabel_index*2+2, ipadx=0, ipady=0, padx=5, sticky=tk.EW)
        buttonPlusList[valueLabel_index].grid(column=2, row=valueLabel_index*2+2, ipadx=0, ipady=0, padx=5, sticky=tk.EW)

    print("last valueLabel_index")
    print(valueLabel_index)



    ### ADD SAVEANDQUIT BUTTON

    saveQuitButton = tk.Button(pulseValueSettingFrame,
              text=" Salvar e sair ",
              # font=('SegoeUI', 20, 'bold'),
              font=('Ubuntu', 16),
              # command=button_clicked(button_index),
              command= lambda: saveQuit_button_clicked())

    saveQuitButton.grid(column=0, row=3, sticky=tk.S, pady=0, padx=20)

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
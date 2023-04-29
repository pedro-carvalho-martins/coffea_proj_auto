import tkinter as tk

## TEMPORARY COMMENT TO TEST ON WINDOWS. UNCOMMENT ASAP
import navigation
import rwPricesList
## TEMPORARY COMMENT ENDS. UNCOMMENT ASAP.



def modprice_button_clicked(index_button, sign_mod):
    print('Button clicked')
    print(index_button)
    print(sign_mod)

    global lista_precos
    global priceLabelList

    modValue = 0

    if sign_mod == "plus":
        modValue = +0.25
    elif sign_mod == "minus" and lista_precos[index_button] > 0.25:
        modValue = -0.25


    lista_precos[index_button] = lista_precos[index_button] + modValue

    priceLabelList[index_button].config(
        text=str(lista_precos[index_button]))

    print(lista_precos)


def appendPriceLabel(precoFloat):

    priceLabelList.append(
        tk.Label(
            prices_frame,
            text=str(precoFloat),
            font=('Ubuntu',18)
        )
    )


def appendMinusButton(priceLabel_index):

    buttonMinusList.append(
        tk.Button(prices_frame,
                  text=" - ",
                  # font=('SegoeUI', 20, 'bold'),
                  font=('Ubuntu', 24),
                  # command=button_clicked(button_index),
                  command=lambda idx=priceLabel_index: modprice_button_clicked(idx, "minus"))
        # height=1,
        # width=1)
    )


def appendPlusButton(priceLabel_index):

    buttonPlusList.append(
        tk.Button(prices_frame,
                  text=" + ",
                  # font=('SegoeUI', 20, 'bold'),
                  font=('Ubuntu', 24),
                  # command=button_clicked(button_index),
                  command= lambda idx=priceLabel_index: modprice_button_clicked(idx, "plus"))
        # height=1,
        # width=1)
    )


def addprice_button_clicked():

    ## TEMPORARY LIMIT ON NUMBER OF PRICES? REMOVE?
    if len(lista_precos)>=5:
        return
    ##

    # Append price label
    appendPriceLabel(0.25)

    # Append minus button
    appendMinusButton(len(lista_precos))

    # Append plus button
    appendPlusButton(len(lista_precos))

    # Add items to the grid
    priceLabelList[len(lista_precos)].grid(column=1, row=(len(lista_precos)) + 1, ipadx=20, ipady=0, padx=5,
                                           sticky=tk.EW)
    buttonMinusList[len(lista_precos)].grid(column=0, row=(len(lista_precos)) + 1, ipadx=0, ipady=0, padx=5,
                                            sticky=tk.EW)
    buttonPlusList[len(lista_precos)].grid(column=2, row=(len(lista_precos)) + 1, ipadx=0, ipady=0, padx=5,
                                           sticky=tk.EW)

    # Append price to price list
    lista_precos.append(0.25)



def removeprice_button_clicked():

    if len(lista_precos) <= 1:
        return

    # Remove price label
    priceLabelList[-1].destroy()
    del priceLabelList[-1]

    # Remove minus button
    buttonMinusList[-1].destroy()
    del buttonMinusList[-1]

    # Remove plus button
    buttonPlusList[-1].destroy()
    del buttonPlusList[-1]

    # Remove price from price list
    del lista_precos[-1]



def saveQuit_button_clicked():

    rwPricesList.writeListSettings(lista_precos)

    # TEST
    global settingsContainer
    global mainContainer

    settingsContainer.destroy()
    mainContainer.destroy()
    # TEST ENDS


## Função de criação do Frame de preços

def createPriceSettingFrame(settingsContainer):

    ### VER SE ESSA DECLARAÇÃO VAI FUNCIONAR NA IMPLEMENTAÇÃO FINAL
    global lista_precos
    global priceLabelList
    global prices_frame

    global buttonMinusList
    global buttonPlusList


    ### TEMPORARY COMMENT TO TEST IMPLEMENTATION. UNCOMMENT ASAP
    lista_precos = rwPricesList.readList()
    ### TEMPORARY COMMENT TO TEST IMPLEMENTATION ENDS.


    #### TEMPORARY TO TEST IMPLEMENTATION: DELETE ASAP
    # lista_precos = [2.5,3.0]
    #### TEMPORARY ENDS. DELETE ASAP


    priceSettingFrame = tk.Frame(settingsContainer, height=480, width=320)

    ## Configurando o Grid

    priceSettingFrame.rowconfigure(0, weight=3)
    priceSettingFrame.rowconfigure(1, weight=6)
    priceSettingFrame.rowconfigure(2, weight=1)
    priceSettingFrame.rowconfigure(3, weight=1)
    priceSettingFrame.rowconfigure(4, weight=1)
    priceSettingFrame.columnconfigure(0, weight=1)


    ## Adiciono o label principal

    titleLabel = tk.Label(
       priceSettingFrame,
       text="CONFIG PREÇOS",
       font=('SegoeUI', 18))
    titleLabel.grid(column=0, row=0, sticky=tk.S, pady=0, padx=20)


    ## Crio o Frame dos preços e botões

    prices_frame = tk.Frame(priceSettingFrame)
    prices_frame.grid(column=0, row=1, pady=10, padx=20)


    priceLabelList = []
    buttonMinusList = []
    buttonPlusList = []

    # add a set of 1) Label 2) Minus button 3) Plus button for each price on the price list

    for priceLabel_index in range(len(lista_precos)):

        # Append price label
        appendPriceLabel(lista_precos[priceLabel_index])

        # Append minus button
        appendMinusButton(priceLabel_index)

        # Append plus button
        appendPlusButton(priceLabel_index)

    # place items on the grid

    for priceLabel_index in range(len(priceLabelList)):
        priceLabelList[priceLabel_index].grid(column=1, row=priceLabel_index+1, ipadx=20, ipady=0, padx=5, sticky=tk.EW)
        buttonMinusList[priceLabel_index].grid(column=0, row=priceLabel_index+1, ipadx=0, ipady=0, padx=5, sticky=tk.EW)
        buttonPlusList[priceLabel_index].grid(column=2, row=priceLabel_index+1, ipadx=0, ipady=0, padx=5, sticky=tk.EW)

    print("last priceLabel_index")
    print(priceLabel_index)

    ### ADD ADDPRICE BUTTON

    addPriceButton = tk.Button(priceSettingFrame,
              text=" ADDPRICE ",
              # font=('SegoeUI', 20, 'bold'),
              font=('Ubuntu', 16),
              # command=button_clicked(button_index),
              command= lambda: addprice_button_clicked())

    addPriceButton.grid(column=0, row=2, sticky=tk.S, pady=0, padx=20)




    ### ADD REMOVEPRICE BUTTON

    removePriceButton = tk.Button(priceSettingFrame,
                               text=" REMOVEPRICE ",
                               # font=('SegoeUI', 20, 'bold'),
                               font=('Ubuntu', 16),
                               # command=button_clicked(button_index),
                               command=lambda: removeprice_button_clicked())

    removePriceButton.grid(column=0, row=3, sticky=tk.S, pady=0, padx=20)



    ### ADD SAVEANDQUIT BUTTON

    saveQuitButton = tk.Button(priceSettingFrame,
              text=" Save and quit (just save atm) ",
              # font=('SegoeUI', 20, 'bold'),
              font=('Ubuntu', 16),
              # command=button_clicked(button_index),
              command= lambda: saveQuit_button_clicked())

    saveQuitButton.grid(column=0, row=4, sticky=tk.S, pady=0, padx=20)




    return priceSettingFrame







##### TEMPORARY SCRIPT JUST TO TEST EXECUTION OF FRAME ######

# mainContainer = tk.Tk()
# mainContainer.title("teste")
#
# mainContainer.geometry('320x480')
# mainContainer.resizable(False, False)
# mainContainer.attributes('-fullscreen', False)
#
# helloFrame = createPriceSettingFrame()
# helloFrame.pack(side="top", fill="both", expand=True)
#
# mainContainer.mainloop()

####### TEMPORARY SCRIPT ENDS. DELETE ASAP.
#################################################
import tkinter as tk



## TEMPORARY COMMENT TO TEST ON WINDOWS. UNCOMMENT ASAP
#import navigation
#import rwPricesList
## TEMPORARY COMMENT ENDS. UNCOMMENT ASAP.



def modprice_button_clicked(index_button, sign_mod, priceSettingFrame):
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


## Função de criação do Frame de preços

def createPriceSettingFrame():

    ### VER SE ESSA DECLARAÇÃO VAI FUNCIONAR NA IMPLEMENTAÇÃO FINAL
    global lista_precos
    global priceLabelList


    ### TEMPORARY COMMENT TO TEST IMPLEMENTATION. UNCOMMENT ASAP
    #lista_precos = rwPricesList.readList()
    ### TEMPORARY COMMENT TO TEST IMPLEMENTATION ENDS.


    #### TEMPORARY TO TEST IMPLEMENTATION: DELETE ASAP
    lista_precos = [2.5,3.0]
    #### TEMPORARY ENDS. DELETE ASAP


    priceSettingFrame = tk.Frame(height=480, width=320)

    ## Configurando o Grid

    priceSettingFrame.rowconfigure(0, weight=3)
    priceSettingFrame.rowconfigure(1, weight=6)
    priceSettingFrame.rowconfigure(2, weight=1)
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

    for priceLabel_index in range(len(lista_precos)):

        # Append price label
        priceLabelList.append(
            tk.Label(
                prices_frame,
                text=str(lista_precos[priceLabel_index]),
                font=('Ubuntu',18)
            )
        )

        # Append minus button
        buttonMinusList.append(
            tk.Button(prices_frame,
                      text=" - ",
                      # font=('SegoeUI', 20, 'bold'),
                      font=('Ubuntu', 28),
                      # command=button_clicked(button_index),
                      command=lambda idx=priceLabel_index: modprice_button_clicked(idx, "minus", priceSettingFrame))
            # height=1,
            # width=1)
        )

        # Append plus button
        buttonPlusList.append(
            tk.Button(prices_frame,
                      text=" + ",
                      # font=('SegoeUI', 20, 'bold'),
                      font=('Ubuntu', 28),
                      # command=button_clicked(button_index),
                      command= lambda idx=priceLabel_index: modprice_button_clicked(idx, "plus", prices_frame))
            # height=1,
            # width=1)
        )

    for priceLabel_index in range(len(priceLabelList)):
        priceLabelList[priceLabel_index].grid(column=1, row=priceLabel_index+1, ipadx=20, ipady=0, padx=5, sticky=tk.EW)
        buttonMinusList[priceLabel_index].grid(column=0, row=priceLabel_index+1, ipadx=0, ipady=0, padx=5, sticky=tk.EW)
        buttonPlusList[priceLabel_index].grid(column=2, row=priceLabel_index+1, ipadx=0, ipady=0, padx=5, sticky=tk.EW)

    print("last priceLabel_index")
    print(priceLabel_index)

    ### ADD ADDPRICE BUTTON

    ### ADD REMOVEPRICE BUTTON

    ### ADD SAVEANDQUIT BUTTON




    return priceSettingFrame







##### TEMPORARY SCRIPT JUST TO TEST EXECUTION OF FRAME ######

mainContainer = tk.Tk()
mainContainer.title("teste")

mainContainer.geometry('320x480')
mainContainer.resizable(False, False)
mainContainer.attributes('-fullscreen', False)

helloFrame = createPriceSettingFrame()
helloFrame.pack(side="top", fill="both", expand=True)

mainContainer.mainloop()

####### TEMPORARY SCRIPT ENDS. DELETE ASAP.
#################################################
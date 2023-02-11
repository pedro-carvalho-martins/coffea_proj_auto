import tkinter as tk

import navigation


## Ação de clique em botão

def button_clicked(index_button, lista_precos, priceFrame):
   print('Button clicked')
   print(index_button)
   print(lista_precos[index_button])
   navigation.navigate_payment_method_Frame(lista_precos[index_button], priceFrame)


## Função de formatação dos textos dos botões de preço

def display_button_text(input_price):
    return ("R$ {:.2f}".format(input_price)).replace(".",",")


## Função de criação do Frame de preços

def createPriceFrame():


    ## Fazer a lista de preços ser obtida de arquivo externo!
    # lista_precos = [2.50, 3, 3.50, 4.00]
    lista_precos = [2.50, 3]


    priceFrame = tk.Frame(height=480, width=320)


    ## Configurando o Grid

    priceFrame.rowconfigure(0, weight=3)
    priceFrame.rowconfigure(1, weight=6)
    priceFrame.rowconfigure(2, weight=1)
    priceFrame.columnconfigure(0, weight=1)


    ## Adiciono o label principal

    label = tk.Label(
       priceFrame,
       text="Inserir crédito:",
       font=('SegoeUI', 26))
    label.grid(column=0, row=0, sticky=tk.S, pady=0, padx=20)


    ## Crio o Frame dos botões

    button_frame = tk.Frame(priceFrame)
    button_frame.grid(column=0, row=1, pady=10, padx=20)


    ## Adiciono os botões



    buttons_list=[]

    for button_index in range(len(lista_precos)):
       buttons_list.append(
          tk.Button(button_frame,
                    text=display_button_text(lista_precos[button_index]),
                    #font=('SegoeUI', 20, 'bold'),
                    font=('Ubuntu', 20),
                    #command=button_clicked(button_index),
                    command= lambda idx=button_index: button_clicked(idx, lista_precos, priceFrame))
                    #height=1,
                    #width=1)
       )

    for button_index in range(len(buttons_list)):
       buttons_list[button_index].grid(column=0, row=button_index+1, ipadx=80, ipady=10, pady=5, sticky=tk.EW)


    ## Crio o Frame inferior

    lower_frame = tk.Frame(priceFrame)
    lower_frame.grid(column=0, row=2, sticky=tk.NS, pady=1, padx=20)

    return priceFrame


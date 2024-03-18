import tkinter as tk

import navigation
import rwPricesList

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

def createPriceFrame(mainContainer):


    ### OLD IMPLEMENTATION STARTS

    ## Fazer a lista de preços ser obtida de arquivo externo!
    # lista_precos = [2.50, 3, 3.50, 4.00]
    #lista_precos = [2.50, 3]

    ### OLD IMPLEMENTATION ENDS



    ## INÍCIO DA NOVA IMPLEMENTAÇÃO: PREÇOS LIDOS DE ARQUIVO .txt - TESTE PENDENTE

    lista_precos = rwPricesList.readList()

    ## FIM DA NOVA IMPLEMENTAÇÃO


    priceFrame = tk.Frame(mainContainer, height=480, width=320)


    ## Configurando o Grid

    priceFrame.rowconfigure(0, weight=3)
    priceFrame.rowconfigure(1, weight=6)
    priceFrame.rowconfigure(2, weight=1)
    priceFrame.columnconfigure(0, weight=1)


    ## Adiciono o label principal

    label = tk.Label(
       priceFrame,
       text="Selecione o valor\ndo produto:",
       font=('SegoeUI', 22))
    label.grid(column=0, row=0, sticky=tk.S, pady=0, padx=20)


    ## Crio o Frame dos botões

    button_frame = tk.Frame(priceFrame)
    button_frame.grid(column=0, row=1, pady=5, padx=0)


    ## Adiciono os botões



    buttons_list=[]

    for button_index in range(len(lista_precos)):
       buttons_list.append(
          tk.Button(button_frame,
                    text=display_button_text(lista_precos[button_index]),
                    #font=('SegoeUI', 20, 'bold'),
                    font=('Ubuntu', 20),
                    #command=button_clicked(button_index),
                    command= lambda idx=button_index: button_clicked(idx, lista_precos, priceFrame)
                    #### inicio do teste de remoção da mudança de visual com hover
                    ,
                    activebackground = button_frame.cget(
                        "background")  # Set the active background color to the regular background color
                    #### fim do teste de remoção da mudança de visual com hover
                    # Modificação OK. aplicar nos outros Frames
                    #)
                    #height=1,
                    #tmp test 2024.02.15
                    ,
                    width=7)
                    #tmp test 2024.02.15
       )


    #teste: oito preços, dois por coluna, duas colunas.



    ipady_buttons = 10

    # If there are five rows, shorten the height of the buttons
    if len(buttons_list) % 5 == 0:
        ipady_buttons = 7



    for button_index in range(len(buttons_list)):



        # implementação pendente: visual de "clique para pagar" com apenas um preço
        #if len(buttons_list) == 1:
        #    buttons_list[button_index].grid(column=0, row=0, ipadx=80, ipady=1000, pady=500, sticky=tk.EW)

        if len(buttons_list) > 5:
            # Set a two-column structure
            column_input = button_index % 2
            row_input = button_index // 2
            buttons_list[button_index].grid(column=column_input, row=row_input + 1, ipadx=0, ipady=ipady_buttons, padx=4, pady=5, sticky=tk.EW)
            #buttons_list[button_index].grid(column=column_input, row=row_input + 1, ipadx=0, ipady=10, padx=5, pady=5, sticky=tk.EW)

        else:
            # Set a single-column structure
            buttons_list[button_index].grid(column=0, row=button_index + 1, ipadx=40, ipady=ipady_buttons, pady=5, sticky=tk.EW)
            #buttons_list[button_index].grid(column=0, row=button_index + 1, ipadx=80, ipady=10, pady=5, sticky=tk.EW)


    ## Crio o Frame inferior

    lower_frame = tk.Frame(priceFrame)
    lower_frame.grid(column=0, row=2, sticky=tk.NS, pady=1, padx=20)

    return priceFrame


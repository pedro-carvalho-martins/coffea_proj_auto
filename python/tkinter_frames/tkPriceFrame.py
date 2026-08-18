import tkinter as tk

import navigation
import rwPricesList
from tkinter_frames.ui_components import create_screen, create_touch_button, format_brl
from tkinter_frames.ui_theme import COLORS, FONT_PRICE_BUTTON, FONT_TITLE


## Ação de clique em botão

def button_clicked(buttons_list, index_button, lista_precos, priceFrame):
    for btn in buttons_list:
        btn.config(state=tk.DISABLED)

    print('Button clicked')
    print(index_button)
    print(lista_precos[index_button])
    navigation.navigate_payment_method_Frame(lista_precos[index_button], priceFrame)


## Função de formatação dos textos dos botões de preço

def display_button_text(input_price):
    return format_brl(input_price)


## Função de criação do Frame de preços

def createPriceFrame(mainContainer):
    ### OLD IMPLEMENTATION STARTS

    ## Fazer a lista de preços ser obtida de arquivo externo!
    # lista_precos = [2.50, 3, 3.50, 4.00]
    # lista_precos = [2.50, 3]

    ### OLD IMPLEMENTATION ENDS

    ## INÍCIO DA NOVA IMPLEMENTAÇÃO: PREÇOS LIDOS DE ARQUIVO .txt - TESTE PENDENTE

    lista_precos = rwPricesList.readList()

    ## FIM DA NOVA IMPLEMENTAÇÃO

    priceFrame = create_screen(mainContainer)

    ## Configurando o Grid

    priceFrame.rowconfigure(0, weight=3)
    priceFrame.rowconfigure(1, weight=6)
    priceFrame.rowconfigure(2, weight=1)
    priceFrame.columnconfigure(0, weight=1)

    ## Adiciono o label principal

    label = tk.Label(
        priceFrame,
        text="Selecione o valor\ndo produto:",
        font=FONT_TITLE,
        bg=COLORS["background"],
        fg=COLORS["text"],
    )
    label.grid(column=0, row=0, sticky=tk.S, pady=(18, 8), padx=20)

    ## Crio o Frame dos botões

    button_frame = tk.Frame(priceFrame, bg=COLORS["background"])
    button_frame.grid(column=0, row=1, sticky=tk.NSEW, pady=5, padx=16)
    button_frame.columnconfigure(0, weight=1)
    button_frame.columnconfigure(1, weight=1)

    ## Adiciono os botões

    buttons_list = []

    for button_index in range(len(lista_precos)):
        button = create_touch_button(
            button_frame,
            display_button_text(lista_precos[button_index]),
            None,
            font=FONT_PRICE_BUTTON,
        )
        buttons_list.append(button)

    # Now set the command for each button
    for idx, button in enumerate(buttons_list):
        button.config(command=lambda btns=buttons_list, i=idx: button_clicked(btns, i, lista_precos, priceFrame))


    # teste: oito preços, dois por coluna, duas colunas.

    ipady_buttons = 10

    # If there are five rows, shorten the height of the buttons
    if len(buttons_list) % 5 == 0:
        ipady_buttons = 7

    for button_index in range(len(buttons_list)):

        # implementação pendente: visual de "clique para pagar" com apenas um preço
        # if len(buttons_list) == 1:
        #    buttons_list[button_index].grid(column=0, row=0, ipadx=80, ipady=1000, pady=500, sticky=tk.EW)

        if len(buttons_list) > 5:
            # Set a two-column structure
            column_input = button_index % 2
            row_input = button_index // 2
            buttons_list[button_index].grid(column=column_input, row=row_input + 1, ipady=ipady_buttons,
                                            padx=4, pady=4, sticky=tk.EW)
            # buttons_list[button_index].grid(column=column_input, row=row_input + 1, ipadx=0, ipady=10, padx=5, pady=5, sticky=tk.EW)

        else:
            # Set a single-column structure
            buttons_list[button_index].grid(column=0, row=button_index + 1, ipady=ipady_buttons, pady=4,
                                            sticky=tk.EW)
            # buttons_list[button_index].grid(column=0, row=button_index + 1, ipadx=80, ipady=10, pady=5, sticky=tk.EW)

    ## Crio o Frame inferior

    lower_frame = tk.Frame(priceFrame, bg=COLORS["background"])
    lower_frame.grid(column=0, row=2, sticky=tk.NS, pady=1, padx=20)

    return priceFrame

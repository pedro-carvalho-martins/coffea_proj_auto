import tkinter as tk

import navigation
import rwPaymentMethodsList
import rwConnCheckFile
from tkinter_frames.ui_components import (
    create_amount_display,
    create_screen,
    create_touch_button,
)
from tkinter_frames.ui_theme import COLORS, FONT_BUTTON


PAYMENT_METHOD_DISPLAY_NAMES = {
    "QR Code (Pix)": "Pix (QR Code)",
}


def display_payment_method_name(payment_method):
    return PAYMENT_METHOD_DISPLAY_NAMES.get(payment_method, payment_method)


## Ação de clique em botão

def button_clicked(index_button, lista_metodos_pag, price_selected, pmethodFrame):
   print('Button clicked')
   print(lista_metodos_pag[index_button])
   print(price_selected)
   navigation.navigate_payment_process(price_selected, lista_metodos_pag[index_button], pmethodFrame)


## Obtém lista de métodos de pagamento válidos com conexão validada
def getPaymentMethodList():

    lista_metodos_pag_habilitados = rwPaymentMethodsList.readListDisplay()
    status_conexoes = rwConnCheckFile.readConnCheckStatus()

    conn_error_pMethods = []

    for i in range(len(lista_metodos_pag_habilitados)-1,-1,-1):
        if (lista_metodos_pag_habilitados[i] == "Crédito"
            or lista_metodos_pag_habilitados[i] == "Débito"
            or lista_metodos_pag_habilitados[i] == "Voucher"):

            if status_conexoes["Moderninha"] == "error":
                conn_error_pMethods.append(lista_metodos_pag_habilitados.pop(i))

        elif (lista_metodos_pag_habilitados[i] == "QR Code (Pix)"):
            if status_conexoes["QR Code (Pix)"] == "error":
                conn_error_pMethods.append(lista_metodos_pag_habilitados.pop(i))

    return lista_metodos_pag_habilitados, conn_error_pMethods


## Função de criação do Frame de método de pagamento

def createPaymentMethodFrame(mainContainer, price_selected, cancel_command=None):

    # Antiga lista de métodos de pagamento sem configuração no app
    # lista_metodos_pag = ["Crédito", "Débito", "Voucher", "QR Code (Pix)"]


    # START DEV 2023.04.07 - TESTAR NO RPI

    # Nova lista de métodos de pagamento puxados de um txt
    #lista_metodos_pag = rwPaymentMethodsList.readListDisplay()
    lista_metodos_pag, conn_error_pMethods = getPaymentMethodList()

    # END DEV 2023.04.07 - TESTAR NO RPI


    pmethodFrame = create_screen(mainContainer)


    ## Configurando o Grid

    pmethodFrame.rowconfigure(0, weight=0)
    pmethodFrame.rowconfigure(1, weight=1)
    pmethodFrame.rowconfigure(2, weight=0)
    pmethodFrame.columnconfigure(0, weight=1)


    ## Adiciono o label principal

    selected_price_frame = create_amount_display(pmethodFrame, price_selected)
    selected_price_frame.grid(
        column=0,
        row=0,
        sticky=tk.EW,
        pady=(12, 6),
        padx=16,
    )

    divider = tk.Frame(pmethodFrame, height=1, bg=COLORS["divider"])
    divider.grid(column=0, row=0, sticky=tk.SEW, padx=22)


    ## Crio o Frame dos botões

    button_frame = tk.Frame(pmethodFrame, bg=COLORS["background"])
    button_frame.grid(column=0, row=1, sticky=tk.NSEW, pady=(8, 3), padx=16)
    button_frame.columnconfigure(0, weight=1)


    ## Adiciono os botões

    buttons_list=[]

    for button_index in range(len(lista_metodos_pag)):
       buttons_list.append(create_touch_button(
           button_frame,
           display_payment_method_name(lista_metodos_pag[button_index]),
           lambda idx=button_index: button_clicked(
               idx,
               lista_metodos_pag,
               price_selected,
               pmethodFrame,
           ),
           font=FONT_BUTTON,
       ))

    for button_index in range(len(buttons_list)):
       buttons_list[button_index].grid(
           column=0,
           row=button_index,
           ipady=8,
           pady=4,
           sticky=tk.EW,
       )


    ## Adiciono o label de flag de eventuais falhas de conexão

    label_flag_fail = tk.Label(
       pmethodFrame,
       text="Falha de conexão: "+str(conn_error_pMethods)+"\n" + "Entrar em contato com suporte técnico",
       font=('SegoeUI', 10), fg=COLORS["danger"],
       bg=COLORS["background"],
       wraplength=250)

    # Feature de exibição dos métodos de pagamento cujo ConnCheck falhou.
    # Código comentado - feature abandonada para não confundir o usuário no momento do pagamento.

    # if len(conn_error_pMethods) > 0:
    #     label_flag_fail.grid(column=0, row=2, sticky=tk.S, pady=0, padx=20)


    ## Crio o Frame inferior

    lower_frame = tk.Frame(pmethodFrame, bg=COLORS["background"])
    lower_frame.grid(column=0, row=2, sticky=tk.EW, pady=(0, 10), padx=16)
    lower_frame.columnconfigure(0, weight=1)

    cancelar_compra_button = create_touch_button(
        lower_frame,
        "Cancelar",
        cancel_command or mainContainer.destroy,
        variant="danger",
        font=("Ubuntu", 15, "bold"),
    )

    cancelar_compra_button.grid(column=0, row=0, ipady=8, pady=3, sticky=tk.EW)

    return pmethodFrame


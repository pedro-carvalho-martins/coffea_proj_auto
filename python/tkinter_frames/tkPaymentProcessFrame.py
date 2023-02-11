import tkinter as tk

import navigation


## Ação de clique em botão

def button_clicked(index_button):
   print('Button clicked')
   print(index_button)


## Função de criação do Frame de início

def createPayProcessFrame():


    payProcessFrame = tk.Frame(height=480, width=320)


    ## Configurando o Grid

    payProcessFrame.rowconfigure(0, weight=1)
    payProcessFrame.columnconfigure(0, weight=1)


    ## Adiciono o label

    label = tk.Label(
       payProcessFrame,
       text="Proceda ao pagamento na máquina de cartão",
       font=('SegoeUI', 20),
       wraplength=300)
    label.grid(column=0, row=0, ipadx=10, ipady=180)


    return payProcessFrame


def createPaySuccessFrame():

    payCompleteFrame = tk.Frame(height=480, width=320)


    ## Configurando o Grid

    payCompleteFrame.rowconfigure(0, weight=1)
    payCompleteFrame.columnconfigure(0, weight=1)


    ## Adiciono o label

    label = tk.Label(
       payCompleteFrame,
       text="Pagamento concluído. Favor escolher a sua bebida.",
       font=('SegoeUI', 20),
       wraplength=300)
    label.grid(column=0, row=0, ipadx=10, ipady=180)

    return payCompleteFrame



def createPayFailureFrame():

    payFailureFrame = tk.Frame(height=480, width=320)


    ## Configurando o Grid

    payFailureFrame.rowconfigure(0, weight=1)
    payFailureFrame.columnconfigure(0, weight=1)


    ## Adiciono o label

    label = tk.Label(
       payFailureFrame,
       text="Erro no pagamento. Favor recomeçar a compra.",
       font=('SegoeUI', 20),
       wraplength=300)
    label.grid(column=0, row=0, ipadx=10, ipady=180)

    return payFailureFrame

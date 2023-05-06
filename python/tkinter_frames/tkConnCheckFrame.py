import tkinter as tk

import navigation


def createConnCheckFrame(mainContainer):

    connCheckFrame = tk.Frame(mainContainer, height=480, width=320)


    ## Configurando o Grid

    connCheckFrame.rowconfigure(0, weight=1)
    connCheckFrame.columnconfigure(0, weight=1)


    ## Adiciono o label

    label = tk.Label(
       connCheckFrame,
       text="Aguardando conexão com máquina de cartão.",
       font=('SegoeUI', 20),
       wraplength=300)
    label.grid(column=0, row=0, ipadx=10, ipady=180)

    return connCheckFrame

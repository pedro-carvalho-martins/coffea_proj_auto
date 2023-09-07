import tkinter as tk

import navigation

## Função de criação do Frame de Inhibit

def createInhibitFrame(inhibitContainer):



    inhibitFrame = tk.Frame(inhibitContainer, height=480, width=320)

    ## Configurando o Grid

    inhibitFrame.rowconfigure(0, weight=3)
    inhibitFrame.rowconfigure(1, weight=3)
    inhibitFrame.rowconfigure(2, weight=3)
    inhibitFrame.columnconfigure(0, weight=3)
    inhibitFrame.columnconfigure(1, weight=3)
    inhibitFrame.columnconfigure(2, weight=3)

    ## Adiciono o label principal

    label = tk.Label(
        inhibitFrame,
        text="Máquina\nem espera",
        font=('SegoeUI', 20),
        wraplength=250,
        justify=tk.CENTER)
    label.grid(column=1, row=1, sticky=tk.EW, pady=0, padx=0)

    return inhibitFrame
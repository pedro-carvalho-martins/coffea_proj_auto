import tkinter as tk

import navigation

## Função de criação do Frame de Inhibit

def createInhibitFrame(inhibitContainer):


    lista_tipos_config = ["Preços", "Métodos pagamento", "Endereço MAC Moderninha", "Voltar"]


    inhibitFrame = tk.Frame(inhibitContainer, height=480, width=320)


    ## Configurando o Grid

    inhibitFrame.rowconfigure(0, weight=3)
    inhibitFrame.rowconfigure(1, weight=3)
    inhibitFrame.rowconfigure(2, weight=3)


    ## Adiciono o label principal

    label = tk.Label(
       inhibitFrame,
       text="Máquina de café\nfora de serviço",
       font=('SegoeUI', 20),
       wraplength=250)
    label.grid(column=0, row=1, sticky=tk.S, pady=0, padx=20)

    return inhibitFrame
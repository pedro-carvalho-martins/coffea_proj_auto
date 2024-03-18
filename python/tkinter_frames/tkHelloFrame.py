import tkinter as tk

import navigation


## Ação de clique em botão

def button_clicked(index_button):
   print('Button clicked')
   print(index_button)


## Função de criação do Frame de início

def createHelloFrame(mainContainer):


    helloFrame = tk.Frame(mainContainer, height=480, width=320)


    ## Configurando o Grid

    helloFrame.rowconfigure(0, weight=1)
    helloFrame.columnconfigure(0, weight=1)


    # ## Adiciono o label principal
    #
    # label = tk.Label(
    #    helloFrame,
    #    text="Toque na tela para iniciar",
    #    font=('SegoeUI', 26))
    # label.grid(column=0, row=0, sticky=tk.S, pady=0, padx=20)

    ## Adiciono um botão que ocupa toda a tela

    helloButton = tk.Button(
        helloFrame,
        text="Toque na tela para iniciar a compra",
        font=('SegoeUI', 20),
        wraplength=300,
        command= lambda: navigation.navigate_priceFrame(helloFrame))

    helloButton.grid(row=0, column=0, ipadx=10, ipady=180)

    return helloFrame


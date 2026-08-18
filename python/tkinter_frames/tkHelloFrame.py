import tkinter as tk

import navigation
from tkinter_frames.ui_components import create_screen, create_touch_button
from tkinter_frames.ui_theme import COLORS


## Ação de clique em botão

def button_clicked(index_button):
   print('Button clicked')
   print(index_button)


## Função de criação do Frame de início

def createHelloFrame(mainContainer):
    helloFrame = create_screen(mainContainer)

    helloFrame.rowconfigure(0, weight=1)
    helloFrame.columnconfigure(0, weight=1)

    helloButton = create_touch_button(
        helloFrame,
        "Toque na tela\npara iniciar a compra",
        lambda: navigation.navigate_priceFrame(helloFrame),
        font=("SegoeUI", 22, "bold"),
        wraplength=300,
    )

    helloButton.grid(
        row=0,
        column=0,
        sticky=tk.NSEW,
        padx=16,
        pady=24,
    )
    helloButton.configure(
        activebackground=COLORS["surface_alt"],
        highlightbackground=COLORS["divider"],
    )

    return helloFrame


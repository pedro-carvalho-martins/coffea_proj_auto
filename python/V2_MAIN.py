import tkinter as tk

import V2_HELLOFRAME
import V2_PRICEFRAME

## Configurando o container principal

mainContainer = tk.Tk()
mainContainer.title("sistema_pagamento_plugpag")

mainContainer.geometry('320x480')
mainContainer.resizable(False, False)
mainContainer.attributes('-fullscreen', True)


myFrame = V2_HELLOFRAME.createHelloFrame()
myFrame.pack(side="top", fill="both", expand=True)



## Temporary

def quit_win():
   mainContainer.destroy()

#Create a Quit Button
#button_quit=tk.Button(mainContainer,text="Quit", font=('Ubuntu', 13, 'bold'), command= quit_win)
#button_quit.grid(column=0, row=5)

## Temporary ends



mainContainer.mainloop()
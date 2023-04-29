import tkinter as tk

#import tkinter_frames.tkHelloFrame as tkHelloFrame

import navigation


## Configurando o container principal

##mainContainer = tk.Tk()
##mainContainer.title("sistema_pagamento_plugpag")
##
##mainContainer.geometry('320x480')
##mainContainer.resizable(False, False)
##mainContainer.attributes('-fullscreen', True)

# Determines a session number to check how many times the loop has been executed
session_number = 0

#while True:
session_number = session_number + 1
navigation.navigate_helloFrame(session_number)


##navigation.navigate_helloFrame()


# myFrame = tkHelloFrame.createHelloFrame()
# myFrame.pack(side="top", fill="both", expand=True)

print('debug2')

#mainContainer.mainloop()




## Temporary

def quit_win():
   mainContainer.destroy()

#Create a Quit Button
#button_quit=tk.Button(mainContainer,text="Quit", font=('Ubuntu', 13, 'bold'), command= quit_win)
#button_quit.grid(column=0, row=5)

## Temporary ends




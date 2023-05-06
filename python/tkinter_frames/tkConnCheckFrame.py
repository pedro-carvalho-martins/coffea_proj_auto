import tkinter as tk

import navigation


def createConnCheckFrame(mainContainer):

    connCheckFrame = tk.Frame(mainContainer, height=480, width=320)


    ## Configurando o Grid

    connCheckFrame.rowconfigure(0, weight=7)
    connCheckFrame.rowconfigure(1, weight=1)
    connCheckFrame.rowconfigure(2, weight=1)
    connCheckFrame.rowconfigure(3, weight=1)
    connCheckFrame.rowconfigure(4, weight=6)
    connCheckFrame.columnconfigure(0, weight=1)


    # Configuro o GIF

    imgFrameCount = 12
    imgFrames = [tk.PhotoImage(file='./tkinter_frames/img/loading.gif', format='gif -index %i' % (i)) for i in range(imgFrameCount)]


    def update(ind):

        imgFrame = imgFrames[ind]
        ind += 1
        if ind == imgFrameCount:
            ind = 0
        gifLabel.configure(image=imgFrame)
        connCheckFrame.after(100, update, ind)

    textLabel = tk.Label(
        connCheckFrame,
        text="Aguardando conexão com máquina de cartão.",
        font=('SegoeUI', 20),
        wraplength=300)
    textLabel.grid(column=0, row=1, ipadx=10, ipady=0)

    gifLabel = tk.Label(connCheckFrame)

    gifLabel.grid(row=2, column=0, ipadx=10, ipady=10)

    connCheckFrame.pack(side="top", fill="both", expand=True)

    connCheckFrame.after(0, update, 0)

    return connCheckFrame

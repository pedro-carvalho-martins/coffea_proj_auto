import tkinter as tk

import navigation

# Initializing the global variables
global status_conn_moderninha
global status_conn_servidor_pix
global display_buttons
global flag_reconectar
global flag_continuar

status_conn_moderninha = None
status_conn_servidor_pix = None
display_buttons = None
flag_reconectar = "none"
flag_continuar = "none"




def button_click_1():
    global flag_reconectar
    flag_reconectar = "sim"
def button_click_2():
    global flag_continuar
    flag_continuar = "sim"

def createNewConnCheckFrame(mainContainer):

    global status_conn_moderninha
    global status_conn_servidor_pix
    global display_buttons

    status_conn_moderninha = "loading"
    status_conn_servidor_pix = "loading"
    display_buttons = "no"

    connCheckFrame = tk.Frame(mainContainer, height=480, width=320)


    ## Configurando o Grid

    connCheckFrame.rowconfigure(0, weight=7)
    connCheckFrame.rowconfigure(1, weight=1)
    connCheckFrame.rowconfigure(2, weight=1)
    connCheckFrame.rowconfigure(3, weight=3)
    connCheckFrame.rowconfigure(4, weight=1)
    connCheckFrame.rowconfigure(5, weight=1)
    connCheckFrame.rowconfigure(6, weight=1)
    connCheckFrame.rowconfigure(7, weight=1)
    connCheckFrame.rowconfigure(8, weight=4)
    connCheckFrame.columnconfigure(0, weight=1)


    # Configuro o GIF

    loadingGifFrameCount = 12
    loadingGifFrames = [tk.PhotoImage(file='./tkinter_frames/img/loading.gif', format='gif -index %i' % (i)) for i in range(loadingGifFrameCount)]

    connCheckFrame.checkImg = tk.PhotoImage(file='./tkinter_frames/img/img_check.png')
    connCheckFrame.crossImg = tk.PhotoImage(file='./tkinter_frames/img/img_cross.png')
    connCheckFrame.disabledImg = tk.PhotoImage(file='./tkinter_frames/img/img_disabled.png')

    #status_conn_moderninha = "loading"
    #status_conn_servidor_pix = "loading"

    def update(ind):

        loadingGifCurrentFrame = loadingGifFrames[ind]

        ind += 1
        if ind == loadingGifFrameCount:
            ind = 0

        if status_conn_moderninha == "loading":
            imgLabel1.configure(image=loadingGifCurrentFrame)
        elif status_conn_moderninha == "check":
            imgLabel1.configure(image=connCheckFrame.checkImg)
        elif status_conn_moderninha == "disabled":
            imgLabel1.configure(image=connCheckFrame.disabledImg)
        else:
            imgLabel1.configure(image=connCheckFrame.crossImg)


        if status_conn_servidor_pix == "loading":
            imgLabel2.configure(image=loadingGifCurrentFrame)
        elif status_conn_servidor_pix == "check":
            imgLabel2.configure(image=connCheckFrame.checkImg)
        elif status_conn_servidor_pix == "disabled":
            imgLabel2.configure(image=connCheckFrame.disabledImg)
        else:
            imgLabel2.configure(image=connCheckFrame.crossImg)

        if display_buttons == "yes":
            if not hasattr(connCheckFrame, 'button1'):
                connCheckFrame.button1 = tk.Button(connCheckFrame, text="Reconectar", command=button_click_1, width=20, font=('Ubuntu', 14))
                connCheckFrame.button1.grid(row=6, column=0, ipadx=10, ipady=10)
            if not hasattr(connCheckFrame, 'button2'):
                connCheckFrame.button2 = tk.Button(connCheckFrame, text="Continuar", command=button_click_2, width=20, font=('Ubuntu', 14))
                connCheckFrame.button2.grid(row=7, column=0, ipadx=10, ipady=10)
        else:
            if hasattr(connCheckFrame, 'button1'):
                connCheckFrame.button1.grid_forget()
                delattr(connCheckFrame, 'button1')
            if hasattr(connCheckFrame, 'button2'):
                connCheckFrame.button2.grid_forget()
                delattr(connCheckFrame, 'button2')

        connCheckFrame.after(100, update, ind)

    textLabel1 = tk.Label(
        connCheckFrame,
        text="Status de conexão com máquina de cartão",
        font=('SegoeUI', 16),
        wraplength=300)
    textLabel1.grid(column=0, row=1, ipadx=10, ipady=0)

    textLabel2 = tk.Label(
        connCheckFrame,
        text="Status de conexão com servidor Pix",
        font=('SegoeUI', 16),
        wraplength=300)
    textLabel2.grid(column=0, row=4, ipadx=10, ipady=0)

    imgLabel1 = tk.Label(connCheckFrame)
    imgLabel2 = tk.Label(connCheckFrame)
    #imgLabel3 = tk.Label(connCheckFrame)

    imgLabel1.grid(row=2, column=0, ipadx=10, ipady=0)
    imgLabel2.grid(row=5, column=0, ipadx=10, ipady=0)
    #imgLabel3.grid(row=6, column=0, ipadx=10, ipady=10)

    imgLabel2.configure(image=connCheckFrame.checkImg)
    #imgLabel3.configure(image=connCheckFrame.crossImg)


    connCheckFrame.pack(side="top", fill="both", expand=True)



    connCheckFrame.after(0, update, 0)

    return connCheckFrame
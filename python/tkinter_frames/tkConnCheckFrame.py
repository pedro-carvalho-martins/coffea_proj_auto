import tkinter as tk

import rwServerPairingSettings
from tkinter_frames.ui_components import StatusCard, create_screen, create_touch_button
from tkinter_frames.ui_theme import COLORS, FONT_NORMAL_BOLD, FONT_TITLE


status_conn_moderninha = None
status_conn_servidor_pix = None
display_buttons = None
flag_reconectar = "none"
flag_continuar = "none"

SERVER_FAILURE_MESSAGES = {
    "pending": "Pareamento pendente",
    "no_internet": "Sem conexão com a internet",
    "connection_problem": "Problema de conexão",
}


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
    pairing_code = rwServerPairingSettings.get_pairing_code()

    connCheckFrame = create_screen(mainContainer)
    connCheckFrame.columnconfigure(0, weight=1)
    connCheckFrame.rowconfigure(0, weight=1)
    connCheckFrame.rowconfigure(5, weight=1)

    loadingGifFrameCount = 12
    loadingGifFrames = [
        tk.PhotoImage(
            file="./tkinter_frames/img/loading.gif",
            format="gif -index %i" % index,
        )
        for index in range(loadingGifFrameCount)
    ]
    connCheckFrame.checkImg = tk.PhotoImage(
        file="./tkinter_frames/img/img_check.png"
    )
    connCheckFrame.crossImg = tk.PhotoImage(
        file="./tkinter_frames/img/img_cross.png"
    )
    connCheckFrame.disabledImg = tk.PhotoImage(
        file="./tkinter_frames/img/img_disabled.png"
    )

    tk.Label(
        connCheckFrame,
        text="Verificando conexão",
        font=FONT_TITLE,
        bg=COLORS["background"],
        fg=COLORS["text"],
    ).grid(row=1, column=0, padx=16, pady=(8, 14))

    moderninha_card = StatusCard(
        connCheckFrame,
        "Status de conexão com máquina de cartão",
    )
    moderninha_card.grid(
        row=2,
        column=0,
        sticky=tk.EW,
        padx=16,
        pady=(0, 8),
    )

    server_card = StatusCard(
        connCheckFrame,
        "Status de conexão com servidor",
    )
    server_card.grid(
        row=3,
        column=0,
        sticky=tk.EW,
        padx=16,
        pady=(0, 8),
    )

    serverFailureLabel = tk.Label(
        connCheckFrame,
        text="",
        font=FONT_NORMAL_BOLD,
        bg=COLORS["background"],
        fg=COLORS["danger"],
        wraplength=285,
        justify=tk.CENTER,
    )
    serverFailureLabel.grid(row=4, column=0, padx=16, pady=(6, 0))

    def visual_state(status, loading_image):
        if status == "loading":
            return loading_image, "Verificando...", "loading"
        if status == "check":
            return connCheckFrame.checkImg, "Conectado", "success"
        if status == "disabled":
            return connCheckFrame.disabledImg, "Desabilitado", "disabled"
        return (
            connCheckFrame.crossImg,
            SERVER_FAILURE_MESSAGES.get(status, "Indisponível"),
            "error",
        )

    def update(index):
        loading_image = loadingGifFrames[index]
        next_index = (index + 1) % loadingGifFrameCount

        moderninha_card.set_state(
            *visual_state(status_conn_moderninha, loading_image)
        )
        server_card.set_state(
            *visual_state(status_conn_servidor_pix, loading_image)
        )

        server_message = SERVER_FAILURE_MESSAGES.get(
            status_conn_servidor_pix,
            "",
        )
        if status_conn_servidor_pix == "pending":
            server_message += "\nCódigo de pareamento: {}".format(pairing_code)
        if serverFailureLabel.cget("text") != server_message:
            serverFailureLabel.configure(text=server_message)

        if display_buttons == "yes":
            if not hasattr(connCheckFrame, "button1"):
                connCheckFrame.button1 = create_touch_button(
                    connCheckFrame,
                    "Reconectar",
                    button_click_1,
                    variant="primary",
                    font=("Ubuntu", 14, "bold"),
                )
                connCheckFrame.button1.grid(
                    row=5,
                    column=0,
                    sticky=tk.SEW,
                    padx=16,
                    pady=(8, 3),
                    ipady=8,
                )
            if not hasattr(connCheckFrame, "button2"):
                connCheckFrame.button2 = create_touch_button(
                    connCheckFrame,
                    "Continuar",
                    button_click_2,
                    font=("Ubuntu", 14, "bold"),
                )
                connCheckFrame.button2.grid(
                    row=6,
                    column=0,
                    sticky=tk.EW,
                    padx=16,
                    pady=(3, 10),
                    ipady=8,
                )
        else:
            if hasattr(connCheckFrame, "button1"):
                connCheckFrame.button1.grid_forget()
                delattr(connCheckFrame, "button1")
            if hasattr(connCheckFrame, "button2"):
                connCheckFrame.button2.grid_forget()
                delattr(connCheckFrame, "button2")

        connCheckFrame.after(100, update, next_index)

    connCheckFrame.pack(side="top", fill="both", expand=True)
    connCheckFrame.after(0, update, 0)
    return connCheckFrame

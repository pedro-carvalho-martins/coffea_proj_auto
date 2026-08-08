import tkinter as tk


def _message_frame(main_container, message, background="SystemButtonFace", foreground="black"):
    frame = tk.Frame(main_container, height=480, width=320, bg=background)
    frame.rowconfigure(0, weight=1)
    frame.columnconfigure(0, weight=1)
    label = tk.Label(
        frame,
        text=message,
        font=("SegoeUI", 20),
        wraplength=285,
        bg=background,
        fg=foreground,
    )
    label.grid(column=0, row=0, padx=15, pady=120)
    frame.mdb_status_label = label
    return frame


def createWaitingFrame(main_container):
    return _message_frame(main_container, "Inicializando MDB...\nAguarde.")


def updateWaitingFrame(frame, message):
    if frame and frame.winfo_exists() and hasattr(frame, "mdb_status_label"):
        frame.mdb_status_label.configure(text=message)


def createAwaitingDispenseFrame(main_container):
    return _message_frame(
        main_container,
        "Pagamento aceito.\nAguardando a máquina liberar o produto...",
        "#b06b00",
        "white",
    )


def createDispensedFrame(main_container):
    return _message_frame(main_container, "Produto liberado com sucesso.", "#138713", "white")


def createFailureFrame(main_container, message="Venda cancelada."):
    return _message_frame(main_container, message, "#871313", "white")


def createRecoveryFrame(main_container, resolve_command):
    frame = _message_frame(
        main_container,
        "Resultado da venda incerto. Verifique a Moderninha e a máquina antes de continuar.",
        "#871313",
        "white",
    )
    tk.Button(
        frame,
        text="Já verifiquei — encerrar sessão",
        font=("Ubuntu", 13),
        command=resolve_command,
    ).grid(column=0, row=1, padx=15, pady=(0, 35), ipadx=8, ipady=8)
    return frame

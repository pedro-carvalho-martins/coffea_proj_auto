from tkinter_frames.ui_components import create_result_screen
from tkinter_frames.ui_theme import COLORS


def _message_frame(main_container, message, background=None, foreground=None):
    frame = create_result_screen(
        main_container,
        message,
        background=background or COLORS["background"],
        foreground=foreground or COLORS["text"],
    )
    # Navigation updates this label while the MDB connection state changes.
    frame.mdb_status_label = frame.status_title_label
    return frame


def createWaitingFrame(main_container):
    return _message_frame(
        main_container,
        "Inicializando MDB...\n\nAguarde.",
    )


def updateWaitingFrame(frame, message):
    if frame and frame.winfo_exists() and hasattr(frame, "mdb_status_label"):
        frame.mdb_status_label.configure(text=message)


def createAwaitingDispenseFrame(main_container):
    return _message_frame(
        main_container,
        "Pagamento aceito.\n\nAguardando a máquina\nliberar o produto...",
        COLORS["warning"],
        COLORS["white"],
    )


def createDispensedFrame(main_container):
    return _message_frame(
        main_container,
        "Produto liberado\ncom sucesso.",
        COLORS["success"],
        COLORS["white"],
    )


def createFailureFrame(main_container, message="Venda cancelada."):
    return _message_frame(
        main_container,
        message,
        COLORS["danger"],
        COLORS["white"],
    )


def createRecoveryFrame(main_container, resolve_command):
    frame = create_result_screen(
        main_container,
        "Resultado da venda incerto",
        (
            "Verifique a máquina de cartão e a máquina vending antes de "
            "continuar."
        ),
        background=COLORS["danger"],
        foreground=COLORS["white"],
        button_text="Já verifiquei - encerrar sessão",
        button_command=resolve_command,
    )
    frame.mdb_status_label = frame.status_title_label
    return frame

import tkinter as tk

from PIL import Image, ImageTk

from tkinter_frames.ui_components import (
    create_amount_display,
    create_instruction_screen,
    create_result_screen,
    create_screen,
    create_touch_button,
)
from tkinter_frames.ui_theme import COLORS, FONT_SECONDARY


def createPayProcessFrame(mainContainer):
    return create_instruction_screen(
        mainContainer,
        "Aproxime ou insira\nseu cartão na\nmáquina abaixo",
        "Para cancelar, aperte no botão CANCELA na máquina abaixo.",
    )


def createPaySuccessFrame(mainContainer):
    return create_result_screen(
        mainContainer,
        "Pagamento concluído.",
        "Favor escolher\no seu produto.",
        background=COLORS["success"],
        foreground=COLORS["white"],
    )


def createDeliveryProgressFrame(mainContainer):
    return create_result_screen(
        mainContainer,
        "Pagamento recebido.",
        "Transmissão de créditos\nà máquina em andamento.",
        background=COLORS["progress"],
        foreground=COLORS["white"],
    )


def createPayFailureFrame(mainContainer):
    return create_result_screen(
        mainContainer,
        "Erro no pagamento.",
        "Favor recomeçar\na compra.",
        background=COLORS["danger"],
        foreground=COLORS["white"],
    )


def createDeliveryFailureFrame(mainContainer):
    return create_result_screen(
        mainContainer,
        "Pagamento aprovado",
        (
            "A entrega do crédito não pôde ser confirmada.\n\n"
            "Procure o responsável pelo local."
        ),
        background=COLORS["warning"],
        foreground=COLORS["white"],
    )


def createPayProcessFrame_Pix(mainContainer):
    return create_instruction_screen(
        mainContainer,
        "Inicializando\npagamento por Pix",
        "Aguarde a geração do QR Code.",
    )


def createPixDisplayFrame(
    mainContainer,
    price_selected,
    filename_img_QR_Code_Pix,
    cancel_command,
):
    pixDisplayFrame = create_screen(mainContainer)
    pixDisplayFrame.columnconfigure(0, weight=1)
    pixDisplayFrame.rowconfigure(1, weight=1)

    header_frame = create_amount_display(
        pixDisplayFrame,
        price_selected,
        label="Valor do Pix:",
    )
    header_frame.grid(column=0, row=0, sticky=tk.EW, padx=16, pady=(4, 0))
    tk.Label(
        header_frame,
        text="Escaneie o QR Code abaixo no aplicativo do seu banco",
        font=FONT_SECONDARY,
        bg=COLORS["background"],
        fg=COLORS["text_secondary"],
        wraplength=275,
        justify=tk.CENTER,
    ).pack()

    try:
        img_QR_Code = Image.open(filename_img_QR_Code_Pix)
        img_QR_Code = img_QR_Code.resize((280, 280), Image.ANTIALIAS)
        img_QR_Code = ImageTk.PhotoImage(img_QR_Code)

        imgLabel = tk.Label(
            pixDisplayFrame,
            image=img_QR_Code,
            bg=COLORS["surface"],
            bd=0,
        )
        imgLabel.image = img_QR_Code
        imgLabel.grid(row=1, column=0, pady=2)
    except Exception as error:
        print("error:", error)

    cancelar_compra_button = create_touch_button(
        pixDisplayFrame,
        "Cancelar",
        cancel_command,
        variant="danger",
        font=("Ubuntu", 15, "bold"),
    )
    cancelar_compra_button.grid(
        column=0,
        row=2,
        sticky=tk.EW,
        padx=16,
        pady=(3, 9),
        ipady=7,
    )

    return pixDisplayFrame

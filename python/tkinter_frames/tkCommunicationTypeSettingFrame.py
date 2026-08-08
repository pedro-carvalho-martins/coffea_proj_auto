import tkinter as tk

import navigation
import rwCommunicationType


def createCommunicationTypeSettingFrame(settingsContainer):
    frame = tk.Frame(settingsContainer, height=480, width=320)
    frame.columnconfigure(0, weight=1)

    tk.Label(
        frame,
        text="Tipo de comunicação",
        font=("SegoeUI", 18),
    ).grid(column=0, row=0, pady=(45, 20), padx=20)

    selected = tk.StringVar(value=rwCommunicationType.readCommunicationType())
    for row, (value, label) in enumerate(
        ((rwCommunicationType.PULSE, "Pulso"), (rwCommunicationType.MDB, "MDB")),
        start=1,
    ):
        tk.Radiobutton(
            frame,
            text=label,
            value=value,
            variable=selected,
            font=("Ubuntu", 18),
        ).grid(column=0, row=row, pady=10, padx=30, sticky=tk.W)

    tk.Label(
        frame,
        text="A alteração entra em vigor quando a aplicação reiniciar.",
        font=("SegoeUI", 11),
        wraplength=270,
    ).grid(column=0, row=3, pady=25, padx=20)

    tk.Button(
        frame,
        text="Sair sem salvar",
        font=("Ubuntu", 14),
        command=navigation.quitProgramAfterSettings,
    ).grid(column=0, row=4, ipadx=25, ipady=8, pady=6)

    def save_and_quit():
        rwCommunicationType.writeCommunicationType(selected.get())
        navigation.quitProgramAfterSettings()

    tk.Button(
        frame,
        text="Salvar e sair",
        font=("Ubuntu", 14),
        command=save_and_quit,
    ).grid(column=0, row=5, ipadx=30, ipady=8, pady=6)
    return frame

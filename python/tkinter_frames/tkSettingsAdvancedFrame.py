import tkinter as tk

import navigation


def _open_setting(action, frame):
    navigation.navigate_selected_setting_menu(action, frame)


def createAdvancedSettingSelectionFrame(settingsContainer):
    frame = tk.Frame(settingsContainer, height=480, width=320)
    frame.columnconfigure(0, weight=1)

    tk.Label(
        frame,
        text="Configurações avançadas",
        font=("SegoeUI", 14),
    ).grid(column=0, row=0, pady=(30, 20), padx=20)

    actions = [
        ("Config. valor pulso", "Config. valor pulso"),
        ("Config. tela inicial", "Config. tela inicial"),
        ("Restaurar configurações de fábrica", "Restaurar configurações de fábrica"),
        ("Voltar configurações", "Voltar"),
    ]
    for row, (action, label) in enumerate(actions, start=1):
        tk.Button(
            frame,
            text=label,
            font=("Ubuntu", 11),
            wraplength=250,
            command=lambda selected=action: _open_setting(selected, frame),
        ).grid(
            column=0,
            row=row,
            ipadx=10,
            ipady=8,
            pady=5,
            padx=30,
            sticky=tk.EW,
        )

    return frame

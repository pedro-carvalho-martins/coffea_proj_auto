import tkinter as tk

import navigation
import rwServerPairingSettings


def _open_setting(action, frame):
    navigation.navigate_selected_setting_menu(action, frame)


def createAdvancedSettingSelectionFrame(settingsContainer):
    frame = tk.Frame(settingsContainer, height=480, width=320)
    frame.columnconfigure(0, weight=1)

    tk.Label(
        frame,
        text="Configurações avançadas",
        font=("SegoeUI", 14),
    ).grid(column=0, row=0, pady=(18, 10), padx=20)

    tk.Label(
        frame,
        text=f"Código de pareamento: {rwServerPairingSettings.get_pairing_code()}",
        font=("SegoeUI", 10, "bold"),
    ).grid(column=0, row=1, pady=4, padx=20)

    online_mode_var = tk.BooleanVar(
        value=rwServerPairingSettings.is_online_mode_enabled()
    )
    tk.Checkbutton(
        frame,
        text="Operação on-line",
        variable=online_mode_var,
        command=lambda: rwServerPairingSettings.set_online_mode_enabled(
            online_mode_var.get()
        ),
        font=("SegoeUI", 10),
    ).grid(column=0, row=2, pady=(4, 8), padx=20)

    actions = [
        ("Tipo de comunicacao", "Tipo de comunicacao"),
        ("Config. valor pulso", "Config. valor pulso"),
        ("Config. tela inicial", "Config. tela inicial"),
        ("Restaurar configurações de fábrica", "Restaurar configurações de fábrica"),
        ("Voltar configurações", "Voltar"),
    ]
    for row, (action, label) in enumerate(actions, start=3):
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

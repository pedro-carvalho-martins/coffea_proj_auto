import tkinter as tk
from threading import Thread

import navigation
import rwServerPairingSettings
import rwSystemId
import serverPairingProcess


def _status_label_text(status):
    labels = {
        "not_checked": "Ainda não verificado",
        "pending": "Aguardando aprovação do administrador",
        "paired": "Pareamento concluído",
        "offline": "Operação off-line",
        "connection_error": "Não foi possível conectar ao servidor",
    }
    return labels.get(status, status)


def createServerPairingSettingFrame(settingsContainer):
    frame = tk.Frame(settingsContainer, height=480, width=320)
    frame.columnconfigure(0, weight=1)

    tk.Label(frame, text="Pareamento com servidor", font=("SegoeUI", 14)).grid(
        column=0, row=0, pady=(18, 10), padx=20
    )
    tk.Label(
        frame,
        text=f"ID do sistema:\n{rwSystemId.readSystemId()}",
        font=("SegoeUI", 9),
        wraplength=275,
    ).grid(column=0, row=1, pady=5, padx=20)
    tk.Label(
        frame,
        text=f"Código de pareamento: {rwServerPairingSettings.get_pairing_code()}",
        font=("SegoeUI", 11, "bold"),
    ).grid(column=0, row=2, pady=8, padx=20)

    status_var = tk.StringVar()
    details_var = tk.StringVar()
    tk.Label(frame, textvariable=status_var, font=("SegoeUI", 10), wraplength=275).grid(
        column=0, row=3, pady=6, padx=20
    )
    tk.Label(frame, textvariable=details_var, font=("SegoeUI", 8), wraplength=275).grid(
        column=0, row=4, pady=4, padx=20
    )

    online_mode_var = tk.BooleanVar(value=rwServerPairingSettings.is_online_mode_enabled())

    def refresh_status():
        state = serverPairingProcess.get_pairing_state()
        status_var.set(f"Status: {_status_label_text(state['status'])}")
        details = f"Último contato: {state['last_contact']}"
        if state["last_error"]:
            details = f"{details}\n{state['last_error']}"
        details_var.set(details)
        frame.after(1000, refresh_status)

    def save_mode():
        rwServerPairingSettings.set_online_mode_enabled(online_mode_var.get())
        Thread(target=serverPairingProcess.sync_once, daemon=True).start()

    tk.Checkbutton(
        frame,
        text="Operação on-line",
        variable=online_mode_var,
        command=save_mode,
        font=("SegoeUI", 10),
    ).grid(column=0, row=5, pady=(14, 6))
    tk.Button(
        frame,
        text="Tentar pareamento agora",
        font=("Ubuntu", 10),
        command=lambda: Thread(target=serverPairingProcess.sync_once, daemon=True).start(),
    ).grid(column=0, row=6, pady=6, padx=30, sticky=tk.EW)
    tk.Button(
        frame,
        text="Voltar",
        font=("Ubuntu", 10),
        command=navigation.quitProgramAfterSettings,
    ).grid(column=0, row=7, pady=12, padx=30, sticky=tk.EW)

    refresh_status()
    return frame

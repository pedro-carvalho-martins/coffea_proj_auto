import tkinter as tk

import factoryResetProcess
import navigation


def createFactoryResetFrame(settingsContainer):
    frame = tk.Frame(settingsContainer, height=480, width=320)
    frame.columnconfigure(0, weight=1)

    tk.Label(
        frame,
        text="Restaurar configurações\nde fábrica?",
        font=("SegoeUI", 16, "bold"),
    ).grid(column=0, row=0, pady=(25, 12), padx=20)
    tk.Label(
        frame,
        text=(
            "Todos os ajustes locais, o ID do sistema e o pareamento serão "
            "apagados. O sistema será reiniciado e precisará ser pareado novamente.\n\n"
            "O aplicativo, os logs e os backups serão preservados. O registro antigo "
            "deverá ser inativado manualmente no servidor."
        ),
        font=("SegoeUI", 10),
        wraplength=275,
        justify=tk.CENTER,
    ).grid(column=0, row=1, pady=10, padx=20)

    result_var = tk.StringVar()
    tk.Label(
        frame,
        textvariable=result_var,
        font=("SegoeUI", 9),
        wraplength=275,
        fg="#a00000",
    ).grid(column=0, row=2, pady=5, padx=20)

    def confirm_reset():
        reset_button.config(state="disabled")
        cancel_button.config(state="disabled")
        result_var.set("Restaurando configurações e reiniciando...")
        frame.update_idletasks()
        try:
            factoryResetProcess.reset_settings_and_reboot()
        except Exception as error:
            result_var.set(f"Não foi possível concluir o reset: {error}")
            reset_button.config(state="normal")
            cancel_button.config(state="normal")

    reset_button = tk.Button(
        frame,
        text="Restaurar e reiniciar",
        font=("Ubuntu", 12, "bold"),
        bg="#b71c1c",
        fg="white",
        activebackground="#8e0000",
        activeforeground="white",
        command=confirm_reset,
    )
    reset_button.grid(
        column=0,
        row=3,
        ipadx=10,
        ipady=8,
        pady=(18, 8),
        padx=30,
        sticky=tk.EW,
    )

    cancel_button = tk.Button(
        frame,
        text="Cancelar",
        font=("Ubuntu", 11),
        command=lambda: navigation.navigate_selected_setting_menu(
            "Configurações avançadas",
            frame,
        ),
    )
    cancel_button.grid(
        column=0,
        row=4,
        ipadx=10,
        ipady=6,
        pady=8,
        padx=30,
        sticky=tk.EW,
    )

    return frame

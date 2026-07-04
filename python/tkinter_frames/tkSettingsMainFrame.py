import tkinter as tk

import navigation
import rwSystemVersion


def button_clicked(index_button, lista_tipos_config, settingSelectionFrame):
    print("Button clicked")
    print(lista_tipos_config[index_button])
    navigation.navigate_selected_setting_menu(lista_tipos_config[index_button], settingSelectionFrame)


def createSettingSelectionFrame(settingsContainer):
    lista_tipos_config = [
        "Precos",
        "Metodos pagamento",
        "Nome sistema",
        "Endereco MAC Moderninha",
        "Config. valor pulso",
        "Config. de rede - Encerrar app",
        "Config. tela inicial",
        "Voltar",
    ]

    settingSelectionFrame = tk.Frame(settingsContainer, height=480, width=320)

    settingSelectionFrame.rowconfigure(0, weight=2)
    settingSelectionFrame.rowconfigure(1, weight=6)
    settingSelectionFrame.rowconfigure(2, weight=1)
    settingSelectionFrame.columnconfigure(0, weight=1)

    label = tk.Label(
        settingSelectionFrame,
        text="Configuracoes\nv" + rwSystemVersion.readVersion(),
        font=("SegoeUI", 14),
        wraplength=250,
    )
    label.grid(column=0, row=0, sticky=tk.S, pady=10, padx=20)

    button_frame = tk.Frame(settingSelectionFrame)
    button_frame.grid(column=0, row=1, pady=0, padx=20)

    buttons_list = []

    for button_index in range(len(lista_tipos_config)):
        buttons_list.append(
            tk.Button(
                button_frame,
                text=lista_tipos_config[button_index],
                font=("Ubuntu", 10),
                wraplength=250,
                command=lambda idx=button_index: button_clicked(idx, lista_tipos_config, settingSelectionFrame),
            )
        )

    for button_index in range(len(buttons_list)):
        buttons_list[button_index].grid(column=0, row=button_index + 1, ipadx=10, ipady=5, pady=2, sticky=tk.EW)

    lower_frame = tk.Frame(settingSelectionFrame)
    lower_frame.grid(column=0, row=2, sticky=tk.NS, pady=1, padx=20)

    return settingSelectionFrame

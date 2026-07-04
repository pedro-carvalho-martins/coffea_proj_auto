import tkinter as tk

## TEMPORARY COMMENT TO TEST ON WINDOWS. UNCOMMENT ASAP
import navigation
import rwSystemName
## TEMPORARY COMMENT ENDS. UNCOMMENT ASAP.


# NENHUM TESTE FOI FEITO AINDA. TESTAR!


def add_char(char):
    if len(entry_system_name.get()) < 10:
        entry_system_name.insert(tk.END, char)


def backspace():
    if len(entry_system_name.get()) > 0:
        entry_system_name.delete(len(entry_system_name.get()) - 1, tk.END)


def save_and_quit():
    system_name = entry_system_name.get()

    print(system_name)

    if len(system_name) > 0:
        rwSystemName.writeSystemName(system_name)
        navigation.quitProgramAfterSettings()
        print("ok")


def quit_no_save():
    navigation.quitProgramAfterSettings()


def createSystemNameSettingFrame(settingsContainer):
    systemNameSettingFrame = tk.Frame(settingsContainer, height=480, width=320)

    current_system_name = "Nome do sistema atual: "
    current_system_name = current_system_name + rwSystemName.readSystemName()
    current_name_label = tk.Label(systemNameSettingFrame, text=current_system_name, font=("Arial", 12))
    current_name_label.pack()

    title_label = tk.Label(systemNameSettingFrame, text="Modificar nome do sistema", font=("Arial", 16))
    title_label.pack(pady=10)

    global entry_system_name
    entry_system_name = tk.Entry(systemNameSettingFrame, width=20, font=("Arial", 14))
    entry_system_name.pack(pady=10)

    keyboard_frame = tk.Frame(systemNameSettingFrame)
    keyboard_frame.pack(pady=10)

    letter_layout = [
        ["A", "B"],
        ["C", "D"],
        ["E", "F"],
    ]

    number_layout = [
        ["1", "2", "3"],
        ["4", "5", "6"],
        ["7", "8", "9"],
        ["", "0", ""],
    ]

    letter_frame = tk.Frame(keyboard_frame)
    letter_frame.pack(side=tk.LEFT, padx=10)
    for row in letter_layout:
        button_row = tk.Frame(letter_frame)
        button_row.pack()
        for char in row:
            button = tk.Button(
                button_row,
                text=char,
                width=1,
                height=1,
                font=("Arial", 16),
                command=lambda c=char: add_char(c),
            )
            button.pack(side=tk.LEFT, ipadx=2, ipady=6, padx=2, pady=1)

    number_frame = tk.Frame(keyboard_frame)
    number_frame.pack(side=tk.LEFT)
    for row in number_layout:
        button_row = tk.Frame(number_frame)
        button_row.pack()
        for char in row:
            if char == "":
                spacer = tk.Label(button_row, width=1, height=1, font=("Arial", 16))
                spacer.pack(side=tk.LEFT, padx=2, pady=1)
            else:
                button = tk.Button(
                    button_row,
                    text=char,
                    width=2,
                    height=1,
                    font=("Arial", 16),
                    command=lambda c=char: add_char(c),
                )
                button.pack(side=tk.LEFT, ipadx=2, ipady=2, padx=2, pady=1)

    backspace_button = tk.Button(systemNameSettingFrame, text="Apagar digito", font=("Arial", 14), command=backspace)
    backspace_button.pack(pady=2)

    saveandquit_button = tk.Button(systemNameSettingFrame, text="Salvar e sair", font=("Arial", 14), command=save_and_quit)
    saveandquit_button.pack(pady=2)

    quit_no_save_button = tk.Button(systemNameSettingFrame, text="Sair sem salvar", font=("Arial", 14), command=quit_no_save)
    quit_no_save_button.pack(pady=2)

    return systemNameSettingFrame

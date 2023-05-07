import tkinter as tk

## TEMPORARY COMMENT TO TEST ON WINDOWS. UNCOMMENT ASAP
import navigation
#import rwMACAddress
## TEMPORARY COMMENT ENDS. UNCOMMENT ASAP.


# NENHUM TESTE FOI FEITO AINDA. TESTAR!



## Função de criação do Frame de configuração de endereço MAC

def add_char(char):
    """Add the given character to the next available pair of characters in the MAC address."""
    for entry in mac_address:
        if len(entry.get()) < 2:
            entry.insert(tk.END, char)
            break


def backspace():
    """Remove the last character from the MAC address."""
    for entry in reversed(mac_address):
        if len(entry.get()) > 0:
            entry.delete(len(entry.get()) - 1, tk.END)
            break


def save_and_quit():
    print(mac_address)
    pass


def createMACSettingFrame(settingsContainer):

    MACSettingFrame = tk.Frame(settingsContainer, height=480, width=320)


    # Create label for the title
    title_label = tk.Label(MACSettingFrame, text="Insert MAC Address", font=("Arial", 16))
    title_label.pack(pady=3)

    # Create frame for the MAC address input
    mac_input_frame = tk.Frame(MACSettingFrame)
    mac_input_frame.pack()

    # Create entry widgets for each pair of characters
    global mac_address
    mac_address = []
    for i in range(6):
        entry = tk.Entry(mac_input_frame, width=3, font=("Arial", 14))
        entry.pack(side=tk.LEFT, padx=0, pady=3)
        mac_address.append(entry)
        if i < 5:
            separator = tk.Label(mac_input_frame, text=":", font=("Arial", 14))
            separator.pack(side=tk.LEFT)

    # Create frame for the on-screen keyboard
    keyboard_frame = tk.Frame(MACSettingFrame)
    keyboard_frame.pack(pady=20)

    # Define the MAC address keyboard layout
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

    # Create buttons for each character in the keyboard layout
    letter_frame = tk.Frame(keyboard_frame)
    letter_frame.pack(side=tk.LEFT, padx=10)
    for row in letter_layout:
        button_row = tk.Frame(letter_frame)
        button_row.pack()
        for char in row:
            button = tk.Button(button_row, text=char, width=3, height=2, font=("Arial", 16),
                               command=lambda c=char: add_char(c))
            button.pack(side=tk.LEFT, padx=4, pady=1)

    number_frame = tk.Frame(keyboard_frame)
    number_frame.pack(side=tk.LEFT)
    for row in number_layout:
        button_row = tk.Frame(number_frame)
        button_row.pack()
        for char in row:
            if char == "":
                spacer = tk.Label(button_row, width=3, height=2, font=("Arial", 16))
                spacer.pack(side=tk.LEFT, padx=4, pady=1)
            else:
                button = tk.Button(button_row, text=char, width=3, height=2, font=("Arial", 16),
                                   command=lambda c=char: add_char(c))
                button.pack(side=tk.LEFT, padx=4, pady=1)

    # Create backspace button
    backspace_button = tk.Button(MACSettingFrame, text="Backspace", font=("Arial", 16),
                                 command=backspace)
    backspace_button.pack(pady=5)

    # Create save and quit button
    backspace_button = tk.Button(MACSettingFrame, text="Save and quit", font=("Arial", 16), command=save_and_quit)
    backspace_button.pack(pady=5)




    return MACSettingFrame



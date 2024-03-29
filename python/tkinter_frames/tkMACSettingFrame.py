import tkinter as tk

## TEMPORARY COMMENT TO TEST ON WINDOWS. UNCOMMENT ASAP
import navigation
import rwMACAddress
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

    mac_string = ""

    for field_index in range(len(mac_address)):
        print(mac_address[field_index].get())
        mac_string = mac_string + mac_address[field_index].get()
        if field_index < len(mac_address)-1:
            mac_string = mac_string + ":"

    print(mac_string)

    if len(mac_string) == 17:
        #call WRITE FUNCTION AND QUIT
        rwMACAddress.writeMACAddress(mac_string)
        navigation.quitProgramAfterSettings()
        print('ok')
    else:
        # MAC address is not complete. Notify on-screen?
        print('MAC not complete')

def quit_no_save():
    navigation.quitProgramAfterSettings()
    #pass


def createMACSettingFrame(settingsContainer):

    MACSettingFrame = tk.Frame(settingsContainer, height=480, width=320)


    # Create label for the current MAC address
    current_mac = "MAC atual: "
    current_mac = current_mac + rwMACAddress.readMACAddress()
    #current_mac = current_mac + "AB:CD:EF:12:34:56"
    current_mac_label = tk.Label(MACSettingFrame, text=current_mac, font=("Arial", 12))
    current_mac_label.pack()


    # Create label for the title
    title_label = tk.Label(MACSettingFrame, text="Ajuste de endereço MAC", font=("Arial", 16))
    title_label.pack(pady=10)


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
    keyboard_frame.pack(pady=10)

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
            button = tk.Button(button_row, text=char, width=1, height=1, font=("Arial", 16),
                               command=lambda c=char: add_char(c))
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
                button = tk.Button(button_row, text=char, width=2, height=1, font=("Arial", 16),
                                   command=lambda c=char: add_char(c))
                button.pack(side=tk.LEFT, ipadx=2, ipady=2, padx=2, pady=1) # ERA 6

    # Create backspace button
    backspace_button = tk.Button(MACSettingFrame, text="Apagar dígito", font=("Arial", 14),
                                 command=backspace)
    backspace_button.pack(pady=2)

    # Create save and quit button
    saveandquit_button = tk.Button(MACSettingFrame, text="Salvar e sair", font=("Arial", 14), command=save_and_quit)
    saveandquit_button.pack(pady=2)

    # Create quit without saving button

    quit_no_save_button = tk.Button(MACSettingFrame, text="Sair sem salvar", font=("Arial", 14), command=quit_no_save)
    quit_no_save_button.pack(pady=2)



    return MACSettingFrame


##### TEMPORARY SCRIPT JUST TO TEST EXECUTION OF FRAME ######

# mainContainer = tk.Tk()
# mainContainer.title("teste")
#
# mainContainer.geometry('320x480')
# mainContainer.resizable(False, False)
# mainContainer.attributes('-fullscreen', False)
#
# helloFrame = createMACSettingFrame(mainContainer)
# helloFrame.pack(side="top", fill="both", expand=True)
#
# mainContainer.mainloop()

####### TEMPORARY SCRIPT ENDS. DELETE ASAP.
#################################################
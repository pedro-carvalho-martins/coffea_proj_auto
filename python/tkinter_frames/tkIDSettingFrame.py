import tkinter as tk

## TEMPORARY COMMENT TO TEST ON WINDOWS. UNCOMMENT ASAP
import navigation
import rwSystemID
## TEMPORARY COMMENT ENDS. UNCOMMENT ASAP.


# NENHUM TESTE FOI FEITO AINDA. TESTAR!



## Função de criação do Frame de configuração do ID do sistema

def add_char(char):

    if len(entry_system_ID.get()) < 10:
        entry_system_ID.insert(tk.END, char)


def backspace():

    if len(entry_system_ID.get()) > 0:
        entry_system_ID.delete(len(entry_system_ID.get()) - 1, tk.END)


def save_and_quit():

    system_id = entry_system_ID.get()

    print(system_id)

    if len(system_id) > 0:
        # Call WRITE FUNCTION AND QUIT
        rwSystemID.writeSystemID(system_id)
        navigation.quitProgramAfterSettings()
        print('ok')

def quit_no_save():
    navigation.quitProgramAfterSettings()
    #pass


def createIDSettingFrame(settingsContainer):

    IDSettingFrame = tk.Frame(settingsContainer, height=480, width=320)


    # Create label for the current MAC address
    current_ID = "ID de sistema atual: "
    current_ID = current_ID + rwSystemID.readSystemID()
    current_id_label = tk.Label(IDSettingFrame, text=current_ID, font=("Arial", 12))
    current_id_label.pack()


    # Create label for the title
    title_label = tk.Label(IDSettingFrame, text="Modificar identificador sistema", font=("Arial", 16))
    title_label.pack(pady=10)


    # Create entry widget for the system ID
    global entry_system_ID
    entry_system_ID = tk.Entry(IDSettingFrame, width=20, font=("Arial", 14))
    entry_system_ID.pack(pady=10)


    # Create frame for the on-screen keyboard
    keyboard_frame = tk.Frame(IDSettingFrame)
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
    backspace_button = tk.Button(IDSettingFrame, text="Apagar dígito", font=("Arial", 14),
                                 command=backspace)
    backspace_button.pack(pady=2)

    # Create save and quit button
    saveandquit_button = tk.Button(IDSettingFrame, text="Salvar e sair", font=("Arial", 14), command=save_and_quit)
    saveandquit_button.pack(pady=2)

    # Create quit without saving button

    quit_no_save_button = tk.Button(IDSettingFrame, text="Sair sem salvar", font=("Arial", 14), command=quit_no_save)
    quit_no_save_button.pack(pady=2)



    return IDSettingFrame


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
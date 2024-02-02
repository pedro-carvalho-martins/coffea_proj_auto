import tkinter as tk

import navigation


## Ação de clique em botão

def button_clicked(index_button, lista_tipos_config, settingSelectionFrame):
   print('Button clicked')
   print(lista_tipos_config[index_button])
   navigation.navigate_selected_setting_menu(lista_tipos_config[index_button], settingSelectionFrame)


## Função de criação do Frame de método de pagamento

def createSettingSelectionFrame(settingsContainer):


    lista_tipos_config = ["Preços", "Métodos pagamento", "Endereço MAC Moderninha", "Pareamento BT - Minimizar app", "Voltar"]


    settingSelectionFrame = tk.Frame(settingsContainer, height=480, width=320)


    ## Configurando o Grid

    settingSelectionFrame.rowconfigure(0, weight=3)
    settingSelectionFrame.rowconfigure(1, weight=6)
    settingSelectionFrame.rowconfigure(2, weight=1)
    settingSelectionFrame.columnconfigure(0, weight=1)


    ## Adiciono o label principal

    label = tk.Label(
       settingSelectionFrame,
       text="CONFIGURAÇÕES",
       font=('SegoeUI', 20),
       wraplength=250)
    label.grid(column=0, row=0, sticky=tk.S, pady=0, padx=20)


    ## Crio o Frame dos botões

    button_frame = tk.Frame(settingSelectionFrame)
    button_frame.grid(column=0, row=1, pady=10, padx=20)


    ## Adiciono os botões



    buttons_list=[]

    for button_index in range(len(lista_tipos_config)):
       buttons_list.append(
          tk.Button(button_frame,
                    text=lista_tipos_config[button_index],
                    #font=('SegoeUI', 20, 'bold'),
                    font=('Ubuntu', 20),
                    wraplength=250,
                    #command=button_clicked(button_index),
                    command= lambda idx=button_index: button_clicked(idx, lista_tipos_config, settingSelectionFrame))
                    #height=1,
                    #width=1)
       )

    for button_index in range(len(buttons_list)):
       buttons_list[button_index].grid(column=0, row=button_index+1, ipadx=10, ipady=10, pady=5, sticky=tk.EW)


    ## Crio o Frame inferior

    lower_frame = tk.Frame(settingSelectionFrame)
    lower_frame.grid(column=0, row=2, sticky=tk.NS, pady=1, padx=20)

    return settingSelectionFrame


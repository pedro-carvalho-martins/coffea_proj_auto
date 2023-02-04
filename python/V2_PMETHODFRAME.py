import tkinter as tk

import V2_NAVIGATION


## Ação de clique em botão

def button_clicked(index_button, lista_metodos_pag, price_selected, pmethodFrame):
   print('Button clicked')
   print(lista_metodos_pag[index_button])
   print(price_selected)
   V2_NAVIGATION.navigate_payment_process(price_selected, lista_metodos_pag[index_button], pmethodFrame)


## Função de criação do Frame de método de pagamento

def createPaymentMethodFrame(price_selected):


    lista_metodos_pag = ["Crédito", "Débito", "Voucher", "QR Code (Pix)"]


    pmethodFrame = tk.Frame(height=480, width=320)


    ## Configurando o Grid

    pmethodFrame.rowconfigure(0, weight=3)
    pmethodFrame.rowconfigure(1, weight=6)
    pmethodFrame.rowconfigure(2, weight=1)
    pmethodFrame.columnconfigure(0, weight=1)


    ## Adiciono o label principal

    label = tk.Label(
       pmethodFrame,
       text="Selecione a forma de pagamento:",
       font=('SegoeUI', 20),
       wraplength=250)
    label.grid(column=0, row=0, sticky=tk.S, pady=0, padx=20)


    ## Crio o Frame dos botões

    button_frame = tk.Frame(pmethodFrame)
    button_frame.grid(column=0, row=1, pady=10, padx=20)


    ## Adiciono os botões



    buttons_list=[]

    for button_index in range(len(lista_metodos_pag)):
       buttons_list.append(
          tk.Button(button_frame,
                    text=lista_metodos_pag[button_index],
                    #font=('SegoeUI', 20, 'bold'),
                    font=('Ubuntu', 20),
                    wraplength=150,
                    #command=button_clicked(button_index),
                    command= lambda idx=button_index: button_clicked(idx, lista_metodos_pag, price_selected, pmethodFrame))
                    #height=1,
                    #width=1)
       )

    for button_index in range(len(buttons_list)):
       buttons_list[button_index].grid(column=0, row=button_index+1, ipadx=70, ipady=10, pady=5, sticky=tk.EW)


    ## Crio o Frame inferior

    lower_frame = tk.Frame(pmethodFrame)
    lower_frame.grid(column=0, row=2, sticky=tk.NS, pady=1, padx=20)

    return pmethodFrame


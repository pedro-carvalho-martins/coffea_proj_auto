import tkinter as tk

import navigation


## Ação de clique em botão

def button_clicked(index_button):
   print('Button clicked')
   print(index_button)


## Função de criação do Frame de início

def createPayProcessFrame(mainContainer):


    payProcessFrame = tk.Frame(mainContainer, height=480, width=320)


    ## Configurando o Grid

    payProcessFrame.rowconfigure(0, weight=1)
    payProcessFrame.columnconfigure(0, weight=1)


    ## Adiciono o label

    label = tk.Label(
       payProcessFrame,
   text="Aproxime ou insira seu cartão na máquina abaixo\n\nPara cancelar, aperte no botão CANCELA na máquina abaixo",
       font=('SegoeUI', 20),
       wraplength=300)
    label.grid(column=0, row=0, ipadx=10, ipady=180)


    return payProcessFrame


def createPaySuccessFrame(mainContainer):

    payCompleteFrame = tk.Frame(mainContainer, height=480, width=320)

    payCompleteFrame.configure(bg='#138713')

    ## Configurando o Grid

    payCompleteFrame.rowconfigure(0, weight=1)
    payCompleteFrame.columnconfigure(0, weight=1)


    ## Adiciono o label

    label = tk.Label(
       payCompleteFrame,
       text="Pagamento concluído. Favor escolher a sua bebida.",
       font=('SegoeUI', 20),
       fg='white',
       bg='#138713',
       wraplength=300)
    label.grid(column=0, row=0, ipadx=10, ipady=180)

    return payCompleteFrame



def createPayFailureFrame(mainContainer):

    payFailureFrame = tk.Frame(mainContainer, height=480, width=320)
    payFailureFrame.configure(bg='#871313')

    ## Configurando o Grid

    payFailureFrame.rowconfigure(0, weight=1)
    payFailureFrame.columnconfigure(0, weight=1)


    ## Adiciono o label

    label = tk.Label(
       payFailureFrame,
       text="Erro no pagamento. Favor recomeçar a compra.",
       font=('SegoeUI', 20),
       fg='white',
       bg='#871313',
       wraplength=300)
    label.grid(column=0, row=0, ipadx=10, ipady=180)

    return payFailureFrame

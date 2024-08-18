import os
import tkinter as tk

# temporary to test image implementation (but conncheck does not use it! why should we have it here?)
from PIL import Image, ImageTk

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


    ## Adiciono os labels

    label0 = tk.Label(
        payProcessFrame,
        text="\n ",
        font=('SegoeUI', 20),
        wraplength=300)
    label0.grid(column=0, row=1, ipadx=10, ipady=10)

    label1 = tk.Label(
        payProcessFrame,
        text="Aproxime ou insira seu cartão na máquina abaixo",
        font=('SegoeUI', 20),
        wraplength=300)
    label1.grid(column=0, row=3, ipadx=10, ipady=100)

    # label0.grid(column=0, row=4, ipadx=10, ipady=50)

    label3 = tk.Label(
        payProcessFrame,
        text="Para cancelar, aperte no botão CANCELA na máquina abaixo",
        font=('SegoeUI', 14),
        wraplength=300)
    label3.grid(column=0, row=6, ipadx=0, ipady=25)

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
       text="Pagamento concluído. Favor escolher o seu produto.",
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




def createPayProcessFrame_Pix(mainContainer):


    payProcessFrame = tk.Frame(mainContainer, height=480, width=320)


    ## Configurando o Grid

    payProcessFrame.rowconfigure(0, weight=1)
    payProcessFrame.columnconfigure(0, weight=1)


    ## Adiciono os labels

    label0 = tk.Label(
        payProcessFrame,
        text="\n ",
        font=('SegoeUI', 20),
        wraplength=300)
    label0.grid(column=0, row=1, ipadx=10, ipady=10)

    label1 = tk.Label(
        payProcessFrame,
        text="Inicializando pagamento por Pix",
        font=('SegoeUI', 20),
        wraplength=300)
    label1.grid(column=0, row=3, ipadx=10, ipady=100)

    # label0.grid(column=0, row=4, ipadx=10, ipady=50)

    label3 = tk.Label(
        payProcessFrame,
        text="Aguarde geração do QR Code",
        font=('SegoeUI', 14),
        wraplength=300)
    label3.grid(column=0, row=6, ipadx=0, ipady=25)

    return payProcessFrame


def createPixDisplayFrame(mainContainer, price_selected, filename_img_QR_Code_Pix):

    pixDisplayFrame = tk.Frame(mainContainer, height=480, width=320)


    ## Configurando o Grid

    pixDisplayFrame.rowconfigure(0, weight=1)
    pixDisplayFrame.rowconfigure(1, weight=1)
    pixDisplayFrame.rowconfigure(2, weight=1)
    pixDisplayFrame.columnconfigure(0, weight=1)


    ## Adiciono os labels

    preco_selecionado_str = ("R$ {:.2f}".format(price_selected)).replace(".", ",")

    label0 = tk.Label(
        pixDisplayFrame,
        text="Valor do Pix: "+preco_selecionado_str +"\n"+
             "Escaneie o QR Code abaixo no aplicativo do seu banco",#. ADICIONAR BOTAO DE CANCELAMENTO DE COMPRA E TIMER PARA TIMEOUT APARECER APÓS UM TEMPO",
        font=('SegoeUI', 14),
        wraplength=250)
    label0.grid(column=0, row=0, ipadx=5, ipady=5)



    try:
        img_QR_Code = Image.open(filename_img_QR_Code_Pix)
        img_QR_Code = img_QR_Code.resize((300, 300), Image.ANTIALIAS)
        img_QR_Code = ImageTk.PhotoImage(img_QR_Code)

        imgLabel = tk.Label(pixDisplayFrame, image=img_QR_Code)
        imgLabel.image = img_QR_Code

        #img_QR_Code = tk.PhotoImage(file=filename_img_QR_Code_Pix)
        #imgLabel.configure(image=img_QR_Code)

        imgLabel.grid(row=1, column=0, ipadx=10, ipady=10)

    ### RETRY THIS CODE WITHOUT USING PIL?
    #HYPOTHESIS: THE PICTURE WAS JUST TOO BIG TO DISPLAY DIRECTLY ON TKINTER

    except Exception as e:
        print("error:",e)

    cancelar_compra_button = tk.Button(pixDisplayFrame,
           text="Cancelar",
           # font=('SegoeUI', 20, 'bold'),
           font=('Ubuntu', 14),
           wraplength=150,
           bg='#871313',
           fg='white',
           # command=button_clicked(button_index),
           command=mainContainer.destroy,

           # change behaviour on hover
           activebackground=pixDisplayFrame.cget(
               "background")
           # Set the active background color to the regular background color
           )

    cancelar_compra_button.grid(column=0, row=2, ipadx=5, ipady=5)



    return pixDisplayFrame
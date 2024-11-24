import tkinter as tk

import tkinter_frames.tkPaymentProcessFrame as tkPaymentProcessFrame
import tkinter_frames.tkPMethodFrame as tkPMethodFrame
import tkinter_frames.tkPriceFrame as tkPriceFrame
import tkinter_frames.tkHelloFrame as tkHelloFrame
import tkinter_frames.tkPriceSettingFrame as tkPriceSettingFrame
import tkinter_frames.tkPMethodSettingFrame as tkPMethodSettingFrame
import tkinter_frames.tkMACSettingFrame as tkMACSettingFrame
import tkinter_frames.tkIDSettingFrame as tkIDSettingFrame
import tkinter_frames.tkSettingsMainFrame as tkSettingsMainFrame
import tkinter_frames.tkInhibitFrame as tkInhibitFrame
import tkinter_frames.tkConnCheckFrame as tkConnCheckFrame
import tkinter_frames.tkHelloSettingFrame as tkHelloSettingFrame
import tkinter_frames.tkPulseValueSettingFrame as tkPulseValueSettingFrame

import queue
import time

import threading
from threading import Thread

import paymentProcessing
import paymentProcessing_Pix

## Comment block for Windows testing
import sendSignalGPIO
import signalListenerGPIO
## End of comment block for Windows testing

import connCheckProcess
import kill_shell_loop

import logTransmissionProcess

import rwUltimoPag
import rwHelloSettingFile
import rwLogCSV


## 2024.08.29 New implementation to handle GUI updates in a thread-safe manner

def hide_and_destroy_frame(currentFrame):
    currentFrame.pack_forget()
    currentFrame.destroy()

def pack_new_frame(newFrame):
    newFrame.pack(side="top", fill="both", expand=True)

# Global queue for UI updates
ui_update_queue = queue.Queue()

def enqueue_ui_update(function, *args):
    ui_update_queue.put((function, args))

def process_ui_queue():
    while not ui_update_queue.empty():
        function, args = ui_update_queue.get()
        function(*args)
    mainContainer.after(100, process_ui_queue)

def enqueue_hide_and_destroy_frame(currentFrame):
    enqueue_ui_update(hide_and_destroy_frame, currentFrame)

def enqueue_pack_new_frame(newFrame):
    enqueue_ui_update(pack_new_frame, newFrame)

def enqueue_launchPixRequest(payprocessFrame, price_selected, payment_method_selected):
    enqueue_ui_update(launchPixRequest, payprocessFrame, price_selected, payment_method_selected)

## 2024.08.29 New implementation ends



def navigate_startupFrame(session_number):
    global mainContainer

    # If value of disableInterrupt is 1, the program cannot be interrupted by an inhibit or settings button press
    global disableInterrupt
    disableInterrupt = 0

    global disableBgConnCheck
    disableBgConnCheck = 0

    mainContainer = tk.Tk()
    mainContainer.title("sistema_pagamento_plugpag")

    mainContainer.geometry('320x480')
    # COMMENTED ONLY FOR TESTING. UNCOMMENT LATER!
    mainContainer.resizable(False, False)

    ## Comment block for Windows testing
    mainContainer.attributes('-fullscreen', True)
    # mainContainer.attributes('-fullscreen', False)
    ## End of block for Windows testing

    ### FRAME MODIFICATION CODE BETWEEN THESE COMMENTS

    helloFrame = tkHelloFrame.createHelloFrame(mainContainer)

    #helloFrame.pack(side="top", fill="both", expand=True)

    enqueue_pack_new_frame(helloFrame)

    ### FRAME MODIFICATION CODE BETWEEN THESE COMMENTS

    # Listen GPIO input ports for INHIBIT or SETTINGS signals
    if session_number == 1:
        threadListener = Thread(target=signalListener, args=(0, 0))
        threadListener.daemon = True  # Dies when main thread exits.
        threadListener.start()

    ## DEV: navigate to connection check frame
    navigate_connCheckFrame(helloFrame)

    # Start the process to check the UI update queue
    mainContainer.after(100, process_ui_queue)

    mainContainer.mainloop()


def navigate_connCheckFrame(currentFrame):
    print('navConnCheck')

    ### FRAME MODIFICATION CODE BETWEEN THESE COMMENTS

    #currentFrame.pack_forget()
    #currentFrame.destroy()

    enqueue_hide_and_destroy_frame(currentFrame)

    connCheckFrame = tkConnCheckFrame.createNewConnCheckFrame(mainContainer)

    #connCheckFrame.pack(side="top", fill="both", expand=True)

    enqueue_pack_new_frame(connCheckFrame)

    ### FRAME MODIFICATION CODE BETWEEN THESE COMMENTS

    print('launch connection check function')

    print("NUMBER OF ACTIVE THREADS")
    print(threading.active_count())
    print("ENDS PRINT ACTIVE THREADS")

    ## launch other thread
    threadConnCheck = Thread(target=launchConnCheck, args=(connCheckFrame, 0))
    threadConnCheck.daemon = True
    threadConnCheck.start()


def launchConnCheck(connCheckFrame, dummyVariable):
    print('starting conn check process')
    # time.sleep(3) ##################### TEMPORARY JUST TO TEST CONCEPT

    conn_check_output_code = connCheckProcess.launchStartupConnCheckProcess()

    if conn_check_output_code == 0:  # Sucesso no teste de conexão: mostra checks por 3s e segue a execução do programa
        time.sleep(3)

        ### FRAME MODIFICATION CODE BETWEEN THESE COMMENTS

        #connCheckFrame.pack_forget()
        #connCheckFrame.destroy()

        enqueue_hide_and_destroy_frame(connCheckFrame)

        check_helloScreen(connCheckFrame)

        ### FRAME MODIFICATION CODE BETWEEN THESE COMMENTS


    # Feature de exibição dos botões "Reconectar" e "Continuar" no Frame de ConnCheck.
    # Código comentado - feature abandonada para facilitar a experiência do usuário.
    # No lugar de mostrar os botões, mostra o resultado dos testes com um sleep e segue adiante
    # else: # Falha completa ou parcial no teste de conexão: mostra falhas e botões de reconectar ou continuar
    #    while True:
    #       if tkConnCheckFrame.flag_reconectar == "sim":
    #          tkConnCheckFrame.flag_reconectar = "none"
    #          connCheckFrame.pack_forget()
    #          connCheckFrame.destroy()
    #          navigate_connCheckFrame(connCheckFrame)
    #          break
    #       if tkConnCheckFrame.flag_continuar == "sim":
    #          tkConnCheckFrame.flag_continuar = "none"
    #          connCheckFrame.pack_forget()
    #          connCheckFrame.destroy()
    #          check_helloScreen(connCheckFrame)

    elif conn_check_output_code == 1:  # Falha parcial de conexão - segue normalmente mas indica resultado na tela
        time.sleep(3)

        ### FRAME MODIFICATION CODE BETWEEN THESE COMMENTS

        #connCheckFrame.pack_forget()
        #connCheckFrame.destroy()

        enqueue_hide_and_destroy_frame(connCheckFrame)

        check_helloScreen(connCheckFrame)

        ### FRAME MODIFICATION CODE BETWEEN THESE COMMENTS


    else:  # Falha completa de conexão - Faz o teste novamente.
        time.sleep(10)

        ### FRAME MODIFICATION CODE BETWEEN THESE COMMENTS

        #connCheckFrame.pack_forget()
        #connCheckFrame.destroy()

        enqueue_hide_and_destroy_frame(connCheckFrame)

        navigate_connCheckFrame(connCheckFrame)

        ### FRAME MODIFICATION CODE BETWEEN THESE COMMENTS


def check_helloScreen(currentFrame):
    # Lanço verificação periódica de conexão
    #threadBackgroundConnCheck = Thread(target=connCheckProcess.launchBackgroundConnCheckProcess, args=(0, 0))
    threadBackgroundConnCheck = Thread(target=loopConnCheckBackground, args=(0, 0))
    threadBackgroundConnCheck.daemon = True
    threadBackgroundConnCheck.start()

    # Lanço envio de logs ao servidor
    threadLogTransmission = Thread(target=logTransmissionProcess.startLogTransmission, args=(0, 0))
    threadLogTransmission.daemon = True
    threadLogTransmission.start()

    # helloScreenOn=1
    # Verifica se a tela de "toque aqui para iniciar" está habilitada ou não
    helloScreenOn = rwHelloSettingFile.readListCheckHello()

    if helloScreenOn == 1:
        navigate_helloFrame(currentFrame)
    else:
        navigate_priceFrame(currentFrame)


def navigate_helloFrame(currentFrame):
    ### FRAME MODIFICATION CODE BETWEEN THESE COMMENTS

    currentFrame.pack_forget()
    currentFrame.destroy()

    helloFrame = tkHelloFrame.createHelloFrame(mainContainer)
    helloFrame.pack(side="top", fill="both", expand=True)

    ### FRAME MODIFICATION CODE BETWEEN THESE COMMENTS


def navigate_priceFrame(currentFrame):
    print('navPrice')

    ### FRAME MODIFICATION CODE BETWEEN THESE COMMENTS

    #currentFrame.pack_forget()
    #currentFrame.destroy()

    enqueue_hide_and_destroy_frame(currentFrame)

    priceFrame = tkPriceFrame.createPriceFrame(mainContainer)

    #priceFrame.pack(side="top", fill="both", expand=True)

    enqueue_pack_new_frame(priceFrame)

    ### FRAME MODIFICATION CODE BETWEEN THESE COMMENTS


def navigate_payment_method_Frame(price_selected, currentFrame):

    global disableBgConnCheck
    disableBgConnCheck = 1

    print('navpMethod')
    print('price selected was:' + str(price_selected))

    ### FRAME MODIFICATION CODE BETWEEN THESE COMMENTS

    #currentFrame.pack_forget()
    #currentFrame.destroy()

    enqueue_hide_and_destroy_frame(currentFrame)

    ##### TESTE: pausa de 1 segundo entre telas:
    time.sleep(0.5)
    ##### FIM DO TESTE

    pmethodFrame = tkPMethodFrame.createPaymentMethodFrame(mainContainer, price_selected)

    #pmethodFrame.pack(side="top", fill="both", expand=True)

    enqueue_pack_new_frame(pmethodFrame)

    ### FRAME MODIFICATION CODE BETWEEN THESE COMMENTS


def navigate_payment_process(price_selected, payment_method_selected, currentFrame):
    print('navPayProcess')
    print(price_selected)
    print(payment_method_selected)

    ### FRAME MODIFICATION CODE BETWEEN THESE COMMENTS

    #currentFrame.pack_forget()
    #currentFrame.destroy()

    enqueue_hide_and_destroy_frame(currentFrame)

    ### FRAME MODIFICATION CODE BETWEEN THESE COMMENTS

    if payment_method_selected == "QR Code (Pix)":

        print('payment_method_selected == "QR Code (Pix)"')

        ### FRAME MODIFICATION CODE BETWEEN THESE COMMENTS

        payprocessFrame = tkPaymentProcessFrame.createPayProcessFrame_Pix(mainContainer)

        print('payprocessFrame created')

        #payprocessFrame.pack(side="top", fill="both", expand=True)

        enqueue_pack_new_frame(payprocessFrame)

        ### FRAME MODIFICATION CODE BETWEEN THESE COMMENTS

        print('launch payment processing function')

        ## launch other thread
        #threadPixRequest = Thread(target=launchPixRequest,
        #                          args=(payprocessFrame, price_selected, payment_method_selected))
        #threadPixRequest.start()
        # thread.join()

        enqueue_launchPixRequest(payprocessFrame, price_selected, payment_method_selected)


    # Se o pagamento for através da moderninha, por cartão:

    else:

        ### FRAME MODIFICATION CODE BETWEEN THESE COMMENTS

        payprocessFrame = tkPaymentProcessFrame.createPayProcessFrame(mainContainer)

        #payprocessFrame.pack(side="top", fill="both", expand=True)

        enqueue_pack_new_frame(payprocessFrame)

        ### FRAME MODIFICATION CODE BETWEEN THESE COMMENTS

        print('launch payment processing function')

        print("NUMBER OF ACTIVE THREADS")
        print(threading.active_count())
        print("ENDS PRINT ACTIVE THREADS")

        # Verifico se o preço selecionado corresponde ao valor da última compra realizada. Se sim, desconto um centavo.

        valorUltimaCompra = rwUltimoPag.readValue()
        # Se os valores forem iguais e o valor da ultima compra não for quebrado
        if (valorUltimaCompra % .25 < 0.001) and (price_selected - valorUltimaCompra < 0.001):
            price_selected = price_selected - 0.01
        #

        ## launch other thread
        # Último argumento é zero para pagamento pela maquininha; se aplica apenas para o pagamento por Pix
        threadPay = Thread(target=launchPayment, args=(payprocessFrame, price_selected, payment_method_selected, 0))
        threadPay.start()
        # thread.join()


def launchPixRequest(payprocessFrame, price_selected, payment_method_selected):
    # function must:
    #  - get auth token
    #  - get QR Code text from server
    #  - convert QR Code text to image
    #  - display image on screen
    #  - call thread to verify payment (launchPayment function)

    print('start pix request')

    try:
        pix_copiaecola, pix_txid = paymentProcessing_Pix.PixRequest(price_selected)

        directory_filename_qrcode_pix_img = paymentProcessing_Pix.generate_img_QR_Code_Pix(pix_copiaecola)

        ### FRAME MODIFICATION CODE BETWEEN THESE COMMENTS

        #payprocessFrame.pack_forget()
        #payprocessFrame.destroy()

        enqueue_hide_and_destroy_frame(payprocessFrame)

        pixDisplayFrame = tkPaymentProcessFrame.createPixDisplayFrame(mainContainer, price_selected,
                                                                      directory_filename_qrcode_pix_img)
        #pixDisplayFrame.pack(side="top", fill="both", expand=True)

        enqueue_pack_new_frame(pixDisplayFrame)

        ### FRAME MODIFICATION CODE BETWEEN THESE COMMENTS

        ## launch new thread
        # Último argumento é zero para pagamento pela maquininha; se aplica apenas para o pagamento por Pix
        threadPay = Thread(target=launchPayment,
                           args=(pixDisplayFrame, price_selected, payment_method_selected, pix_txid), daemon=True)
        threadPay.start()

    except Exception as e:

        rwLogCSV.writeCSV("venda_erro", str(price_selected), payment_method_selected, "launchPixRequest",
                          str(e.__class__), str(e))

        ### FRAME MODIFICATION CODE BETWEEN THESE COMMENTS

        #payprocessFrame.pack_forget()
        #payprocessFrame.destroy()

        enqueue_hide_and_destroy_frame(payprocessFrame)

        paycompleteFrame = tkPaymentProcessFrame.createPayFailureFrame(mainContainer)

        #paycompleteFrame.pack(side="top", fill="both", expand=True)

        enqueue_pack_new_frame(paycompleteFrame)

        ### FRAME MODIFICATION CODE BETWEEN THESE COMMENTS

        time_buffer = 5000

        paycompleteFrame.after(time_buffer, lambda: mainContainer.destroy())


def launchPayment(payprocessFrame, price_selected, payment_method_selected, pix_txid):
    print('starting process')

    global disableInterrupt
    disableInterrupt = 1

    try:
        # pay_output_code == 0 => Success ; else: Failure

        if payment_method_selected == "QR Code (Pix)":

            # Verifica status do pagamento
            pay_output_code = paymentProcessing_Pix.verify_payment_pix(pix_txid)

            # launch payment processing pix -> return qr code text
            # pass qr code text to tk function -> display QR Code on screen
            # launch a thread to check for payment completion ((maybe start THIS on this function for Pix, and have a previous func to return qr code and call the tk to display it
            # this func to check for payment completion should last max 3 minutes? then expire. if anything fails or timeout, pay_output_code!=1; if all is good, pay_output_code = 1
            # integrate code from comm_inter_teste_pycharm_project from the folder \Integração API Inter\comm_inter_teste...

            # temporary test
            # pay_output_code = paymentProcessing_Pix.launchPaymentProcessing_Pix_TEST_DONOTCALL(price_selected, payprocessFrame)

            # Chamar função para conexão com API do Inter e gerar QR Code (enquanto isso, tela de loading que já está carregada (mas botar um loading com imagem!!)
            # Assim que gerar o QR Code, passar para a tela que mostra o QR Code e aguardar o pagamento
            # Assim que o pagamento for confirmado, dar pay_output_code = 0




        else:
            pay_output_code = paymentProcessing.launchPaymentProcessing(price_selected, payment_method_selected)

        ### FRAME MODIFICATION CODE BETWEEN THESE COMMENTS

        #payprocessFrame.pack_forget()
        #payprocessFrame.destroy()

        enqueue_hide_and_destroy_frame(payprocessFrame)

        ### FRAME MODIFICATION CODE BETWEEN THESE COMMENTS

        if pay_output_code == 0:

            ### FRAME MODIFICATION CODE BETWEEN THESE COMMENTS

            paycompleteFrame = tkPaymentProcessFrame.createPaySuccessFrame(mainContainer)

            ### FRAME MODIFICATION CODE BETWEEN THESE COMMENTS

            rwUltimoPag.writeValue(price_selected)

            rwLogCSV.writeCSV("venda_sucesso", str(price_selected), payment_method_selected, "", "", "")

            threadSignal = Thread(target=launchSendSignal, args=(price_selected, 0))
            threadSignal.start()
        else:

            ### FRAME MODIFICATION CODE BETWEEN THESE COMMENTS
            paycompleteFrame = tkPaymentProcessFrame.createPayFailureFrame(mainContainer)
            ### FRAME MODIFICATION CODE BETWEEN THESE COMMENTS


    except Exception as e:

        rwLogCSV.writeCSV("venda_erro", str(price_selected), payment_method_selected, "launchPayment", str(e.__class__),
                          str(e))

        ### FRAME MODIFICATION CODE BETWEEN THESE COMMENTS

        #payprocessFrame.pack_forget()
        #payprocessFrame.destroy()

        enqueue_hide_and_destroy_frame(payprocessFrame)

        paycompleteFrame = tkPaymentProcessFrame.createPayFailureFrame(mainContainer)

        ### FRAME MODIFICATION CODE BETWEEN THESE COMMENTS

    ### FRAME MODIFICATION CODE BETWEEN THESE COMMENTS

    #paycompleteFrame.pack(side="top", fill="both", expand=True)

    enqueue_pack_new_frame(paycompleteFrame)

    ### FRAME MODIFICATION CODE BETWEEN THESE COMMENTS

    print('paymentCompleteOK')
    print('process ends')

    ## TEST
    # paycompleteFrame.after(5000, print('ok'))#nav_restart(paycompleteFrame) )
    # paycompleteFrame.after(5000, paycompleteFrame.destroy() )

    time_buffer = 5000
    try:
        if pay_output_code == 0:  # If payment is successful, display successful payment screen for 20s
            time_buffer = 20000
    except:
        pass

    paycompleteFrame.after(time_buffer, lambda: mainContainer.destroy())

    ## TEST ENDS
    print('debug1')



def loopConnCheckBackground(dummyVar1, dummyVar2):

    global disableBgConnCheck

    while True:

        time.sleep(300)
        if disableBgConnCheck == 0:
            connCheckProcess.launchBackgroundConnCheckProcess(0,0)


# Will be able to detect if settings button is pressed or if the inhibit signal is on
def signalListener(dummyVar1, dummyVar2):
    global disableInterrupt

    while True:

        ## Comment block for Windows testing
        listener_outcome = signalListenerGPIO.listenGPIO()
        ## End of comment block for Windows testing

        ## Additional code block for Windows testing
        # listener_outcome = "no"
        # disableInterrupt = 1
        time.sleep(
            2)  # Run loop every two seconds. This might be interesting for the production version (otherwise this is continuously in a loop without a time break)
        ## End of additional code block for Windows testing

        if disableInterrupt == 0:

            if listener_outcome == "settings":
                print('navigate to settings main frame')
                navigate_SettingsMainFrame()
                break

            elif listener_outcome == "inhibit":
                print('launch inhibit')
                navigate_InhibitFrame()
                break

            else:
                print('not defined')


# def navigate_SettingsMainFrame(currentFrame):
def navigate_SettingsMainFrame():
    print('navSettingsMenu')

    global settingsContainer

    settingsContainer = tk.Toplevel()
    settingsContainer.title("settings_container")

    settingsContainer.geometry('320x480')

    # commented for testing
    settingsContainer.resizable(False, False)
    settingsContainer.attributes('-fullscreen', True)

    # currentFrame.pack_forget()
    # currentFrame.destroy()
    settingsFrame = tkSettingsMainFrame.createSettingSelectionFrame(settingsContainer)
    # priceFrame.configure(background='black')
    settingsFrame.pack(side="top", fill="both", expand=True)


#########################################################################

def navigate_selected_setting_menu(settingPageSelection, currentFrame):
    print('nav_selected_setting_menu')
    print(settingPageSelection)
    currentFrame.pack_forget()
    currentFrame.destroy()

    if settingPageSelection == "Preços":
        priceSettingFrame = tkPriceSettingFrame.createPriceSettingFrame(settingsContainer)
        priceSettingFrame.pack(side="top", fill="both", expand=True)

    elif settingPageSelection == "Métodos pagamento":
        pMethodSettingFrame = tkPMethodSettingFrame.createPMethodSettingFrame(settingsContainer)
        pMethodSettingFrame.pack(side="top", fill="both", expand=True)

    elif settingPageSelection == "Identificador sistema":
        IDSettingFrame = tkIDSettingFrame.createIDSettingFrame(settingsContainer)
        IDSettingFrame.pack(side="top", fill="both", expand=True)

    elif settingPageSelection == "Endereço MAC Moderninha":
        MACSettingFrame = tkMACSettingFrame.createMACSettingFrame(settingsContainer)
        MACSettingFrame.pack(side="top", fill="both", expand=True)

    elif settingPageSelection == "Config. valor pulso":
        PulseValueSettingFrame = tkPulseValueSettingFrame.createPulseValueSettingFrame(settingsContainer)
        PulseValueSettingFrame.pack(side="top", fill="both", expand=True)

    elif settingPageSelection == "Config. de rede - Encerrar app":
        kill_shell_loop.kill_pid_executar()
        kill_shell_loop.kill_python()
        mainContainer.destroy()
        settingsContainer.destroy()
        # settingsContainer.geometry('3x4')
        # settingsContainer.resizable(False, False)
        # settingsContainer.attributes('-fullscreen', False)
        #
        # mainContainer.geometry('3x4')
        # mainContainer.resizable(False, False)
        # mainContainer.attributes('-fullscreen', False)
    # new dev ends

    elif settingPageSelection == "Config. tela inicial":
        HelloSettingFrame = tkHelloSettingFrame.createHelloSettingFrame(settingsContainer)
        HelloSettingFrame.pack(side="top", fill="both", expand=True)

    else:
        ## Ver se isso é suficiente para voltar ao início - TESTE PENDENTE
        mainContainer.destroy()
        settingsContainer.destroy()


def navigate_InhibitFrame():
    global inhibitContainer

    logTransmissionProcess.sendInhibitAlert()

    inhibitContainer = tk.Toplevel()
    inhibitContainer.title("inhibit_container")

    inhibitContainer.geometry('320x480')

    inhibitContainer.resizable(False, False)
    inhibitContainer.attributes('-fullscreen', True)

    inhibitFrame = tkInhibitFrame.createInhibitFrame(inhibitContainer)
    inhibitFrame.pack(side="top", fill="both", expand=True)

    threadInhibitEndListener = Thread(target=inhibitEndListener, args=(0, 0))
    threadInhibitEndListener.daemon = True  # Dies when main thread exits.
    threadInhibitEndListener.start()


def inhibitEndListener(dummyVar1, dummyVar2):
    inhibit_end_listener_outcome = signalListenerGPIO.inhibitEndListenGPIO()

    mainContainer.destroy()
    settingsContainer.destroy()


def launchSendSignal(price, dummyVar):
    try:
        sendSignalGPIO.sendOutputSignal(price)
    except Exception as e:
        rwLogCSV.writeCSV("erro_outros", str(price), "Undefined", "launchSendSignal_sendSignalGPIO", str(e.__class__),
                          str(e))


def quitProgramAfterSettings():
    mainContainer.destroy()
    settingsContainer.destroy()

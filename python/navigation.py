import tkinter as tk

import tkinter_frames.tkPaymentProcessFrame as tkPaymentProcessFrame
import tkinter_frames.tkPMethodFrame as tkPMethodFrame
import tkinter_frames.tkPriceFrame as tkPriceFrame
import tkinter_frames.tkHelloFrame as tkHelloFrame
import tkinter_frames.tkPriceSettingFrame as tkPriceSettingFrame
import tkinter_frames.tkPMethodSettingFrame as tkPMethodSettingFrame
import tkinter_frames.tkMACSettingFrame as tkMACSettingFrame
import tkinter_frames.tkSettingsMainFrame as tkSettingsMainFrame
import tkinter_frames.tkInhibitFrame as tkInhibitFrame
import tkinter_frames.tkConnCheckFrame as tkConnCheckFrame
import tkinter_frames.tkHelloSettingFrame as tkHelloSettingFrame


##tmp
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

import rwUltimoPag
import rwHelloSettingFile


##


def navigation(frame):
   frame.pack_forget()  # from
   # PACK to
   
   
def navigate_startupFrame(session_number):

   global mainContainer

   # If value of disableInterrupt is 1, the program cannot be interrupted by an inhibit or settings button press
   global disableInterrupt
   disableInterrupt = 0

   mainContainer = tk.Tk()
   mainContainer.title("sistema_pagamento_plugpag")

   mainContainer.geometry('320x480')
   # COMMENTED ONLY FOR TESTING. UNCOMMENT LATER!
   mainContainer.resizable(False, False)

   ## Comment block for Windows testing
   mainContainer.attributes('-fullscreen', True)
   #mainContainer.attributes('-fullscreen', False)
   ## End of block for Windows testing
    
   helloFrame = tkHelloFrame.createHelloFrame(mainContainer)
   helloFrame.pack(side="top", fill="both", expand=True)


   ############# WARNING! ###############
   # The SESSION NUMBER IMPLEMENTATION might work for SETTINGS, but
   #MIGHT NOT FOR INHIBIT! PAY ATTENTION TO THIS AND THINK OF ANOTHER
   #IMPLEMENTATION!
   ######################################

   # Listen GPIO input ports for INHIBIT or SETTINGS signals
   if session_number == 1:
      threadListener = Thread(target=signalListener, args=(0, 0))
      threadListener.daemon = True # Dies when main thread exits.
      threadListener.start()



   ### temporary modification to skip helloFrame (working as of 2023.05.06. Commented to implement connection check to BT)
   #navigate_priceFrame(helloFrame)

   ## DEV: navigate to connection check frame
   navigate_connCheckFrame(helloFrame)

   
   mainContainer.mainloop()
   
##   
##def nav_restart(currentFrame):
##   currentFrame.pack_forget()
##   currentFrame.destroy()
##   navigate_helloFrame()
   

def navigate_connCheckFrame(currentFrame):


   print('navConnCheck')
   currentFrame.pack_forget()
   currentFrame.destroy()
   connCheckFrame = tkConnCheckFrame.createNewConnCheckFrame(mainContainer)
   #priceFrame.configure(background='black')
   connCheckFrame.pack(side="top", fill="both", expand=True)

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

   #conn_check_output_code = connCheckProcess.launchConnCheckProcess()
   conn_check_output_code = connCheckProcess.launchStartupConnCheckProcess()
   # pay_output_code == 0 => Success ; else: Failure

   ## connection check completion
   # connCheckFrame.pack_forget()
   # connCheckFrame.destroy()
   #
   if conn_check_output_code == 0: # Sucesso no teste de conexão: mostra checks por 3s e segue a execução do programa
      time.sleep(3)
      connCheckFrame.pack_forget()
      connCheckFrame.destroy()
      check_helloScreen(connCheckFrame)

   else: # Falha completa ou parcial no teste de conexão: mostra falhas e botões de reconectar ou continuar
      while True:
         if tkConnCheckFrame.flag_reconectar == "sim":
            tkConnCheckFrame.flag_reconectar = "none"
            connCheckFrame.pack_forget()
            connCheckFrame.destroy()
            navigate_connCheckFrame(connCheckFrame)
            break
         if tkConnCheckFrame.flag_continuar == "sim":
            tkConnCheckFrame.flag_continuar = "none"
            connCheckFrame.pack_forget()
            connCheckFrame.destroy()
            check_helloScreen(connCheckFrame)



def check_helloScreen(currentFrame):

   # Lanço verificação periódica de conexão
   threadBackgoundConnCheck = Thread(target=connCheckProcess.launchBackgroundConnCheckProcess, args=(0, 0))
   threadBackgoundConnCheck.daemon = True
   threadBackgoundConnCheck.start()

   #helloScreenOn=1
   # Verifica se a tela de "toque aqui para iniciar" está habilitada ou não
   helloScreenOn = rwHelloSettingFile.readListCheckHello()

   if helloScreenOn == 1:
      navigate_helloFrame(currentFrame)
   else:
      navigate_priceFrame(currentFrame)


def navigate_helloFrame(currentFrame):

   currentFrame.pack_forget()
   currentFrame.destroy()

   helloFrame = tkHelloFrame.createHelloFrame(mainContainer)
   helloFrame.pack(side="top", fill="both", expand=True)




def navigate_priceFrame(currentFrame):
   print('navPrice')
   currentFrame.pack_forget()
   currentFrame.destroy()
   priceFrame = tkPriceFrame.createPriceFrame(mainContainer)
   #priceFrame.configure(background='black')
   priceFrame.pack(side="top", fill="both", expand=True)

def navigate_payment_method_Frame(price_selected, currentFrame):
   print('navpMethod')
   print('price selected was:'+str(price_selected))
   currentFrame.pack_forget()
   currentFrame.destroy()

   ##### TESTE: pausa de 1 segundo entre telas:
   time.sleep(0.5)
   ##### FIM DO TESTE

   pmethodFrame = tkPMethodFrame.createPaymentMethodFrame(mainContainer, price_selected)
   pmethodFrame.pack(side="top", fill="both", expand=True)

def navigate_payment_process(price_selected, payment_method_selected, currentFrame):
   print('navPayProcess')
   print(price_selected)
   print(payment_method_selected)
   currentFrame.pack_forget()
   currentFrame.destroy()

   if payment_method_selected == "QR Code (Pix)":
      payprocessFrame = tkPaymentProcessFrame.createPayProcessFrame_Pix(mainContainer)
      payprocessFrame.pack(side="top", fill="both", expand=True)
      print('launch payment processing function')

      ## launch other thread
      threadPixRequest = Thread(target=launchPixRequest, args=(payprocessFrame, price_selected, payment_method_selected))
      threadPixRequest.start()
      # thread.join()


   # Se o pagamento for através da moderninha, por cartão:

   else:


      payprocessFrame = tkPaymentProcessFrame.createPayProcessFrame(mainContainer)
      payprocessFrame.pack(side="top", fill="both", expand=True)
      print('launch payment processing function')


      print("NUMBER OF ACTIVE THREADS")
      print(threading.active_count())
      print("ENDS PRINT ACTIVE THREADS")

      # Verifico se o preço selecionado corresponde ao valor da última compra realizada. Se sim, desconto um centavo.

      valorUltimaCompra = rwUltimoPag.readValue()
      # Se os valores forem iguais e o valor da ultima compra não for quebrado
      if (valorUltimaCompra % .25 < 0.001) and (price_selected - valorUltimaCompra < 0.001 ):
         price_selected = price_selected - 0.01
      #

      ## launch other thread
      # Último argumento é zero para pagamento pela maquininha; se aplica apenas para o pagamento por Pix
      threadPay = Thread(target=launchPayment, args=(payprocessFrame, price_selected, payment_method_selected, 0))
      threadPay.start()
      #thread.join()
   
    
    
def launchPixRequest(payprocessFrame, price_selected, payment_method_selected):

   # function must:
   #  - get auth token
   #  - get QR Code text from server
   #  - convert QR Code text to image
   #  - display image on screen
   #  - call thread to verify payment (launchPayment function)

   print('start pix request')

   pix_copiaecola, pix_txid = paymentProcessing_Pix.PixRequest(price_selected)

   directory_filename_qrcode_pix_img = paymentProcessing_Pix.generate_img_QR_Code_Pix(pix_copiaecola)

   payprocessFrame.pack_forget()
   payprocessFrame.destroy()

   pixDisplayFrame = tkPaymentProcessFrame.createPixDisplayFrame(mainContainer, price_selected, directory_filename_qrcode_pix_img)
   pixDisplayFrame.pack(side="top", fill="both", expand=True)

   # CONTINUE CODE TO VERIFY IF PAYMENT HAS BEEN DONE (launchPayment function)

   # 20240525 modification begins #

   # old code

   #launchPayment(pixDisplayFrame, price_selected, payment_method_selected, pix_txid)

   # new code

   ## launch new thread
   # Último argumento é zero para pagamento pela maquininha; se aplica apenas para o pagamento por Pix
   threadPay = Thread(target=launchPayment, args=(pixDisplayFrame, price_selected, payment_method_selected, pix_txid), daemon=True)
   threadPay.start()

   # 20240525 modification ends #
    

def launchPayment(payprocessFrame, price_selected, payment_method_selected, pix_txid):
   print('starting process')


   global disableInterrupt
   disableInterrupt = 1


   #pay_output_code == 0 => Success ; else: Failure


   if payment_method_selected == "QR Code (Pix)":

      # Verifica status do pagamento
      pay_output_code = paymentProcessing_Pix.verify_payment_pix(pix_txid)

      # launch payment processing pix -> return qr code text
      # pass qr code text to tk function -> display QR Code on screen
      # launch a thread to check for payment completion ((maybe start THIS on this function for Pix, and have a previous func to return qr code and call the tk to display it
      # this func to check for payment completion should last max 3 minutes? then expire. if anything fails or timeout, pay_output_code!=1; if all is good, pay_output_code = 1
      # integrate code from comm_inter_teste_pycharm_project from the folder \Integração API Inter\comm_inter_teste...

      #temporary test
      #pay_output_code = paymentProcessing_Pix.launchPaymentProcessing_Pix_TEST_DONOTCALL(price_selected, payprocessFrame)

      # Chamar função para conexão com API do Inter e gerar QR Code (enquanto isso, tela de loading que já está carregada (mas botar um loading com imagem!!)
      # Assim que gerar o QR Code, passar para a tela que mostra o QR Code e aguardar o pagamento
      # Assim que o pagamento for confirmado, dar pay_output_code = 0




   else:
      pay_output_code = paymentProcessing.launchPaymentProcessing(price_selected, payment_method_selected)

   payprocessFrame.pack_forget()
   payprocessFrame.destroy()
   
   if pay_output_code == 0:
       paycompleteFrame = tkPaymentProcessFrame.createPaySuccessFrame(mainContainer)
       rwUltimoPag.writeValue(price_selected)
       threadSignal = Thread(target=launchSendSignal, args=(price_selected,0))
       threadSignal.start()
   else:
       paycompleteFrame = tkPaymentProcessFrame.createPayFailureFrame(mainContainer)
       
   paycompleteFrame.pack(side="top", fill="both", expand=True)

   print('paymentCompleteOK')
   print('process ends')
   
   ## TEST
   #paycompleteFrame.after(5000, print('ok'))#nav_restart(paycompleteFrame) )
   #paycompleteFrame.after(5000, paycompleteFrame.destroy() )

   time_buffer = 5000
   if pay_output_code == 0:
      time_buffer = 20000

   paycompleteFrame.after(time_buffer, lambda: mainContainer.destroy() )

   ## TEST ENDS
   print('debug1')


# Will be able to detect if settings button is pressed or if the inhibit signal is on
def signalListener(dummyVar1,dummyVar2):

   global disableInterrupt

   while True:

      ## Comment block for Windows testing
      listener_outcome = signalListenerGPIO.listenGPIO()
      ## End of comment block for Windows testing

      ## Additional code block for Windows testing
      #listener_outcome = "no"
      #disableInterrupt = 1
      time.sleep(2) # Run loop every two seconds. This might be interesting for the production version (otherwise this is continuously in a loop without a time break)
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


#########################################################################
### PENDING FIX! ###
# PERHAPS ONLY LISTENS ON HELLO SCREEN THEN STOPS??
# PERHAPS PASS HELLOSCREENFRAME AS PARAMETER AND IF THERE IS NO LISTENER
#OUTCOME FINISHES THE THREAD AND GOES ON WITH THE CODE??
## RIGHT NOW IT KIND OF WORKS BUT THE GUI BECOMES COMPLETELY BROKEN.

#def navigate_SettingsMainFrame(currentFrame):
def navigate_SettingsMainFrame():
   print('navSettingsMenu')

   global settingsContainer

   settingsContainer = tk.Toplevel()
   settingsContainer.title("settings_container")

   settingsContainer.geometry('320x480')

   # commented for testing
   settingsContainer.resizable(False, False)
   settingsContainer.attributes('-fullscreen', True)

   #currentFrame.pack_forget()
   #currentFrame.destroy()
   settingsFrame = tkSettingsMainFrame.createSettingSelectionFrame(settingsContainer)
   #priceFrame.configure(background='black')
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

   elif settingPageSelection == "Endereço MAC Moderninha":
      MACSettingFrame = tkMACSettingFrame.createMACSettingFrame(settingsContainer)
      MACSettingFrame.pack(side="top", fill="both", expand=True)
      
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


def inhibitEndListener(dummyVar1,dummyVar2):

   inhibit_end_listener_outcome = signalListenerGPIO.inhibitEndListenGPIO()

   mainContainer.destroy()
   settingsContainer.destroy()


def launchSendSignal(price,dummyVar):
    sendSignalGPIO.sendOutputSignal(price)


def quitProgramAfterSettings():
   mainContainer.destroy()
   settingsContainer.destroy()

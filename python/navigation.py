import tkinter as tk

import tkinter_frames.tkPaymentProcessFrame as tkPaymentProcessFrame
import tkinter_frames.tkPMethodFrame as tkPMethodFrame
import tkinter_frames.tkPriceFrame as tkPriceFrame
import tkinter_frames.tkHelloFrame as tkHelloFrame
import tkinter_frames.tkPriceSettingFrame as tkPriceSettingFrame
import tkinter_frames.tkPMethodSettingFrame as tkPMethodSettingFrame
import tkinter_frames.tkSettingsMainFrame as tkSettingsMainFrame

##tmp
import time

import threading
from threading import Thread

import paymentProcessing
import sendSignalGPIO
import signalListenerGPIO

##


def navigation(frame):
   frame.pack_forget()  # from
   # PACK to
   
   
def navigate_helloFrame():

   global mainContainer

   mainContainer = tk.Tk()
   mainContainer.title("sistema_pagamento_plugpag")

   mainContainer.geometry('320x480')
   # COMMENTED ONLY FOR TESTING. UNCOMMENT LATER!
   # mainContainer.resizable(False, False)
   # mainContainer.attributes('-fullscreen', True)
    
    
   helloFrame = tkHelloFrame.createHelloFrame()
   helloFrame.pack(mainContainer, side="top", fill="both", expand=True)

   # Listen GPIO input ports for INHIBIT or SETTINGS signals
   threadListener = Thread(target=signalListener, args=(0, 0))
   threadListener.start()
   
   mainContainer.mainloop()
   
##   
##def nav_restart(currentFrame):
##   currentFrame.pack_forget()
##   currentFrame.destroy()
##   navigate_helloFrame()
   

def navigate_priceFrame(currentFrame):
   print('navPrice')
   currentFrame.pack_forget()
   currentFrame.destroy()
   priceFrame = tkPriceFrame.createPriceFrame()
   #priceFrame.configure(background='black')
   priceFrame.pack(mainContainer, side="top", fill="both", expand=True)

def navigate_payment_method_Frame(price_selected, currentFrame):
   print('navpMethod')
   print('price selected was:'+str(price_selected))
   currentFrame.pack_forget()
   currentFrame.destroy()
   pmethodFrame = tkPMethodFrame.createPaymentMethodFrame(price_selected)
   pmethodFrame.pack(mainContainer, side="top", fill="both", expand=True)

def navigate_payment_process(price_selected, payment_method_selected, currentFrame):
   print('navPayProcess')
   print(price_selected)
   print(payment_method_selected)
   currentFrame.pack_forget()
   currentFrame.destroy()
   payprocessFrame = tkPaymentProcessFrame.createPayProcessFrame()
   payprocessFrame.pack(mainContainer, side="top", fill="both", expand=True)
   print('launch payment processing function')
   
   
   print("NUMBER OF ACTIVE THREADS")
   print(threading.active_count())
   print("ENDS PRINT ACTIVE THREADS")
   

   ## launch other thread
   threadPay = Thread(target=launchPayment, args=(payprocessFrame, price_selected, payment_method_selected))
   threadPay.start()
   #thread.join()
   
    

def launchPayment(payprocessFrame, price_selected, payment_method_selected):
   print('starting process')
   #time.sleep(3) ##################### TEMPORARY JUST TO TEST CONCEPT

   pay_output_code = paymentProcessing.launchPaymentProcessing(price_selected, payment_method_selected)
   #pay_output_code == 0 => Success ; else: Failure

   ## simulate payment completion
   payprocessFrame.pack_forget()
   payprocessFrame.destroy()
   
   if pay_output_code == 0:
       paycompleteFrame = tkPaymentProcessFrame.createPaySuccessFrame()
       threadSignal = Thread(target=launchSendSignal, args=(price_selected,0))
       threadSignal.start()
   else:
       paycompleteFrame = tkPaymentProcessFrame.createPayFailureFrame()
       
   paycompleteFrame.pack(mainContainer, side="top", fill="both", expand=True)

   print('paymentCompleteOK')
   print('process ends')
   
   ## TEST
   #paycompleteFrame.after(5000, print('ok'))#nav_restart(paycompleteFrame) )
   #paycompleteFrame.after(5000, paycompleteFrame.destroy() )
   paycompleteFrame.after(5000, lambda: mainContainer.destroy() )

   ## TEST ENDS
   print('debug1')


# Will be able to detect if settings button is pressed or if the inhibit signal is on
def signalListener(dummyVar1,dummyVar2):
   listener_outcome = signalListenerGPIO.listenGPIO()

   if listener_outcome == "settings":
      print('navigate to settings main frame')
      navigate_SettingsMainFrame()
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

   #currentFrame.pack_forget()
   #currentFrame.destroy()
   settingsFrame = tkSettingsMainFrame.createSettingSelectionFrame()
   #priceFrame.configure(background='black')
   settingsFrame.pack(settingsContainer, side="top", fill="both", expand=True)
#########################################################################

def navigate_selected_setting_menu(settingPageSelection, currentFrame):
   print('nav_selected_setting_menu')
   print(settingPageSelection)
   currentFrame.pack_forget()
   currentFrame.destroy()

   if settingPageSelection == "Preços":
      priceSettingFrame = tkPriceSettingFrame.createPriceSettingFrame()
      priceSettingFrame.pack(settingsContainer, side="top", fill="both", expand=True)

   elif settingPageSelection == "Métodos pagamento":
      pMethodSettingFrame = tkPMethodSettingFrame.createPMethodSettingFrame()
      pMethodSettingFrame.pack(settingsContainer, side="top", fill="both", expand=True)

   else:
      ## Ver se isso é suficiente para voltar ao início - TESTE PENDENTE
      mainContainer.destroy()



def launchSendSignal(price,dummyVar):
    sendSignalGPIO.sendOutputSignal(price)

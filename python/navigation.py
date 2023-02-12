import tkinter as tk

import tkinter_frames.tkPaymentProcessFrame as tkPaymentProcessFrame
import tkinter_frames.tkPMethodFrame as tkPMethodFrame
import tkinter_frames.tkPriceFrame as tkPriceFrame
import tkinter_frames.tkHelloFrame as tkHelloFrame


##tmp
import time

import threading
from threading import Thread

import paymentProcessing
import sendSignalGPIO

##


def navigation(frame):
   frame.pack_forget()  # from
   # PACK to
   
   
def navigate_helloFrame():

   global mainContainer

   mainContainer = tk.Tk()
   mainContainer.title("sistema_pagamento_plugpag")

   mainContainer.geometry('320x480')
   mainContainer.resizable(False, False)
   mainContainer.attributes('-fullscreen', True)
    
    
   helloFrame = tkHelloFrame.createHelloFrame()
   helloFrame.pack(side="top", fill="both", expand=True)
   
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
   priceFrame.pack(side="top", fill="both", expand=True)

def navigate_payment_method_Frame(price_selected, currentFrame):
   print('navpMethod')
   print('price selected was:'+str(price_selected))
   currentFrame.pack_forget()
   currentFrame.destroy()
   pmethodFrame = tkPMethodFrame.createPaymentMethodFrame(price_selected)
   pmethodFrame.pack(side="top", fill="both", expand=True)

def navigate_payment_process(price_selected, payment_method_selected, currentFrame):
   print('navPayProcess')
   print(price_selected)
   print(payment_method_selected)
   currentFrame.pack_forget()
   currentFrame.destroy()
   payprocessFrame = tkPaymentProcessFrame.createPayProcessFrame()
   payprocessFrame.pack(side="top", fill="both", expand=True)
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
       
   paycompleteFrame.pack(side="top", fill="both", expand=True)

   print('paymentCompleteOK')
   print('process ends')
   
   ## TEST
   #paycompleteFrame.after(5000, print('ok'))#nav_restart(paycompleteFrame) )
   #paycompleteFrame.after(5000, paycompleteFrame.destroy() )
   paycompleteFrame.after(5000, lambda: mainContainer.destroy() )

   ## TEST ENDS
   print('debug1')

def launchSendSignal(price,dummyVar):
    sendSignalGPIO.sendOutputSignal(price)

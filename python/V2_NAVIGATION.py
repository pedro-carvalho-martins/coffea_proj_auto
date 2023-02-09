## Defining navigation button
import V2_PAYPROCESSFRAME
import V2_PMETHODFRAME
import V2_PRICEFRAME

##tmp
import time
from threading import Thread

import V2_PaymentProcessing


##


def navigation(frame):
   frame.pack_forget()  # from
   # PACK to

def navigate_priceFrame(currentFrame):
   print('navPrice')
   currentFrame.pack_forget()
   currentFrame.destroy()
   priceFrame = V2_PRICEFRAME.createPriceFrame()
   priceFrame.pack(side="top", fill="both", expand=True)

def navigate_payment_method_Frame(price_selected, currentFrame):
   print('navpMethod')
   print('price selected was:'+str(price_selected))
   currentFrame.pack_forget()
   currentFrame.destroy()
   pmethodFrame = V2_PMETHODFRAME.createPaymentMethodFrame(price_selected)
   pmethodFrame.pack(side="top", fill="both", expand=True)

def navigate_payment_process(price_selected, payment_method_selected, currentFrame):
   print('navPayProcess')
   print(price_selected)
   print(payment_method_selected)
   currentFrame.pack_forget()
   currentFrame.destroy()
   payprocessFrame = V2_PAYPROCESSFRAME.createPayProcessFrame()
   payprocessFrame.pack(side="top", fill="both", expand=True)
   print('launch payment processing function')

   ## launch other thread
   thread = Thread(target=TaskTest, args=(payprocessFrame, price_selected, payment_method_selected))
   thread.start()
   #thread.join()






def TaskTest(payprocessFrame, price_selected, payment_method_selected):
   print('starting process')
   #time.sleep(3) ##################### TEMPORARY JUST TO TEST CONCEPT

   V2_PaymentProcessing.launchPaymentProcessing(price_selected, payment_method_selected)

   ## simulate payment completion
   payprocessFrame.pack_forget()
   payprocessFrame.destroy()
   paycompleteFrame = V2_PAYPROCESSFRAME.createPayCompleteFrame()
   paycompleteFrame.pack(side="top", fill="both", expand=True)

   print('paymentCompleteOK')
   print('process ends')

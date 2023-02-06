import subprocess

def launchPaymentProcessing(price, paymentMethod):
#TEST
    
    if paymentMethod == "Crédito":
        paymentMethodInput = "1"
    elif paymentMethod == "Débito":
        paymentMethodInput = "2"
    elif paymentMethod == "Voucher":
        paymentMethodInput = "3"
    else:
        paymentMethodInput = "0"
        print("ErrorPaymentMethod "+paymentMethod)
        
    priceInput = str(int(price*100))
        
    
    
    print(priceInput)
    print(paymentMethodInput)
    
    payment_sh_command = [
        "/home/pi/Desktop/sistema_pagamento/coffea_proj_auto/plugpag_integration/rpi_plugpag_dev/output/CommandPromptTest",
        "COM0",
        paymentMethodInput,
        "1",
        "1",
        priceInput,
        "ABC"
        ]

    payment_output = subprocess.run(payment_sh_command,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
    
    print("debugTest")
    
    print(payment_output.stdout.decode("utf-8"))
    print(payment_output.stderr.decode("utf-8"))
    

##    # calculate factorial to simulate processing time
##    time.sleep(5)
##    print(factorial(50))
##
##import time
##def factorial(n):
##    print(n)
##    if n != 1:
##        return n * factorial(n-1)
##    else:
##        return 1

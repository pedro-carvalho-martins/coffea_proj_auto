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
        "/home/pi/Desktop/sistema_pagamento/coffea_proj_auto/plugpag_integration/rpi_plugpag_dev/output/payment_request_plugpag",
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
    
    print("stdout PRINT DEBUG")
    # print(payment_output.stdout.decode("utf-8"))
    payment_stdout_str = payment_output.stdout.decode("utf-8")
    list_payment_stdout_str = payment_stdout_str.split("\n")
    print(list_payment_stdout_str)
    
    print("stderr PRINT DEBUG")
    # print(payment_output.stderr.decode("utf-8"))
    payment_stderr_str = payment_output.stderr.decode("utf-8")
    list_payment_stderr_str = payment_stderr_str.split("\n")
    print(list_payment_stderr_str)
    

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

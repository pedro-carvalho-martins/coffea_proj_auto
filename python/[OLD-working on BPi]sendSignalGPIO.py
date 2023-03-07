import subprocess

def sendOutputSignal(price):
    print("SCRIPT TO SEND SIGNAL CALL")
    print(price)
    
    pulse_coin_value = 0.25
    
    number_of_pulses = round(price/pulse_coin_value)
    
    
    payment_sh_command = [
        "sudo",
        "/home/pi/Desktop/sistema_pagamento/coffea_proj_auto/gpio_scripts/gpio_payment_output",
        str(number_of_pulses)
        ]

    payment_output = subprocess.run(payment_sh_command,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
    
    
    
    print("stdout PRINT DEBUG")
    # print(payment_output.stdout.decode("utf-8"))
    payment_stdout_str = payment_output.stdout.decode("ISO-8859-1")#.decode("ascii")#.decode("utf-8")
    list_payment_stdout_str = payment_stdout_str.split("\n")
    print(list_payment_stdout_str)
    
    print("stderr PRINT DEBUG")
    # print(payment_output.stderr.decode("utf-8"))
    payment_stderr_str = payment_output.stderr.decode("ISO-8859-1")#.decode("utf-8")
    list_payment_stderr_str = payment_stderr_str.split("\n")
    print(list_payment_stderr_str)
    
    print(payment_output.returncode)
    
    # WITH RETURNCODE CONFIRMATION, GO FROM SENDING SIGNAL FRAME TO CHOOSE DRINK
    
    #return payment_output
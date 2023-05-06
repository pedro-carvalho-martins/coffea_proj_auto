import subprocess

def launchConnCheckProcess():
#TEST

    print('debugConnCheck')

    payment_sh_command = [
        "../plugpag_integration/rpi_plugpag_dev/output/payment_request_plugpag",
        "COM0",
        "STATUS"
        ]

    connCheck_output = subprocess.run(payment_sh_command,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
    
    print("debugTest")
    
    print("stdout PRINT DEBUG")
    connCheck_stdout_str = connCheck_output.stdout.decode("ISO-8859-1")#.decode("ascii")#.decode("utf-8")
    list_connCheck_stdout_str = connCheck_stdout_str.split("\n")
    print(list_connCheck_stdout_str)
    
    print("stderr PRINT DEBUG")
    # print(payment_output.stderr.decode("utf-8"))
    connCheck_stderr_str = connCheck_output.stderr.decode("ISO-8859-1")#.decode("utf-8")
    list_connCheck_stderr_str = connCheck_stderr_str.split("\n")
    print(list_connCheck_stderr_str)
    
    connCheck_output = int(list_connCheck_stderr_str[2].split('RETORNO: ',1)[1])
    print(connCheck_output)
    
    return connCheck_output
    


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

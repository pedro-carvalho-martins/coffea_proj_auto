import random
import subprocess
import time
import rwMACAddress
import rwPaymentMethodsList
import rwConnCheckFile
import rwSystemID

import client_connection as servConn

import tkinter_frames.tkConnCheckFrame

def launchConnCheckProcess():
#TEST

    print('debugConnCheck')

    connCheck_sh_command = [
        "../plugpag_integration/rpi_plugpag_dev/output/payment_request_plugpag",
        "COM0",
        "STATUS"
        ]

    connCheck_output = subprocess.run(connCheck_sh_command,
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
    
    connCheck_output = int(list_connCheck_stdout_str[2].split('RETORNO: ',1)[1])
    print(connCheck_output)
    
    return connCheck_output
    


def launchConnectBTProcess():

    # Obtenho endereço MAC da moderninha
    mac_address = rwMACAddress.readMACAddress()[0:17]

    # Construo e executo scripts para conexão BT com a moderninha


    BT_conn_shell_comm_1 = [
        "sudo",
        "rfcomm",
        "release",
        "all"
        ]

    BT_conn_shell_comm_2 = [
        "sudo",
        "rfcomm",
        "bind",
        "/dev/rfcomm0",
        mac_address,
        "1"
        ]

    BT_conn_shell_comm_3 = [
        "sudo",
        "chmod",
        "777",
        "/dev/rfcomm0"
        ]

    BT_conn_output_1 = subprocess.run(BT_conn_shell_comm_1,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
    
    print(BT_conn_shell_comm_1)

    BT_conn_output_2 = subprocess.run(BT_conn_shell_comm_2,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)

    print(BT_conn_shell_comm_2)

    BT_conn_output_3 = subprocess.run(BT_conn_shell_comm_3,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)

    print(BT_conn_shell_comm_3)

    time.sleep(5)


def checkConnModerninha(dict_paymentMethods_settings):

    # If all card payment options are disabled, status_conn_moderninha is disabled. Otherwise, do connection check
    if (dict_paymentMethods_settings['Débito'] == 'disabled'
            and dict_paymentMethods_settings['Crédito'] == 'disabled'
            and dict_paymentMethods_settings['Voucher'] == 'disabled'):
        status_conn_moderninha = "disabled"
        return status_conn_moderninha

    # Função provisória para teste

    # randint1 = random.randint(1, 2)
    # time.sleep(random.randint(1, 2))  # tempo randomizado simula tempo de processamento dos testes
    #
    # print("randint1: "+str(randint1))
    #
    # if randint1 == 1:
    #     status_conn_moderninha = "check"
    # else:
    #     status_conn_moderninha = "erro"

    connCheck_moderninha_sh_command = [
        "../plugpag_integration/rpi_plugpag_dev/output/payment_request_plugpag",
        "COM0",
        "STATUS"
    ]

    attempt = 0
    retries = 3

    while attempt < retries:

        try:
            connCheck_moderninha_output = subprocess.run(
                connCheck_moderninha_sh_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=5  # Set the timeout in seconds
            )

            print("debugTest")

            print("stdout PRINT DEBUG")
            connCheck_stdout_str = connCheck_moderninha_output.stdout.decode("ISO-8859-1")
            list_connCheck_stdout_str = connCheck_stdout_str.split("\n")
            print(list_connCheck_stdout_str)

            print("stderr PRINT DEBUG")
            connCheck_stderr_str = connCheck_moderninha_output.stderr.decode("ISO-8859-1")
            list_connCheck_stderr_str = connCheck_stderr_str.split("\n")
            print(list_connCheck_stderr_str)

            connCheck_moderninha_output = int(list_connCheck_stdout_str[2].split('RETORNO: ', 1)[1])
            print(connCheck_moderninha_output)

            if connCheck_moderninha_output == 0:
                status_conn_moderninha = "check"
                break # If the connection test passes, exit the while loop
            else:
                status_conn_moderninha = "error"

        except subprocess.TimeoutExpired:
            print("Subprocess timed out.")
            status_conn_moderninha = "error"

        except Exception as e:
            print(f"An error occurred: {e}")
            status_conn_moderninha = "error"

        attempt += 1
        time.sleep(2)

    print("status conn moderninha: "+status_conn_moderninha)

    return status_conn_moderninha


def checkConnPixServer(dict_paymentMethods_settings):

    # If QR Code payment option is disabled, status_conn_servidor_pix is disabled. Otherwise, do connection check
    if dict_paymentMethods_settings['QR Code (Pix)'] == 'disabled':
        status_conn_servidor_pix = "disabled"
        return status_conn_servidor_pix

    # Função provisória para teste

    # randint2 = random.randint(1, 2)
    # time.sleep(random.randint(1, 2))  # tempo randomizado simula tempo de processamento dos testes
    #
    # print("randint2: " + str(randint2))
    #
    # if randint2 == 1:
    #     status_conn_servidor_pix = "check"
    # else:
    #     status_conn_servidor_pix = "erro"

    # Get system ID to be sent in request
    systemID = rwSystemID.readSystemID()

    try:
        request_ping = {"type": "ping", "param1": systemID, "param2": 0}
        response_request_ping = servConn.send_request(request_ping)
    except:
        print("Ping failure")
        response_request_ping = {'ping': "erro"}

    if response_request_ping['ping'] == "OK":
        status_conn_servidor_pix = "check"
    else:
        status_conn_servidor_pix = "erro"

    print("status conn servidor pix: " + status_conn_servidor_pix)

    return status_conn_servidor_pix


def launchStartupConnCheckProcess():
    # TEST

    # na implementação final, essa função deve
    # #1: Puxar do rw de payment methods o dictionary com o estado enabled/disabled dos métodos de pagemento
    # #2: Se Moderninha/QR Code estiver disabled, já coloca o status disabled
    # #3: Para o que estiver enabled, chama a função respectiva em um novo thread para verificar a conexão

    print('debugNewConnCheck')

    # Simula um teste de conexão com outcome aleatório e tempo de retorno aleatório
    # Na implementação real, o ideal é chamar duas funções em threads diferentes aqui nessa função; definir cada função de check de conexão nesse arquivo.

    # Gets dictionary of payment method settings to check what is enabled and disabled
    dict_paymentMethods_settings = rwPaymentMethodsList.readListSettings()

    # Call the functions that will retrieve the status of each connection
    checkConnModerninha_result = checkConnModerninha(dict_paymentMethods_settings)
    checkConnPixServer_result = checkConnPixServer(dict_paymentMethods_settings)

    # Assign the connection status to the variables that will define the images displayed on the connCheck frame
    tkinter_frames.tkConnCheckFrame.status_conn_moderninha = checkConnModerninha_result
    tkinter_frames.tkConnCheckFrame.status_conn_servidor_pix = checkConnPixServer_result

    # Update the connCheck file that will be updated over the execution of the program
    rwConnCheckFile.writeConnCheckStatus(
        {"Moderninha": checkConnModerninha_result,
         "QR Code (Pix)": checkConnPixServer_result})

    # If there are no errors (e.g. only check or disable), send success output (=0); otherwise, send fail output (=1)
    if (
        (tkinter_frames.tkConnCheckFrame.status_conn_moderninha == "check"
        or tkinter_frames.tkConnCheckFrame.status_conn_moderninha == "disabled")
        and (tkinter_frames.tkConnCheckFrame.status_conn_servidor_pix == "check"
        or tkinter_frames.tkConnCheckFrame.status_conn_servidor_pix == "disabled")
    ):
        connCheck_output = 0 # Success
    else:
        connCheck_output = 1 # Fail or partial fail
        # Show buttons to reconnect or continue anyway after connection fails or partially fails
        tkinter_frames.tkConnCheckFrame.display_buttons = "yes"

    return connCheck_output


def launchBackgroundConnCheckProcess(arg1, arg2):

    while True:
        time.sleep(10)
        print("background connCheck starts")

        # Gets dictionary of payment method settings to check what is enabled and disabled
        dict_paymentMethods_settings = rwPaymentMethodsList.readListSettings()

        # Call the functions that will retrieve the status of each connection
        checkConnModerninha_result = checkConnModerninha(dict_paymentMethods_settings)
        checkConnPixServer_result = checkConnPixServer(dict_paymentMethods_settings)

        # Assign the connection status to the variables that will define the images displayed on the connCheck frame
        tkinter_frames.tkConnCheckFrame.status_conn_moderninha = checkConnModerninha_result
        tkinter_frames.tkConnCheckFrame.status_conn_servidor_pix = checkConnPixServer_result

        # Update the connCheck file that will be updated over the execution of the program
        rwConnCheckFile.writeConnCheckStatus(
            {"Moderninha": checkConnModerninha_result,
             "QR Code (Pix)": checkConnPixServer_result})
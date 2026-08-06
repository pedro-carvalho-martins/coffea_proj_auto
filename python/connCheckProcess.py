import subprocess
import time

import rwMACAddress
import rwPaymentMethodsList
import rwConnCheckFile
import rwLogCSV
import serverPairingProcess
from connectionAvailability import classify_server_connection, evaluate_connection_outcome

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

    global status_conn_moderninha

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
    retries = 1
    failure_already_logged = False

    while attempt < retries:

        try:
            connCheck_moderninha_output = subprocess.run(
                connCheck_moderninha_sh_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=5  # Set the timeout in seconds
            )

            connCheck_stdout_str = connCheck_moderninha_output.stdout.decode("ISO-8859-1")
            list_connCheck_stdout_str = connCheck_stdout_str.split("\n")

            connCheck_moderninha_output = int(list_connCheck_stdout_str[2].split('RETORNO: ', 1)[1])

            if connCheck_moderninha_output == 0:
                status_conn_moderninha = "check"
                break # If the connection test passes, exit the while loop
            else:
                status_conn_moderninha = "error"

        except subprocess.TimeoutExpired:

            rwLogCSV.writeCSV("erro_outros", "", "", "checkConnModerninha", "TimeoutExpired", "Subprocess timed out")
            failure_already_logged = True
            status_conn_moderninha = "error"

        except Exception as e:
            rwLogCSV.writeCSV("erro_outros", "", "", "checkConnModerninha", str(e.__class__), str(e))
            failure_already_logged = True
            status_conn_moderninha = "error"

        attempt += 1
        time.sleep(0)

    if attempt == retries and not failure_already_logged:
        rwLogCSV.writeCSV(
            "erro_outros",
            "",
            "",
            "checkConnModerninha",
            "ModerninhaReturnCode",
            "Return code " + str(connCheck_moderninha_output),
        )

    return status_conn_moderninha


def checkConnServer():

    global status_conn_servidor_pix

    serverPairingProcess.sync_once()
    pairing_state = serverPairingProcess.get_pairing_state()
    status_conn_servidor_pix = classify_server_connection(pairing_state)

    return status_conn_servidor_pix


def launchStartupConnCheckProcess():
    settings, moderninha_status, server_status = _run_connection_checks()

    return evaluate_connection_outcome(
        settings,
        moderninha_status,
        server_status,
    )


def launchBackgroundConnCheckProcess(arg1, arg2):
    _run_connection_checks()


def _run_connection_checks():
    settings = rwPaymentMethodsList.readListSettings()
    moderninha_status = checkConnModerninha(settings)
    server_status = checkConnServer()
    settings = rwPaymentMethodsList.readListSettings()

    tkinter_frames.tkConnCheckFrame.status_conn_moderninha = moderninha_status
    tkinter_frames.tkConnCheckFrame.status_conn_servidor_pix = server_status
    rwConnCheckFile.writeConnCheckStatus(
        {
            "Moderninha": moderninha_status,
            "QR Code (Pix)": server_status,
        }
    )
    return settings, moderninha_status, server_status

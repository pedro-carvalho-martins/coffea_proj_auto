import subprocess
import time
import rwMACAddress


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
import subprocess

import requests
import ssl
import qrcode
import time

import rwSystemID

from PIL import Image

import client_connection as servConn




def PixRequest(price_selected):

    # Get system ID to be sent in request
    systemID = rwSystemID.readSystemID()

    request_create_pix = {"type": "create_pix", "param1": systemID, "param2": price_selected}
    response_PixRequest = servConn.send_request(request_create_pix)

    return response_PixRequest['pix_qrcode_copiaecola'], response_PixRequest['pix_txid']


def generate_img_QR_Code_Pix(pixCopiaECola):

    directory_filename_pix_img = "qrCodePix.png"

    img_qrcode = qrcode.make(pixCopiaECola)
    img_qrcode.save(directory_filename_pix_img)


    return directory_filename_pix_img



def get_status_cobranca(txid):

    # Get system ID to be sent in request
    systemID = rwSystemID.readSystemID()

    request_cob_read = {"type": "cob_read", "param1": systemID, "param2": txid}
    response_StatusCob = servConn.send_request(request_cob_read, max_retries=5, delay=0)

    return response_StatusCob



def verify_payment_pix(txid):


    time_sec = 0

    while time_sec < 300:
        time_sec += 5
        time.sleep(5)

        response_payment_status = get_status_cobranca(txid)

        payment_status = response_payment_status['status_cob_pix']

        if payment_status == "ATIVA":
            # Pix está ativo e ainda não foi pago; volta ao início do loop
            continue

        elif payment_status == "CONCLUIDA":
            # Se o pagamento for realizado, retorna o código 0 (sucesso)
            return 0

        else:
            # Status não é ATIVA nem CONCLUIDA. Há algum erro.
            return -1


import tkinter as tk
import threading
import time
import queue
import rwLogCSV  # ✅ Keep Original CSV Logging
from logger import logger  # ✅ New system logging

# Existing imports remain unchanged
import paymentProcessing
import paymentProcessing_Pix
import connCheckProcess
import sendSignalGPIO
import signalListenerGPIO
import logTransmissionProcess
import rwUltimoPag
import rwHelloSettingFile

# New logging additions start here

def launchPixRequest(payprocessFrame, price_selected, payment_method_selected):
    logger.info(f"Starting Pix request for {price_selected} {payment_method_selected}")

    try:
        pix_copiaecola, pix_txid = paymentProcessing_Pix.PixRequest(price_selected)
        directory_filename_qrcode_pix_img = paymentProcessing_Pix.generate_img_QR_Code_Pix(pix_copiaecola)

        enqueue_hide_and_destroy_frame(payprocessFrame)
        pixDisplayFrame = tkPaymentProcessFrame.createPixDisplayFrame(mainContainer, price_selected, directory_filename_qrcode_pix_img)
        enqueue_pack_new_frame(pixDisplayFrame)

        threadPay = threading.Thread(target=launchPayment, args=(pixDisplayFrame, price_selected, payment_method_selected, pix_txid), daemon=True)
        threadPay.start()

    except Exception as e:
        logger.exception("Error in launchPixRequest:")
        rwLogCSV.writeCSV("venda_erro", str(price_selected), payment_method_selected, "launchPixRequest", str(e.__class__), str(e))

        enqueue_hide_and_destroy_frame(payprocessFrame)
        paycompleteFrame = tkPaymentProcessFrame.createPayFailureFrame(mainContainer)
        enqueue_pack_new_frame(paycompleteFrame)
        paycompleteFrame.after(5000, lambda: mainContainer.destroy())


def launchPayment(payprocessFrame, price_selected, payment_method_selected, pix_txid):
    logger.info(f"Processing payment: {payment_method_selected} - {price_selected}")

    global disableInterrupt
    disableInterrupt = 1

    try:
        if payment_method_selected == "QR Code (Pix)":
            pay_output_code = paymentProcessing_Pix.verify_payment_pix(pix_txid)
        else:
            pay_output_code = paymentProcessing.launchPaymentProcessing(price_selected, payment_method_selected)

        enqueue_hide_and_destroy_frame(payprocessFrame)

        if pay_output_code == 0:
            paycompleteFrame = tkPaymentProcessFrame.createPaySuccessFrame(mainContainer)
            rwUltimoPag.writeValue(price_selected)
            rwLogCSV.writeCSV("venda_sucesso", str(price_selected), payment_method_selected, "", "", "")
            threadSignal = threading.Thread(target=launchSendSignal, args=(price_selected, 0))
            threadSignal.start()
        else:
            paycompleteFrame = tkPaymentProcessFrame.createPayFailureFrame(mainContainer)

    except Exception as e:
        logger.exception("Error in launchPayment:")
        rwLogCSV.writeCSV("venda_erro", str(price_selected), payment_method_selected, "launchPayment", str(e.__class__), str(e))

        enqueue_hide_and_destroy_frame(payprocessFrame)
        paycompleteFrame = tkPaymentProcessFrame.createPayFailureFrame(mainContainer)

    enqueue_pack_new_frame(paycompleteFrame)
    paycompleteFrame.after(5000, lambda: mainContainer.destroy())


def launchConnCheck(connCheckFrame, dummyVariable):
    logger.info("Starting connection check process")

    try:
        conn_check_output_code = connCheckProcess.launchStartupConnCheckProcess()

        if conn_check_output_code == 0:
            time.sleep(3)
            enqueue_hide_and_destroy_frame(connCheckFrame)
            check_helloScreen(connCheckFrame)

        elif conn_check_output_code == 1:
            time.sleep(3)
            enqueue_hide_and_destroy_frame(connCheckFrame)
            check_helloScreen(connCheckFrame)

        else:
            time.sleep(10)
            enqueue_hide_and_destroy_frame(connCheckFrame)
            navigate_connCheckFrame(connCheckFrame)

    except Exception as e:
        logger.exception("Error in launchConnCheck:")
        rwLogCSV.writeCSV("erro_outros", "", "", "launchConnCheck", str(e.__class__), str(e))


def navigate_payment_process(price_selected, payment_method_selected, currentFrame):
    logger.info(f"Navigating to payment process: {payment_method_selected} - {price_selected}")

    enqueue_hide_and_destroy_frame(currentFrame)

    if payment_method_selected == "QR Code (Pix)":
        payprocessFrame = tkPaymentProcessFrame.createPayProcessFrame_Pix(mainContainer)
        enqueue_pack_new_frame(payprocessFrame)
        enqueue_launchPixRequest(payprocessFrame, price_selected, payment_method_selected)
    else:
        payprocessFrame = tkPaymentProcessFrame.createPayProcessFrame(mainContainer)
        enqueue_pack_new_frame(payprocessFrame)

        threadPay = threading.Thread(target=launchPayment, args=(payprocessFrame, price_selected, payment_method_selected, 0))
        threadPay.start()


def navigate_selected_setting_menu(settingPageSelection, currentFrame):
    logger.info(f"Navigating to settings menu: {settingPageSelection}")

    currentFrame.pack_forget()
    currentFrame.destroy()

    if settingPageSelection == "Preços":
        priceSettingFrame = tkPriceSettingFrame.createPriceSettingFrame(settingsContainer)
        priceSettingFrame.pack(side="top", fill="both", expand=True)

    elif settingPageSelection == "Métodos pagamento":
        pMethodSettingFrame = tkPMethodSettingFrame.createPMethodSettingFrame(settingsContainer)
        pMethodSettingFrame.pack(side="top", fill="both", expand=True)

    elif settingPageSelection == "Identificador sistema":
        IDSettingFrame = tkIDSettingFrame.createIDSettingFrame(settingsContainer)
        IDSettingFrame.pack(side="top", fill="both", expand=True)

    elif settingPageSelection == "Config. tela inicial":
        HelloSettingFrame = tkHelloSettingFrame.createHelloSettingFrame(settingsContainer)
        HelloSettingFrame.pack(side="top", fill="both", expand=True)


def launchSendSignal(price, dummyVar):
    try:
        sendSignalGPIO.sendOutputSignal(price)
    except Exception as e:
        logger.exception("Error in launchSendSignal:")
        rwLogCSV.writeCSV("erro_outros", str(price), "Undefined", "launchSendSignal_sendSignalGPIO", str(e.__class__), str(e))

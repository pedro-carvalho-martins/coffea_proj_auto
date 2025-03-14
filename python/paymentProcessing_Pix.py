import rwLogCSV  # ✅ Keep Original CSV Logging
from logger import logger  # ✅ New system logging

def verify_payment_pix(txid):
    logger.info(f"Verifying Pix payment for txid: {txid}")

    try:
        response_payment_status = get_status_cobranca(txid)
        logger.debug(f"Raw Pix payment response: {response_payment_status}")

        payment_status = response_payment_status.get('status_cob_pix')

        if not isinstance(payment_status, str) or not payment_status.lstrip('-').isdigit():
            logger.error(f"Invalid payment status format received: {payment_status}")
            rwLogCSV.writeCSV("venda_erro", "", "QR Code (Pix)", "verify_payment_pix", "InvalidFormat", payment_status)  # ✅ Keep Original CSV Logging
            return -1  # ✅ Prevents crashing if response is malformed

        payment_status = int(payment_status)
        logger.info(f"Converted Pix payment status to int: {payment_status}")

        return payment_status

    except Exception as e:
        logger.exception("Error in verify_payment_pix:")
        rwLogCSV.writeCSV("venda_erro", "", "QR Code (Pix)", "verify_payment_pix", str(e.__class__), str(e))  # ✅ Keep Original CSV Logging
        return -1

"""Durable payment-record handoff for MDB vending outcomes."""

import paymentProcessing
import pixDeliveryConfirmation


def finalize_vend_success(payment, price):
    provider = payment.get("provider")
    payment_method = payment.get("payment_method", "N/A")
    if provider == "pix":
        pixDeliveryConfirmation.report_delivery(
            payment["txid"],
            "concluida",
            0,
            0,
            0,
        )
        return True
    if provider == "moderninha":
        return paymentProcessing.finish_delivery_record(
            payment.get("record_id"),
            price,
            payment_method,
            "concluida",
        )
    raise ValueError("Provedor de pagamento MDB desconhecido")


def mark_delivery_uncertain(payment, price, reason):
    provider = payment.get("provider")
    payment_method = payment.get("payment_method", "N/A")
    message = "Entrega MDB nao confirmada: " + str(reason)[:250]
    if provider == "pix":
        pixDeliveryConfirmation.report_delivery(
            payment["txid"],
            "incerta",
            0,
            0,
            0,
            message,
        )
        return True
    if provider == "moderninha":
        return paymentProcessing.finish_delivery_record(
            payment.get("record_id"),
            price,
            payment_method,
            "pago_entrega_nao_confirmada",
            erro_entrega=message,
        )
    return False

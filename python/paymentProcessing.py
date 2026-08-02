import re
import subprocess
import unicodedata
from decimal import Decimal, ROUND_HALF_UP

import diagnosticLog
import paymentOutbox
import rwLogCSV


PAYMENT_METHOD_INPUTS = {
    "Crédito": "1",
    "Débito": "2",
    "Voucher": "3",
}
UNKNOWN_RESULT_CODES = {-1005, -1019}
RETURN_CODE_PATTERN = re.compile(r"RETORNO:\s*(-?\d+)")
RESULT_FIELD_PATTERN = re.compile(r"^\s*([^\[]+?)\s*\[(.*)\]\s*$")
RESULT_FIELD_NAMES = {
    "message": "message",
    "transactionCode": "transaction_code",
    "date": "terminal_date",
    "time": "terminal_time",
    "hostNsu": "host_nsu",
    "cardBrand": "card_brand",
    "holder": "card_last_four",
    "user reference": "user_reference",
}


def _price_to_centavos(price):
    amount = Decimal(str(price)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return int(amount * 100)


def _parse_moderninha_output(output):
    return_match = RETURN_CODE_PATTERN.search(output)
    if return_match is None:
        raise ValueError("Moderninha output did not contain a return code")

    details = {}
    for line in output.splitlines():
        field_match = RESULT_FIELD_PATTERN.match(line)
        if field_match is None:
            continue
        source_name = field_match.group(1).strip()
        destination_name = RESULT_FIELD_NAMES.get(source_name)
        if destination_name:
            details[destination_name] = field_match.group(2).strip()

    details["return_code"] = int(return_match.group(1))
    return details


def _normalize_message(message):
    return unicodedata.normalize("NFKD", message).encode("ascii", "ignore").decode().lower()


def _status_from_result(return_code, message):
    normalized_message = _normalize_message(message or "")
    if return_code == 0:
        return "concluida"
    if return_code in UNKNOWN_RESULT_CODES:
        return "resultado_desconhecido"
    if "cancel" in normalized_message:
        return "cancelada"
    if (
        "recus" in normalized_message
        or "negad" in normalized_message
        or "nao autoriz" in normalized_message
        or return_code == -1004
    ):
        return "recusada"
    return "falha"


def launchPaymentProcessing(price, paymentMethod):
    payment_method_input = PAYMENT_METHOD_INPUTS.get(paymentMethod, "0")
    price_centavos = _price_to_centavos(price)
    transaction = paymentOutbox.begin_transaction(price_centavos, paymentMethod)
    if not transaction["persisted"]:
        diagnosticLog.record_event(
            "critical",
            "payment.outbox_create_failed",
            "paymentProcessing",
            "Moderninha payment started without a durable local transaction record",
            context={
                "transaction_id": transaction["transaction_id"],
                "valor_centavos": price_centavos,
                "metodo_pagamento": paymentMethod,
            },
        )

    payment_command = [
        "../plugpag_integration/rpi_plugpag_dev/output/payment_request_plugpag",
        "COM0",
        payment_method_input,
        "1",
        "1",
        str(price_centavos),
        transaction["user_reference"],
    ]

    attempt = 0
    retries = 2
    payment_output = -1
    transaction_details = {
        "user_reference": transaction["user_reference"],
    }
    last_error = None

    while attempt < retries:
        try:
            process_result = subprocess.run(
                payment_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            stdout = process_result.stdout.decode("ISO-8859-1")
            stderr = process_result.stderr.decode("ISO-8859-1")
            transaction_details.update(_parse_moderninha_output(stdout))
            transaction_details["subprocess_return_code"] = process_result.returncode
            if stderr.strip():
                transaction_details["stderr"] = stderr.strip()[:500]
            payment_output = transaction_details["return_code"]
            break
        except Exception as error:
            last_error = error
            diagnosticLog.record_exception(
                "payment.moderninha_exception",
                "paymentProcessing",
                error,
                context={
                    "transaction_id": transaction["transaction_id"],
                    "valor_centavos": price_centavos,
                    "metodo_pagamento": paymentMethod,
                    "attempt": attempt + 1,
                },
            )
            attempt += 1

    if attempt == retries:
        rwLogCSV.writeCSV(
            "venda_erro",
            str(price),
            paymentMethod,
            "launchPaymentProcessing_Moderninha",
            type(last_error).__name__ if last_error else "",
            "maximum number of attempts to connect to Moderninha exceeded",
        )
        status = "resultado_desconhecido"
        if last_error:
            transaction_details["processing_error"] = str(last_error)[:500]
    else:
        status = _status_from_result(
            payment_output,
            transaction_details.get("message", ""),
        )

    paymentOutbox.complete_transaction(
        transaction["transaction_id"],
        status,
        transaction_details,
    )
    return payment_output

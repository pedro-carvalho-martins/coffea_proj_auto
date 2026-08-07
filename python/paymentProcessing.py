import subprocess
import re
import uuid

import localRecordQueue
import rwLogCSV


PAYMENT_EXECUTABLE = "../plugpag_integration/rpi_plugpag_dev/output/payment_request_plugpag"


def _field(output, label):
    match = re.search(r"\b" + re.escape(label) + r"\s*\[(.*?)\]", output)
    return match.group(1).strip() if match else ""


def parse_payment_output(output):
    return_match = re.search(r"RETORNO:\s*(-?\d+)", output)
    if return_match is None:
        raise ValueError("PlugPag output does not contain RETORNO")
    holder_digits = re.sub(r"\D", "", _field(output, "holder"))
    return int(return_match.group(1)), {
        "identificador_pagamento": _field(output, "transactionCode"),
        "cartao_ultimos_quatro": (
            holder_digits[-4:] if len(holder_digits) >= 4 else ""
        ),
        "moderninha_reference": _field(output, "user reference"),
        "host_nsu": _field(output, "hostNsu"),
        "card_brand": _field(output, "cardBrand"),
        "card_bin": _field(output, "bin"),
        "moderninha_message": _field(output, "message"),
    }


def _record_pending_payment(price, payment_method, reference):
    try:
        return localRecordQueue.record_transaction(
            price,
            payment_method,
            "pendente",
            moderninha_reference=reference,
        )
    except Exception:
        return None


def _finish_payment_record(record_id, price, payment_method, status, metadata):
    try:
        if record_id and localRecordQueue.update_transaction(
            record_id,
            status,
            **metadata,
        ):
            return
        localRecordQueue.record_transaction(
            price,
            payment_method,
            status,
            **metadata,
        )
    except Exception:
        # Diagnostic persistence must never alter the payment result.
        pass

def launchPaymentProcessing(price, paymentMethod):
#TEST
    
    if paymentMethod == "Crédito":
        paymentMethodInput = "1"
    elif paymentMethod == "Débito":
        paymentMethodInput = "2"
    elif paymentMethod == "Voucher":
        paymentMethodInput = "3"
    else:
        paymentMethodInput = "0"
        print("ErrorPaymentMethod "+paymentMethod)
        
    priceInput = str(int(price*100))
    
    print(priceInput)
    print(paymentMethodInput)
    
    reference = uuid.uuid4().hex[:10].upper()
    record_id = _record_pending_payment(price, paymentMethod, reference)
    payment_sh_command = [
        PAYMENT_EXECUTABLE,
        "COM0",
        paymentMethodInput,
        "1",
        "1",
        priceInput,
        reference,
        ]
    metadata = {
        "moderninha_reference": reference,
        "moderninha_return_code": -1,
    }

    try:
        completed_process = subprocess.run(
            payment_sh_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        payment_stdout = completed_process.stdout.decode("ISO-8859-1", errors="replace")
        payment_stderr = completed_process.stderr.decode("ISO-8859-1", errors="replace")
        print(payment_stdout.splitlines())
        print(payment_stderr.splitlines())
        payment_output, parsed_metadata = parse_payment_output(payment_stdout)
        metadata.update(parsed_metadata)
        metadata["moderninha_reference"] = reference
        metadata["moderninha_return_code"] = payment_output
    except Exception as exc:
        payment_output = -1
        metadata["moderninha_message"] = str(exc)[:200]
        try:
            rwLogCSV.writeCSV(
                "venda_erro",
                str(price),
                paymentMethod,
                "launchPaymentProcessing_Moderninha",
                exc.__class__.__name__,
                str(exc),
            )
        except Exception:
            pass

    _finish_payment_record(
        record_id,
        price,
        paymentMethod,
        "concluida" if payment_output == 0 else "falha",
        metadata,
    )
    return payment_output
    


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

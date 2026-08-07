import subprocess
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch


PYTHON_DIR = Path(__file__).resolve().parents[1] / "python"
sys.path.insert(0, str(PYTHON_DIR))

# Avoid creating Raspberry Pi runtime directories while importing on Windows.
rw_log_stub = types.ModuleType("rwLogCSV")
rw_log_stub.writeCSV = lambda *args, **kwargs: None
sys.modules["rwLogCSV"] = rw_log_stub

import paymentProcessing


SUCCESS_OUTPUT = """VENDA

RETORNO: 0

Transaction Result
\tmessage [Transacao realizada com sucesso]
\ttransactionCode [3742D61768C8486D8ABA20A36C5A369A]
\tdate [2026-08-06]
\ttime [17:06:59]
\thostNsu [080623012641]
\tcardBrand [MASTERCARD]
\tbin [521422]
\tholder [7379]
\tuser reference [T07DC96155]
"""


class PaymentProcessingTests(unittest.TestCase):
    def test_parser_extracts_reconciliation_fields(self):
        return_code, metadata = paymentProcessing.parse_payment_output(SUCCESS_OUTPUT)

        self.assertEqual(return_code, 0)
        self.assertEqual(
            metadata["identificador_pagamento"],
            "3742D61768C8486D8ABA20A36C5A369A",
        )
        self.assertEqual(metadata["cartao_ultimos_quatro"], "7379")
        self.assertEqual(metadata["moderninha_reference"], "T07DC96155")
        self.assertEqual(metadata["host_nsu"], "080623012641")

    def test_parser_keeps_only_the_last_four_holder_digits(self):
        output = SUCCESS_OUTPUT.replace("holder [7379]", "holder [**** 7379]")

        _, metadata = paymentProcessing.parse_payment_output(output)

        self.assertEqual(metadata["cartao_ultimos_quatro"], "7379")

    def test_parse_failure_never_retries_the_payment_command(self):
        completed = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout=b"unexpected output",
            stderr=b"",
        )
        with patch.object(
            paymentProcessing.localRecordQueue,
            "record_transaction",
            return_value="record-id",
        ), patch.object(
            paymentProcessing.localRecordQueue,
            "update_transaction",
            return_value=True,
        ), patch.object(
            paymentProcessing.subprocess,
            "run",
            return_value=completed,
        ) as run, patch.object(paymentProcessing.rwLogCSV, "writeCSV"):
            result = paymentProcessing.launchPaymentProcessing(1, "Voucher")

        self.assertEqual(result, -1)
        run.assert_called_once()

    def test_success_updates_the_pending_record_without_changing_return_code(self):
        completed = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout=SUCCESS_OUTPUT.encode("ISO-8859-1"),
            stderr=b"",
        )
        with patch.object(
            paymentProcessing.uuid,
            "uuid4",
        ) as uuid4, patch.object(
            paymentProcessing.localRecordQueue,
            "record_transaction",
            return_value="record-id",
        ), patch.object(
            paymentProcessing.localRecordQueue,
            "update_transaction",
            return_value=True,
        ) as update, patch.object(
            paymentProcessing.subprocess,
            "run",
            return_value=completed,
        ) as run:
            uuid4.return_value.hex = "07dc96155abcdef"
            result = paymentProcessing.launchPaymentProcessing(1, "Voucher")

        self.assertEqual(result, 0)
        self.assertEqual(run.call_args.args[0][-1], "07DC96155A")
        update.assert_called_once()
        self.assertEqual(update.call_args.args[:2], ("record-id", "concluida"))
        self.assertEqual(
            update.call_args.kwargs["identificador_pagamento"],
            "3742D61768C8486D8ABA20A36C5A369A",
        )


if __name__ == "__main__":
    unittest.main()

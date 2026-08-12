import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch


PYTHON_DIR = Path(__file__).resolve().parents[1] / "python"
sys.path.insert(0, str(PYTHON_DIR))

rw_log_stub = types.ModuleType("rwLogCSV")
rw_log_stub.writeCSV = lambda *args, **kwargs: None
sys.modules.setdefault("rwLogCSV", rw_log_stub)

import mdb_payment_delivery


class MdbPaymentDeliveryTests(unittest.TestCase):
    def test_pix_success_uses_existing_delivery_confirmation(self):
        payment = {
            "provider": "pix",
            "txid": "txid",
            "payment_method": "QR Code (Pix)",
        }
        with patch.object(
            mdb_payment_delivery.pixDeliveryConfirmation,
            "report_delivery",
            return_value=False,
        ) as report:
            finalized = mdb_payment_delivery.finalize_vend_success(payment, 4.5)

        self.assertTrue(finalized)
        report.assert_called_once_with("txid", "concluida", 0, 0, 0)

    def test_moderninha_success_finalizes_existing_record(self):
        payment = {
            "provider": "moderninha",
            "record_id": "record-id",
            "payment_method": "Credito",
        }
        with patch.object(
            mdb_payment_delivery.paymentProcessing,
            "finish_delivery_record",
            return_value=True,
        ) as finish:
            finalized = mdb_payment_delivery.finalize_vend_success(payment, 4.5)

        self.assertTrue(finalized)
        finish.assert_called_once_with(
            "record-id",
            4.5,
            "Credito",
            "concluida",
        )

    def test_uncertain_pix_delivery_requests_refund_path(self):
        payment = {
            "provider": "pix",
            "txid": "txid",
            "payment_method": "QR Code (Pix)",
        }
        with patch.object(
            mdb_payment_delivery.pixDeliveryConfirmation,
            "report_delivery",
            return_value=True,
        ) as report:
            marked = mdb_payment_delivery.mark_delivery_uncertain(
                payment,
                4.5,
                "vend_failure",
            )

        self.assertTrue(marked)
        self.assertEqual(report.call_args.args[:2], ("txid", "incerta"))


if __name__ == "__main__":
    unittest.main()

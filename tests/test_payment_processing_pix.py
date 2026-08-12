import sys
import unittest
from pathlib import Path
from unittest.mock import patch


PYTHON_DIR = Path(__file__).resolve().parents[1] / "python"
sys.path.insert(0, str(PYTHON_DIR))

import paymentProcessing_Pix


class PaymentProcessingPixTests(unittest.TestCase):
    def test_status_request_declares_delivery_confirmation(self):
        with patch.object(
            paymentProcessing_Pix.rwSystemId,
            "readSystemId",
            return_value="system-id",
        ), patch.object(
            paymentProcessing_Pix.rwServerPairingSettings,
            "read_pairing_token",
            return_value="token",
        ), patch.object(
            paymentProcessing_Pix,
            "get_json",
            return_value={"status": "pago_aguardando_confirmacao_entrega"},
        ) as get_json:
            result = paymentProcessing_Pix.get_status_cobranca("txid", 4)

        self.assertEqual(result["status"], "pago_aguardando_confirmacao_entrega")
        self.assertEqual(
            get_json.call_args.args[1],
            {
                "sistema_pag_id": "system-id",
                "delivery_confirmation": "v1",
                "expected_delivery_seconds": 4,
            },
        )

    def test_waiting_delivery_status_means_payment_is_confirmed(self):
        with patch.object(paymentProcessing_Pix.time, "sleep"), patch.object(
            paymentProcessing_Pix,
            "get_status_cobranca",
            return_value={"status": "pago_aguardando_confirmacao_entrega"},
        ):
            result = paymentProcessing_Pix.verify_payment_pix("txid", 4)

        self.assertEqual(result, 0)


if __name__ == "__main__":
    unittest.main()

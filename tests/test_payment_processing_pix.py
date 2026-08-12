import sys
import threading
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

    def test_cancellation_interrupts_status_wait_without_request(self):
        cancellation_event = threading.Event()
        cancellation_event.set()

        with patch.object(paymentProcessing_Pix, "get_status_cobranca") as status:
            result = paymentProcessing_Pix.verify_payment_pix(
                "txid",
                4,
                cancellation_event,
            )

        self.assertEqual(result, paymentProcessing_Pix.PIX_PAYMENT_CANCELLED)
        status.assert_not_called()

    def test_pending_response_honors_cancellation_requested_in_flight(self):
        cancellation_event = threading.Event()

        def pending_response(*_args):
            cancellation_event.set()
            return {"status": "pendente"}

        with patch.object(
            paymentProcessing_Pix,
            "_wait_or_cancel",
            return_value=False,
        ), patch.object(
            paymentProcessing_Pix,
            "get_status_cobranca",
            side_effect=pending_response,
        ):
            result = paymentProcessing_Pix.verify_payment_pix(
                "txid",
                4,
                cancellation_event,
            )

        self.assertEqual(result, paymentProcessing_Pix.PIX_PAYMENT_CANCELLED)

    def test_paid_response_wins_over_cancellation_requested_in_flight(self):
        cancellation_event = threading.Event()

        def paid_response(*_args):
            cancellation_event.set()
            return {"status": "pago_aguardando_confirmacao_entrega"}

        with patch.object(
            paymentProcessing_Pix,
            "_wait_or_cancel",
            return_value=False,
        ), patch.object(
            paymentProcessing_Pix,
            "get_status_cobranca",
            side_effect=paid_response,
        ):
            result = paymentProcessing_Pix.verify_payment_pix(
                "txid",
                4,
                cancellation_event,
            )

        self.assertEqual(result, 0)


if __name__ == "__main__":
    unittest.main()

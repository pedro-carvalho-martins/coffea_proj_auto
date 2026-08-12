import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


PYTHON_DIR = Path(__file__).resolve().parents[1] / "python"
sys.path.insert(0, str(PYTHON_DIR))

import pixDeliveryConfirmation


class PixDeliveryConfirmationTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.queue_file = os.path.join(self.temporary_directory.name, "delivery.csv")

    def tearDown(self):
        self.temporary_directory.cleanup()

    def test_failed_immediate_attempts_remain_durable(self):
        with patch.object(
            pixDeliveryConfirmation,
            "_send",
            side_effect=RuntimeError("offline"),
        ) as send, patch.object(pixDeliveryConfirmation.time, "sleep"):
            confirmed = pixDeliveryConfirmation.report_delivery(
                "txid",
                "concluida",
                6,
                6,
                0,
                file_path=self.queue_file,
            )

        self.assertFalse(confirmed)
        self.assertEqual(send.call_count, len(pixDeliveryConfirmation.ACTIVE_RETRY_DELAYS_SECONDS))
        self.assertEqual(
            pixDeliveryConfirmation.read_pending(self.queue_file)[0]["txid"],
            "txid",
        )

    def test_successful_retry_removes_pending_confirmation(self):
        with patch.object(
            pixDeliveryConfirmation,
            "_send",
            side_effect=(RuntimeError("offline"), {"status": "concluida"}),
        ), patch.object(pixDeliveryConfirmation.time, "sleep"):
            confirmed = pixDeliveryConfirmation.report_delivery(
                "txid",
                "concluida",
                6,
                6,
                1,
                file_path=self.queue_file,
            )

        self.assertTrue(confirmed)
        self.assertEqual(pixDeliveryConfirmation.read_pending(self.queue_file), [])

    def test_later_sync_transmits_a_persisted_result(self):
        pixDeliveryConfirmation.queue_delivery_result(
            "txid",
            "incerta",
            6,
            3,
            1,
            "gpio failure",
            self.queue_file,
        )
        with patch.object(
            pixDeliveryConfirmation,
            "_send",
            return_value={"status": "reembolsada_entrega_nao_confirmada"},
        ):
            sent = pixDeliveryConfirmation.transmit_pending(self.queue_file)

        self.assertEqual(sent, 1)
        self.assertEqual(pixDeliveryConfirmation.read_pending(self.queue_file), [])

    def test_local_queue_failure_still_attempts_immediate_confirmation(self):
        with patch.object(
            pixDeliveryConfirmation,
            "_persist_record",
            side_effect=OSError("read-only filesystem"),
        ), patch.object(
            pixDeliveryConfirmation,
            "_send",
            return_value={"status": "concluida"},
        ) as send:
            confirmed = pixDeliveryConfirmation.report_delivery(
                "txid",
                "concluida",
                6,
                6,
                0,
                file_path=self.queue_file,
            )

        self.assertTrue(confirmed)
        send.assert_called_once()


if __name__ == "__main__":
    unittest.main()

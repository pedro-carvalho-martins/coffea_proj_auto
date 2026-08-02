import os
import tempfile
import unittest

import paymentOutbox


class PaymentOutboxTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.original_path = paymentOutbox.PAYMENT_OUTBOX_FILE
        paymentOutbox.PAYMENT_OUTBOX_FILE = os.path.join(
            self.temporary_directory.name,
            "logs",
            "payment_outbox.sqlite3",
        )

    def tearDown(self):
        paymentOutbox.PAYMENT_OUTBOX_FILE = self.original_path
        self.temporary_directory.cleanup()

    def test_completed_transaction_is_returned_and_acknowledged(self):
        transaction = paymentOutbox.begin_transaction(350, "Débito")
        paymentOutbox.complete_transaction(
            transaction["transaction_id"],
            "concluida",
            {"card_brand": "VISA", "card_last_four": "1234"},
        )

        pending = paymentOutbox.get_pending_transactions()

        self.assertEqual(len(pending), 1)
        self.assertEqual(pending[0]["transaction_id"], transaction["transaction_id"])
        self.assertEqual(pending[0]["amount_centavos"], 350)
        self.assertEqual(pending[0]["status"], "concluida")
        paymentOutbox.acknowledge_transactions([transaction["transaction_id"]])
        self.assertEqual(paymentOutbox.get_pending_transactions(), [])

    def test_interrupted_pending_transaction_becomes_unknown(self):
        paymentOutbox.begin_transaction(500, "Crédito")

        paymentOutbox.mark_interrupted_transactions_unknown()
        pending = paymentOutbox.get_pending_transactions()

        self.assertEqual(len(pending), 1)
        self.assertEqual(pending[0]["status"], "resultado_desconhecido")
        self.assertIsNotNone(pending[0]["completed_at"])


if __name__ == "__main__":
    unittest.main()

import os
import csv
import sys
import tempfile
import unittest
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import patch


PYTHON_DIR = Path(__file__).resolve().parents[1] / "python"
sys.path.insert(0, str(PYTHON_DIR))

import localRecordQueue
import recordTransmissionProcess
import shared_resource


class LocalRecordQueueTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.transactions_file = os.path.join(
            self.temporary_directory.name,
            "pending_transactions.csv",
        )
        self.events_file = os.path.join(
            self.temporary_directory.name,
            "pending_events.csv",
        )
        localRecordQueue.reset_runtime_state_for_tests()
        shared_resource.customer_interaction_active.clear()

    def tearDown(self):
        localRecordQueue.reset_runtime_state_for_tests()
        shared_resource.customer_interaction_active.clear()
        self.temporary_directory.cleanup()

    def test_transaction_survives_until_its_uuid_is_acknowledged(self):
        first_id = localRecordQueue.record_transaction(
            "2.50",
            "Debito",
            "concluida",
            self.transactions_file,
        )
        second_id = localRecordQueue.record_transaction(
            "3.00",
            "Credito",
            "falha",
            self.transactions_file,
        )

        batch = localRecordQueue.read_batch(
            self.transactions_file,
            localRecordQueue.TRANSACTION_FIELDS,
            limit=50,
        )
        self.assertEqual([row["record_id"] for row in batch], [first_id, second_id])
        self.assertEqual(batch[0]["valor_centavos"], "250")

        removed = localRecordQueue.acknowledge_records(
            self.transactions_file,
            localRecordQueue.TRANSACTION_FIELDS,
            "record_id",
            [first_id],
        )

        self.assertEqual(removed, 1)
        remaining = localRecordQueue.read_batch(
            self.transactions_file,
            localRecordQueue.TRANSACTION_FIELDS,
        )
        self.assertEqual([row["record_id"] for row in remaining], [second_id])

    def test_pending_transaction_is_updated_in_place(self):
        record_id = localRecordQueue.record_transaction(
            "1.00",
            "Credito",
            "pendente",
            self.transactions_file,
            moderninha_reference="ABC1234567",
        )

        updated = localRecordQueue.update_transaction(
            record_id,
            "concluida",
            self.transactions_file,
            identificador_pagamento="TRANSACTION-CODE",
            cartao_ultimos_quatro="7379",
            moderninha_return_code=0,
        )

        self.assertTrue(updated)
        records = localRecordQueue.read_batch(
            self.transactions_file,
            localRecordQueue.TRANSACTION_FIELDS,
        )
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["status"], "concluida")
        self.assertEqual(records[0]["identificador_pagamento"], "TRANSACTION-CODE")
        self.assertEqual(records[0]["cartao_ultimos_quatro"], "7379")
        self.assertTrue(records[0]["datetime_conclusao"])

    def test_delivery_result_is_kept_with_the_moderninha_transaction(self):
        record_id = localRecordQueue.record_transaction(
            "1.49",
            "Credito",
            "pago_aguardando_confirmacao_entrega",
            self.transactions_file,
        )

        localRecordQueue.update_transaction(
            record_id,
            "concluida",
            self.transactions_file,
            pulsos_esperados=6,
            pulsos_concluidos=6,
            pulsos_retentados=1,
        )

        record = localRecordQueue.read_batch(
            self.transactions_file,
            localRecordQueue.TRANSACTION_FIELDS,
        )[0]
        self.assertEqual(record["status"], "concluida")
        self.assertEqual(record["pulsos_esperados"], "6")
        self.assertEqual(record["pulsos_concluidos"], "6")
        self.assertEqual(record["pulsos_retentados"], "1")

    def test_legacy_transaction_queue_is_migrated_in_place(self):
        with open(self.transactions_file, "w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(
                csv_file,
                fieldnames=localRecordQueue.LEGACY_TRANSACTION_FIELDS,
            )
            writer.writeheader()
            writer.writerow(
                {
                    "record_id": "legacy-id",
                    "datetime": "2026-08-06T10:00:00-03:00",
                    "valor_centavos": "100",
                    "metodo_pag": "Credito",
                    "status": "concluida",
                }
            )

        records = localRecordQueue.read_batch(
            self.transactions_file,
            localRecordQueue.TRANSACTION_FIELDS,
        )

        self.assertEqual(records[0]["record_id"], "legacy-id")
        self.assertEqual(records[0]["identificador_pagamento"], "")
        with open(self.transactions_file, "r", newline="", encoding="utf-8") as csv_file:
            self.assertEqual(
                tuple(csv.DictReader(csv_file).fieldnames),
                localRecordQueue.TRANSACTION_FIELDS,
            )

    def test_identical_error_is_suppressed_during_cooldown(self):
        self.assertTrue(localRecordQueue.should_record_error("sync", "timeout", "offline", now=10))
        self.assertFalse(localRecordQueue.should_record_error("sync", "timeout", "offline", now=20))
        self.assertTrue(
            localRecordQueue.should_record_error(
                "sync",
                "timeout",
                "offline",
                now=10 + localRecordQueue.ERROR_COOLDOWN_SECONDS,
            )
        )

    def test_connection_outage_emits_only_one_start_and_one_summary(self):
        self.assertTrue(localRecordQueue.note_connection_failure(now=100))
        self.assertFalse(localRecordQueue.note_connection_failure(now=200))
        self.assertFalse(localRecordQueue.note_connection_failure(now=300))

        recovery = localRecordQueue.note_connection_restored(now=400)

        self.assertEqual(recovery["duration_seconds"], 300)
        self.assertEqual(recovery["failed_attempts"], 3)
        self.assertIsNone(localRecordQueue.note_connection_restored(now=500))

    def test_transmitter_removes_only_server_acknowledged_records(self):
        record_id = localRecordQueue.record_transaction(
            "2.50",
            "Debito",
            "concluida",
            self.transactions_file,
        )
        with ExitStack() as stack:
            stack.enter_context(patch.object(
                recordTransmissionProcess,
                "PENDING_TRANSACTIONS_FILE",
                self.transactions_file,
            ))
            stack.enter_context(patch.object(
                recordTransmissionProcess,
                "PENDING_EVENTS_FILE",
                self.events_file,
            ))
            stack.enter_context(patch.object(
                recordTransmissionProcess.rwSystemId,
                "readSystemId",
                return_value="38a486cd-a2af-42a4-a107-e6e467ef04aa",
            ))
            stack.enter_context(patch.object(
                recordTransmissionProcess.rwServerPairingSettings,
                "read_pairing_token",
                return_value="token",
            ))
            post_json = stack.enter_context(patch.object(
                recordTransmissionProcess,
                "post_json",
                return_value={"accepted_ids": [record_id]},
            ))
            transmitted = recordTransmissionProcess.transmit_pending_records()

        self.assertTrue(transmitted)
        post_json.assert_called_once()
        self.assertEqual(
            localRecordQueue.read_batch(
                self.transactions_file,
                localRecordQueue.TRANSACTION_FIELDS,
            ),
            [],
        )

    def test_transmitter_does_nothing_during_customer_interaction(self):
        shared_resource.customer_interaction_active.set()
        with patch.object(recordTransmissionProcess, "post_json") as post_json:
            transmitted = recordTransmissionProcess.transmit_pending_records()

        self.assertFalse(transmitted)
        post_json.assert_not_called()


if __name__ == "__main__":
    unittest.main()

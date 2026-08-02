import os
import tempfile
import unittest

import diagnosticLog


class DiagnosticLogTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.original_path = diagnosticLog.DIAGNOSTIC_OUTBOX_FILE
        diagnosticLog.DIAGNOSTIC_OUTBOX_FILE = os.path.join(
            self.temporary_directory.name,
            "logs",
            "diagnostic_outbox.sqlite3",
        )

    def tearDown(self):
        diagnosticLog.DIAGNOSTIC_OUTBOX_FILE = self.original_path
        self.temporary_directory.cleanup()

    def test_outbox_is_created_and_duplicate_event_is_aggregated(self):
        first_id = diagnosticLog.record_event(
            "warning",
            "server.sync_failed",
            "serverPairingProcess",
            "Network unavailable",
            dedupe_key="server.sync_failed",
        )
        second_id = diagnosticLog.record_event(
            "warning",
            "server.sync_failed",
            "serverPairingProcess",
            "Network still unavailable",
            dedupe_key="server.sync_failed",
        )

        events = diagnosticLog.get_pending_events()

        self.assertEqual(first_id, second_id)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["occurrence_count"], 2)
        self.assertEqual(events[0]["message"], "Network still unavailable")
        self.assertTrue(os.path.exists(diagnosticLog.DIAGNOSTIC_OUTBOX_FILE))

    def test_acknowledged_events_are_removed(self):
        event_id = diagnosticLog.record_event(
            "error",
            "test.failure",
            "test",
            "Failure",
        )

        diagnosticLog.acknowledge_events([event_id])

        self.assertEqual(diagnosticLog.get_pending_events(), [])


if __name__ == "__main__":
    unittest.main()

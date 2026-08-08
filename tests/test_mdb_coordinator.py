import sys
import tempfile
import unittest
from pathlib import Path


PYTHON_DIR = Path(__file__).resolve().parents[1] / "python"
sys.path.insert(0, str(PYTHON_DIR))

from mdb_coordinator import MdbSessionCoordinator
from mdb_protocol import parse_line
from mdb_state_store import MdbStateStore


class MdbCoordinatorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.commands = []
        self.events = []
        self.store = MdbStateStore(str(Path(self.temp.name) / "active.json"))
        self.coordinator = MdbSessionCoordinator(
            self.commands.append,
            lambda event, data: self.events.append((event, data)),
            self.store,
        )

    def tearDown(self):
        self.temp.cleanup()

    def _open_vend(self):
        self.coordinator.handle(parse_line("BOOT protocol=2 boot=abcd1234"))
        self.coordinator.handle(parse_line("MDB READER_ENABLE boot=abcd1234"))
        self.assertEqual(self.commands[-1], "SESSION 65535")
        self.coordinator.handle(
            parse_line("MDB SESSION_BEGIN boot=abcd1234 session=1 funds=65535")
        )
        self.coordinator.handle(
            parse_line(
                "MDB VEND_REQUEST boot=abcd1234 session=1 vend=9 price=450 item=7"
            )
        )

    def test_ack_approve_is_not_dispense_success(self):
        self._open_vend()
        self.assertTrue(
            self.coordinator.payment_result(
                True,
                {"provider": "pix", "payment_method": "QR Code (Pix)"},
            )
        )
        self.assertEqual(self.commands[-1], "APPROVE abcd1234 9")
        self.coordinator.handle(
            parse_line("ACK command=APPROVE status=queued boot=abcd1234 vend=9")
        )
        self.assertIsNotNone(self.store.load())
        self.assertFalse(any(event == "vend_success" for event, _ in self.events))

        self.coordinator.handle(
            parse_line(
                "MDB VEND_SUCCESS boot=abcd1234 session=1 vend=9 price=450 item=7"
            )
        )
        self.assertIsNone(self.store.load())
        self.assertEqual(self.events[-1][0], "vend_success")

    def test_timeout_denies_before_cancelling_session(self):
        self._open_vend()
        self.assertTrue(self.coordinator.cancel_active("payment_timeout"))
        self.assertEqual(
            self.commands[-2:],
            ["DENY abcd1234 9", "CANCEL abcd1234 1"],
        )

    def test_duplicate_vend_request_does_not_start_second_payment(self):
        self._open_vend()
        original_count = sum(event == "vend_request" for event, _ in self.events)
        self.coordinator.handle(
            parse_line(
                "MDB VEND_REQUEST boot=abcd1234 session=1 vend=9 price=450 item=7"
            )
        )
        self.assertEqual(
            sum(event == "vend_request" for event, _ in self.events),
            original_count,
        )

    def test_reset_after_payment_requires_operator_recovery(self):
        self._open_vend()
        self.coordinator.payment_result(True, {"provider": "moderninha"})
        self.coordinator.handle(
            parse_line("MDB RESET boot=abcd1234 session=1 vend=9")
        )
        self.assertEqual(self.store.load()["state"], "recovery")
        self.assertEqual(self.events[-1][0], "recovery")

    def test_session_does_not_reopen_while_cancelled_payment_is_running(self):
        self._open_vend()
        self.assertTrue(self.coordinator.payment_started("moderninha"))
        self.coordinator.handle(
            parse_line(
                "MDB VEND_CANCEL boot=abcd1234 session=1 vend=9 price=450 item=7"
            )
        )
        command_count = len(self.commands)
        self.coordinator.handle(
            parse_line("MDB SESSION_COMPLETE boot=abcd1234 session=1 vend=9")
        )
        self.assertEqual(len(self.commands), command_count)

        self.assertFalse(self.coordinator.payment_result(False, reason="cancelled"))
        self.assertIsNone(self.store.load())
        self.assertEqual(self.commands[-1], "SESSION 65535")

    def test_late_success_enters_recovery(self):
        self._open_vend()
        self.coordinator.payment_started("moderninha")
        self.coordinator.handle(
            parse_line(
                "MDB VEND_CANCEL boot=abcd1234 session=1 vend=9 price=450 item=7"
            )
        )
        self.assertFalse(
            self.coordinator.payment_result(True, {"provider": "moderninha"})
        )
        self.assertEqual(self.store.load()["state"], "recovery")

    def test_local_settings_pause_cancels_and_blocks_new_vends(self):
        self.coordinator.handle(parse_line("BOOT protocol=2 boot=abcd1234"))
        self.coordinator.handle(parse_line("MDB READER_ENABLE boot=abcd1234"))
        self.coordinator.handle(
            parse_line("MDB SESSION_BEGIN boot=abcd1234 session=1 funds=65535")
        )
        self.coordinator.pause("settings_opened")
        self.assertEqual(self.commands[-1], "CANCEL")
        self.coordinator.handle(
            parse_line(
                "MDB VEND_REQUEST boot=abcd1234 session=1 vend=9 price=450 item=7"
            )
        )
        self.assertEqual(self.commands[-1], "DENY abcd1234 9")
        self.assertIsNone(self.coordinator.active)


if __name__ == "__main__":
    unittest.main()

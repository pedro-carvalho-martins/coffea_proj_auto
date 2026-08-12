import sys
import tempfile
import unittest
from pathlib import Path


PYTHON_DIR = Path(__file__).resolve().parents[1] / "python"
sys.path.insert(0, str(PYTHON_DIR))

from mdb_coordinator import (
    MDB_SESSION_FUNDS_UNITS,
    VEND_SUCCESS_PENDING_FINALIZATION,
    MdbSessionCoordinator,
)
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
        self.assertEqual(
            self.commands[-1],
            f"SESSION {MDB_SESSION_FUNDS_UNITS}",
        )
        self.coordinator.handle(
            parse_line("MDB SESSION_BEGIN boot=abcd1234 session=1 funds=9900")
        )
        self.coordinator.handle(
            parse_line(
                "MDB VEND_REQUEST boot=abcd1234 session=1 vend=9 price=450 item=7"
            )
        )

    def test_approve_ack_is_not_dispense_success(self):
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
        self.assertFalse(any(event == "vend_success" for event, _ in self.events))

    def test_vend_success_is_retained_until_finalization_acknowledged(self):
        self._open_vend()
        self.coordinator.payment_result(True, {"provider": "pix"})
        self.coordinator.handle(
            parse_line(
                "MDB VEND_SUCCESS boot=abcd1234 session=1 vend=9 price=450 item=7"
            )
        )

        self.assertEqual(
            self.store.load()["state"],
            VEND_SUCCESS_PENDING_FINALIZATION,
        )
        self.assertEqual(self.events[-1][0], "vend_success")
        self.assertTrue(
            self.coordinator.complete_vend_success("abcd1234", 9)
        )
        self.assertIsNone(self.store.load())

    def test_restart_replays_pending_vend_finalization(self):
        self._open_vend()
        self.coordinator.payment_result(True, {"provider": "moderninha"})
        self.coordinator.handle(
            parse_line(
                "MDB VEND_SUCCESS boot=abcd1234 session=1 vend=9 price=450 item=7"
            )
        )
        events = []
        restarted = MdbSessionCoordinator(
            self.commands.append,
            lambda event, data: events.append((event, data)),
            self.store,
        )

        restarted.start()

        self.assertEqual(events[-1][0], "vend_success")

    def test_esp_reset_does_not_downgrade_known_vend_success(self):
        self._open_vend()
        self.coordinator.payment_result(True, {"provider": "pix"})
        self.coordinator.handle(
            parse_line(
                "MDB VEND_SUCCESS boot=abcd1234 session=1 vend=9 price=450 item=7"
            )
        )

        self.coordinator.handle(
            parse_line("MDB RESET boot=abcd1234 session=1 vend=9")
        )

        self.assertEqual(
            self.store.load()["state"],
            VEND_SUCCESS_PENDING_FINALIZATION,
        )

    def test_overlapping_vend_does_not_downgrade_known_vend_success(self):
        self._open_vend()
        self.coordinator.payment_result(True, {"provider": "pix"})
        self.coordinator.handle(
            parse_line(
                "MDB VEND_SUCCESS boot=abcd1234 session=1 vend=9 price=450 item=7"
            )
        )

        self.coordinator.handle(
            parse_line(
                "MDB VEND_REQUEST boot=abcd1234 session=2 vend=10 price=200 item=2"
            )
        )

        self.assertEqual(
            self.store.load()["state"],
            VEND_SUCCESS_PENDING_FINALIZATION,
        )
        self.assertEqual(self.store.load()["vend"], 9)
        self.assertEqual(self.commands[-1], "DENY abcd1234 10")

    def test_late_vend_messages_do_not_downgrade_known_vend_success(self):
        self._open_vend()
        self.coordinator.payment_result(True, {"provider": "pix"})
        success = (
            "boot=abcd1234 session=1 vend=9 price=450 item=7"
        )
        self.coordinator.handle(parse_line("MDB VEND_SUCCESS " + success))

        self.coordinator.handle(parse_line("MDB VEND_SUCCESS " + success))
        self.coordinator.handle(parse_line("MDB VEND_CANCEL " + success))
        self.coordinator.handle(parse_line("MDB VEND_FAILURE " + success))

        self.assertEqual(
            self.store.load()["state"],
            VEND_SUCCESS_PENDING_FINALIZATION,
        )

    def test_timeout_denies_before_cancelling_session(self):
        self._open_vend()
        self.assertTrue(self.coordinator.cancel_active("payment_timeout"))
        self.assertEqual(
            self.commands[-2:],
            ["DENY abcd1234 9", "CANCEL abcd1234 1"],
        )

    def test_customer_cancel_keeps_running_payment_for_late_result(self):
        self._open_vend()
        self.assertTrue(self.coordinator.payment_started("pix"))
        self.assertTrue(self.coordinator.cancel_active("customer_cancel"))
        self.assertTrue(self.store.load()["payment_in_progress"])
        self.assertFalse(
            self.coordinator.payment_result(True, {"provider": "pix"})
        )
        self.assertEqual(self.store.load()["state"], "recovery")
        self.assertEqual(
            self.store.load()["reason"],
            "payment_completed_after_mdb_cancel",
        )

    def test_session_does_not_reopen_while_cancelled_payment_is_running(self):
        self._open_vend()
        self.coordinator.payment_started("moderninha")
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

        self.assertFalse(
            self.coordinator.payment_result(False, reason="cancelled")
        )
        self.assertIsNone(self.store.load())
        self.assertEqual(self.commands[-1], "SESSION 9900")

    def test_reset_after_payment_requires_operator_recovery(self):
        self._open_vend()
        self.coordinator.payment_result(True, {"provider": "moderninha"})
        self.coordinator.handle(parse_line("MDB RESET boot=abcd1234 session=1 vend=9"))
        self.assertEqual(self.store.load()["state"], "recovery")

    def test_reconnect_status_keeps_matching_active_vend(self):
        self._open_vend()
        self.coordinator.payment_started("moderninha")

        self.coordinator.handle(
            parse_line(
                "STATUS boot=abcd1234 state=4 reader=1 session_open=1 "
                "session=1 vend=9 price=450 item=7 dropped=0"
            )
        )

        self.assertEqual(self.store.load()["state"], "awaiting_payment")

    def test_reconnect_status_marks_missing_active_vend_as_recovery(self):
        self._open_vend()
        self.coordinator.payment_result(True, {"provider": "moderninha"})

        self.coordinator.handle(
            parse_line(
                "STATUS boot=abcd1234 state=3 reader=1 session_open=1 "
                "session=1 vend=9 price=450 item=7 dropped=0"
            )
        )

        state = self.store.load()
        self.assertEqual(state["state"], "recovery")
        self.assertEqual(
            state["reason"],
            "bridge_no_longer_reports_active_vend",
        )
        self.assertEqual(state["bridge_status"]["state"], "3")

    def test_identical_recovery_reason_notifies_once(self):
        self._open_vend()
        self.coordinator._mark_recovery("test_reason")
        self.coordinator._mark_recovery("test_reason")

        matching = [
            event
            for event, data in self.events
            if event == "recovery" and data.get("reason") == "test_reason"
        ]
        self.assertEqual(len(matching), 1)

    def test_two_completed_vends_reuse_one_coordinator(self):
        self._open_vend()
        self.coordinator.payment_result(True, {"provider": "pix"})
        self.coordinator.handle(
            parse_line(
                "MDB VEND_SUCCESS boot=abcd1234 session=1 vend=9 price=450 item=7"
            )
        )
        self.coordinator.handle(
            parse_line("MDB SESSION_COMPLETE boot=abcd1234 session=1 vend=9")
        )
        self.assertTrue(
            self.coordinator.complete_vend_success("abcd1234", 9)
        )
        self.assertEqual(self.commands[-1], "SESSION 9900")

        self.coordinator.handle(
            parse_line("MDB SESSION_BEGIN boot=abcd1234 session=2 funds=9900")
        )
        self.coordinator.handle(
            parse_line(
                "MDB VEND_REQUEST boot=abcd1234 session=2 vend=10 price=500 item=8"
            )
        )
        self.assertEqual(self.coordinator.active["vend"], 10)


if __name__ == "__main__":
    unittest.main()

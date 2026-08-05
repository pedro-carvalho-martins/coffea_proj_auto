import os
import sys
import unittest
from unittest.mock import MagicMock, call, patch


PYTHON_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "python"))
if PYTHON_DIR not in sys.path:
    sys.path.insert(0, PYTHON_DIR)

with patch.dict(sys.modules, {"rwLogCSV": MagicMock()}):
    import serverPairingProcess


class ServerPairingProcessTests(unittest.TestCase):
    def test_applied_commands_trigger_lightweight_confirmation_cycle(self):
        with patch.object(
            serverPairingProcess,
            "_sync_cycle",
            side_effect=[(True, True), (True, False)],
        ) as sync_cycle:
            paired = serverPairingProcess.sync_once()

        self.assertTrue(paired)
        self.assertEqual(sync_cycle.call_args_list, [call(True), call(False)])

    def test_reboot_command_does_not_request_pre_reboot_confirmation(self):
        self.assertFalse(
            serverPairingProcess._commands_need_confirmation(
                [
                    {"type": "settings"},
                    {"type": "reboot"},
                ]
            )
        )

    def test_settings_commands_request_confirmation(self):
        self.assertTrue(
            serverPairingProcess._commands_need_confirmation(
                [
                    {"type": "settings"},
                    {"type": "settings"},
                    {"type": "settings"},
                ]
            )
        )


if __name__ == "__main__":
    unittest.main()

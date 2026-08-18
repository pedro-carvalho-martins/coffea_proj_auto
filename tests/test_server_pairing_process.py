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
    def test_sync_payload_reports_latest_moderninha_check(self):
        methods = {
            method: "enabled"
            for method in serverPairingProcess.remoteCommandProcess.SUPPORTED_PAYMENT_METHODS
        }
        serverPairingProcess.shared_resource.set_moderninha_connection_status(
            "connected"
        )
        with patch.object(
            serverPairingProcess.rwServerPairingSettings,
            "is_online_mode_enabled",
            return_value=True,
        ), patch.object(
            serverPairingProcess.rwServerPairingSettings,
            "get_pairing_code",
            return_value="123456",
        ), patch.object(
            serverPairingProcess.rwServerPairingSettings,
            "read_pairing_token",
            return_value="token",
        ), patch.object(
            serverPairingProcess.rwPulseCoinValue,
            "readPulseCharacteristics",
            return_value=(0.25, 100, 400),
        ), patch.object(
            serverPairingProcess.rwSystemId,
            "readSystemId",
            return_value="system-id",
        ), patch.object(
            serverPairingProcess.rwSystemName,
            "readSystemName",
            return_value="Terminal",
        ), patch.object(
            serverPairingProcess.rwSystemVersion,
            "readVersion",
            return_value="version",
        ), patch.object(
            serverPairingProcess.rwPricesList,
            "readList",
            return_value=[1.0],
        ), patch.object(
            serverPairingProcess.rwMACAddress,
            "readMACAddress",
            return_value="AA:BB:CC:DD:EE:FF",
        ), patch.object(
            serverPairingProcess.rwHelloSettingFile,
            "readListCheckHello",
            return_value=1,
        ), patch.object(
            serverPairingProcess.rwPaymentMethodsList,
            "readListSettings",
            return_value=methods,
        ), patch.object(
            serverPairingProcess.remoteCommandProcess,
            "read_pending_results",
            return_value=[],
        ), patch.object(
            serverPairingProcess.localRecordQueue,
            "note_connection_restored",
            return_value=None,
        ), patch.object(
            serverPairingProcess,
            "post_json",
            return_value={"status": "pending", "commands": []},
        ) as post_json:
            serverPairingProcess._sync_cycle(False)

        payload = post_json.call_args.args[1]
        self.assertEqual(payload["moderninha_connection_status"], "connected")

    def test_applied_commands_trigger_lightweight_confirmation_cycle(self):
        with patch.object(
            serverPairingProcess,
            "_sync_cycle",
            side_effect=[(True, True, False), (True, False, False)],
        ) as sync_cycle:
            paired = serverPairingProcess.sync_once()

        self.assertTrue(paired)
        self.assertEqual(
            sync_cycle.call_args_list,
            [
                call(True, accept_commands=True),
                call(False, accept_commands=True),
            ],
        )

    def test_close_app_happens_after_confirmation_cycle(self):
        with patch.object(
            serverPairingProcess,
            "_sync_cycle",
            side_effect=[(True, True, True), (True, False, False)],
        ), patch.object(serverPairingProcess.kill_shell_loop, "close_application") as close:
            paired = serverPairingProcess.sync_once()

        self.assertTrue(paired)
        close.assert_called_once_with()

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

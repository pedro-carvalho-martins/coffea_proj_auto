import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


PYTHON_DIR = Path(__file__).resolve().parents[1] / "python"
sys.path.insert(0, str(PYTHON_DIR))

import remoteCommandProcess
import rwHelloSettingFile
import rwMACAddress
import rwPaymentMethodsList
import rwPulseCoinValue
import rwPricesList
import rwSystemName
import shared_resource


class RemoteCommandProcessTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        base = self.temporary_directory.name
        self.result_file = os.path.join(base, "remoteCommandResult.json")
        self.update_file = os.path.join(base, "update_input.txt")
        self.name_file = os.path.join(base, "systemName.txt")
        self.prices_file = os.path.join(base, "listaPrecos.txt")
        self.methods_file = os.path.join(base, "paymentMethods.txt")
        self.mac_file = os.path.join(base, "enderecoMAC.txt")
        self.pulse_file = os.path.join(base, "pulseCoinValue.txt")
        self.hello_file = os.path.join(base, "helloScreenSetting.txt")

        self.patchers = [
            patch.object(remoteCommandProcess, "REMOTE_COMMAND_RESULT_FILE", self.result_file),
            patch.object(remoteCommandProcess, "UPDATE_INPUT_FILE", self.update_file),
            patch.object(rwSystemName, "system_name_filename", self.name_file),
            patch.object(rwPricesList, "price_list_filename", self.prices_file),
            patch.object(rwPaymentMethodsList, "filename", self.methods_file),
            patch.object(rwMACAddress, "mac_filename", self.mac_file),
            patch.object(rwPulseCoinValue, "pulse_coin_filename", self.pulse_file),
            patch.object(rwHelloSettingFile, "hello_filename", self.hello_file),
        ]
        for patcher in self.patchers:
            patcher.start()
        shared_resource.customer_interaction_active.clear()

    def tearDown(self):
        shared_resource.customer_interaction_active.clear()
        for patcher in reversed(self.patchers):
            patcher.stop()
        self.temporary_directory.cleanup()

    def test_update_command_writes_exact_updater_contract(self):
        handled = remoteCommandProcess.process_command_if_safe(
            {
                "command_id": "12dcd41c-210d-45e2-b63d-ab67b4b4ee8e",
                "type": "update",
                "payload": {"tag": "v1.5.2-codex-beta-2"},
            }
        )

        self.assertTrue(handled)
        with open(self.update_file, "r", encoding="utf-8") as file:
            self.assertEqual(file.read(), "True\nv1.5.2-codex-beta-2\n")
        self.assertEqual(remoteCommandProcess.read_pending_result()["status"], "completed")

    def test_settings_command_writes_existing_file_formats(self):
        remoteCommandProcess.process_command_if_safe(
            {
                "command_id": "d9ee789f-e20c-4541-a58f-725288caeb97",
                "type": "settings",
                "payload": {
                    "system_name": "Coffea Teste",
                    "prices": [2.5, 4.0],
                    "payment_methods": {
                        "Débito": True,
                        "Crédito": False,
                        "Voucher": True,
                        "QR Code (Pix)": False,
                    },
                    "moderninha_mac": "AA:BB:CC:DD:EE:FF",
                    "pulse_value": 0.5,
                    "pulse_duration_ms": 120,
                    "pulse_interval_ms": 420,
                    "hello_screen_enabled": False,
                },
            }
        )

        self.assertEqual(rwSystemName.readSystemName(), "Coffea Teste")
        self.assertEqual(rwPricesList.readList(), [2.5, 4.0])
        self.assertEqual(
            rwPaymentMethodsList.readListSettings(),
            {
                "Débito": "enabled",
                "Crédito": "disabled",
                "Voucher": "enabled",
                "QR Code (Pix)": "disabled",
            },
        )
        self.assertEqual(rwMACAddress.readMACAddress(), "AA:BB:CC:DD:EE:FF")
        self.assertEqual(
            rwPulseCoinValue.readPulseCharacteristics(),
            (0.5, 120.0, 420.0),
        )
        self.assertFalse(rwHelloSettingFile.readListCheckHello())
        self.assertIn(
            "novo MAC",
            remoteCommandProcess.read_pending_result()["message"],
        )

    def test_command_is_deferred_during_customer_interaction(self):
        shared_resource.customer_interaction_active.set()

        handled = remoteCommandProcess.process_command_if_safe(
            {
                "command_id": "28edb0d1-07ad-403b-95fb-936c3060ac61",
                "type": "update",
                "payload": {"tag": "v1.0.0"},
            }
        )

        self.assertFalse(handled)
        self.assertFalse(os.path.exists(self.update_file))
        self.assertIsNone(remoteCommandProcess.read_pending_result())

    def test_reboot_result_is_persisted_before_reboot_request(self):
        with patch.object(remoteCommandProcess, "_request_reboot") as reboot:
            remoteCommandProcess.process_command_if_safe(
                {
                    "command_id": "d20dbcc0-c92b-4fbd-b97b-62f8d78600e1",
                    "type": "reboot",
                    "payload": {},
                }
            )

        reboot.assert_called_once_with()
        result = remoteCommandProcess.read_pending_result()
        self.assertEqual(result["status"], "completed")

    def test_update_and_reboot_results_are_both_persisted(self):
        commands = [
            {
                "command_id": "12dcd41c-210d-45e2-b63d-ab67b4b4ee8e",
                "type": "update",
                "payload": {"tag": "v1.6.0"},
            },
            {
                "command_id": "d20dbcc0-c92b-4fbd-b97b-62f8d78600e1",
                "type": "reboot",
                "payload": {},
            },
        ]

        with patch.object(remoteCommandProcess, "_request_reboot") as reboot:
            handled_count = remoteCommandProcess.process_commands_if_safe(commands)

        self.assertEqual(handled_count, 2)
        self.assertEqual(len(remoteCommandProcess.read_pending_results()), 2)
        reboot.assert_called_once_with()

    def test_close_app_is_persisted_and_stops_later_commands(self):
        commands = [
            {
                "command_id": "98a52da9-6627-4143-871a-1c83bbc0c72b",
                "type": "close_app",
                "payload": {},
            },
            {
                "command_id": "12dcd41c-210d-45e2-b63d-ab67b4b4ee8e",
                "type": "update",
                "payload": {"tag": "v1.6.0"},
            },
        ]

        handled_count = remoteCommandProcess.process_commands_if_safe(commands)

        self.assertEqual(handled_count, 1)
        self.assertEqual(len(remoteCommandProcess.read_pending_results()), 1)
        self.assertFalse(os.path.exists(self.update_file))
        self.assertIn(
            "Encerramento",
            remoteCommandProcess.read_pending_result()["message"],
        )

    def test_legacy_single_result_file_is_still_read(self):
        with open(self.result_file, "w", encoding="utf-8") as file:
            file.write(
                '{"command_id":"12dcd41c-210d-45e2-b63d-ab67b4b4ee8e",'
                '"status":"completed","message":"ok"}'
            )

        results = remoteCommandProcess.read_pending_results()

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["message"], "ok")

    def test_invalid_update_tag_is_recorded_as_failure(self):
        remoteCommandProcess.process_command_if_safe(
            {
                "command_id": "306e6ce7-c36a-4df9-99da-a283c19e22b4",
                "type": "update",
                "payload": {"tag": "invalid tag"},
            }
        )

        self.assertEqual(remoteCommandProcess.read_pending_result()["status"], "failed")
        self.assertFalse(os.path.exists(self.update_file))

    def test_non_finite_price_is_recorded_as_failure(self):
        remoteCommandProcess.process_command_if_safe(
            {
                "command_id": "60ed5548-165c-4db3-b7b5-56d71371124e",
                "type": "settings",
                "payload": {
                    "system_name": "Coffea Teste",
                    "prices": [float("nan")],
                    "payment_methods": {
                        "Débito": True,
                        "Crédito": True,
                        "Voucher": True,
                        "QR Code (Pix)": True,
                    },
                    "moderninha_mac": "AA:BB:CC:DD:EE:FF",
                    "pulse_value": 0.25,
                    "pulse_duration_ms": 100,
                    "pulse_interval_ms": 400,
                    "hello_screen_enabled": True,
                },
            }
        )

        self.assertEqual(remoteCommandProcess.read_pending_result()["status"], "failed")
        self.assertFalse(os.path.exists(self.prices_file))

    def test_invalid_mac_does_not_partially_apply_settings(self):
        remoteCommandProcess.process_command_if_safe(
            {
                "command_id": "8d684e09-94b3-41ce-80de-046716c39630",
                "type": "settings",
                "payload": {
                    "system_name": "Coffea Teste",
                    "prices": [2.5],
                    "payment_methods": {
                        "Débito": True,
                        "Crédito": True,
                        "Voucher": True,
                        "QR Code (Pix)": True,
                    },
                    "moderninha_mac": "invalid",
                    "pulse_value": 0.25,
                    "pulse_duration_ms": 100,
                    "pulse_interval_ms": 400,
                    "hello_screen_enabled": True,
                },
            }
        )

        self.assertEqual(remoteCommandProcess.read_pending_result()["status"], "failed")
        self.assertFalse(os.path.exists(self.name_file))


if __name__ == "__main__":
    unittest.main()

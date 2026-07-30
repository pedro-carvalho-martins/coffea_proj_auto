import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


PYTHON_DIR = Path(__file__).resolve().parents[1] / "python"
sys.path.insert(0, str(PYTHON_DIR))

import factoryResetProcess
import shared_resource


class FactoryResetProcessTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.base = self.temporary_directory.name
        self.settings_directory = os.path.join(self.base, "settings")
        self.logs_directory = os.path.join(self.base, "log_files")
        os.makedirs(self.settings_directory)
        os.makedirs(self.logs_directory)

        with open(
            os.path.join(self.settings_directory, "systemId.txt"),
            "w",
            encoding="utf-8",
        ) as file:
            file.write("old-id")
        with open(
            os.path.join(self.settings_directory, "serverPairingToken.txt"),
            "w",
            encoding="utf-8",
        ) as file:
            file.write("old-token")
        with open(
            os.path.join(self.logs_directory, "events.csv"),
            "w",
            encoding="utf-8",
        ) as file:
            file.write("preserve me")

        self.patchers = [
            patch.object(factoryResetProcess, "SETTINGS_DIR", self.settings_directory),
            patch.object(
                factoryResetProcess,
                "EXPECTED_SETTINGS_DIR",
                self.settings_directory,
            ),
        ]
        for patcher in self.patchers:
            patcher.start()
        shared_resource.factory_reset_in_progress.clear()

    def tearDown(self):
        shared_resource.factory_reset_in_progress.clear()
        for patcher in reversed(self.patchers):
            patcher.stop()
        self.temporary_directory.cleanup()

    def test_reset_clears_only_settings_and_requests_reboot(self):
        with patch.object(factoryResetProcess, "_request_reboot") as reboot:
            factoryResetProcess.reset_settings_and_reboot()

        self.assertTrue(shared_resource.factory_reset_in_progress.is_set())
        self.assertTrue(os.path.isdir(self.settings_directory))
        self.assertEqual(os.listdir(self.settings_directory), [])
        self.assertTrue(os.path.exists(os.path.join(self.logs_directory, "events.csv")))
        reboot.assert_called_once_with()

    def test_reset_refuses_an_unexpected_directory(self):
        with patch.object(
            factoryResetProcess,
            "EXPECTED_SETTINGS_DIR",
            os.path.join(self.base, "different-settings"),
        ):
            with self.assertRaises(RuntimeError):
                factoryResetProcess._reset_settings_directory()

        self.assertTrue(os.path.exists(os.path.join(self.settings_directory, "systemId.txt")))


if __name__ == "__main__":
    unittest.main()

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


PYTHON_DIR = Path(__file__).resolve().parents[1] / "python"
sys.path.insert(0, str(PYTHON_DIR))

import rwCommunicationType


class CommunicationTypeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.temp.name, "communicationType.txt")
        self.path_patch = patch.object(
            rwCommunicationType,
            "COMMUNICATION_TYPE_FILE",
            self.path,
        )
        self.path_patch.start()

    def tearDown(self):
        self.path_patch.stop()
        self.temp.cleanup()

    def test_missing_setting_defaults_to_pulse(self):
        self.assertEqual(
            rwCommunicationType.readCommunicationType(),
            rwCommunicationType.PULSE,
        )
        self.assertTrue(os.path.isfile(self.path))

    def test_mdb_round_trip_and_invalid_value(self):
        rwCommunicationType.writeCommunicationType("MDB")
        self.assertTrue(rwCommunicationType.isMdbEnabled())
        with self.assertRaises(ValueError):
            rwCommunicationType.writeCommunicationType("unsupported")


if __name__ == "__main__":
    unittest.main()

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


PYTHON_DIR = Path(__file__).resolve().parents[1] / "python"
sys.path.insert(0, str(PYTHON_DIR))

import rwCommunicationType


class CommunicationTypeTests(unittest.TestCase):
    def test_missing_setting_defaults_to_pulse(self):
        with tempfile.TemporaryDirectory() as temp:
            path = str(Path(temp) / "communicationType.txt")
            with patch.object(rwCommunicationType, "COMMUNICATION_TYPE_FILE", path):
                self.assertEqual(rwCommunicationType.readCommunicationType(), "pulso")
                self.assertEqual(Path(path).read_text(encoding="utf-8"), "pulso\n")

    def test_mdb_round_trip_and_invalid_value(self):
        with tempfile.TemporaryDirectory() as temp:
            path = str(Path(temp) / "communicationType.txt")
            with patch.object(rwCommunicationType, "COMMUNICATION_TYPE_FILE", path):
                rwCommunicationType.writeCommunicationType("MDB")
                self.assertTrue(rwCommunicationType.isMdbEnabled())
                with self.assertRaises(ValueError):
                    rwCommunicationType.writeCommunicationType("wifi")


if __name__ == "__main__":
    unittest.main()

import os
import sys
import unittest


PYTHON_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "python"))
if PYTHON_DIR not in sys.path:
    sys.path.insert(0, PYTHON_DIR)

from connectionAvailability import evaluate_connection_outcome


class ConnectionAvailabilityTests(unittest.TestCase):
    def test_pix_failure_with_cards_disabled_retries(self):
        settings = self._settings(cards="disabled", pix="enabled")
        self.assertEqual(-1, evaluate_connection_outcome(settings, "disabled", "error"))

    def test_moderninha_failure_with_pix_disabled_retries(self):
        settings = self._settings(cards="enabled", pix="disabled")
        self.assertEqual(-1, evaluate_connection_outcome(settings, "error", "disabled"))

    def test_all_methods_disabled_retries(self):
        settings = self._settings(cards="disabled", pix="disabled")
        self.assertEqual(-1, evaluate_connection_outcome(settings, "disabled", "disabled"))

    def test_pix_available_with_moderninha_failure_continues_partially(self):
        settings = self._settings(cards="enabled", pix="enabled")
        self.assertEqual(1, evaluate_connection_outcome(settings, "error", "check"))

    def test_moderninha_available_with_pix_failure_continues_partially(self):
        settings = self._settings(cards="enabled", pix="enabled")
        self.assertEqual(1, evaluate_connection_outcome(settings, "check", "error"))

    def test_all_enabled_connections_available_succeeds(self):
        settings = self._settings(cards="enabled", pix="enabled")
        self.assertEqual(0, evaluate_connection_outcome(settings, "check", "check"))

    def test_available_cards_with_pix_disabled_succeeds(self):
        settings = self._settings(cards="enabled", pix="disabled")
        self.assertEqual(0, evaluate_connection_outcome(settings, "check", "disabled"))

    def test_available_pix_with_cards_disabled_succeeds(self):
        settings = self._settings(cards="disabled", pix="enabled")
        self.assertEqual(0, evaluate_connection_outcome(settings, "disabled", "check"))

    @staticmethod
    def _settings(cards, pix):
        return {
            "Débito": cards,
            "Crédito": cards,
            "Voucher": cards,
            "QR Code (Pix)": pix,
        }


if __name__ == "__main__":
    unittest.main()

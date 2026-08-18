import sys
import unittest
from pathlib import Path


PYTHON_DIR = Path(__file__).resolve().parents[1] / "python"
sys.path.insert(0, str(PYTHON_DIR))

from tkinter_frames.ui_components import format_brl
from tkinter_frames.ui_theme import FONT_AMOUNT, SCREEN_HEIGHT, SCREEN_WIDTH


class TkUiComponentTests(unittest.TestCase):
    def test_payment_amount_uses_brazilian_currency_format(self):
        self.assertEqual(format_brl(10), "R$ 10,00")
        self.assertEqual(format_brl(2.5), "R$ 2,50")

    def test_theme_keeps_terminal_dimensions_and_large_amount(self):
        self.assertEqual((SCREEN_WIDTH, SCREEN_HEIGHT), (320, 480))
        self.assertGreaterEqual(FONT_AMOUNT[1], 30)


if __name__ == "__main__":
    unittest.main()

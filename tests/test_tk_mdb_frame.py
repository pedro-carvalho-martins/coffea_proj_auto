import sys
import unittest
from pathlib import Path
from unittest.mock import patch


PYTHON_DIR = Path(__file__).resolve().parents[1] / "python"
sys.path.insert(0, str(PYTHON_DIR))

import tkinter_frames.tkMdbFrame as tkMdbFrame
import tkinter_frames.ui_components as ui_components
from tkinter_frames.ui_theme import COLORS


class FakeFrame:
    def __init__(self, *args, **kwargs):
        self.background = kwargs.get("bg", "platform-default")

    def configure(self, **kwargs):
        self.background = kwargs.get("bg", self.background)

    def cget(self, name):
        if name != "background":
            raise KeyError(name)
        return self.background

    def rowconfigure(self, *args, **kwargs):
        pass

    def columnconfigure(self, *args, **kwargs):
        pass

    def grid(self, *args, **kwargs):
        pass


class FakeLabel:
    def __init__(self, *args, **kwargs):
        self.options = kwargs

    def grid(self, *args, **kwargs):
        pass

    def configure(self, **kwargs):
        self.options.update(kwargs)


class MdbFrameTests(unittest.TestCase):
    def test_waiting_frame_uses_neutral_theme_background(self):
        with patch.object(ui_components.tk, "Frame", FakeFrame), patch.object(
            ui_components.tk,
            "Label",
            FakeLabel,
        ):
            frame = tkMdbFrame.createWaitingFrame(object())

        self.assertEqual(frame.background, COLORS["background"])
        self.assertEqual(
            frame.mdb_status_label.options["bg"],
            COLORS["background"],
        )

    def test_status_frames_keep_explicit_colors(self):
        with patch.object(ui_components.tk, "Frame", FakeFrame), patch.object(
            ui_components.tk,
            "Label",
            FakeLabel,
        ):
            frame = tkMdbFrame.createFailureFrame(object())

        self.assertEqual(frame.background, COLORS["danger"])
        self.assertEqual(
            frame.mdb_status_label.options["bg"],
            COLORS["danger"],
        )


if __name__ == "__main__":
    unittest.main()

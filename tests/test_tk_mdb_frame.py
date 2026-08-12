import sys
import unittest
from pathlib import Path
from unittest.mock import patch


PYTHON_DIR = Path(__file__).resolve().parents[1] / "python"
sys.path.insert(0, str(PYTHON_DIR))

import tkinter_frames.tkMdbFrame as tkMdbFrame


class FakeFrame:
    def __init__(self, *args, **kwargs):
        self.background = "platform-default"

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


class FakeLabel:
    def __init__(self, *args, **kwargs):
        self.options = kwargs

    def grid(self, *args, **kwargs):
        pass


class MdbFrameTests(unittest.TestCase):
    def test_waiting_frame_uses_tk_platform_background(self):
        with patch.object(tkMdbFrame.tk, "Frame", FakeFrame), patch.object(
            tkMdbFrame.tk,
            "Label",
            FakeLabel,
        ):
            frame = tkMdbFrame.createWaitingFrame(object())

        self.assertEqual(frame.background, "platform-default")
        self.assertEqual(
            frame.mdb_status_label.options["bg"],
            "platform-default",
        )

    def test_status_frames_keep_explicit_colors(self):
        with patch.object(tkMdbFrame.tk, "Frame", FakeFrame), patch.object(
            tkMdbFrame.tk,
            "Label",
            FakeLabel,
        ):
            frame = tkMdbFrame.createFailureFrame(object())

        self.assertEqual(frame.background, "#871313")
        self.assertEqual(frame.mdb_status_label.options["bg"], "#871313")


if __name__ == "__main__":
    unittest.main()

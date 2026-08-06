import os
import sys
import unittest
from types import ModuleType, SimpleNamespace
from unittest.mock import MagicMock, patch


PYTHON_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "python"))
if PYTHON_DIR not in sys.path:
    sys.path.insert(0, PYTHON_DIR)

frame_module = SimpleNamespace(
    status_conn_moderninha=None,
    status_conn_servidor_pix=None,
)
tkinter_frames_package = ModuleType("tkinter_frames")
tkinter_frames_package.__path__ = []
tkinter_frames_package.tkConnCheckFrame = frame_module
mock_modules = {
    "rwMACAddress": MagicMock(),
    "rwPaymentMethodsList": MagicMock(),
    "rwConnCheckFile": MagicMock(),
    "rwLogCSV": MagicMock(),
    "serverPairingProcess": MagicMock(),
    "tkinter_frames": tkinter_frames_package,
    "tkinter_frames.tkConnCheckFrame": frame_module,
}
with patch.dict(sys.modules, mock_modules):
    import connCheckProcess


class ConnectionCheckProcessTests(unittest.TestCase):
    def test_combined_check_runs_moderninha_then_server_and_writes_results(self):
        call_order = []
        initial_settings = {"QR Code (Pix)": "enabled"}
        reported_settings = {"QR Code (Pix)": "disabled"}
        connCheckProcess.rwPaymentMethodsList.readListSettings.side_effect = [
            initial_settings,
            reported_settings,
        ]

        with patch.object(
            connCheckProcess,
            "checkConnModerninha",
            side_effect=lambda settings: call_order.append("moderninha") or "check",
        ), patch.object(
            connCheckProcess,
            "checkConnServer",
            side_effect=lambda: call_order.append("server") or "pending",
        ):
            result = connCheckProcess._run_connection_checks()

        self.assertEqual(call_order, ["moderninha", "server"])
        self.assertEqual(result, (reported_settings, "check", "pending"))
        self.assertEqual(frame_module.status_conn_moderninha, "check")
        self.assertEqual(frame_module.status_conn_servidor_pix, "pending")
        connCheckProcess.rwConnCheckFile.writeConnCheckStatus.assert_called_once_with(
            {
                "Moderninha": "check",
                "QR Code (Pix)": "pending",
            }
        )


if __name__ == "__main__":
    unittest.main()

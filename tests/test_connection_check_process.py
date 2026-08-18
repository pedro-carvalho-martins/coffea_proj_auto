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
    import shared_resource


class ConnectionCheckProcessTests(unittest.TestCase):
    def setUp(self):
        shared_resource.customer_interaction_active.clear()
        shared_resource.set_moderninha_connection_status("not_checked")
        connCheckProcess.rwConnCheckFile.reset_mock()
        connCheckProcess.rwPaymentMethodsList.reset_mock()

    def tearDown(self):
        shared_resource.customer_interaction_active.clear()

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
        self.assertEqual(
            shared_resource.get_moderninha_connection_status(),
            "connected",
        )
        connCheckProcess.rwConnCheckFile.writeConnCheckStatus.assert_called_once_with(
            {
                "Moderninha": "check",
                "QR Code (Pix)": "pending",
            }
        )

    def test_background_check_does_not_start_during_customer_interaction(self):
        shared_resource.customer_interaction_active.set()

        with patch.object(connCheckProcess, "checkConnModerninha") as moderninha, patch.object(
            connCheckProcess, "checkConnServer"
        ) as server:
            result = connCheckProcess.launchBackgroundConnCheckProcess(0, 0)

        self.assertIsNone(result)
        moderninha.assert_not_called()
        server.assert_not_called()
        connCheckProcess.rwConnCheckFile.writeConnCheckStatus.assert_not_called()

    def test_background_check_stops_before_server_when_interaction_starts(self):
        connCheckProcess.rwPaymentMethodsList.readListSettings.return_value = {
            "QR Code (Pix)": "enabled"
        }

        def finish_moderninha_check(settings):
            shared_resource.customer_interaction_active.set()
            return "check"

        with patch.object(
            connCheckProcess,
            "checkConnModerninha",
            side_effect=finish_moderninha_check,
        ), patch.object(connCheckProcess, "checkConnServer") as server:
            result = connCheckProcess.launchBackgroundConnCheckProcess(0, 0)

        self.assertIsNone(result)
        server.assert_not_called()
        self.assertEqual(
            shared_resource.get_moderninha_connection_status(),
            "connected",
        )
        connCheckProcess.rwConnCheckFile.writeConnCheckStatus.assert_not_called()


if __name__ == "__main__":
    unittest.main()

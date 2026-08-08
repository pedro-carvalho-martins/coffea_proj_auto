import sys
import unittest
from pathlib import Path


PYTHON_DIR = Path(__file__).resolve().parents[1] / "python"
sys.path.insert(0, str(PYTHON_DIR))

from mdb_protocol import (
    LineFramer,
    MessageKind,
    ProtocolError,
    command_decision,
    parse_line,
)


class MdbProtocolTests(unittest.TestCase):
    def test_framer_handles_partial_and_multiple_lines(self):
        framer = LineFramer()
        self.assertEqual(framer.feed(b"MDB VEND_"), [])
        lines = framer.feed(
            b"REQUEST boot=abc session=2 vend=3 price=450 item=7\r\n"
            b"ACK command=APPROVE status=queued\n"
        )
        self.assertEqual(len(lines), 2)
        event = parse_line(lines[0])
        self.assertEqual(event.kind, MessageKind.VEND_REQUEST)
        self.assertEqual(event.integer("price"), 450)
        self.assertEqual(parse_line(lines[1]).kind, MessageKind.ACK)

    def test_overlong_line_is_rejected_and_buffer_is_reset(self):
        framer = LineFramer(max_line_bytes=5)
        self.assertEqual(framer.feed(b"123456\nOK\n"), ["OK"])
        self.assertEqual(framer.pop_errors(), ["Serial line exceeds limit"])

    def test_vend_request_requires_correlation_fields(self):
        with self.assertRaises(ProtocolError):
            parse_line("MDB VEND_REQUEST price=100 item=1")

    def test_decision_contains_boot_and_vend_id(self):
        self.assertEqual(command_decision(True, "00ab12cd", 8), "APPROVE 00ab12cd 8")


if __name__ == "__main__":
    unittest.main()

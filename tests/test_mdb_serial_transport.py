import sys
import tempfile
import unittest
from pathlib import Path


PYTHON_DIR = Path(__file__).resolve().parents[1] / "python"
sys.path.insert(0, str(PYTHON_DIR))

from mdb_serial_transport import MdbSerialTransport


class FakeSerial:
    def __init__(self, transport):
        self.transport = transport
        self.writes = []
        self.reads = [
            b"BAD LINE\nMDB VEND_REQUEST boot=abc session=1 ",
            b"vend=2 price=300 item=4\n",
        ]

    def write(self, data):
        self.writes.append(data)

    def flush(self):
        pass

    def read(self, size):
        if self.reads:
            return self.reads.pop(0)
        self.transport._stop.set()
        return b""


class MdbSerialTransportTests(unittest.TestCase):
    def test_fake_serial_transcript_and_command(self):
        messages = []
        states = []
        with tempfile.TemporaryDirectory() as temp:
            transport = MdbSerialTransport(
                messages.append,
                lambda state, detail: states.append((state, detail)),
                lock_path=str(Path(temp) / "owner.lock"),
            )
            port = FakeSerial(transport)
            transport.send("STATUS")
            transport._communicate(port)

        self.assertEqual(port.writes, [b"STATUS\n"])
        self.assertEqual(messages[0].integer("price"), 300)
        self.assertEqual(states[0][0], "protocol_error")


if __name__ == "__main__":
    unittest.main()

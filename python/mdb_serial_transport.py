"""The process-wide, exclusive owner of the Pi UART connected to the ESP32."""

import os
import queue
import threading
import time

from app_paths import MDB_OWNER_LOCK_FILE, ensure_parent_dir
from mdb_protocol import LineFramer, ProtocolError, parse_line


class SerialOwnershipError(RuntimeError):
    pass


class MdbSerialTransport:
    def __init__(
        self,
        on_message,
        on_state=None,
        device="/dev/serial0",
        baudrate=115200,
        serial_factory=None,
        reconnect_seconds=2,
        lock_path=MDB_OWNER_LOCK_FILE,
    ):
        self.on_message = on_message
        self.on_state = on_state or (lambda *_: None)
        self.device = device
        self.baudrate = int(baudrate)
        self.serial_factory = serial_factory
        self.reconnect_seconds = float(reconnect_seconds)
        self.lock_path = lock_path
        self._commands = queue.Queue()
        self._stop = threading.Event()
        self._thread = None
        self._lock_file = None

    @property
    def running(self):
        return self._thread is not None and self._thread.is_alive()

    def start(self):
        if self.running:
            return
        self._acquire_lock()
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, name="mdb-serial0", daemon=True)
        self._thread.start()

    def stop(self):
        self._stop.set()
        if self._thread and self._thread is not threading.current_thread():
            self._thread.join(timeout=3)
        self._thread = None
        self._release_lock()

    def send(self, command):
        normalized = str(command).strip()
        if not normalized or "\n" in normalized or "\r" in normalized:
            raise ValueError("Command must be one non-empty line")
        self._commands.put(normalized)

    def _acquire_lock(self):
        ensure_parent_dir(self.lock_path)
        self._lock_file = open(self.lock_path, "a+", encoding="ascii")
        try:
            import fcntl
            fcntl.flock(self._lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except ImportError:
            # The production target is Linux. Windows tests still exercise that
            # only one owner exists inside this process.
            pass
        except OSError as exc:
            self._lock_file.close()
            self._lock_file = None
            raise SerialOwnershipError(self.device + " is already owned") from exc
        self._lock_file.seek(0)
        self._lock_file.truncate()
        self._lock_file.write(str(os.getpid()))
        self._lock_file.flush()

    def _release_lock(self):
        if self._lock_file is None:
            return
        try:
            try:
                import fcntl
                fcntl.flock(self._lock_file.fileno(), fcntl.LOCK_UN)
            except ImportError:
                pass
        finally:
            self._lock_file.close()
            self._lock_file = None

    def _open_serial(self):
        if self.serial_factory is not None:
            return self.serial_factory(self.device, self.baudrate)
        try:
            import serial
        except ImportError as exc:
            raise RuntimeError("pyserial is required for MDB mode") from exc
        return serial.Serial(
            self.device,
            self.baudrate,
            timeout=0.1,
            write_timeout=0.5,
            exclusive=True,
        )

    def _run(self):
        try:
            while not self._stop.is_set():
                port = None
                try:
                    port = self._open_serial()
                    self.on_state("connected", self.device)
                    self._communicate(port)
                except Exception as exc:
                    self.on_state("disconnected", str(exc))
                finally:
                    if port is not None:
                        try:
                            port.close()
                        except Exception:
                            pass
                self._stop.wait(self.reconnect_seconds)
        finally:
            self._release_lock()

    def _communicate(self, port):
        framer = LineFramer()
        while not self._stop.is_set():
            while True:
                try:
                    command = self._commands.get_nowait()
                except queue.Empty:
                    break
                port.write((command + "\n").encode("ascii"))
                if hasattr(port, "flush"):
                    port.flush()
            chunk = port.read(128)
            if not chunk:
                continue
            lines = framer.feed(chunk)
            for error in framer.pop_errors():
                self.on_state("protocol_error", error)
            for line in lines:
                try:
                    self.on_message(parse_line(line))
                except ProtocolError as exc:
                    self.on_state("protocol_error", str(exc))

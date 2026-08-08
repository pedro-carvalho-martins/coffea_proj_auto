"""Typed adapter for the line-oriented Raspberry Pi/ESP32 MDB protocol."""

from dataclasses import dataclass
from enum import Enum


MAX_LINE_BYTES = 256


class ProtocolError(ValueError):
    pass


class MessageKind(Enum):
    BOOT = "BOOT"
    READER_ENABLE = "READER_ENABLE"
    SESSION_BEGIN = "SESSION_BEGIN"
    VEND_REQUEST = "VEND_REQUEST"
    VEND_CANCEL = "VEND_CANCEL"
    VEND_SUCCESS = "VEND_SUCCESS"
    VEND_FAILURE = "VEND_FAILURE"
    SESSION_COMPLETE = "SESSION_COMPLETE"
    RESET = "RESET"
    ACK = "ACK"
    STATUS = "STATUS"
    ERROR = "ERROR"
    LOG = "LOG"


@dataclass(frozen=True)
class BridgeMessage:
    kind: MessageKind
    raw: str
    fields: dict

    def text(self, name, default=None):
        return self.fields.get(name, default)

    def integer(self, name, required=False, default=None):
        value = self.fields.get(name)
        if value is None:
            if required:
                raise ProtocolError("Missing integer field: " + name)
            return default
        try:
            return int(value, 10)
        except ValueError as exc:
            raise ProtocolError("Invalid integer field: " + name) from exc


_MDB_EVENTS = {
    "READER_ENABLE": MessageKind.READER_ENABLE,
    "SESSION_BEGIN": MessageKind.SESSION_BEGIN,
    "VEND_REQUEST": MessageKind.VEND_REQUEST,
    "VEND_CANCEL": MessageKind.VEND_CANCEL,
    "VEND_SUCCESS": MessageKind.VEND_SUCCESS,
    "VEND_FAILURE": MessageKind.VEND_FAILURE,
    "SESSION_COMPLETE": MessageKind.SESSION_COMPLETE,
    "RESET": MessageKind.RESET,
}


def _parse_fields(tokens):
    fields = {}
    for token in tokens:
        if "=" not in token:
            raise ProtocolError("Expected key=value token: " + token)
        name, value = token.split("=", 1)
        if not name or not value or name in fields:
            raise ProtocolError("Invalid protocol field: " + token)
        fields[name] = value
    return fields


def parse_line(line):
    raw = str(line).strip()
    if not raw:
        raise ProtocolError("Empty protocol line")
    tokens = raw.split()

    if tokens[0] == "MDB":
        if len(tokens) < 2 or tokens[1] not in _MDB_EVENTS:
            raise ProtocolError("Unknown MDB event")
        kind = _MDB_EVENTS[tokens[1]]
        fields = _parse_fields(tokens[2:])
    else:
        try:
            kind = MessageKind(tokens[0])
        except ValueError as exc:
            raise ProtocolError("Unknown protocol message") from exc
        fields = _parse_fields(tokens[1:])

    message = BridgeMessage(kind=kind, raw=raw, fields=fields)
    if kind == MessageKind.BOOT:
        if message.integer("protocol", required=True) != 2:
            raise ProtocolError("Unsupported bridge protocol version")
        if not message.text("boot"):
            raise ProtocolError("BOOT is missing boot id")
    elif kind in (
        MessageKind.VEND_REQUEST,
        MessageKind.VEND_CANCEL,
        MessageKind.VEND_SUCCESS,
        MessageKind.VEND_FAILURE,
    ):
        message.integer("session", required=True)
        message.integer("vend", required=True)
        if not message.text("boot"):
            raise ProtocolError("Vend event is missing boot id")
        if kind == MessageKind.VEND_REQUEST:
            message.integer("price", required=True)
            message.integer("item", required=True)
    elif kind == MessageKind.SESSION_BEGIN:
        message.integer("session", required=True)
        if not message.text("boot"):
            raise ProtocolError("SESSION_BEGIN is missing boot id")
    return message


class LineFramer:
    """Accumulate arbitrary UART chunks and return complete ASCII lines."""

    def __init__(self, max_line_bytes=MAX_LINE_BYTES):
        self.max_line_bytes = int(max_line_bytes)
        self._buffer = bytearray()
        self._discarding = False
        self._errors = []

    def pop_errors(self):
        errors = self._errors
        self._errors = []
        return errors

    def feed(self, chunk):
        if not isinstance(chunk, (bytes, bytearray)):
            raise TypeError("Serial data must be bytes")
        lines = []
        for byte in chunk:
            if byte == 10:
                if self._discarding:
                    self._discarding = False
                    self._buffer.clear()
                    continue
                line = bytes(self._buffer).rstrip(b"\r")
                self._buffer.clear()
                if line:
                    try:
                        lines.append(line.decode("ascii"))
                    except UnicodeDecodeError:
                        self._errors.append("Non-ASCII serial data")
                continue
            if self._discarding:
                continue
            if len(self._buffer) >= self.max_line_bytes:
                self._buffer.clear()
                self._discarding = True
                self._errors.append("Serial line exceeds limit")
                continue
            self._buffer.append(byte)
        return lines


def command_status():
    return "STATUS"


def command_session(funds=65535):
    value = int(funds)
    if not 0 <= value <= 65535:
        raise ValueError("MDB funds must fit in 16 bits")
    return "SESSION " + str(value)


def command_decision(approved, boot_id, vend_id):
    if not boot_id:
        raise ValueError("boot_id is required")
    vend = int(vend_id)
    if vend <= 0:
        raise ValueError("vend_id must be positive")
    return ("APPROVE" if approved else "DENY") + " " + str(boot_id) + " " + str(vend)


def command_cancel(boot_id=None, session_id=None):
    if boot_id is None and session_id is None:
        return "CANCEL"
    if not boot_id or session_id is None:
        raise ValueError("Correlated CANCEL needs boot and session ids")
    return "CANCEL " + str(boot_id) + " " + str(int(session_id))

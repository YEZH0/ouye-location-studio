"""Simulated-device (mock) tests for the engine.

A scripted in-process "phone" peer drives a full iAP2 session: handshake,
identification, authentication, location subscription and stop. No real device,
USB stack, or credential is involved. These tests are reported separately from
unit tests and real-device acceptance.
"""

import asyncio
import struct

from ouye_location_studio.core.engine import LocationEngine
from ouye_location_studio.core.wire import ACK, SYN, Message, Packet, parameter
from ouye_location_studio.platforms.base import DeviceStream, PlatformAdapter
from ouye_location_studio.state import (
    EVENT_AUTHENTICATION_SUCCEEDED,
    EVENT_FINISHED,
    EVENT_IDENTIFICATION_ACCEPTED,
    EVENT_LOCATION_LINK_ACKNOWLEDGED,
    EVENT_LOCATION_REQUESTED,
    EVENT_LOCATION_STOPPED,
    EVENT_RESTORE_REQUIRED,
    EngineEvent,
    EngineListener,
)


class MockStream(DeviceStream):
    """Bidirectional stream between engine and scripted phone peer."""

    def __init__(self):
        self.to_engine: asyncio.Queue = asyncio.Queue()     # phone -> engine
        self.from_engine: asyncio.Queue = asyncio.Queue()   # engine -> phone
        self._rbuf = bytearray()
        self.sent_log = bytearray()                          # every byte the engine sent
        self.closed = False

    # Engine side ----------------------------------------------------------
    async def recvall(self, size: int) -> bytes:
        while len(self._rbuf) < size:
            data = await self.to_engine.get()
            if data == b"":
                raise EOFError("stream closed")
            self._rbuf += data
        out = bytes(self._rbuf[:size])
        del self._rbuf[:size]
        return out

    async def sendall(self, data: bytes) -> None:
        self.sent_log += data
        await self.from_engine.put(bytes(data))

    async def close(self) -> None:
        self.closed = True
        await self.to_engine.put(b"")

    # Phone (peer) side ----------------------------------------------------
    async def peer_write(self, packet: Packet) -> None:
        await self.to_engine.put(packet.encode())

    async def peer_read(self) -> Packet:
        data = await self.from_engine.get()
        if not data:
            raise EOFError("stream closed")
        return Packet.decode(data)


async def _ack_loop(stream: MockStream):
    """Acknowledge every data packet the engine sends; ignore empty ACKs."""
    while True:
        try:
            packet = await stream.peer_read()
        except EOFError:
            return
        if packet.flags & ACK and packet.payload:
            await stream.peer_write(Packet(ACK, 0, packet.sequence, 1))


async def _drive_phone(stream: MockStream, script: list[Message]):
    """Perform the handshake, feed the scripted messages, then finish."""
    syn = await stream.peer_read()
    assert syn.flags & SYN
    offer = struct.pack(">BBHHHBB", 1, 1, 4096, 2000, 22, 5, 1) + bytes([1, 0, 2])
    await stream.peer_write(Packet(0xC0, 0x01, syn.sequence, 0, offer))

    ack_task = asyncio.create_task(_ack_loop(stream))
    try:
        peer_seq = 0x01
        for message in script:
            peer_seq = (peer_seq + 1) & 255
            await stream.peer_write(Packet(ACK, peer_seq, 0, 1, message.encode()))
            await asyncio.sleep(0.03)
        await asyncio.sleep(0.25)  # let trailing location sends be ACKed
    finally:
        ack_task.cancel()
        try:
            await ack_task
        except asyncio.CancelledError:
            pass


class _FakeAuth:
    async def certificate(self):
        return Message(0xAA01, parameter(0, b"fake-certificate"))

    async def sign(self, challenge):
        assert len(challenge) == 32
        return Message(0xAA03, parameter(0, b"fake-signature-32-bytes-long!!"))

    async def close(self):
        pass


class _Adapter(PlatformAdapter):
    transport = "usb"

    def __init__(self, stream):
        self._stream = stream

    def list_devices(self):
        return [{"label": "iPhone (mock)"}]

    async def open(self, emit=None):
        return self._stream

    async def close(self):
        return None


class _Collector(EngineListener):
    def __init__(self):
        self.events: list[EngineEvent] = []

    def on_event(self, event: EngineEvent):
        self.events.append(event)


def _names(events):
    return [e.name for e in events]


async def _run_engine(stream, *, latitude=31.2304, longitude=121.4737,
                      duration=5.0, interval=1.0, auth=_FakeAuth(), stop_after=None):
    collector = _Collector()
    engine = LocationEngine(_Adapter(stream), auth_provider=auth, listener=collector)
    task = asyncio.create_task(
        engine.run_session(latitude=latitude, longitude=longitude,
                           duration=duration, interval=interval)
    )
    if stop_after is not None:
        await asyncio.sleep(stop_after)
        engine.request_stop()
    await task
    return collector


async def test_full_session_event_sequence():
    stream = MockStream()
    script = [
        Message(0x1D00),
        Message(0x1D02),
        Message(0xAA00),
        Message(0xAA02, parameter(0, b"\x00" * 32)),
        Message(0xAA05),
        Message(0xFFFA, parameter(1) + parameter(2)),
        Message(0xFFFC),
    ]
    phone = asyncio.create_task(_drive_phone(stream, script))
    collector = await _run_engine(stream, duration=8.0)
    await phone

    names = _names(collector.events)
    assert EVENT_IDENTIFICATION_ACCEPTED in names
    assert EVENT_AUTHENTICATION_SUCCEEDED in names
    assert EVENT_LOCATION_REQUESTED in names
    assert EVENT_LOCATION_LINK_ACKNOWLEDGED in names  # NMEA was sent and ACKed
    assert EVENT_LOCATION_STOPPED in names
    assert EVENT_RESTORE_REQUIRED in names
    assert names[-1] == EVENT_FINISHED

    finished = collector.events[-1]
    assert finished.data["identified"] is True
    assert finished.data["authenticated"] is True
    assert finished.data["phone_location_verified"] is False  # never auto-claimed


async def test_nmea_sent_matches_target():
    stream = MockStream()
    script = [
        Message(0x1D00), Message(0x1D02), Message(0xAA00),
        Message(0xAA02, parameter(0, b"\x00" * 32)), Message(0xAA05),
        Message(0xFFFA, parameter(1) + parameter(2)),
    ]
    phone = asyncio.create_task(_drive_phone(stream, script))
    await _run_engine(stream, latitude=31.2304, longitude=121.4737, duration=3.0)
    await phone

    wire = bytes(stream.sent_log)
    assert b"\x40\x40" in wire  # control-message marker
    assert b"GPGGA," in wire
    assert b"GPRMC," in wire
    # Coordinate fragments (time-independent): 31.2304 -> "3113.8240", 121.4737 -> "12128.4220"
    assert b"3113.8240" in wire
    assert b"12128.4220" in wire


async def test_stop_is_requested_cleanly():
    stream = MockStream()
    script = [Message(0x1D00), Message(0x1D02), Message(0xAA00),
              Message(0xAA02, parameter(0, b"\x00" * 32)), Message(0xAA05),
              Message(0xFFFA, parameter(1) + parameter(2))]
    phone = asyncio.create_task(_drive_phone(stream, script))
    collector = await _run_engine(stream, duration=60.0, stop_after=1.0)
    await phone
    finished = collector.events[-1]
    assert finished.name == EVENT_FINISHED
    assert finished.data["stop_reason"] == "stopped"


async def test_missing_auth_material_is_reported():
    stream = MockStream()
    script = [Message(0x1D00), Message(0x1D02), Message(0xAA00)]
    phone = asyncio.create_task(_drive_phone(stream, script))
    collector = await _run_engine(stream, duration=5.0, auth=None)
    await phone
    names = _names(collector.events)
    assert "error" in names
    assert any("认证材料" in e.message for e in collector.events)

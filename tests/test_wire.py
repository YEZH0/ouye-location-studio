"""Unit tests for iAP2 framing."""

import pytest

from ouye_location_studio.core.wire import (
    ACK,
    SYN,
    Message,
    MessageBuffer,
    Packet,
    ProtocolError,
    parameter,
    parameters,
    text_parameter,
)


def test_synack_reference_vector():
    payload = bytes.fromhex("017fffff07d000161e03010002")
    packet = Packet(0xC0, 176, 71, 0, payload)
    assert packet.encode()[:9] == bytes.fromhex("ff5a0017c0b04700d9")
    assert Packet.decode(packet.encode()) == packet


@pytest.mark.parametrize("offset", [0, 3, 6, 8, 10, 13])
def test_corruption_is_rejected(offset):
    raw = bytearray(Packet(ACK, 2, 3, 1, b"hello").encode())
    raw[offset] ^= 1
    with pytest.raises(ProtocolError):
        Packet.decode(bytes(raw))


def test_control_messages_survive_arbitrary_fragmentation():
    expected = [Message(0x1D00), Message(0x1D01, b"abcdef"), Message(0xFFFC)]
    wire = b"".join(m.encode() for m in expected)
    for width in range(1, len(wire) + 1):
        buffer = MessageBuffer()
        collected = []
        for offset in range(0, len(wire), width):
            collected.extend(buffer.feed(wire[offset : offset + width]))
        assert collected == expected


def test_parameters_roundtrip():
    raw = parameter(0, b"abc") + parameter(3, b"\x01\x02") + text_parameter(12, "en")
    assert parameters(raw) == [(0, b"abc"), (3, b"\x01\x02"), (12, b"en\0")]


def test_invalid_marker_rejected():
    with pytest.raises(ProtocolError):
        MessageBuffer().feed(b"XX\x00\x06\x00\x01")


def test_undersized_message_rejected():
    with pytest.raises(ProtocolError):
        MessageBuffer().feed(b"@@\x00\x03\x00\x01")


def test_partial_message_buffered_until_complete():
    buffer = MessageBuffer()
    # Header declares size 10 (6 header + 4 body); first feed is only 8 bytes.
    assert buffer.feed(b"@@\x00\x0a\x00\x01ab") == []
    assert buffer.feed(b"cd") == [Message(0x0001, b"abcd")]

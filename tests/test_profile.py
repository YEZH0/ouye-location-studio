"""Unit tests for accessory identity and NMEA sentence generation."""

from datetime import UTC, datetime

import pytest

from ouye_location_studio.core.profile import (
    coordinate,
    identity,
    location_sentences,
    sentence,
)
from ouye_location_studio.core.wire import parameters


def test_coordinate_formatting():
    assert coordinate(40.7570095, True) == ("4045.4206", "N")
    assert coordinate(-73.9859724, False) == ("07359.1583", "W")
    assert coordinate(0.0, True) == ("0000.0000", "N")
    assert coordinate(-0.5, False) == ("00030.0000", "W")


def test_coordinate_out_of_range():
    with pytest.raises(ValueError):
        coordinate(91.0, True)
    with pytest.raises(ValueError):
        coordinate(-181.0, False)


def test_sentence_checksum():
    # XOR of "GPGGA,120000" is 0x79.
    assert sentence("GPGGA,120000") == "$GPGGA,120000*79\r\n"


def test_location_sentences_are_valid():
    when = datetime(2026, 1, 2, 3, 4, 5, tzinfo=UTC)
    result = location_sentences(31.2304, 121.4737, when)
    assert set(result) == {1, 2}
    assert result[1].startswith("$GPGGA,")
    assert result[2].startswith("$GPRMC,")
    for line in result.values():
        body, checksum = line[1:].split("*")
        value = 0
        for byte in body.encode("ascii"):
            value ^= byte
        assert f"{value:02X}" == checksum[:2]


def test_identity_declares_location_transport():
    message = identity("usb")
    assert message.identifier == 0x1D01
    field_ids = [i for i, _ in parameters(message.body)]
    assert 16 in field_ids  # USB transport group
    assert 22 in field_ids  # location group

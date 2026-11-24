"""Mac adapter contract tests. Fake lockdown connections do not prove adoption."""

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from pymobiledevice3 import lockdown, usbmux
from pymobiledevice3.exceptions import NoDeviceConnectedError

from ouye_location_studio.platforms.base import NoDeviceError, ServiceError, TrustRequiredError
from ouye_location_studio.platforms.macos import MacOSAdapter


@pytest.fixture
def usb(monkeypatch):
    connection = SimpleNamespace(
        close=AsyncMock(), sendall=AsyncMock(), recvall=AsyncMock(return_value=b"abc"),
    )
    phone = SimpleNamespace(
        paired=True, close=AsyncMock(),
        start_lockdown_service=AsyncMock(return_value=connection),
    )
    devices = AsyncMock(return_value=[
        SimpleNamespace(connection_type="USB", serial="private"),
        SimpleNamespace(connection_type="Network", serial="private"),
    ])
    connect = AsyncMock(return_value=phone)
    monkeypatch.setattr(usbmux, "list_devices", devices)
    monkeypatch.setattr(lockdown, "create_using_usbmux", connect)
    return SimpleNamespace(connection=connection, phone=phone, devices=devices, connect=connect)


async def test_usb_only_and_private_detection(usb):
    assert await MacOSAdapter().list_devices() == [{"label": "iPhone / iPad（USB 已连接）"}]


async def test_no_usb(usb):
    usb.devices.return_value = []
    with pytest.raises(NoDeviceError):
        await MacOSAdapter().open()
    usb.connect.assert_not_called()


async def test_disconnect_during_open(usb):
    usb.connect.side_effect = NoDeviceConnectedError()
    with pytest.raises(NoDeviceError):
        await MacOSAdapter().open()


async def test_trust_required_releases_lockdown(usb):
    usb.phone.paired = False
    with pytest.raises(TrustRequiredError):
        await MacOSAdapter().open()
    usb.phone.start_lockdown_service.assert_not_called()
    usb.phone.close.assert_awaited_once()


async def test_service_failure_releases_lockdown(usb):
    usb.phone.start_lockdown_service.side_effect = OSError("private backend details")
    with pytest.raises(ServiceError, match="无法打开"):
        await MacOSAdapter().open()
    usb.phone.close.assert_awaited_once()


async def test_cancellation_releases_lockdown(usb):
    usb.phone.start_lockdown_service.side_effect = asyncio.CancelledError
    with pytest.raises(asyncio.CancelledError):
        await MacOSAdapter().open()
    usb.phone.close.assert_awaited_once()


async def test_usb_stream_and_idempotent_cleanup(usb):
    adapter = MacOSAdapter()
    stream = await adapter.open()
    usb.connect.assert_awaited_once_with(connection_type="USB", autopair=False)
    usb.phone.start_lockdown_service.assert_awaited_once_with("com.apple.carkit.service")
    await stream.sendall(b"abc")
    usb.connection.sendall.assert_awaited_once_with(b"abc")
    assert await stream.recvall(3) == b"abc"
    usb.connection.recvall.side_effect = ConnectionResetError
    with pytest.raises(ConnectionResetError):
        await stream.recvall(3)
    await stream.close()
    await adapter.close()
    await adapter.close()
    usb.connection.close.assert_awaited_once()
    usb.phone.close.assert_awaited_once()

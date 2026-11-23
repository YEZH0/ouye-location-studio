"""Windows platform adapter: USB transport via pymobiledevice3 + Apple USB driver check.

Only imported on Windows. The Apple USB driver check uses the registry and does
not require an attached device. See docs/build.md for the install entry.
"""

from __future__ import annotations

import asyncio
import sys
from typing import Any, Callable

from .base import DeviceError, DeviceStream, NoDeviceError, PlatformAdapter, ServiceError, TrustRequiredError

# Official Apple support entry for the Apple Mobile Device USB driver (installed
# with iTunes or the Microsoft Store "Apple Devices" app). Verifiable, official URL.
APPLE_DRIVER_URL = "https://www.apple.com/itunes/"

# Registry service names for the Apple Mobile Device USB driver (64-bit / 32-bit).
_APPLE_USB_SERVICES = ("USBAAPL64", "USBAAPL")

try:
    import winreg  # type: ignore
except ImportError:  # pragma: no cover - non-Windows import guard
    winreg = None  # type: ignore


def has_apple_usb_driver() -> bool | None:
    """Return True if an Apple Mobile Device USB driver is installed.

    ``None`` means the check could not be completed (registry unreadable).
    """
    if winreg is None:  # pragma: no cover - non-Windows
        return None
    for service in _APPLE_USB_SERVICES:
        try:
            with winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                rf"SYSTEM\CurrentControlSet\Services\{service}",
            ):
                return True
        except FileNotFoundError:
            continue
        except OSError:
            return None
    # Fall back to the driver store file repository name.
    import os
    from pathlib import Path

    store = Path(os.environ["SystemRoot"]) / "System32/DriverStore/FileRepository"
    try:
        return any(
            path.name.lower().startswith(("usbaapl", "appleusb.inf_"))
            for path in store.iterdir()
        )
    except OSError:
        return None


class _UsbStream(DeviceStream):
    """Adapts a pymobiledevice3 lockdown service connection to the Link contract."""

    def __init__(self, conn):
        self._conn = conn

    async def recvall(self, size: int) -> bytes:
        if size <= 0:
            return b""
        recvall = getattr(self._conn, "recvall", None)
        if callable(recvall):
            return await recvall(size)
        reader = getattr(self._conn, "reader", None)
        if reader is not None:
            try:
                return await reader.readexactly(size)
            except asyncio.IncompleteReadError as exc:
                return exc.partial
        raise DeviceError("Unsupported stream backend")

    async def sendall(self, data: bytes) -> None:
        sendall = getattr(self._conn, "sendall", None)
        if callable(sendall):
            await sendall(data)
            return
        writer = getattr(self._conn, "writer", None)
        if writer is not None:
            writer.write(data)
            await writer.drain()
            return
        raise DeviceError("Unsupported stream backend")

    async def close(self) -> None:
        close = getattr(self._conn, "close", None)
        if callable(close):
            await close()


def _classify_device_error(error: Exception) -> DeviceError:
    """Map a pymobiledevice3/OS error to a platform DeviceError subtype."""
    name = type(error).__name__.lower()
    text = str(error).lower()
    if "nodevice" in name or "no device" in text or "no connected" in text:
        return NoDeviceError(str(error))
    if "pair" in name or "trust" in name or "pairing" in text or "trusted" in text:
        return TrustRequiredError(str(error))
    return DeviceError(str(error))


class WindowsUSBAdapter(PlatformAdapter):
    """USB transport over ``com.apple.carkit.service`` via pymobiledevice3."""

    transport = "usb"

    def __init__(self):
        self._phone = None

    async def list_devices(self) -> list[dict[str, Any]]:
        try:
            from pymobiledevice3.usbmux import list_devices as _usb_list
        except ImportError:  # pragma: no cover
            return []
        devices = []
        try:
            for device in await _usb_list():
                connection_type = str(getattr(device, "connection_type", "")).lower()
                if "usb" not in connection_type:
                    continue
                # Privacy-safe: never expose serial number / UDID / identifiers.
                devices.append({"label": "iPhone / iPad（USB 已连接）"})
        except Exception:  # noqa: BLE001 - detection is best-effort
            return []
        return devices

    async def open(self, emit: Callable[..., Any] | None = None) -> DeviceStream:
        try:
            from pymobiledevice3.lockdown import create_using_usbmux
        except ImportError as exc:  # pragma: no cover
            raise DeviceError("pymobiledevice3 未安装") from exc

        try:
            self._phone = await create_using_usbmux(connection_type="USB", autopair=False)
        except Exception as error:  # noqa: BLE001
            raise _classify_device_error(error) from error

        # Best-effort device name for display (not required for the session).
        device_name = None
        try:
            device_name = await self._phone.get_value(key="DeviceName")
        except Exception:  # noqa: BLE001 - device name is cosmetic
            device_name = None

        try:
            service = await self._phone.start_lockdown_service("com.apple.carkit.service")
        except Exception as error:  # noqa: BLE001
            raise _classify_device_error(error) from error

        stream = _UsbStream(service)
        stream.device_name = device_name  # type: ignore[attr-defined]
        return stream

    async def close(self) -> None:
        phone, self._phone = self._phone, None
        if phone is None:
            return
        close = getattr(phone, "close", None)
        if callable(close):
            await close()

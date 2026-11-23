"""macOS platform adapter — reserved for a future Mac frontend.

The unified event/state interface (``ouye_location_studio.state``) and the
engine (``core.engine``) are platform-agnostic; this adapter is a placeholder
so that the package can be imported on macOS and the future frontend can plug in
a USB (or Bluetooth) transport without touching the engine.
"""

from __future__ import annotations

from typing import Any, Callable

from .base import DeviceError, DeviceStream, PlatformAdapter


class MacOSAdapter(PlatformAdapter):
    transport = "usb"

    async def list_devices(self) -> list[dict[str, Any]]:
        return []

    async def open(self, emit: Callable[..., Any] | None = None) -> DeviceStream:
        raise DeviceError("macOS transport is not implemented yet")

    async def close(self) -> None:
        return None

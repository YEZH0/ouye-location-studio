"""Platform abstraction: transports, device streams, and adapters.

The engine depends only on ``DeviceStream`` and ``PlatformAdapter``, so the
Windows USB transport and a future macOS transport share the same engine and
the same event/state interface.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Callable


class DeviceError(Exception):
    """Base class for platform transport failures."""


class NoDeviceError(DeviceError):
    """No eligible device is connected or paired."""

    no_device = True


class TrustRequiredError(DeviceError):
    """The device is not trusted yet; the user must accept the prompt on the phone."""

    trust_required = True


class ServiceError(DeviceError):
    """The iAP2/CarKit lockdown service could not be opened."""


class DeviceStream(ABC):
    """The byte-stream contract required by ``core.link.Link``."""

    async def recvall(self, size: int) -> bytes:  # pragma: no cover - interface
        raise NotImplementedError

    async def sendall(self, data: bytes) -> None:  # pragma: no cover - interface
        raise NotImplementedError

    async def close(self) -> None:  # pragma: no cover - interface
        raise NotImplementedError


class PlatformAdapter(ABC):
    """Opens the iAP2 transport for a given platform."""

    transport: str = "usb"

    @abstractmethod
    async def open(self, emit: Callable[..., Any] | None = None) -> DeviceStream:
        """Open the transport and return a connected device stream."""

    @abstractmethod
    async def close(self) -> None:
        """Release any platform-held connection resources."""

    @abstractmethod
    async def list_devices(self) -> list[dict[str, Any]]:
        """Detect connected devices without opening a session.

        Returns a list of small, privacy-safe dictionaries (no serial number,
        UDID, Apple ID or other identifiers).
        """

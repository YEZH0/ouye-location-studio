"""Platform adapters package."""

from .base import (
    DeviceError,
    DeviceStream,
    NoDeviceError,
    PlatformAdapter,
    ServiceError,
    TrustRequiredError,
)

__all__ = [
    "DeviceError",
    "DeviceStream",
    "NoDeviceError",
    "PlatformAdapter",
    "ServiceError",
    "TrustRequiredError",
]


def create_platform():
    """Return the platform adapter for the current operating system."""
    import sys

    if sys.platform == "win32":
        from .windows import WindowsUSBAdapter

        return WindowsUSBAdapter()
    from .macos import MacOSAdapter

    return MacOSAdapter()

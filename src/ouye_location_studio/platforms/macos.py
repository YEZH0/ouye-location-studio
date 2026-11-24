"""macOS USB transport using the system usbmuxd and a trusted iPhone."""

from __future__ import annotations

from contextlib import AsyncExitStack
from typing import Any, Callable

from .base import DeviceStream, NoDeviceError, PlatformAdapter, ServiceError, TrustRequiredError


class _USBStream(DeviceStream):
    def __init__(self, connection):
        self._connection = connection

    async def recvall(self, size: int) -> bytes:
        return await self._connection.recvall(size)

    async def sendall(self, data: bytes) -> None:
        await self._connection.sendall(data)

    async def close(self) -> None:
        connection, self._connection = self._connection, None
        if connection is not None:
            await connection.close()


class MacOSAdapter(PlatformAdapter):
    """Use Apple's USB pairing and CarKit service without developer services."""

    def __init__(self):
        self._resources = AsyncExitStack()

    async def list_devices(self) -> list[dict[str, Any]]:
        from pymobiledevice3.usbmux import list_devices

        return [
            {"label": "iPhone / iPad（USB 已连接）"}
            for device in await list_devices()
            if device.connection_type == "USB"
        ]

    async def open(self, emit: Callable[..., Any] | None = None) -> DeviceStream:
        from pymobiledevice3.exceptions import NoDeviceConnectedError, NotPairedError, PairingError
        from pymobiledevice3.lockdown import create_using_usbmux

        if not await self.list_devices():
            raise NoDeviceError("未检测到 USB 设备")

        async with AsyncExitStack() as resources:
            try:
                phone = await create_using_usbmux(connection_type="USB", autopair=False)
                resources.push_async_callback(phone.close)
                if not phone.paired:
                    raise TrustRequiredError("请在 iPhone 上信任此电脑")
                connection = await phone.start_lockdown_service("com.apple.carkit.service")
            except NoDeviceConnectedError as error:
                raise NoDeviceError("USB 设备已断开") from error
            except (NotPairedError, PairingError) as error:
                raise TrustRequiredError("请在 iPhone 上信任此电脑") from error
            except TrustRequiredError:
                raise
            except Exception as error:
                raise ServiceError("无法打开 iPhone USB 配件服务，请解锁并重新连接设备") from error

            stream = _USBStream(connection)
            resources.push_async_callback(stream.close)
            self._resources = resources.pop_all()
            return stream

    async def close(self) -> None:
        await self._resources.aclose()

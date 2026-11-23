"""Session orchestrator: turns raw iAP2 control messages into a unified event stream.

Adapted from TetherPin's ``cli.run`` loop (GPL-3.0-only); see package docstring
for provenance. The authentication flow, USB transport, NMEA sentence encoding,
ACK handling, subscription handling and stop logic are preserved.

A single engine instance runs a single active location session at a time.
``request_stop`` is safe to call from any thread.
"""

from __future__ import annotations

import asyncio
import math
import threading
import time

from ..state import (
    EVENT_AUTHENTICATION_FAILED,
    EVENT_AUTHENTICATION_REQUIRED,
    EVENT_AUTHENTICATION_SUCCEEDED,
    EVENT_DEVICE_CONNECTED,
    EVENT_DEVICE_TRUST_REQUIRED,
    EVENT_ERROR,
    EVENT_FINISHED,
    EVENT_IDENTIFICATION_ACCEPTED,
    EVENT_IDENTIFICATION_REJECTED,
    EVENT_INTERRUPTED,
    EVENT_LINK_READY,
    EVENT_LOCATION_LINK_ACKNOWLEDGED,
    EVENT_LOCATION_REQUESTED,
    EVENT_LOCATION_STOPPED,
    EVENT_MESSAGE,
    EVENT_RESTORE_REQUIRED,
    EVENT_RETRANSMIT,
    EngineEvent,
    EngineListener,
    SessionPhase,
    SessionStatus,
)
from .auth import AuthenticationProvider
from .link import Link
from .profile import coordinate, identity, location_message, location_sentences
from .wire import parameters

MAX_DURATION_SECONDS = 3600


class _NullListener(EngineListener):
    def on_event(self, event: EngineEvent) -> None:
        return None


class _AuthRejected(RuntimeError):
    """Terminal: the device rejected the accessory identity. Already emitted."""


class LocationEngine:
    """Runs one iAP2 location session and reports progress via EngineListener."""

    def __init__(self, adapter, *, auth_helper_path: str | None = None,
                 auth_provider=None, listener: EngineListener | None = None):
        self.adapter = adapter
        self.auth_helper_path = auth_helper_path
        self._auth_provider = auth_provider
        self.listener = listener or _NullListener()
        self._stop = threading.Event()
        self.status = SessionStatus(transport=getattr(adapter, "transport", "usb"))

    # -- control -----------------------------------------------------------

    def request_stop(self) -> None:
        """Ask the running session to stop; safe from any thread."""
        self._stop.set()

    def reset(self) -> None:
        self._stop.clear()
        self.status = SessionStatus(transport=getattr(self.adapter, "transport", "usb"))

    # -- event plumbing ----------------------------------------------------

    def _emit(self, name: str, *, phase: SessionPhase | None = None,
              message: str = "", **data) -> None:
        if phase is not None:
            self.status.phase = phase
        self.listener.on_event(EngineEvent(name, phase=phase, message=message, data=data))

    def _on_link_event(self, **kw) -> None:
        kind = kw.get("event")
        if kind == "link_ready":
            self._emit(EVENT_LINK_READY, phase=SessionPhase.IDENTIFYING,
                       message="iAP2 链路已建立", control_session=kw.get("control_session"))
        elif kind == "retransmit":
            self._emit(EVENT_RETRANSMIT, message="数据未确认，正在重传",
                       attempt=kw.get("attempt"))

    # -- session -----------------------------------------------------------

    async def run_session(self, *, latitude: float | None = None,
                          longitude: float | None = None,
                          duration: float = 60.0,
                          interval: float = 1.0,
                          send_location: bool = True,
                          device_name: str | None = None) -> None:
        if send_location and (latitude is None or longitude is None):
            raise ValueError("send_location requires latitude and longitude")
        if not math.isfinite(duration) or not 0 < duration <= MAX_DURATION_SECONDS:
            raise ValueError("duration must be between 0 and 3600 seconds")
        if send_location:
            coordinate(latitude, True)
            coordinate(longitude, False)
            if not math.isfinite(interval) or interval < 1:
                raise ValueError("interval must be at least 1 second")

        self.reset()
        self.status.device_name = device_name
        self.status.started_at = time.time()

        phone_stream = None
        link: Link | None = None
        auth: AuthenticationProvider | None = None
        interrupted = False
        try:
            self._emit(EVENT_DEVICE_CONNECTED, phase=SessionPhase.CONNECTING,
                       message="正在连接设备…", transport=self.adapter.transport)
            phone_stream = await self.adapter.open(self._emit)
            self.status.device_name = self.status.device_name or getattr(
                phone_stream, "device_name", None)

            link = Link(phone_stream, self._on_link_event)
            self._emit(EVENT_MESSAGE, phase=SessionPhase.HANDSHAKING,
                       message="正在进行 iAP2 握手…")
            await link.handshake()

            if self._auth_provider is not None:
                auth = self._auth_provider
            elif self.auth_helper_path:
                auth = AuthenticationProvider(self.auth_helper_path)

            deadline = time.time() + duration
            active: set[int] = set()
            intervals: dict[int, float] = {}
            last_sent: dict[int, float] = {}
            identified = False
            authenticated = False
            sent_count = 0
            stop_reason = "finished"

            while True:
                if self._stop.is_set():
                    interrupted = True
                    stop_reason = "stopped"
                    break
                remaining = deadline - time.time()
                if remaining <= 0:
                    break
                try:
                    message = await link.receive(min(0.25, remaining))
                except TimeoutError:
                    message = None
                if message is not None:
                    fields = parameters(message.body)
                    self._emit(
                        EVENT_MESSAGE,
                        message=f"收到控制消息 0x{message.identifier:04x}",
                        identifier=f"0x{message.identifier:04x}",
                        parameters=[{"id": i, "bytes": len(b)} for i, b in fields],
                    )

                    if message.identifier == 0x1D00:
                        await link.send(identity(self.adapter.transport))
                    elif message.identifier == 0x1D02:
                        identified = True
                        self.status.identified = True
                        self._emit(EVENT_IDENTIFICATION_ACCEPTED, message="设备身份识别已接受")
                    elif message.identifier == 0x1D03:
                        self._emit(EVENT_IDENTIFICATION_REJECTED, phase=SessionPhase.ERROR,
                                   message=f"设备拒绝了配件身份（参数 {[i for i, _ in fields]}）")
                        raise RuntimeError(f"Identification rejected: {[i for i, _ in fields]}")
                    elif message.identifier == 0xAA00:
                        if auth is None:
                            raise RuntimeError(
                                "需要配件认证，但尚未配置认证材料（证书与私钥）")
                        self._emit(EVENT_AUTHENTICATION_REQUIRED,
                                   phase=SessionPhase.AUTHENTICATING,
                                   message="正在提交配件证书…")
                        await link.send(await auth.certificate())
                    elif message.identifier == 0xAA02:
                        if auth is None:
                            raise RuntimeError(
                                "需要配件认证，但尚未配置认证材料（证书与私钥）")
                        challenges = [b for i, b in fields if i == 0]
                        if len(challenges) != 1:
                            raise RuntimeError("Invalid authentication challenge parameters")
                        self._emit(EVENT_AUTHENTICATION_REQUIRED,
                                   phase=SessionPhase.AUTHENTICATING,
                                   message="正在签署认证挑战…")
                        await link.send(await auth.sign(challenges[0]))
                    elif message.identifier == 0xAA05:
                        authenticated = True
                        self.status.authenticated = True
                        self._emit(EVENT_AUTHENTICATION_SUCCEEDED, message="配件认证成功")
                    elif message.identifier == 0xAA04:
                        self._emit(EVENT_AUTHENTICATION_FAILED, phase=SessionPhase.ERROR,
                                   message="配件认证被设备拒绝")
                        raise _AuthRejected("配件认证被设备拒绝")
                    elif message.identifier == 0xFFFA:
                        active = {i for i, b in fields if i in (1, 2) and not b}
                        intervals = {
                            i - 0x8000: max(1.0, int.from_bytes(b, "big") / 1000)
                            for i, b in fields
                            if i in (0x8001, 0x8002) and len(b) == 4
                        }
                        last_sent.clear()
                        self.status.sentences = frozenset(active)
                        self._emit(EVENT_LOCATION_REQUESTED, phase=SessionPhase.LOCATING,
                                   message="设备请求定位信息", sentences=sorted(active))
                    elif message.identifier == 0xFFFC:
                        active.clear()
                        self.status.active = False
                        self.status.sentences = frozenset()
                        self._emit(EVENT_LOCATION_STOPPED, phase=SessionPhase.DONE,
                                   message="设备已停止请求定位")
                        self._emit(EVENT_RESTORE_REQUIRED,
                                   message="请在 iPhone 上确认位置已恢复真实定位")

                if send_location and identified and authenticated and active:
                    now = time.time()
                    due = sorted(
                        i for i in active
                        if now - last_sent.get(i, -math.inf) >= max(interval, intervals.get(i, 1))
                    )
                    if due:
                        sentences = location_sentences(latitude, longitude)
                        await link.send(location_message([sentences[i] for i in due]))
                        last_sent.update({i: now for i in due})
                        sent_count += 1
                        self.status.active = True
                        self.status.sent_count = sent_count
                        if sent_count == 1 or sent_count % 10 == 0:
                            # Link-layer ACK only: this does NOT prove the phone
                            # accepted or applied the location.
                            self._emit(EVENT_LOCATION_LINK_ACKNOWLEDGED,
                                       message="定位数据已由链路确认（不代表手机已定位成功）",
                                       count=sent_count)

            self.status.deadline = time.time()
            self._emit(
                EVENT_FINISHED,
                phase=SessionPhase.DONE if not interrupted else SessionPhase.STOPPING,
                message="会话已结束",
                identified=identified,
                authenticated=authenticated,
                location_packets_acknowledged=sent_count,
                phone_location_verified=False,
                stop_reason=stop_reason,
            )
        except asyncio.CancelledError:
            interrupted = True
            self._emit(EVENT_INTERRUPTED, phase=SessionPhase.DONE, message="会话已取消")
            raise
        except _AuthRejected:
            # The specific EVENT_AUTHENTICATION_FAILED was already emitted.
            pass
        except Exception as error:  # noqa: BLE001 - surface to frontend
            if getattr(error, "trust_required", False):
                self._emit(EVENT_DEVICE_TRUST_REQUIRED, phase=SessionPhase.ERROR,
                           message="请在 iPhone 上点击「信任此电脑」并输入锁屏密码")
            elif getattr(error, "no_device", False):
                self._emit(EVENT_ERROR, phase=SessionPhase.ERROR,
                           message="未检测到设备，请连接 iPhone 并重新检测",
                           type=type(error).__name__)
            else:
                self._emit(EVENT_ERROR, phase=SessionPhase.ERROR,
                           message=str(error) or type(error).__name__,
                           type=type(error).__name__)
        finally:
            # Best-effort cleanup of every owned resource; a failed close must
            # not mask the real error and must not skip the remaining resources.
            if link is not None:
                try:
                    await link.close()
                except Exception:  # noqa: BLE001
                    pass
            try:
                await self.adapter.close()
            except Exception:  # noqa: BLE001
                pass
            if auth is not None:
                try:
                    await auth.close()
                except Exception:  # noqa: BLE001
                    pass

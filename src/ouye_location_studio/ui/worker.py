"""Qt worker thread that runs the engine and bridges events to the GUI thread."""

from __future__ import annotations

import asyncio
import os

from PySide6.QtCore import QObject, QThread, Signal

from ..auth_helper import CERT_ENV, KEY_ENV
from ..core.engine import LocationEngine
from ..state import EngineEvent, EngineListener


class EngineBridge(QObject):
    """Lives in the GUI thread; receives events emitted from the worker thread."""

    event = Signal(object)  # EngineEvent
    finished = Signal()


class _Listener(EngineListener):
    def __init__(self, bridge: EngineBridge):
        self._bridge = bridge

    def on_event(self, event: EngineEvent) -> None:
        self._bridge.event.emit(event)


class EngineWorker(QThread):
    """Runs one engine session on a background thread.

    ``configure`` must be called (from the GUI thread) before ``start``.
    ``request_stop`` is thread-safe and may be called at any time.
    """

    def __init__(self, adapter, *, auth_helper_path: str | None = None,
                 cert_file: str | None = None, key_file: str | None = None,
                 parent=None):
        super().__init__(parent)
        self.bridge = EngineBridge()
        self._engine = LocationEngine(
            adapter, auth_helper_path=auth_helper_path, listener=_Listener(self.bridge)
        )
        self._cert_file = cert_file
        self._key_file = key_file
        self._params: dict = {}

    def configure(self, *, latitude: float, longitude: float, duration: float,
                  interval: float, device_name: str | None = None) -> None:
        self._params = dict(
            latitude=latitude,
            longitude=longitude,
            duration=duration,
            interval=interval,
            send_location=True,
            device_name=device_name,
        )
        # Configure the helper's identity files in the GUI thread before start.
        if self._cert_file:
            os.environ[CERT_ENV] = self._cert_file
        if self._key_file:
            os.environ[KEY_ENV] = self._key_file

    def request_stop(self) -> None:
        self._engine.request_stop()

    def run(self) -> None:  # noqa: D102 - QThread entry point
        try:
            asyncio.run(self._engine.run_session(**self._params))
        finally:
            self.bridge.finished.emit()

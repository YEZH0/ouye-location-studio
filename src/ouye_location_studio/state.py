"""Unified engine state interface.

The engine communicates with any frontend (Windows PySide6 today, macOS later)
through an immutable, serialisable event stream plus a coarse lifecycle phase.
Nothing in this module references Qt, so the macOS frontend can reuse it verbatim.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class SessionPhase(str, Enum):
    """Coarse lifecycle phases shared by every platform frontend."""

    IDLE = "idle"
    DETECTING = "detecting"
    CONNECTING = "connecting"
    HANDSHAKING = "handshaking"
    IDENTIFYING = "identifying"
    AUTHENTICATING = "authenticating"
    LOCATING = "locating"
    STOPPING = "stopping"
    DONE = "done"
    ERROR = "error"


# Stable event names emitted by the engine. Frontends switch on these names;
# adding a name is backwards compatible, renaming one is a breaking change.
EVENT_DEVICE_CONNECTED = "device_connected"
EVENT_DEVICE_TRUST_REQUIRED = "device_trust_required"
EVENT_LINK_READY = "link_ready"
EVENT_IDENTIFICATION_ACCEPTED = "identification_accepted"
EVENT_IDENTIFICATION_REJECTED = "identification_rejected"
EVENT_AUTHENTICATION_REQUIRED = "authentication_required"
EVENT_AUTHENTICATION_SUCCEEDED = "authentication_succeeded"
EVENT_AUTHENTICATION_FAILED = "authentication_failed"
EVENT_LOCATION_REQUESTED = "location_requested"
EVENT_LOCATION_LINK_ACKNOWLEDGED = "location_link_acknowledged"
EVENT_LOCATION_STOPPED = "location_stopped"
EVENT_RESTORE_REQUIRED = "restore_required"
EVENT_RETRANSMIT = "retransmit"
EVENT_FINISHED = "finished"
EVENT_ERROR = "error"
EVENT_INTERRUPTED = "interrupted"
EVENT_MESSAGE = "message"


@dataclass(frozen=True)
class EngineEvent:
    """A single immutable event emitted by the engine.

    ``name`` is one of the EVENT_* constants above. ``phase`` is the new
    lifecycle phase (or ``None`` if the event does not change phase).
    ``message`` is a short, human-readable, non-sensitive description.
    ``data`` carries machine-readable, non-sensitive fields only.
    """

    name: str
    phase: SessionPhase | None = None
    message: str = ""
    data: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "phase": self.phase.value if self.phase is not None else None,
            "message": self.message,
            "data": self.data,
        }


@dataclass
class SessionStatus:
    """Aggregate snapshot a frontend can render at any moment."""

    phase: SessionPhase = SessionPhase.IDLE
    transport: str = "usb"
    device_name: str | None = None
    identified: bool = False
    authenticated: bool = False
    active: bool = False
    sentences: frozenset[int] = frozenset()
    sent_count: int = 0
    started_at: float | None = None
    deadline: float | None = None

    def remaining_seconds(self, now: float) -> float:
        if self.deadline is None:
            return 0.0
        return max(0.0, self.deadline - now)

    def as_dict(self) -> dict[str, Any]:
        return {
            "phase": self.phase.value,
            "transport": self.transport,
            "device_name": self.device_name,
            "identified": self.identified,
            "authenticated": self.authenticated,
            "active": self.active,
            "sentences": sorted(self.sentences),
            "sent_count": self.sent_count,
            "started_at": self.started_at,
            "deadline": self.deadline,
        }


class EngineListener:
    """Protocol any frontend implements to receive engine events.

    The engine calls ``on_event`` from its own asyncio loop/thread, so
    implementations must be safe to call from that context (the Qt frontend
    bridges to the GUI thread with a queued signal).
    """

    def on_event(self, event: EngineEvent) -> None:  # pragma: no cover - interface
        raise NotImplementedError

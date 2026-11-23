"""Unit tests for the unified state interface."""

from ouye_location_studio.state import (
    EngineEvent,
    SessionPhase,
    SessionStatus,
)


def test_event_serialisation():
    event = EngineEvent("location_requested", phase=SessionPhase.LOCATING,
                        message="x", data={"sentences": [1, 2]})
    payload = event.as_dict()
    assert payload == {
        "name": "location_requested",
        "phase": "locating",
        "message": "x",
        "data": {"sentences": [1, 2]},
    }


def test_status_remaining_seconds():
    status = SessionStatus(deadline=100.0)
    assert status.remaining_seconds(40.0) == 60.0
    assert status.remaining_seconds(120.0) == 0.0
    assert status.remaining_seconds(40.0) == 60.0  # no mutation


def test_status_dict_hides_internals():
    status = SessionStatus(sentences=frozenset({1, 2}))
    assert status.as_dict()["sentences"] == [1, 2]
    assert status.as_dict()["phase"] == "idle"

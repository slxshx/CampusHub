from campushub.models.event import CreateEvent
import pytest
from pydantic import ValidationError
from datetime import datetime

def test_create_event_with_valid_data():
    create_event = CreateEvent(
            device_id=1,
            timestamp=datetime(2026, 9, 3, 7, 30, 0),
            type="Critical",
            description="Switch 1 ist ausgefallen."
            )

    assert create_event.device_id == 1
    assert create_event.timestamp == datetime(2026, 9, 3, 7, 30, 0)
    assert create_event.type == "Critical"
    assert create_event.description == "Switch 1 ist ausgefallen."

def test_create_event_with_optional_none():
    create_event = CreateEvent(
            device_id=1,
            timestamp=datetime(2026, 9, 3, 7, 30, 0),
            type="Critical",
            description=None
            )

    assert create_event.device_id == 1
    assert create_event.timestamp == datetime(2026, 9, 3, 7, 30, 0)
    assert create_event.type == "Critical"
    assert create_event.description == None


def test_create_event_without_optional():
    create_event = CreateEvent(
            device_id=1,
            timestamp=datetime(2026, 9, 3, 7, 30, 0),
            type="Critical",
            )

    assert create_event.device_id == 1
    assert create_event.timestamp == datetime(2026, 9, 3, 7, 30, 0)
    assert create_event.type == "Critical"
    assert create_event.description == None

def test_create_event_without_device_id_fails():
    with pytest.raises(ValidationError):
       CreateEvent(
            timestamp=datetime(2026, 9, 3, 7, 30, 0),
            type="Critical",
            description=None
            )

def test_create_event_without_timestamp_fails():
    with pytest.raises(ValidationError):
       CreateEvent(
            device_id=1,
            type="Critical",
            description=None
            )

def test_create_event_without_type_fails():
    with pytest.raises(ValidationError):
       CreateEvent(
            device_id=1,
            timestamp=datetime(2026, 9, 3, 7, 30, 0),
            description=None
            )



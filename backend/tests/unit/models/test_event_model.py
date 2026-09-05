from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from campushub.models.event import CreateEvent, UpdateEvent


def test_create_event_with_valid_data():
    timestamp = datetime.now(timezone.utc)

    create_event = CreateEvent(
        device_id=1,
        timestamp=timestamp,
        type="interface_down",
        description="Interface Gi0/1 is down",
    )

    assert create_event.device_id == 1
    assert create_event.timestamp == timestamp
    assert create_event.type == "interface_down"
    assert create_event.description == "Interface Gi0/1 is down"


def test_create_event_with_optional_none():
    create_event = CreateEvent(
        device_id=1,
        timestamp=datetime.now(timezone.utc),
        type="device_online",
        description=None,
    )

    assert create_event.description is None


def test_create_event_without_optional():
    create_event = CreateEvent(
        device_id=1,
        timestamp=datetime.now(timezone.utc),
        type="device_online",
    )

    assert create_event.description is None


@pytest.mark.parametrize(
    "test_data",
    [
        {
            "timestamp": datetime.now(timezone.utc),
            "type": "device_online",
        },
        {
            "device_id": 1,
            "type": "device_online",
        },
        {
            "device_id": 1,
            "timestamp": datetime.now(timezone.utc),
        },
    ],
)
def test_create_event_without_required_field_fails(test_data):
    with pytest.raises(ValidationError):
        CreateEvent(**test_data)


def test_update_event_one_parameter():
    update_event = UpdateEvent(
        description="Updated event description"
    )

    data = update_event.model_dump(exclude_unset=True)

    assert data == {
        "description": "Updated event description"
    }


def test_update_event_multiple_parameters():
    update_event = UpdateEvent(
        type="warning",
        description="Something happened",
    )

    data = update_event.model_dump(exclude_unset=True)

    assert data == {
        "type": "warning",
        "description": "Something happened",
    }


def test_update_event_without_parameters():
    update_event = UpdateEvent()

    data = update_event.model_dump(exclude_unset=True)

    assert data == {}


def test_update_event_explicit_none():
    update_event = UpdateEvent(
        description=None
    )

    data = update_event.model_dump(exclude_unset=True)

    assert data == {
        "description": None
    }

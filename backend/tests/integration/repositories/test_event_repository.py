from campushub.models.event import UpdateEvent
from campushub.repositories.event_repository import EventRepository


def test_create_event(test_event):
    assert test_event.id is not None
    assert test_event.type == "device_online"
    assert test_event.description == "Created by fixture"


def test_get_all_events(test_event):
    repository = EventRepository()

    result = repository.get_all_events()

    assert isinstance(result, list)
    assert any(event.id == test_event.id for event in result)


def test_get_event_by_id(test_event):
    repository = EventRepository()

    result = repository.get_event_by_id(test_event.id)

    assert result is not None
    assert result.id == test_event.id


def test_update_event(test_event):
    repository = EventRepository()

    update_event = UpdateEvent(
        type="interface_down",
        description="Gi0/1 went down",
    )

    result = repository.update_event(
        test_event.id,
        update_event,
    )

    assert result is True

    new_test_event = repository.get_event_by_id(test_event.id)

    assert new_test_event is not None
    assert new_test_event.type == "interface_down"
    assert new_test_event.description == "Gi0/1 went down"


def test_delete_event(test_event):
    repository = EventRepository()

    result = repository.delete_event(test_event.id)

    assert result is True

    is_event_deleted = repository.get_event_by_id(test_event.id)

    assert is_event_deleted is None

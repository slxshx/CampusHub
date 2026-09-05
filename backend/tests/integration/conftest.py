import pytest

from datetime import datetime, timezone
from ipaddress import IPv4Interface

from campushub.models.device import CreateDevice
from campushub.models.interface import CreateInterface
from campushub.models.metric import CreateMetric
from campushub.models.event import CreateEvent
from campushub.models.user import CreateUser

from campushub.repositories.device_repository import DeviceRepository
from campushub.repositories.interface_repository import InterfaceRepository
from campushub.repositories.metric_repository import MetricRepository
from campushub.repositories.event_repository import EventRepository
from campushub.repositories.user_repository import UserRepository


@pytest.fixture
def test_device(monkeypatch):
    monkeypatch.setenv("DB_NAME", "campushub_test")

    repository = DeviceRepository()

    create_device = CreateDevice(
        hostname="Fixture-Switch",
        description="Created by fixture",
        device_type="Switch",
        location="Test Campus",
    )

    created_device = repository.create_device(create_device)

    assert created_device is not None

    yield created_device

    repository.delete_device(created_device.id)


@pytest.fixture
def test_interface(test_device):
    repository = InterfaceRepository()

    create_interface = CreateInterface(
        device_id=test_device.id,
        name="Gi0/1",
        description="Fixture Interface",
        ip_address=IPv4Interface("192.168.100.1/24"),
        mac_address="00:11:22:33:44:55",
    )

    created_interface = repository.create_interface(create_interface)

    assert created_interface is not None

    yield created_interface

    repository.delete_interface(created_interface.id)


@pytest.fixture
def test_metric(test_device):
    repository = MetricRepository()

    create_metric = CreateMetric(
        device_id=test_device.id,
        timestamp=datetime.now(timezone.utc),
        cpu_usage=25.5,
        ram_usage=50.0,
        storage_usage=75.0,
        temperature=42.0,
        uptime=12345,
    )

    created_metric = repository.create_metric(create_metric)

    assert created_metric is not None

    yield created_metric

    repository.delete_metric(created_metric.id)


@pytest.fixture
def test_event(test_device):
    repository = EventRepository()

    create_event = CreateEvent(
        device_id=test_device.id,
        timestamp=datetime.now(timezone.utc),
        type="device_online",
        description="Created by fixture",
    )

    created_event = repository.create_event(create_event)

    assert created_event is not None

    yield created_event

    repository.delete_event(created_event.id)


@pytest.fixture
def test_user(monkeypatch):
    monkeypatch.setenv("DB_NAME", "campushub_test")

    repository = UserRepository()

    create_user = CreateUser(
        username="fixture-user",
        password_hash="fixture-hash",
        role="user",
    )

    created_user = repository.create_user(create_user)

    assert created_user is not None

    yield created_user

    repository.delete_user(created_user.id)

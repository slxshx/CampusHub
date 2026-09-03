from campushub.models.device import CreateDevice
from campushub.repositories.device_repository import DeviceRepository


def test_create_device(monkeypatch):
    monkeypatch.setenv("DB_NAME", "campushub_test")

    repository = DeviceRepository()

    create_device = CreateDevice(
        hostname="integration-test-switch",
        description="Created by repository integration test",
        device_type="Switch",
        location="Test Campus",
    )

    created_device = repository.create_device(create_device)

    assert created_device is not None
    assert created_device.id is not None
    assert created_device.hostname == "integration-test-switch"
    assert created_device.description == "Created by repository integration test"
    assert created_device.device_type == "Switch"
    assert created_device.location == "Test Campus"

    repository.delete_device(created_device.id)

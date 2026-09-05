from campushub.models.device import CreateDevice, UpdateDevice
from campushub.repositories.device_repository import DeviceRepository


def test_create_device(test_device):

    assert test_device.id is not None
    assert test_device.hostname == "Fixture-Switch"
    assert test_device.description == "Created by fixture"
    assert test_device.device_type == "Switch"
    assert test_device.location == "Test Campus"

def test_get_all_devices(test_device):
    repository = DeviceRepository()

    result = repository.get_all_devices()

    assert isinstance(result, list)
    assert any(device.id == test_device.id for device in result)


def test_get_device_by_id(test_device):

    repository = DeviceRepository()

    result = repository.get_device_by_id(test_device.id)

    assert result is not None
    assert result.id == test_device.id

def test_update_device(test_device):

    repository = DeviceRepository()

    updateDevice = UpdateDevice(
            hostname="Loose-Server",
            description="Destroyed by fixture",
            device_type="Server",
            location="Real Campus"
            )

    result = repository.update_device(test_device.id, updateDevice)

    assert result is True

    new_test_device = repository.get_device_by_id(test_device.id)

    assert new_test_device is not None

    assert new_test_device.hostname == "Loose-Server"
    assert new_test_device.description == "Destroyed by fixture"
    assert new_test_device.device_type == "Server"
    assert new_test_device.location == "Real Campus"

def test_delete_device(test_device):

    repository = DeviceRepository()

    result = repository.delete_device(test_device.id)

    assert result is True

    is_device_deleted = repository.get_device_by_id(test_device.id)

    assert is_device_deleted is None


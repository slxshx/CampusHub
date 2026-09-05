from ipaddress import IPv4Interface

from campushub.models.interface import UpdateInterface
from campushub.repositories.interface_repository import InterfaceRepository


def test_create_interface(test_interface):
    assert test_interface.id is not None
    assert test_interface.name == "Gi0/1"
    assert test_interface.description == "Fixture Interface"
    assert test_interface.ip_address == IPv4Interface("192.168.100.1/24")
    assert test_interface.mac_address == "00:11:22:33:44:55"


def test_get_all_interfaces(test_interface):
    repository = InterfaceRepository()

    result = repository.get_all_interfaces()

    assert isinstance(result, list)
    assert any(interface.id == test_interface.id for interface in result)


def test_get_interface_by_id(test_interface):
    repository = InterfaceRepository()

    result = repository.get_interface_by_id(test_interface.id)

    assert result is not None
    assert result.id == test_interface.id


def test_update_interface(test_interface):
    repository = InterfaceRepository()

    update_interface = UpdateInterface(
        name="Gi0/2",
        description="Updated Interface",
        ip_address=IPv4Interface("10.0.0.1/24"),
        mac_address="AA:BB:CC:DD:EE:FF",
    )

    result = repository.update_interface(
        test_interface.id,
        update_interface,
    )

    assert result is True

    new_test_interface = repository.get_interface_by_id(
        test_interface.id
    )

    assert new_test_interface is not None
    assert new_test_interface.name == "Gi0/2"
    assert new_test_interface.description == "Updated Interface"
    assert new_test_interface.ip_address == IPv4Interface("10.0.0.1/24")
    assert new_test_interface.mac_address == "aa:bb:cc:dd:ee:ff"


def test_delete_interface(test_interface):
    repository = InterfaceRepository()

    result = repository.delete_interface(test_interface.id)

    assert result is True

    is_interface_deleted = repository.get_interface_by_id(
        test_interface.id
    )

    assert is_interface_deleted is None

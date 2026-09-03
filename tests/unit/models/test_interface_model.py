from ipaddress import IPv4Interface, IPv6Interface

import pytest
from pydantic import ValidationError

from campushub.models.interface import CreateInterface, UpdateInterface


def test_create_interface_with_valid_ipv4():
    interface = CreateInterface(
        device_id=1,
        name="Gi0/1",
        description="Uplink",
        ip_address="192.168.10.1/24",
        mac_address="00:1a:2b:3c:4d:5e",
    )

    assert interface.device_id == 1
    assert interface.name == "Gi0/1"
    assert interface.description == "Uplink"
    assert interface.ip_address == IPv4Interface("192.168.10.1/24")
    assert interface.mac_address == "00:1a:2b:3c:4d:5e"


def test_create_interface_with_valid_ipv6():
    interface = CreateInterface(
        device_id=1,
        name="eth0",
        ip_address="2001:db8::1/64",
    )

    assert interface.ip_address == IPv6Interface("2001:db8::1/64")


def test_create_interface_without_optional_fields():
    interface = CreateInterface(
        device_id=1,
        name="Gi0/2",
    )

    assert interface.description is None
    assert interface.ip_address is None
    assert interface.mac_address is None


@pytest.mark.parametrize(
    "test_data",
    [
        {
            "name": "Gi0/1",
        },
        {
            "device_id": 1,
        },
    ],
)
def test_create_interface_without_required_field_fails(test_data):
    with pytest.raises(ValidationError):
        CreateInterface(**test_data)


def test_create_interface_with_invalid_ip_fails():
    with pytest.raises(ValidationError):
        CreateInterface(
            device_id=1,
            name="Gi0/1",
            ip_address="definitely-not-an-ip",
        )


def test_update_interface_one_parameter():
    update_interface = UpdateInterface(
        description="New description"
    )

    data = update_interface.model_dump(exclude_unset=True)

    assert data == {
        "description": "New description"
    }


def test_update_interface_multiple_parameters():
    update_interface = UpdateInterface(
        name="Gi0/5",
        ip_address="10.0.0.5/24",
    )

    data = update_interface.model_dump(exclude_unset=True)

    assert data == {
        "name": "Gi0/5",
        "ip_address": IPv4Interface("10.0.0.5/24"),
    }


def test_update_interface_without_parameters():
    update_interface = UpdateInterface()

    data = update_interface.model_dump(exclude_unset=True)

    assert data == {}


def test_update_interface_explicit_none():
    update_interface = UpdateInterface(
        ip_address=None
    )

    data = update_interface.model_dump(exclude_unset=True)

    assert data == {
        "ip_address": None
    }

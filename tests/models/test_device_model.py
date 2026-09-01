from campushub.models.device import CreateDevice
import pytest
from pydantic import ValidationError

def test_create_device_with_valid_data():
    create_device = CreateDevice(
            hostname="Switch 1",
            description="Ich bin der erste Test-Switch.",
            device_type="Switch",
            location="Campus 1"
            )

    assert create_device.hostname == "Switch 1"
    assert create_device.description == "Ich bin der erste Test-Switch."
    assert create_device.device_type == "Switch"
    assert create_device.location == "Campus 1"


def test_create_device_with_optional_none():
    create_device = CreateDevice(
            hostname="Switch 1",
            description=None,
            device_type="Switch",
            location=None
            )

    assert create_device.hostname == "Switch 1"
    assert create_device.description is None
    assert create_device.device_type == "Switch"
    assert create_device.location is None

def test_create_device_with_only_one_optional_description():
    create_device = CreateDevice(
            hostname="Switch 1",
            description="Ich connecte euch alle amk.",
            device_type="Switch",
            location=None
            )

    assert create_device.hostname == "Switch 1"
    assert create_device.description == "Ich connecte euch alle amk."
    assert create_device.device_type == "Switch"
    assert create_device.location is None

def test_create_device_with_only_one_optional_location():
    create_device = CreateDevice(
            hostname="Switch 1",
            description=None,
            device_type="Switch",
            location="Besenkammer 4"
            )

    assert create_device.hostname == "Switch 1"
    assert create_device.description is None
    assert create_device.device_type == "Switch"
    assert create_device.location == "Besenkammer 4"

def test_create_device_without_optional():
    create_device = CreateDevice(
            hostname="Switch 1",
            device_type="Switch",
            )

    assert create_device.hostname == "Switch 1"
    assert create_device.device_type == "Switch"

def test_create_device_without_hostname_fails():
    with pytest.raises(ValidationError):
        CreateDevice(
                description="Bester Switch",
                device_type="Server",
                location="Campus 2"
                )

def test_create_device_without_type_fails():
    with pytest.raises(ValidationError):
        CreateDevice(
                hostname="Server 3",
                description="Der wichtigste Server von allen.",
                location="Besenkammer 1"
                )



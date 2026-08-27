from ipaddress import IPv4Interface, IPv6Interface
from typing import ClassVar
from pydantic import BaseModel

class Interface(BaseModel):
    TABLE_NAME: ClassVar[str] = "interfaces"

    id: int
    device_id: int
    name: str
    description: str | None = None
    ip_address: IPv4Interface | IPv6Interface | None = None
    mac_address: str | None = None

class CreateInterface(BaseModel):
    TABLE_NAME: ClassVar[str] = "interfaces"

    device_id: int
    name: str
    description: str | None = None
    ip_address: IPv4Interface | IPv6Interface | None = None
    mac_address: str | None = None

class UpdateInterface(BaseModel):
    TABLE_NAME: ClassVar[str] = "interfaces"

    name: str | None = None
    description: str | None = None
    ip_address: IPv4Interface | IPv6Interface | None = None
    mac_address: str | None = None



from typing import ClassVar
from pydantic import BaseModel, IPvAnyAddress
from .enums import DeviceType, SnmpVersion

class ManagedDevice(BaseModel):
    TABLE_NAME: ClassVar[str] = "managed_device"

    id: int
    management_ip: IPvAnyAddress
    device_type: DeviceType
    enabled: bool
    snmp_port: int
    snmp_version: SnmpVersion

class CreateManagedDevice(BaseModel):
    TABLE_NAME: ClassVar[str] = "managed_device"

    management_ip: IPvAnyAddress
    device_type: DeviceType
    enabled: bool
    snmp_port: int
    snmp_version: SnmpVersion

class UpdateManagedDevice(BaseModel):
    TABLE_NAME: ClassVar[str] = "managed_device"

    management_ip: IPvAnyAddress | None = None
    device_type: DeviceType | None = None
    enabled: bool | None = None
    snmp_port: int | None = None
    snmp_version: SnmpVersion | None = None



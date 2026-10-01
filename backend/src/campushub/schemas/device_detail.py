from pydantic import BaseModel, IPvAnyAddress

from ..models.enums import DeviceType, SnmpVersion
from .system_detail import SystemDetail
from .interface_detail import InterfaceDetail
from .route_detail import RouteDetail


class DeviceDetail(BaseModel):
    id: int
    management_ip: IPvAnyAddress
    device_type: DeviceType
    enabled: bool
    snmp_port: int
    snmp_version: SnmpVersion

    system: SystemDetail | None = None
    interfaces: list[InterfaceDetail]
    routes: list[RouteDetail]

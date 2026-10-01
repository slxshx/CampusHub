from pydantic import BaseModel

from .snmp_system import SnmpSystem
from .snmp_interface import SnmpInterface
from .snmp_ipaddress import SnmpIpAddress
from .snmp_route import SnmpRoute


class SnmpDeviceSnapshot(BaseModel):
    system: SnmpSystem
    interfaces: list[SnmpInterface]
    ip_addresses: list[SnmpIpAddress]
    routes: list[SnmpRoute]

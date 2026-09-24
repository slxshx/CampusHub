from pydantic import BaseModel, IPvAnyAddress
from typing import ClassVar

class SnmpIpAddress(BaseModel): 
    TABLE_NAME: ClassVar[str] = "snmp_ipaddress"

    device_id: int
    interface_index: int
    address: IPvAnyAddress
    subnet_mask: IPvAnyAddress | None = None

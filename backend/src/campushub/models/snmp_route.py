from pydantic import BaseModel, IPvAnyAddress
from typing import ClassVar

class SnmpRoute(BaseModel):
    TABLE_NAME: ClassVar[str] = "snmp_route"

    device_id: int
    interface_index: int
    destination: IPvAnyAddress
    subnet_mask: IPvAnyAddress | None = None
    next_hop: IPvAnyAddress | None = None
    route_type: int | None = None
    protocol: int | None = None
    age: int | None = None

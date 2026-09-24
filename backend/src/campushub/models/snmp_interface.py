from pydantic import BaseModel
from typing import ClassVar

class SnmpInterface(BaseModel):
    TABLE_NAME: ClassVar[str] = "snmp_interface"

    device_id: int
    if_index: int
    description: str | None = None
    interface_type: int | None = None
    mtu: int | None = None
    speed: int | None = None
    mac_address: str | None = None
    admin_status: int | None = None
    oper_status: int | None = None

from pydantic import BaseModel
from typing import ClassVar

class SnmpSystem(BaseModel):
    TABLE_NAME: ClassVar[str] = "snmp_system"

    device_id: int
    description: str | None = None
    object_id: str | None = None
    uptime: str | None = None
    name: str | None = None
    location: str | None = None


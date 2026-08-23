from typing import ClassVar
from pydantic import BaseModel

class Device(BaseModel):
    TABLE_NAME: ClassVar[str] = "devices"

    id: int
    hostname: str
    description: str | None
    device_type: str
    location: str | None


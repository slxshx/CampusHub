from typing import ClassVar
from pydantic import BaseModel

class Device(BaseModel):
    TABLE_NAME: ClassVar[str] = "devices"

    id: int
    hostname: str
    description: str | None = None
    device_type: str
    location: str | None = None

class CreateDevice(BaseModel):
    TABLE_NAME: ClassVar[str] = "devices"

    hostname: str
    description: str | None = None
    device_type: str
    location: str | None = None

class UpdateDevice(BaseModel):
    TABLE_NAME: ClassVar[str] = "devices"

    hostname: str | None = None
    description: str | None = None
    device_type: str | None = None
    location: str | None = None


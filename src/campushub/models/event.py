from datetime import datetime
from typing import ClassVar
from pydantic import BaseModel

class Event(BaseModel):
    TABLE_NAME: ClassVar[str] = "events"

    id: int
    device_id: int
    timestamp: datetime
    type: str
    description: str | None = None

class CreateEvent(BaseModel):
    TABLE_NAME: ClassVar[str] = "events"

    device_id: int
    timestamp: datetime
    type: str
    description: str | None = None

class UpdateEvent(BaseModel):
    TABLE_NAME: ClassVar[str] = "events"

    type: str | None = None
    description: str | None = None


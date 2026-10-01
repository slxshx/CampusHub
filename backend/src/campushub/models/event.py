from datetime import datetime
from typing import ClassVar
from pydantic import BaseModel

from .enums import EventSeverity, EventSource

class Event(BaseModel):
    TABLE_NAME: ClassVar[str] = "events"

    id: int
    device_id: int
    interface_index: int | None = None
    timestamp: datetime
    severity: EventSeverity
    event_type: str
    source: EventSource
    message: str

class EventCreate(BaseModel):
    TABLE_NAME: ClassVar[str] = "events"

    device_id: int
    interface_index: int | None = None
    severity: EventSeverity
    event_type: str
    source: EventSource
    message: str

    

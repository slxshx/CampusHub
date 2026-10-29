from pydantic import BaseModel
from datetime import datetime
from campushub.models.enums import EventSeverity, EventSource, EventType

class EventDetail(BaseModel):
    id: int
    device_id: int
    interface_index: int | None = None
    timestamp: datetime
    severity: EventSeverity
    event_type: EventType
    source: EventSource
    message: str



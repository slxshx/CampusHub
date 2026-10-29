from fastapi import APIRouter

from campushub.schemas.event_detail import EventDetail
from campushub.services.event_read_service import EventReadService

event_router = APIRouter()
event_read_service = EventReadService()


@event_router.get("/events", response_model=list[EventDetail])
def get_events():
    return event_read_service.get_events()


@event_router.get(
    "/devices/{device_id}/events",
    response_model=list[EventDetail]
)
def get_events_by_device_id(device_id: int):
    return event_read_service.get_events_by_device(device_id)

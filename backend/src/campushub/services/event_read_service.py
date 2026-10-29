from campushub.repositories.event_repository import EventRepository
from campushub.schemas.event_detail import EventDetail

class EventReadService():
    def __init__(self) -> None:
        self.events: EventRepository = EventRepository()

    def get_events(self) -> list[EventDetail]:
        events = self.events.get_events()

        return [
                EventDetail.model_validate(event.model_dump())
                for event in events
                ]

    def get_events_by_device(self, device_id: int) -> list[EventDetail]:
        events = self.events.get_events_by_device(device_id)

        return [
                EventDetail.model_validate(event.model_dump())
                for event in events
                ]





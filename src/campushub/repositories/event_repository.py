from campushub.models.event import Event, CreateEvent, UpdateEvent
from ..repositories.base_repository import BaseRepository

class EventRepository(BaseRepository):
    def get_all_events(self) -> list[Event]:
        return self.get_all(Event, Event.TABLE_NAME)

    def get_event_by_id(self, entity_id: int) -> Event | None:
        return self.get_by_id(entity_id, Event, Event.TABLE_NAME)

    def create_event(self, create_event: CreateEvent) -> Event | None:
        return self.create(create_event, Event, Event.TABLE_NAME)

    def update_event(self, entity_id: int, update_event: UpdateEvent) -> bool:
        return self.update(entity_id, update_event, Event.TABLE_NAME)

    def delete_event(self, entity_id: int) -> bool:
        return self.delete_by_id(entity_id, Event.TABLE_NAME)







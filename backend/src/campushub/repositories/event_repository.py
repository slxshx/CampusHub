from psycopg.rows import dict_row
from psycopg.sql import SQL, Identifier

from .base_repository import BaseRepository
from ..database.connection import get_connection
from ..models.event import Event, EventCreate


class EventRepository(BaseRepository):

    def get_events(self) -> list[Event]:
        return BaseRepository.get_all(
            self,
            Event,
            Event.TABLE_NAME,
        )

    def create_event(self, event: EventCreate) -> Event | None:
        return BaseRepository.create(
            self,
            event,
            Event,
            Event.TABLE_NAME,
        )

    def get_events_by_device(self, device_id: int) -> list[Event]:
        with get_connection() as connection:
            with connection.cursor(row_factory=dict_row) as cursor:
                query = SQL("""
                    SELECT *
                    FROM {}
                    WHERE device_id = %s
                    ORDER BY timestamp DESC
                """).format(
                    Identifier(Event.TABLE_NAME)
                )

                cursor.execute(query, (device_id,))
                results = cursor.fetchall()

                return [
                    Event(**result)
                    for result in results
                ]

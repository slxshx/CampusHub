from psycopg.rows import dict_row
from psycopg.sql import SQL, Identifier

from ..database.connection import get_connection
from ..models.snmp_system import SnmpSystem


class SnmpSystemRepository:

    def get_by_device(self, device_id: int) -> SnmpSystem | None:
        with get_connection() as connection:
            with connection.cursor(row_factory=dict_row) as cursor:
                query = SQL(
                    "SELECT * FROM {} WHERE device_id = %s"
                ).format(
                    Identifier(SnmpSystem.TABLE_NAME)
                )

                cursor.execute(query, (device_id,))
                result = cursor.fetchone()

                if result is None:
                    return None

                return SnmpSystem(**result)

    def upsert(self, system: SnmpSystem) -> SnmpSystem:
        with get_connection() as connection:
            with connection.cursor(row_factory=dict_row) as cursor:
                query = SQL("""
                    INSERT INTO {} (
                        device_id,
                        description,
                        object_id,
                        uptime,
                        name,
                        location
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (device_id)
                    DO UPDATE SET
                        description = EXCLUDED.description,
                        object_id = EXCLUDED.object_id,
                        uptime = EXCLUDED.uptime,
                        name = EXCLUDED.name,
                        location = EXCLUDED.location
                    RETURNING *
                """).format(
                    Identifier(SnmpSystem.TABLE_NAME)
                )

                cursor.execute(
                    query,
                    (
                        system.device_id,
                        system.description,
                        system.object_id,
                        system.uptime,
                        system.name,
                        system.location,
                    ),
                )

                result = cursor.fetchone()

                if result is None:
                    raise RuntimeError("SNMP system upsert failed")

                return SnmpSystem(**result)

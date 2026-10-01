from psycopg.rows import dict_row
from psycopg.sql import SQL, Identifier

from ..database.connection import get_connection
from ..models.snmp_route import SnmpRoute


class SnmpRouteRepository:

    def get_by_device(self, device_id: int) -> list[SnmpRoute]:
        with get_connection() as connection:
            with connection.cursor(row_factory=dict_row) as cursor:
                query = SQL("""
                    SELECT *
                    FROM {}
                    WHERE device_id = %s
                    ORDER BY destination
                """).format(
                    Identifier(SnmpRoute.TABLE_NAME)
                )

                cursor.execute(query, (device_id,))
                results = cursor.fetchall()

                return [
                    SnmpRoute(**result)
                    for result in results
                ]

    def replace_for_device(
        self,
        device_id: int,
        routes: list[SnmpRoute],
    ) -> None:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                delete_query = SQL(
                    "DELETE FROM {} WHERE device_id = %s"
                ).format(
                    Identifier(SnmpRoute.TABLE_NAME)
                )

                cursor.execute(delete_query, (device_id,))

                if not routes:
                    return

                insert_query = SQL("""
                    INSERT INTO {} (
                        device_id,
                        interface_index,
                        destination,
                        subnet_mask,
                        next_hop,
                        route_type,
                        protocol,
                        age
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """).format(
                    Identifier(SnmpRoute.TABLE_NAME)
                )

                values = [
                    (
                        route.device_id,
                        route.interface_index,
                        route.destination,
                        route.subnet_mask,
                        route.next_hop,
                        route.route_type,
                        route.protocol,
                        route.age,
                    )
                    for route in routes
                ]

                cursor.executemany(insert_query, values)

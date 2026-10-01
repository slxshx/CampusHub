from psycopg.rows import dict_row
from psycopg.sql import SQL, Identifier

from ..database.connection import get_connection
from ..models.snmp_interface import SnmpInterface


class SnmpInterfaceRepository:

    def get_by_device(self, device_id: int) -> list[SnmpInterface]:
        with get_connection() as connection:
            with connection.cursor(row_factory=dict_row) as cursor:
                query = SQL("""
                    SELECT *
                    FROM {}
                    WHERE device_id = %s
                    ORDER BY if_index
                """).format(
                    Identifier(SnmpInterface.TABLE_NAME)
                )

                cursor.execute(query, (device_id,))
                results = cursor.fetchall()

                return [
                    SnmpInterface(**result)
                    for result in results
                ]

    def replace_for_device(
        self,
        device_id: int,
        interfaces: list[SnmpInterface],
    ) -> None:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                delete_query = SQL(
                    "DELETE FROM {} WHERE device_id = %s"
                ).format(
                    Identifier(SnmpInterface.TABLE_NAME)
                )

                cursor.execute(delete_query, (device_id,))

                if not interfaces:
                    return

                insert_query = SQL("""
                    INSERT INTO {} (
                        device_id,
                        if_index,
                        description,
                        interface_type,
                        mtu,
                        speed,
                        mac_address,
                        admin_status,
                        oper_status
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """).format(
                    Identifier(SnmpInterface.TABLE_NAME)
                )

                values = [
                    (
                        interface.device_id,
                        interface.if_index,
                        interface.description,
                        interface.interface_type,
                        interface.mtu,
                        interface.speed,
                        interface.mac_address,
                        interface.admin_status,
                        interface.oper_status,
                    )
                    for interface in interfaces
                ]

                cursor.executemany(insert_query, values)

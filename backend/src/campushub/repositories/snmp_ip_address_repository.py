from psycopg.rows import dict_row
from psycopg.sql import SQL, Identifier

from ..database.connection import get_connection
from ..models.snmp_ipaddress import SnmpIpAddress


class SnmpIpAddressRepository:

    def get_by_device(self, device_id: int) -> list[SnmpIpAddress]:
        with get_connection() as connection:
            with connection.cursor(row_factory=dict_row) as cursor:
                query = SQL("""
                    SELECT *
                    FROM {}
                    WHERE device_id = %s
                    ORDER BY interface_index, address
                """).format(
                    Identifier(SnmpIpAddress.TABLE_NAME)
                )

                cursor.execute(query, (device_id,))
                results = cursor.fetchall()

                return [
                    SnmpIpAddress(**result)
                    for result in results
                ]

    def replace_for_device(
        self,
        device_id: int,
        ip_addresses: list[SnmpIpAddress],
    ) -> None:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                delete_query = SQL(
                    "DELETE FROM {} WHERE device_id = %s"
                ).format(
                    Identifier(SnmpIpAddress.TABLE_NAME)
                )

                cursor.execute(delete_query, (device_id,))

                if not ip_addresses:
                    return

                insert_query = SQL("""
                    INSERT INTO {} (
                        device_id,
                        interface_index,
                        address,
                        subnet_mask
                    )
                    VALUES (%s, %s, %s, %s)
                """).format(
                    Identifier(SnmpIpAddress.TABLE_NAME)
                )

                values = [
                    (
                        ip_address.device_id,
                        ip_address.interface_index,
                        ip_address.address,
                        ip_address.subnet_mask,
                    )
                    for ip_address in ip_addresses
                ]

                cursor.executemany(insert_query, values)

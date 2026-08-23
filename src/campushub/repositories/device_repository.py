from psycopg.rows import dict_row

from campushub.models.device import Device
from ..database.connection import get_connection

def get_all_devices() -> list[Device]:
    connection = get_connection()

    cursor = connection.cursor(row_factory=dict_row)

    cursor.execute("SELECT * FROM devices;")

    rows = cursor.fetchall()

    devices = []

    for row in rows:
        device = Device(**row)
        devices.append(device)
        

    cursor.close()
    connection.close()

    return devices





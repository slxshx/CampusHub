from psycopg.rows import dict_row
from psycopg.sql import SQL, Identifier
from ..database.connection import get_connection

class BaseRepository():
    def get_all(self, model, table):
        connection = get_connection()

        cursor = connection.cursor(row_factory=dict_row)

        query = SQL("SELECT * FROM {}").format(
                Identifier(table)
                )

        cursor.execute(query)

        results = cursor.fetchall()

        data = []

        for result in results:
            row = model(**result)
            data.append(row)

        cursor.close()
        connection.close()

        return data

from psycopg.rows import dict_row
from psycopg.sql import SQL, Identifier
from ..database.connection import get_connection
from psycopg.sql import Placeholder

class BaseRepository():
    def get_all(self, model, table):
        with get_connection() as connection:
            with connection.cursor(row_factory=dict_row) as cursor:

                query = SQL("SELECT * FROM {}").format(
                        Identifier(table)
                        )

                cursor.execute(query)

                results = cursor.fetchall()

                data = []

                for result in results:
                    row = model(**result)
                    data.append(row)

                return data

    def get_by_id(self, entity_id, model, table):
        with get_connection() as connection:
            with connection.cursor(row_factory=dict_row) as cursor:

                query = SQL("SELECT * FROM {} WHERE id = %s").format(
                        Identifier(table)
                        )

                cursor.execute(query, (entity_id,))

                result = cursor.fetchone()

                if result is None:
                    return None

                data = model(**result)

                return data

    def delete_by_id(self, entity_id, table) -> bool:
        with get_connection() as connection:
            with connection.cursor(row_factory=dict_row) as cursor:

                query = SQL("DELETE FROM {} WHERE id = %s").format(
                        Identifier(table)
                        )

                cursor.execute(query, (entity_id,))

                result = cursor.rowcount

                if result > 0:
                    return True

                return False

    def create(self, input_model, output_model, table):
        with get_connection() as connection:
            with connection.cursor(row_factory=dict_row) as cursor:

                data = input_model.model_dump()
                keys = data.keys()
                values = tuple(data.values())
                placeholder_count = len(keys)

                placeholders = []

                for _ in range(placeholder_count):
                    placeholders.append(Placeholder())

                placeholder_sql = SQL(', ').join(placeholders)

                columns = []

                for key in keys:
                    columns.append(Identifier(key))

                columns_sql = SQL(", ").join(columns)


                query = SQL("INSERT INTO {} ({}) VALUES ({}) RETURNING *").format(
                        Identifier(table),
                        columns_sql,
                        placeholder_sql
                        )

                cursor.execute(query, values)

                result = cursor.fetchone()

                if result is None:
                    return None

                return output_model(**result)

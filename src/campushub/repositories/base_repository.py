from psycopg.rows import dict_row
from psycopg.sql import SQL, Composable, Identifier, Placeholder
from ..database.connection import get_connection
from typing import TypeVar
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)
TOutput = TypeVar("TOutput", bound=BaseModel)

class BaseRepository():
    def get_all(self, model: type[T], table: str) -> list[T]:
        with get_connection() as connection:
            with connection.cursor(row_factory=dict_row) as cursor:

                query = SQL("SELECT * FROM {}").format(
                        Identifier(table)
                        )

                _ = cursor.execute(query)

                results = cursor.fetchall()

                data: list[T] = []

                for result in results:
                    row = model(**result)
                    data.append(row)

                return data

    def get_by_id(self, entity_id: int, model: type[T], table: str) -> T | None:
        with get_connection() as connection:
            with connection.cursor(row_factory=dict_row) as cursor:

                query = SQL("SELECT * FROM {} WHERE id = %s").format(
                        Identifier(table)
                        )

                _ = cursor.execute(query, (entity_id,))

                result = cursor.fetchone()

                if result is None:
                    return None

                data = model(**result)

                return data

    def delete_by_id(self, entity_id: int, table: str) -> bool:
        with get_connection() as connection:
            with connection.cursor(row_factory=dict_row) as cursor:

                query = SQL("DELETE FROM {} WHERE id = %s").format(
                        Identifier(table)
                        )

                _ = cursor.execute(query, (entity_id,))

                result = cursor.rowcount

                if result > 0:
                    return True

                return False

    def create(self, input_model: BaseModel, output_model: type[TOutput], table: str) -> TOutput | None:
        with get_connection() as connection:
            with connection.cursor(row_factory=dict_row) as cursor:

                data = input_model.model_dump()
                
                keys = data.keys()
                values = tuple(data.values())
                placeholder_count = len(keys)

                placeholders: list[Composable] = []

                for _ in range(placeholder_count):
                    placeholders.append(Placeholder())

                placeholder_sql = SQL(', ').join(placeholders)

                columns: list[Composable] = []

                for key in keys:
                    columns.append(Identifier(key))

                columns_sql = SQL(", ").join(columns)


                query = SQL("INSERT INTO {} ({}) VALUES ({}) RETURNING *").format(
                        Identifier(table),
                        columns_sql,
                        placeholder_sql
                        )

                _ = cursor.execute(query, values)

                result = cursor.fetchone()

                if result is None:
                    return None

                return output_model(**result)

    def update(self, entity_id: int, input_model: BaseModel, table: str) -> bool:
        with get_connection() as connection:
            with connection.cursor(row_factory=dict_row) as cursor:

                data = input_model.model_dump(exclude_unset=True)

                if not data:
                    return False

                values = tuple(data.values())

                set_parts: list[Composable] = []

                for key in data.keys():
                    set_parts.append(SQL("{} = {}").format(
                        
                            Identifier(key),
                            Placeholder()
                            ))

                set_sql = SQL(", ").join(set_parts)

                query = SQL("UPDATE {} SET {} WHERE id = %s").format(
                        Identifier(table),
                        set_sql
                        )

                parameters = values + (entity_id,)

                _ = cursor.execute(query, parameters)

                result = cursor.rowcount

                if result > 0:
                    return True

                return False

from psycopg import Connection, connect
from ..config.settings import Settings


settings = Settings()

def get_connection() -> Connection:
    return connect(
            host=settings.db_host,
            port=settings.db_port,
            dbname=settings.db_name,
            user=settings.db_user,
            password=settings.db_password
            )





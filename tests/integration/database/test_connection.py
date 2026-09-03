from campushub.database.connection import get_connection


def test_connection_uses_test_database(monkeypatch):
    monkeypatch.setenv("DB_NAME", "campushub_test")

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT current_database();")
            result = cursor.fetchone()

    assert result is not None
    assert result[0] == "campushub_test"

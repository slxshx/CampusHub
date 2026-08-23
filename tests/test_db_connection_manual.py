from campushub.database.connection import get_connection

connection = get_connection();

print(connection)

connection.close()

from db import engine

def get_connection():
    connection = engine.connect()
    try:
        yield connection
    finally:
        connection.close()

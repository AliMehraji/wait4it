from typing import Tuple
import psycopg
from checker.consul_check import create_consul_client


def can_establish_database_connection(prefix: str, key: str) -> Tuple[bool, str]:
    """
    Checks if a connection to the database can be established using parameters stored in Consul.

    This function retrieves database connection parameters from Consul using the provided prefix and key,
    and attempts to establish a connection to the database. If successful, it executes a simple query
    to verify the connection.

    Args:
        prefix (str): The prefix used in Consul to locate the database configuration.
        key (str): The key used in Consul to locate the specific database configuration.

    Returns:
        Tuple[bool, str]: A tuple containing a boolean indicating success (True) or failure (False),
                          and a message describing the result or the exception if failed.
    """

    consul_client = create_consul_client()
    connection = None
    cursor = None
    try:
        database_keys = consul_client.get(f"{prefix}/{key}", {})
        db_params = {
            "host": database_keys.get("DB_HOST", "DATABASE_HOST"),
            "port": database_keys.get("DB_PORT", "DATABASE_PORT"),
            "user": database_keys.get("DB_USER", "DATABASE_USER"),
            "password": database_keys.get("DB_PASS", "DATABASE_PASS"),
            "dbname": database_keys.get("DB_NAME", "DATABASE_NAME"),
        }
        connection = psycopg.connect(**db_params)
        cursor = connection.cursor()
        query = "SELECT datname FROM pg_database;"
        cursor.execute(query)
        cursor.fetchone()

    except Exception as database_exception:
        return False, str(database_exception)

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
    return True, f"host: {db_params["host"]} on port: {db_params["port"]}"

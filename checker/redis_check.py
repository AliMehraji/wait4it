from typing import Tuple
import uuid
import redis

from checker.consul_check import create_consul_client


def can_establish_redis_connection(prefix, key) -> Tuple[bool, str]:
    """
    Attempts to establish a connection to a Redis server using and performs a basic operation
    
    This function try to connect to redis server , set and get a random key in redis 
    if it can set and then get the same key it returns True.

    Args:
        prefix (str): The prefix used to construct the key path in Consul to retrieve Redis connection details.
        key (str): The key path within the Consul prefix that stores Redis connection details.

    Returns:
        tuple[bool, str]: A tuple containing a boolean indicating success and a message providing details.
            - The boolean is True if a connection is established and the basic operation is successful, False otherwise.
            - The message provides information about the connection or an error message.

    Raises:
        Exception: Any exception encountered while connecting to or interacting with the Redis server.
    """

    try:
        consul_client = create_consul_client()
        redis_keys = consul_client.get(f"{prefix}/{key}", {})
        # Connect to the Redis server
        redis_params = {
            "host": redis_keys.get("REDIS_HOST", "localhost"),
            "port": redis_keys.get("REDIS_PORT", "6379"),
            "db": 0,
            "decode_responses": True,
            "retry_on_timeout": True,
            "socket_connect_timeout": 10,
            "socket_timeout": 10
        }
        redis_connection = redis.Redis(**redis_params)

        # Set and get a random uuid key to perform a basic operation
        uuid_key = f"health-check-key-{str(uuid.uuid4())}"
        uuid_value = f"health-check-value-{str(uuid.uuid4())}"
        redis_connection.set(uuid_key, uuid_value)
        result = redis_connection.get(uuid_key)

        if result:
            # redis_connection.delete(uuid_key)
            redis_connection.delete(uuid_key)
            return True, f"host: {redis_params["host"]} on port: {redis_params["port"]}"
        return False, f"Key {uuid_key} Not Found."

    except Exception as redis_exception:
        return False, redis_exception

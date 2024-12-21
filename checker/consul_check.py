import os
import json
from typing import Tuple
import consul


class ConsulClient:
    """
    A client for interacting with a Consul key-value store.

    Attributes:
        consul (consul.Consul): An instance of the Consul client.

    Methods:
        get(key, default=None) -> json: Retrieves the value for the given key from the Consul.
    """

    def __init__(self, host: str = "localhost", port: int = 8500, scheme: str = "http"):
        self.consul = consul.Consul(host=host, port=port, scheme=scheme)

    def get(self, key: str, default=None) -> json:
        """
        Retrieves the value for the given key from the Consul key-value store.

        Args:
            - key (str): The key to retrieve the value for.
            - default (Any): The default value to return if the key is not found. Defaults to None.

        Returns:
            json: The value associated with the key, parsed as JSON.

        Raises:
            KeyError: If the key is not found and no default value is provided.
            json.JSONDecodeError: If the value cannot be parsed as JSON.
        """
        _, data = self.consul.kv.get(key)
        string_value = data["Value"].decode("utf-8")
        return json.loads(string_value)


def create_consul_client():
    """
    Creates and returns a ConsulClient instance using environment variables for configuration.

    The function reads the `CONSUL_HOST` and `CONSUL_PORT` environment variables to configure the client.
    If these variables are not set, it defaults to "localhost" for the host and 8500 for the port.

    Returns:
        ConsulClient: An instance of ConsulClient configured with the specified or default host and port.
    """
    consul_host = os.getenv("CONSUL_HOST", "localhost")
    consul_port = int(os.getenv("CONSUL_PORT", "8500"))
    return ConsulClient(host=consul_host, port=consul_port)


def can_connect_to_consul(consul_connection_check_key:str = "consul_connection_check") -> Tuple[bool, str]:
    """
    Checks if a connection to the Consul server can be established.

    The function attempts to retrieve a value from the Consul key-value store using a key
    named "CONSUL_CONNECTION". If the retrieval is successful, it indicates that the connection
    to the Consul server is successful.

    Returns:
        tuple: A tuple containing a boolean indicating success (True) or failure (False),
               and a message or exception object describing the result.
    """
    try:
        consul_client = create_consul_client()
        consul_client.get(consul_connection_check_key, {})
    except Exception as consul_exception:
        return False, str(consul_exception)
    return True, "Successful"

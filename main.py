import os
import sys
from checker.consul_check import can_connect_to_consul
from checker.logger import setup_logger
from checker.database_check import can_establish_database_connection
from checker.redis_check import can_establish_redis_connection
from checker.rabbitmq_check import perform_rabbitmq_operations

logger = setup_logger()

def connection_check_decorator():

    """
    Decorator to check the connection status of a service and log the result.

    This decorator wraps a function that checks the connection status of a service.
    It logs the success or failure of the connection attempt and returns the connection status.
    The wrapped function should return a tuple containing a boolean status and a message.

    The log entries include the service key and message, and they use a logging tag that
    matches the service key.

    Returns:
        - `function`: The decorator function that wraps the connection-checking function.

    Example:
        ```python
        @connection_check_decorator()
        def check_database_connection(consul_prefix: str, key: str):
            return can_establish_database_connection(consul_prefix, key)

        check_database_connection("some_prefix", "DATABASE")
        ```
    """
    def decorator(func):
        def wrapper(consul_prefix: str, key: str):
            ok_status, message = func(consul_prefix, key)
            if ok_status:
                logger.info(f"{key} connection successful: %s", message, extra={"tag": key})
            else:
                logger.error(f"{key} connection failed: %s", message, extra={"tag": key})
            return ok_status
        return wrapper
    return decorator

def get_consul_configuration():

    """
    Retrieves and processes Consul configuration from environment variables.

    This function fetches the Consul configuration settings from environment variables.
    The mandatory keys are required to be present in the environment.
    The optional keys are retrieved if present; otherwise, an empty list is used.
    Specifically, it retrieves:
        - `CONSUL_PREFIX`
        - `CONSUL_MANDATORY_KEYS`
        - `CONSUL_OPTIONAL_KEYS`
    
    Returns:
        tuple: A tuple containing:
        - `consul_prefix` (str): The prefix used for Consul keys.
        - `consul_mandatory_keys` (list): A list of mandatory Consul keys.
        - `consul_optional_keys` (list): A list of optional Consul keys.

    Raises:
        `EnvironmentError` If below environment variables are now set
        - `CONSUL_PREFIX`
        - `CONSUL_MANDATORY_KEYS` 
    """

    consul_prefix = os.getenv("CONSUL_PREFIX", default=None)
    consul_mandatory_keys = os.getenv("CONSUL_MANDATORY_KEYS", default=None)
    consul_optional_keys = os.getenv("CONSUL_OPTIONAL_KEYS", "")
    consul_connection_check_key = os.getenv("CONSUL_CONNECTION_CHECK_KEY", "")

    if not consul_prefix:
        raise EnvironmentError("CONSUL_PREFIX is not set in environment variables")
    if not consul_mandatory_keys:
        raise EnvironmentError("CONSUL_MANDATORY_KEYS is not set in environment variables")
    if not consul_connection_check_key:
        raise EnvironmentError("CONSUL_CONNECTION_CHECK_KEY is not set in environment variables")
    return consul_connection_check_key, consul_prefix, consul_mandatory_keys.split(","), consul_optional_keys.split(",")


@connection_check_decorator()
def check_database_connection(consul_prefix: str, key: str):
    """
    Checks the database connection status and logs the result.

    This function attempts to establish a connection to the database using the given
    Consul prefix and key. It logs the success or failure of the connection attempt
    and returns the connection status.

    Args:
        - `consul_prefix` (str): The Consul prefix used for the connection.
        - `key` (str): The specific key used for the database connection.

    Returns:
        - `bool`: True if the connection was successful, False otherwise.
    """
    return can_establish_database_connection(consul_prefix, key)

@connection_check_decorator()
def check_redis_connection(consul_prefix: str, key: str):
    """
    Checks the redis connection status and logs the result.

    This function attempts to establish a connection to the redis using the given
    Consul prefix and key. It logs the success or failure of the connection attempt
    and returns the connection status.

    Args:
        - `consul_prefix` (str): The Consul prefix used for the connection.
        - `key` (str): The specific key used for the database connection.

    Returns:
        - `bool`: True if the connection was successful, False otherwise.
    """
    return can_establish_redis_connection(consul_prefix, key)

@connection_check_decorator()
def check_rabbitmq_connection(consul_prefix: str, key: str):
    """
    Checks connection and performs an action on rabbitmq status and logs the result.

    This function attempts to Checks connection and performs action on rabbitmq using the given
    Consul prefix and key. It logs the success or failure of the connection attempt
    and returns the connection status.

    Args:
        - `consul_prefix` (str): The Consul prefix used for the connection.
        - `key` (str): The specific key used for the database connection.

    Returns:
        - `bool`: True if the connection was successful, False otherwise.
    """
    return perform_rabbitmq_operations(consul_prefix, key)

def keys_check_decorator():
    """
    Decorator to check the status of multiple keys using specified functions.

    This decorator wraps a function that checks the status of multiple keys.
    It iterates over the provided keys and applies corresponding functions from
    a dictionary to check their status. The wrapped function should return True
    if all keys pass their checks, and False if any key fails its check.

    The wrapped function should accept the following parameters:
        - `prefix` (str): A prefix used in the checks.
        - `keys` (list): A list of keys to be checked.
        - `functions` (dict): A dictionary mapping keys to their corresponding check functions.

    Returns:
        - `function`: The decorator function that wraps the key-checking function.
    """
    def decorator(func):
        def wrapper(prefix: str, keys: list, functions: dict):
            checks_passed = True
            for key in keys:
                if key in functions:
                    if not functions[key](prefix, key):
                        checks_passed = False
            return checks_passed
        return wrapper
    return decorator

@keys_check_decorator()
def mandatory_keys_check(prefix: str, keys: list, functions: dict):
    """
    Mandatory Keys Function.
    """
    return mandatory_keys_check(prefix, keys, functions)

@keys_check_decorator()
def optional_keys_check(prefix: str, keys: list, functions: dict):
    """
    Optional Keys Function.
    """
    return optional_keys_check(prefix, keys, functions)

if __name__ == "__main__":
    try:
        # Getting consul Env from os env
        consul_connection_check_key, consul_prefix, consul_mandatory_keys, consul_optional_keys = get_consul_configuration()
        
        # Connection To Consul as very first check
        # If couldn't connect to consul, exit.
        consul_ok_status, consul_message = can_connect_to_consul(consul_connection_check_key)
        if not consul_ok_status:
            logger.error(
                "Consul connection failed: %s", consul_message, extra={"tag": "CONSUL"}
            )
            sys.exit(1)

        logger.info(
            "Consul connection successful: %s", consul_message, extra={"tag": "CONSUL"}
        )


        keys_functions = {
            "DATABASE": check_database_connection,
            "REDIS": check_redis_connection,
            "RABBITMQ": check_rabbitmq_connection,
        }

        if not optional_keys_check(consul_prefix, consul_optional_keys, keys_functions):
            logger.info("Optional Keys Check Failed.", extra={"tag": "OPTIONAL_KEYS_CHECK"})
        if not mandatory_keys_check(consul_prefix, consul_mandatory_keys, keys_functions):
            logger.info("Mandatory Keys Check Failed.", extra={"tag": "MANDATORY_KEYS_CHECK"})
            sys.exit(1)

        sys.exit(0)

    except EnvironmentError as env_err:
        logger.error(
            "Environment configuration error: %s", env_err, extra={"tag": "ENV_ERROR"}
        )
        sys.exit(1)
    except Exception as main_exception:
        logger.error(
            "Unexpected error: %s", main_exception, extra={"tag": "MAIN_EXCEPTION"}
        )
        sys.exit(1)

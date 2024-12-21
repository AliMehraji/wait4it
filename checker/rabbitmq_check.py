import uuid
from typing import Tuple
import pika
import pika.exceptions

from checker.consul_check import create_consul_client

uuid_queue = f"health-check-queue-{str(uuid.uuid4())}"


def _publish_message(connection) -> Tuple[bool, str]:
    try:
        channel = connection.channel()
        channel.queue_declare(queue=f'{uuid_queue}')
        channel.basic_publish(
            exchange='',
            routing_key=f'{uuid_queue}',
            body=bytes("RabbitMQ Health Checking", encoding="utf-8")
        )
        return True, "Successful"
    except Exception as publish_exception:
        return False, str(publish_exception)
    finally:
        channel.close()


def _on_message_callback(ch, method, properties, body):
    ch.stop_consuming()
    ch.queue_delete(queue=f'{uuid_queue}')


def _consume_messages(connection) -> Tuple[bool, str]:
    try:
        channel = connection.channel()
        channel.queue_declare(queue=f'{uuid_queue}')
        channel.basic_consume(
            queue=f'{uuid_queue}',
            on_message_callback=_on_message_callback,
            auto_ack=True
        )
        channel.start_consuming()
        return True, "Successful"
    except Exception as consume_exception:
        return False, str(consume_exception)
    finally:
        channel.close()
        connection.close()


def perform_rabbitmq_operations(prefix: str, key: str) -> Tuple[bool, str]:
    """
    Establishes a connection to a RabbitMQ server using credentials and connection details retrieved
    from Consul and performs message publishing and consuming operations.

    Args:
        prefix (str): The prefix used to construct the key path in Consul to retrieve RabbitMQ connection details.
        key (str): The key path within the Consul prefix that stores RabbitMQ connection details.

    Returns:
        tuple[bool, str]: A tuple containing a boolean indicating success and a message providing details.
            - The boolean is True if both publishing and consuming messages were successful, False otherwise.
            - The message provides information about the connection or an error message if a connection error occurs.

    Raises:
        pika.exceptions.AMQPConnectionError: If an error occurs while connecting to the RabbitMQ server.
    """

    try:
        consul_client = create_consul_client()
        rabbitmq_keys = consul_client.get(f"{prefix}/{key}", {})

        # Define the connection parameters
        credentials = pika.PlainCredentials(
            rabbitmq_keys.get("RABBITMQ_USERNAME", "DEFAULT_USERNAME"),
            rabbitmq_keys.get("RABBITMQ_PASSWORD", "DEFAULT_PASSWORD")
        )
        connection_params = pika.ConnectionParameters(
            host=rabbitmq_keys.get("RABBITMQ_HOSTNAME", "localhost"),
            port=rabbitmq_keys.get("RABBITMQ_PORT", "5672"),
            credentials=credentials
        )
        connection = pika.BlockingConnection(connection_params)
    except pika.exceptions.AMQPConnectionError:
        return False, f"Connection Error! {connection_params}"

    published, _ = _publish_message(connection)
    if published:
        consumed, _ = _consume_messages(connection)
        if consumed:
            return True, f"host: {connection_params.host} on port: {connection_params.port}"

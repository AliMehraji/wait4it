# Kubernetes Init Container - Dependency Checker

This repository provides a Python script designed to be used as a Kubernetes Init Container. The script ensures that all necessary dependencies are available before the main application starts. It checks connections to PostgreSQL, Redis, RabbitMQ, and HashiCorp Consul, and verifies environment variables retrieved from Consul.

## Features

- Validates PostgreSQL database connection.
- Checks Redis availability.
- Confirms RabbitMQ connection.
- Fetches and verifies environment variables from HashiCorp Consul.
- Waits until all dependencies are ready before proceeding.

## Requirements

- Python 3.8+
- Kubernetes cluster
- HashiCorp Consul
- Access to the required services (PostgreSQL, Redis, RabbitMQ, and Consul).

## Environment Variables

The script uses the following environment variables to configure connections:

| Variable | Description | Type | Default |
| -------- | ----------- |----- | ------- |
| `CONSUL_HOST` | Hostname or IP of the Consul server. | `str` | `localhost` |
| `CONSUL_PORT` | Port number of the Consul server. | `int` | `8500` |
| `CONSUL_PREFIX` | The prefix used for Consul keys. | `str` | `None` |
| `CONSUL_MANDATORY_KEYS` | Mandatory Consul keys. | `list` | `None` |
| `CONSUL_OPTIONAL_KEYS` | Optional Consul keys. | `list` | `""` |
| `CONSUL_CONNECTION_CHECK_KEY` | An Arbitrary Key has to be set in Consul, to check the Consul its own connectivity. | `str` | `""` |
| `DB_HOST` | Hostname or IP of the PostgreSQL server. | `str` | `DATABASE_HOST` |
| `DB_PORT` | Port number of the PostgreSQL server. | `str` | `DATABASE_PORT` |
| `DB_USER` | Username for PostgreSQL authentication.  | `str` | `DATABASE_USER` |
| `DB_PASS` | Password for PostgreSQL authentication. | `str` | `DATABASE_PASS` |
| `DB_NAME` | Name of the PostgreSQL database. | `str` | `DATABASE_NAME` |
| `REDIS_HOST` | Hostname or IP of the Redis server. | `str` | ` localhost` |
| `REDIS_PORT` | Port number of the Redis server. | `str` | `6379` |
| `RABBITMQ_HOSTNAME` | Hostname or IP of the RabbitMQ server. | `str` | `localhost` |
| `RABBITMQ_PORT` | Port number of the RabbitMQ server. | `str` | `5672` |
| `RABBITMQ_USERNAME` | Username for RabbitMQ authentication. | `str` | `DEFAULT_USERNAME` |
| `RABBITMQ_PASSWORD` | Password for RabbitMQ authentication. | `str` | `DEFAULT_PASSWORD` |

## Usage

### Kubernetes Deployment Example

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: example-deployment
spec:
  replicas: 1
  selector:
    matchLabels:
      app: example-app
  template:
    metadata:
      labels:
        app: example-app
    spec:
      initContainers:
      - name: dependency-checker
        image: your-image:tag
        env:
        - name: CONSUL_HOST
          value: "consul.example.com"
        - name: CONSUL_PORT
          value: "8500"
        - name: CONSUL_PREFIX
          value: "config/"
        - name: CONSUL_MANDATORY_KEYS
          value: "redis,postgresql"
        - name: CONSUL_OPTIONAL_KEYS
          value: "rabbitmq"
        # This below key,value has to be set in Consul
        - name: CONSUL_CONNECTION_CHECK_KEY
          value: "consul_connection_key"

      containers:
      - name: example-app
        image: example-app:latest
```

## Docker Build and Push Example

```bash
docker build -t your-image:tag .
docker push your-image:tag
```

## Dependencies

- `py-consul` - HashiCorp Consul client.
- `psycopg` - PostgreSQL client.
- `psycopg[binary]` - contains the optional optimization for PostgreSQL client.
- `redis` - Redis client.
- `pika` - RabbitMQ client.

```bash
pip install -r requirements.txt
```

## License

[MIT](LICENSE)


## Author Information

Created and maintained by Ali Mehraji <a.mehraji75@gmail.com>
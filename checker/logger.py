import json
import logging


class JsonFormatter(logging.Formatter):
    """
    A logging formatter that outputs log records as JSON strings.

    This formatter converts log records into JSON format, including the time,
    logger name, log level, tag, and message.

    Methods:
        format(record: logging.LogRecord) -> str: Formats the specified log record as a JSON string.
    """
    def format(self, record) -> json:
        """
        Formats the specified log record as a JSON string.

        Args:
            record (logging.LogRecord): The log record to format.

        Returns:
            str: The formatted log record as a JSON string.
        """
        log_record = {
            'time': self.formatTime(record, self.datefmt),
            'name': record.name,
            'level': record.levelname,
            'tag': record.tag,
            'message': record.getMessage()
        }
        return json.dumps(log_record)


def setup_logger(name: str = "InitScript", level: int = logging.DEBUG) -> logging.Logger:
    """
    Sets up a logger with a console handler that uses JSON formatting.

    This function creates a logger with the specified name and log level,
    attaches a console handler with a custom JSON formatter, and ensures that
    multiple handlers are not added to the logger.

    Args:
        name (str): The name of the logger. Defaults to "InitScript".
        level (int): The logging level. Defaults to logging.DEBUG.

    Returns:
        logging.Logger: The configured logger.
    """

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        JsonFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', '%Y-%m-%d %H:%M:%S'))

    logger = logging.getLogger(name)
    logger.setLevel(level)
    # Avoid adding handlers multiple times in case of multiple imports
    if not logger.handlers:
        logger.addHandler(console_handler)

    return logger

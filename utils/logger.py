import logging
import os
from utils.helpers import get_operator_id

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_FILE = os.path.join(BASE_DIR, "data", "app.log")


class OperatorFormatter(logging.Formatter):
    """Custom formatter to inject the operator identity into the log."""
    def format(self, record):
        record.operator_id = get_operator_id()
        return super().format(record)

def setup_logger():
    """Configures the root logger to output to a file and console."""
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

    # Configure the logger
    logger = logging.getLogger('yandex360_app')
    logger.setLevel(logging.INFO)

    # Prevent adding handlers multiple times
    if not logger.handlers:
        formatter = OperatorFormatter('%(asctime)s - %(levelname)s - [Operator: %(operator_id)s] - %(message)s')

        # File handler
        file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Console handler (optional, but good for debugging)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger

def get_logger():
    """Returns the configured logger instance."""
    return logging.getLogger('yandex360_app')

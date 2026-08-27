import logging
import os
import re
import sys
from logging.handlers import RotatingFileHandler
from utils.helpers import get_operator_id


def _get_base_dir() -> str:
    """Returns the base directory for data files.

    When running as a PyInstaller --onefile bundle, sys.executable points to
    the .exe itself, so we use its parent directory.  When running as a plain
    Python script we fall back to the project root.
    """
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


BASE_DIR = _get_base_dir()
LOG_FILE = os.path.join(BASE_DIR, "data", "app.log")

_BOLD = "\033[1m"
_RESET = "\033[0m"
_QUOTED_RE = re.compile(r"'([^']+)'")


class OperatorFormatter(logging.Formatter):
    """Custom formatter to inject the operator identity into the log."""
    def format(self, record):
        record.operator_id = get_operator_id()
        return super().format(record)


class AnsiConsoleFormatter(OperatorFormatter):
    """Console formatter: wraps quoted values in ANSI bold for readability."""
    def format(self, record):
        result = super().format(record)
        return _QUOTED_RE.sub(lambda m: f"'{_BOLD}{m.group(1)}{_RESET}'", result)

def setup_logger():
    """Configures the root logger to output to a file and console."""
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

    # Configure the logger
    logger = logging.getLogger('yandex360_app')
    logger.setLevel(logging.INFO)

    # Prevent adding handlers multiple times
    if not logger.handlers:
        formatter = OperatorFormatter('%(asctime)s - %(levelname)s - [Operator: %(operator_id)s] - %(message)s')

        # File handler with rotation: 5 MB max, 3 backup files
        file_handler = RotatingFileHandler(
            LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3, encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Console handler with ANSI bold highlighting for quoted values
        console_handler = logging.StreamHandler()
        console_formatter = AnsiConsoleFormatter('%(asctime)s - %(levelname)s - [Operator: %(operator_id)s] - %(message)s')
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    return logger

def get_logger():
    """Returns the configured logger instance."""
    return logging.getLogger('yandex360_app')

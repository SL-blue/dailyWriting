"""
Logging configuration for DailyWriting application.

Provides a centralized logging setup with both console and file handlers.
Logs are stored in ~/.dailywriting/logs/ with automatic rotation.
"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import sys

# Log directory in user's home
LOG_DIR = Path.home() / ".dailywriting" / "logs"
LOG_FILE = LOG_DIR / "dailywriting.log"

# Create a custom logger for the application
logger = logging.getLogger("dailywriting")


def setup_logging(debug: bool = False) -> logging.Logger:
    """
    Configure logging for the application.

    Args:
        debug: If True, set console level to DEBUG. Otherwise INFO.

    Returns:
        Configured logger instance.
    """
    # Ensure log directory exists
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    # Set root logger level
    logger.setLevel(logging.DEBUG)

    # Clear any existing handlers
    logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if debug else logging.INFO)
    console_format = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S"
    )
    console_handler.setFormatter(console_format)

    # File handler with rotation (5MB max, keep 3 backups)
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=3,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s:%(funcName)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(file_format)

    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    logger.debug("Logging initialized. Log file: %s", LOG_FILE)

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a child logger for a specific module.

    Args:
        name: Module name (e.g., "storage", "session_manager")

    Returns:
        Logger instance for the module.
    """
    return logger.getChild(name)

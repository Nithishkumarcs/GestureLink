"""
GestureLink - Logging Utility
Provides structured rotating file and console logging for GestureLink.
"""

import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

DEFAULT_LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
DEFAULT_LOG_FILE = os.path.join(DEFAULT_LOG_DIR, "gesturelink.log")

_LOGGER = None


def setup_logger(log_file: str = DEFAULT_LOG_FILE, level: int = logging.INFO) -> logging.Logger:
    """Configures and returns the central logger."""
    global _LOGGER
    if _LOGGER is not None:
        return _LOGGER

    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    logger = logging.getLogger("GestureLink")
    logger.setLevel(level)
    logger.propagate = False

    # Clear any existing handlers
    if logger.hasHandlers():
        logger.handlers.clear()

    # Formatter
    formatter = logging.Formatter(
        fmt="[%(asctime)s] [%(levelname)s] [%(module)s:%(lineno)d] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Rotating File Handler (5 MB max, 3 backups)
    try:
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=5 * 1024 * 1024,
            backupCount=3,
            encoding="utf-8"
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"[WARN] Failed to initialize file logger at {log_file}: {e}", file=sys.stderr)

    # Console Handler with clean formatting
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S"
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    _LOGGER = logger
    _LOGGER.info("=== GestureLink Logging Initialized ===")
    return _LOGGER


def get_logger(name: str = "GestureLink") -> logging.Logger:
    """Retrieves the application logger."""
    global _LOGGER
    if _LOGGER is None:
        return setup_logger()
    return logging.getLogger(name)

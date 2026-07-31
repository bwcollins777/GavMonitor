"""
Application logging.

Creates a logger that writes to both the console and a rotating log file.
"""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler

from config import LOG_FILE, LOG_LEVEL


def get_logger(name: str = "nfd-monitor") -> logging.Logger:
    """
    Create and configure the application logger.

    Multiple calls return the same configured logger without adding duplicate
    handlers.

    Args:
        name:
            Logger name.

    Returns:
        Configured Logger instance.
    """

    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Log file (keeps the last five 1 MB log files)
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=1_048_576,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    # Console output (visible in GitHub Actions logs)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logger.propagate = False

    return logger

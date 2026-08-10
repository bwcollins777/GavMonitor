"""
Shared logging configuration for GavMonitor.

Creates a single application logger that writes to both the console
(GitHub Actions log) and a rotating log file.
"""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler

from config import LOG_FILE, LOG_LEVEL

_LOGGER_NAME = "gavmonitor"


def get_logger(name: str | None = None) -> logging.Logger:
    """
    Return a configured logger.

    The logger is configured only once, regardless of how many modules
    import it.

    Parameters
    ----------
    name
        Optional child logger name.

    Returns
    -------
    logging.Logger
    """

    root_logger = logging.getLogger(_LOGGER_NAME)

    if not root_logger.handlers:

        level = getattr(
            logging,
            LOG_LEVEL.upper(),
            logging.INFO,
        )

        root_logger.setLevel(level)

        formatter = logging.Formatter(
            fmt=(
                "%(asctime)s | "
                "%(levelname)-8s | "
                "%(name)s | "
                "%(message)s"
            ),
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        file_handler = RotatingFileHandler(
            filename=LOG_FILE,
            maxBytes=1_048_576,
            backupCount=5,
            encoding="utf-8",
        )

        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)

        console_handler = logging.StreamHandler()

        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)

        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)

        root_logger.propagate = False

    if name:
        return root_logger.getChild(name)

    return root_logger


def log_startup(logger: logging.Logger) -> None:
    """
    Write a startup banner.
    """

    logger.info("=" * 72)
    logger.info("GavMonitor starting.")
    logger.info("=" * 72)


def log_shutdown(logger: logging.Logger) -> None:
    """
    Write a shutdown banner.
    """

    logger.info("=" * 72)
    logger.info("GavMonitor finished.")
    logger.info("=" * 72)

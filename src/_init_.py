"""
GavMonitor

A production-quality cloud application that monitors the Nashville Fire
Department Active Incidents ArcGIS REST API for new incidents involving
specified apparatus and sends HTML email notifications.

Package Modules
---------------
api.py
    ArcGIS REST API client.

config.py
    Application configuration and constants.

emailer.py
    Gmail SMTP email delivery.

logger.py
    Shared logging configuration.

models.py
    Application data models.

monitor.py
    Main application entry point.

state.py
    Persistent duplicate-alert state management.
"""

from __future__ import annotations

__title__ = "GavMonitor"
__version__ = "2.0.0"
__author__ = "Brian Collins"
__license__ = "MIT"

VERSION = __version__

__all__ = [
    "VERSION",
]

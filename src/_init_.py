"""
Nashville Fire Department Unit Monitor

Monitors the Nashville Fire Department Active Incidents ArcGIS REST API
and sends email notifications when a new incident includes EN41 or EN42.

Modules:
    api.py        - ArcGIS REST API client
    config.py     - Environment configuration
    emailer.py    - HTML email delivery
    logger.py     - Logging configuration
    monitor.py    - Main application entry point
    state.py      - Duplicate alert tracking
"""

__version__ = "1.0.0"
__author__ = "Brian Collins"
__license__ = "MIT"

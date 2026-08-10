"""
Application configuration for GavMonitor.

This module centralizes all configurable values, loads environment
variables, validates required settings, and defines the verified
Nashville Fire Department ArcGIS REST endpoint.
"""

from __future__ import annotations

import os
from pathlib import Path

# ---------------------------------------------------------------------
# Project Paths
# ---------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data"
LOG_DIR = PROJECT_ROOT / "logs"

STATE_FILE = DATA_DIR / "alerted_incidents.json"
LOG_FILE = LOG_DIR / "monitor.log"

DATA_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------
# ArcGIS REST API
# ---------------------------------------------------------------------

ARCGIS_QUERY_URL = (
    "https://services2.arcgis.com/"
    "HdTo6HJqh92wn4D8/"
    "arcgis/rest/services/"
    "Nashville_Fire_Department_Active_Incidents_view/"
    "FeatureServer/0/query"
)

ACTIVE_INCIDENTS_PAGE = (
    "https://www.nashville.gov/departments/fire/operations/"
    "active-incidents"
)

# Request only verified fields.
ARCGIS_FIELDS = [
    "ObjectId",
    "event_number",
    "Unit_ID",
    "incident_type_id",
    "DispatchDateTime",
]

QUERY_PARAMETERS = {
    "where": "1=1",
    "outFields": ",".join(ARCGIS_FIELDS),
    "returnGeometry": "false",
    "f": "json",
}

REQUEST_TIMEOUT = 30
MAX_RETRIES = 3

# ---------------------------------------------------------------------
# Monitoring
# ---------------------------------------------------------------------

TARGET_UNITS = {
    "EN41",
    "EN42",
}

POLL_INTERVAL_MINUTES = 5

# ---------------------------------------------------------------------
# SMTP
# ---------------------------------------------------------------------

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465

EMAIL_USERNAME = os.getenv("EMAIL_USERNAME", "").strip()
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "").strip()
EMAIL_RECIPIENT = os.getenv("EMAIL_RECIPIENT", "").strip()

# ---------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------

LOG_LEVEL = "INFO"

# ---------------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------------


def validate_configuration() -> None:
    """
    Validate required environment variables.

    Raises
    ------
    RuntimeError
        If one or more required environment variables are missing.
    """

    missing: list[str] = []

    if not EMAIL_USERNAME:
        missing.append("EMAIL_USERNAME")

    if not EMAIL_PASSWORD:
        missing.append("EMAIL_PASSWORD")

    if not EMAIL_RECIPIENT:
        missing.append("EMAIL_RECIPIENT")

    if missing:
        raise RuntimeError(
            "Missing required GitHub Secret(s): "
            + ", ".join(missing)
        )

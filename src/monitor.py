"""
Main application entry point.

Monitors the Nashville Fire Department Active Incidents ArcGIS API for
new incidents involving EN41 or EN42.

Workflow

1. Validate configuration
2. Download active incidents
3. Remove old incidents from state
4. Find incidents containing monitored units
5. Send notification for new incidents only
6. Record sent notifications
"""

from __future__ import annotations

import sys

from api import fetch_incidents
from config import TARGET_UNITS, validate_configuration
from emailer import send_email
from logger import get_logger
from state import AlertState

log = get_logger(__name__)


def incident_contains_target_unit(units: str) -> bool:
    """
    Returns True if any monitored unit appears in the Unit_ID field.

    The ArcGIS feed stores units as a comma-separated string.
    Matching is performed case-insensitively and ignores whitespace.
    """

    if not units:
        return False

    parsed_units = {
        unit.strip().upper()
        for unit in units.split(",")
        if unit.strip()
    }

    return bool(parsed_units & TARGET_UNITS)


def main() -> int:
    """
    Main monitoring routine.

    Returns
    -------
    int
        Exit code.
    """

    try:
        validate_configuration()

    except Exception as exc:
        log.exception("Configuration error: %s", exc)
        return 1

    log.info("=" * 70)
    log.info("NFD Unit Monitor starting.")

    state = AlertState()

    try:
        incidents = fetch_incidents()

    except Exception as exc:
        log.exception(
            "Unable to retrieve incident feed: %s",
            exc,
        )
        return 2

    active_incident_numbers = {
        incident.incident_number
        for incident in incidents
        if incident.incident_number
    }

    state.purge_missing(active_incident_numbers)

    monitored_count = 0
    emailed_count = 0

    for incident in incidents:

        if not incident.incident_number:
            continue

        if not incident_contains_target_unit(
            incident.units
        ):
            continue

        monitored_count += 1

        log.info(
            "Matched monitored unit(s): %s | %s",
            incident.incident_number,
            incident.units,
        )

        if state.has_alerted(
            incident.incident_number
        ):
            log.info(
                "Incident %s already alerted.",
                incident.incident_number,
            )
            continue

        try:

            send_email(incident)

            state.mark_alerted(
                incident.incident_number
            )

            emailed_count += 1

        except Exception as exc:
            log.exception(
                "Failed sending email for %s: %s",
                incident.incident_number,
                exc,
            )

    log.info(
        "Scan complete. "
        "Matched=%d  "
        "Emails Sent=%d  "
        "Active=%d",
        monitored_count,
        emailed_count,
        len(incidents),
    )

    log.info("Monitor completed successfully.")

    return 0


if __name__ == "__main__":
    sys.exit(main())

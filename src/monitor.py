"""
Main application entry point for GavMonitor.

Workflow

1. Validate configuration
2. Download active incidents
3. Remove inactive incidents from state
4. Find incidents involving EN41 or EN42
5. Send notifications for new incidents
6. Save updated state
"""

from __future__ import annotations

import sys

from api import ArcGISAPIError, fetch_incidents
from config import TARGET_UNITS, validate_configuration
from emailer import send_email
from logger import get_logger, log_shutdown, log_startup
from models import Incident
from state import AlertState

log = get_logger(__name__)


def contains_monitored_unit(incident: Incident) -> bool:
    """
    Returns True if the incident contains one of the monitored units.
    """

    return any(
        unit in TARGET_UNITS
        for unit in incident.unit_list
    )


def process_incident(
    incident: Incident,
    state: AlertState,
) -> bool:
    """
    Process a single incident.

    Returns True if an email was sent.
    """

    if not contains_monitored_unit(incident):
        return False

    log.info(
        "Matched monitored incident: %s | Units: %s",
        incident.incident_number,
        incident.units,
    )

    if state.has_alerted(incident.incident_number):

        log.info(
            "Incident %s already alerted.",
            incident.incident_number,
        )

        return False

    send_email(incident)

    state.mark_alerted(
        incident.incident_number,
    )

    return True


def main() -> int:
    """
    Main application entry point.

    Returns
    -------
    int
        Process exit code.
    """

    try:
        validate_configuration()

    except Exception as exc:

        log.exception(
            "Configuration error: %s",
            exc,
        )

        return 1

    log_startup(log)

    state = AlertState()

    try:

        incidents = fetch_incidents()

    except ArcGISAPIError as exc:

        log.exception(
            "ArcGIS query failed: %s",
            exc,
        )

        log_shutdown(log)

        return 2

    except Exception as exc:

        log.exception(
            "Unexpected application error: %s",
            exc,
        )

        log_shutdown(log)

        return 3

    active_incidents = {
        incident.incident_number
        for incident in incidents
        if incident.incident_number
    }

    state.purge_inactive(active_incidents)

    emails_sent = 0
    monitored = 0

    for incident in incidents:

        if not contains_monitored_unit(
            incident,
        ):
            continue

        monitored += 1

        try:

            if process_incident(
                incident,
                state,
            ):
                emails_sent += 1

        except Exception as exc:

            log.exception(
                "Unable to process incident %s: %s",
                incident.incident_number,
                exc,
            )

    log.info(
        "Run Summary"
    )

    log.info(
        "Active Incidents : %d",
        len(incidents),
    )

    log.info(
        "Matching Incidents : %d",
        monitored,
    )

    log.info(
        "Emails Sent : %d",
        emails_sent,
    )

    log.info(
        "Tracked Incidents : %d",
        len(state),
    )

    log_shutdown(log)

    return 0


if __name__ == "__main__":
    sys.exit(main())

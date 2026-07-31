"""
ArcGIS REST API client.

Queries the Nashville Fire Department Active Incidents ArcGIS FeatureServer,
normalizes the returned data, and handles transient failures gracefully.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List

import requests

from config import (
    ARCGIS_QUERY_URL,
    QUERY_PARAMETERS,
    REQUEST_TIMEOUT,
)
from logger import get_logger

log = get_logger(__name__)


# Link included in notification emails
ACTIVE_INCIDENTS_MAP = (
    "https://www.nashville.gov/departments/fire/operations/"
    "active-incidents"
)


@dataclass(slots=True)
class Incident:
    """
    Normalized incident returned by the ArcGIS API.
    """

    incident_number: str
    dispatch_time: str
    incident_type: str
    address: str
    units: str
    incident_link: str


def _format_dispatch_time(value) -> str:
    """
    Convert ArcGIS epoch milliseconds into a readable local timestamp.

    If the value is invalid, return 'Unknown'.
    """

    if value in (None, "", 0):
        return "Unknown"

    try:
        dt = datetime.fromtimestamp(
            value / 1000,
            tz=timezone.utc,
        ).astimezone()

        return dt.strftime("%Y-%m-%d %H:%M:%S")

    except Exception:
        return "Unknown"


def _normalize(feature: dict) -> Incident:
    """
    Convert one ArcGIS feature into an Incident object.
    """

    attrs = feature.get("attributes", {})

    return Incident(
        incident_number=str(
            attrs.get("event_number") or ""
        ).strip(),
        dispatch_time=_format_dispatch_time(
            attrs.get("DispatchDateTime")
        ),
        incident_type=str(
            attrs.get("incident_type_id") or "Unknown"
        ).strip(),
        address="Not available from public ArcGIS feed",
        units=str(
            attrs.get("Unit_ID") or ""
        ).strip(),
        incident_link=ACTIVE_INCIDENTS_MAP,
    )


def fetch_incidents(
    retries: int = 3,
    timeout: int = REQUEST_TIMEOUT,
) -> List[Incident]:
    """
    Download active incidents.

    Retries transient failures automatically.

    Returns:
        List[Incident]

    Raises:
        RuntimeError
            If all retry attempts fail.
    """

    last_error = None

    for attempt in range(1, retries + 1):

        try:

            log.info(
                "Querying ArcGIS API (attempt %d/%d)...",
                attempt,
                retries,
            )

            response = requests.get(
                ARCGIS_QUERY_URL,
                params=QUERY_PARAMETERS,
                timeout=timeout,
            )

            response.raise_for_status()

            payload = response.json()

if "features" not in payload:
    log.error("ArcGIS response: %s", payload)
    raise RuntimeError(
        "ArcGIS response does not contain 'features'."
    )
               

            incidents = [
                _normalize(feature)
                for feature in payload["features"]
            ]

            log.info(
                "Retrieved %d active incident(s).",
                len(incidents),
            )

            return incidents

        except requests.Timeout as exc:
            last_error = exc
            log.warning(
                "ArcGIS request timed out."
            )

        except requests.ConnectionError as exc:
            last_error = exc
            log.warning(
                "Unable to connect to ArcGIS service."
            )

        except requests.HTTPError as exc:
            last_error = exc
            log.warning(
                "ArcGIS returned HTTP %s.",
                exc.response.status_code
                if exc.response
                else "Unknown",
            )

        except Exception as exc:
            last_error = exc
            log.exception(
                "Unexpected ArcGIS error."
            )

    raise RuntimeError(
        f"Unable to retrieve incidents after "
        f"{retries} attempts."
    ) from last_error

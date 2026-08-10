"""
ArcGIS REST API client for GavMonitor.

Downloads the current Nashville Fire Department active incidents,
validates the ArcGIS response, retries transient failures, and returns
normalized Incident objects.
"""

from __future__ import annotations

from datetime import datetime, timezone
from time import sleep

import requests

from config import (
    ACTIVE_INCIDENTS_PAGE,
    ARCGIS_QUERY_URL,
    MAX_RETRIES,
    QUERY_PARAMETERS,
    REQUEST_TIMEOUT,
)
from logger import get_logger
from models import Incident

log = get_logger(__name__)


class ArcGISAPIError(RuntimeError):
    """Raised when the ArcGIS API returns an invalid response."""


def _format_dispatch_time(value: object) -> str:
    """
    Convert ArcGIS epoch milliseconds into a local time string.
    """

    if value in (None, "", 0):
        return "Unknown"

    try:
        milliseconds = int(value)

        dt = datetime.fromtimestamp(
            milliseconds / 1000,
            tz=timezone.utc,
        ).astimezone()

        return dt.strftime("%Y-%m-%d %H:%M:%S")

    except Exception:
        return "Unknown"


def _normalize(feature: dict) -> Incident:
    """
    Convert one ArcGIS feature into an Incident object.
    """

    attributes = feature.get("attributes", {})

    return Incident(
        incident_number=str(
            attributes.get("event_number") or ""
        ).strip(),
        dispatch_time=_format_dispatch_time(
            attributes.get("DispatchDateTime")
        ),
        incident_type=str(
            attributes.get("incident_type_id") or "Unknown"
        ).strip(),
        address="Not available from the public ArcGIS feed",
        units=str(
            attributes.get("Unit_ID") or ""
        ).strip(),
        incident_link=ACTIVE_INCIDENTS_PAGE,
        object_id=int(
            attributes.get("ObjectId") or 0
        ),
    )


def fetch_incidents() -> list[Incident]:
    """
    Retrieve active incidents from the ArcGIS REST API.

    Returns
    -------
    list[Incident]

    Raises
    ------
    ArcGISAPIError
        If all retry attempts fail.
    """

    last_error: Exception | None = None

    for attempt in range(1, MAX_RETRIES + 1):

        try:

            log.info(
                "Querying ArcGIS API (attempt %d of %d)...",
                attempt,
                MAX_RETRIES,
            )

            response = requests.get(
                ARCGIS_QUERY_URL,
                params=QUERY_PARAMETERS,
                timeout=REQUEST_TIMEOUT,
            )

            log.info(
                "ArcGIS HTTP status: %s",
                response.status_code,
            )

            response.raise_for_status()

            payload = response.json()

            if "error" in payload:
                log.error(
                    "ArcGIS returned an error: %s",
                    payload["error"],
                )
                raise ArcGISAPIError(
                    payload["error"].get(
                        "message",
                        "Unknown ArcGIS error.",
                    )
                )

            if "features" not in payload:
                log.error(
                    "Unexpected ArcGIS response: %s",
                    payload,
                )
                raise ArcGISAPIError(
                    "ArcGIS response did not contain "
                    "'features'."
                )

            incidents = [
                _normalize(feature)
                for feature in payload["features"]
            ]

            log.info(
                "Retrieved %d incident(s).",
                len(incidents),
            )

            return incidents

        except (
            requests.Timeout,
            requests.ConnectionError,
        ) as exc:

            last_error = exc

            log.warning(
                "Temporary network error: %s",
                exc,
            )

        except requests.HTTPError as exc:

            last_error = exc

            log.warning(
                "HTTP error: %s",
                exc,
            )

        except Exception as exc:

            last_error = exc

            log.exception(
                "ArcGIS query failed."
            )

        if attempt < MAX_RETRIES:
            sleep(2)

    raise ArcGISAPIError(
        "Unable to retrieve active incidents "
        f"after {MAX_RETRIES} attempts."
    ) from last_error

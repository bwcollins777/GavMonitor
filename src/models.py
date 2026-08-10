"""
Application data models.

Defines the normalized Incident object used throughout GavMonitor.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class Incident:
    """
    Represents one active Nashville Fire Department incident.

    Attributes
    ----------
    incident_number
        Unique incident number (event_number).

    dispatch_time
        Human-readable dispatch timestamp.

    incident_type
        Incident type identifier.

    address
        Address of the incident if available from the public API.
        Otherwise a descriptive message indicating that the public
        feed does not expose address information.

    units
        Comma-separated list of dispatched units.

    incident_link
        URL to the Nashville Active Incidents page.

    object_id
        ArcGIS ObjectId for logging and troubleshooting.
    """

    incident_number: str
    dispatch_time: str
    incident_type: str
    address: str
    units: str
    incident_link: str
    object_id: int

    @property
    def unit_list(self) -> list[str]:
        """
        Returns the dispatched units as a normalized list.

        Handles comma- or semicolon-separated values, trims whitespace,
        removes empty entries, and converts unit names to uppercase.
        """

        if not self.units:
            return []

        normalized = self.units.replace(";", ",")

        return [
            unit.strip().upper()
            for unit in normalized.split(",")
            if unit.strip()
        ]

    @property
    def monitored(self) -> bool:
        """
        Returns True if EN41 or EN42 appears in the dispatched units.
        """

        monitored_units = {"EN41", "EN42"}

        return any(
            unit in monitored_units
            for unit in self.unit_list
        )

    @property
    def email_subject(self) -> str:
        """
        Subject line used for notification emails.
        """

        return (
            f"NFD Alert - "
            f"{self.incident_number} "
            f"({self.incident_type})"
        )

    def to_dict(self) -> dict:
        """
        Returns a JSON-serializable representation of the incident.
        """

        return {
            "incident_number": self.incident_number,
            "dispatch_time": self.dispatch_time,
            "incident_type": self.incident_type,
            "address": self.address,
            "units": self.units,
            "incident_link": self.incident_link,
            "object_id": self.object_id,
        }

    def __str__(self) -> str:
        """
        Human-readable description used in logs.
        """

        return (
            f"{self.incident_number} | "
            f"{self.incident_type} | "
            f"{self.units}"
        )

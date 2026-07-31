"""
Persistent state management.

Keeps track of incident numbers that have already generated an alert so
duplicate emails are not sent.

The state is stored as a JSON array in:

    data/alerted_incidents.json
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Set

from config import STATE_FILE
from logger import get_logger

log = get_logger(__name__)


class AlertState:
    """
    Maintains the set of incident IDs that have already generated alerts.
    """

    def __init__(self, state_file: Path = STATE_FILE):
        self.state_file = state_file
        self.alerted: Set[str] = set()
        self.load()

    def load(self) -> None:
        """
        Load the saved alert state from disk.

        If the file does not exist or is invalid, an empty state is created.
        """

        if not self.state_file.exists():
            self.alerted = set()
            self.save()
            log.info("Created new incident state file.")
            return

        try:
            with self.state_file.open("r", encoding="utf-8") as f:
                data = json.load(f)

            if isinstance(data, list):
                self.alerted = set(str(x) for x in data)
            else:
                self.alerted = set()

            log.info(
                "Loaded %d previously alerted incidents.",
                len(self.alerted),
            )

        except Exception as exc:
            log.exception(
                "Unable to read state file. Starting with empty state. %s",
                exc,
            )
            self.alerted = set()

    def save(self) -> None:
        """
        Persist the current alert state.
        """

        self.state_file.parent.mkdir(parents=True, exist_ok=True)

        with self.state_file.open("w", encoding="utf-8") as f:
            json.dump(
                sorted(self.alerted),
                f,
                indent=2,
            )

    def has_alerted(self, incident_number: str) -> bool:
        """
        Returns True if this incident has already generated an email.
        """

        return incident_number in self.alerted

    def mark_alerted(self, incident_number: str) -> None:
        """
        Record an incident as alerted and immediately save the state.
        """

        if incident_number not in self.alerted:
            self.alerted.add(incident_number)
            self.save()
            log.info(
                "Recorded incident %s as alerted.",
                incident_number,
            )

    def purge_missing(self, active_incidents: set[str]) -> None:
        """
        Remove incidents that are no longer active.

        This keeps the state file from growing forever while still preventing
        duplicate alerts during the lifetime of an active incident.

        Args:
            active_incidents:
                Set containing the incident numbers currently returned by
                the ArcGIS API.
        """

        original_size = len(self.alerted)

        self.alerted.intersection_update(active_incidents)

        if len(self.alerted) != original_size:
            self.save()
            log.info(
                "Purged %d inactive incident(s) from state.",
                original_size - len(self.alerted),
            )

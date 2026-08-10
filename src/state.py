"""
Persistent state management for GavMonitor.

Tracks which incident numbers have already generated email notifications,
preventing duplicate alerts while incidents remain active.
"""

from __future__ import annotations

import json
from pathlib import Path

from config import STATE_FILE
from logger import get_logger

log = get_logger(__name__)


class AlertState:
    """
    Manages persistent duplicate-alert state.

    The state file stores a JSON array containing incident numbers that
    have already generated notifications.
    """

    def __init__(self, state_file: Path = STATE_FILE) -> None:
        self.state_file = state_file
        self.alerted: set[str] = set()
        self.load()

    def load(self) -> None:
        """
        Load the saved alert state from disk.
        """

        if not self.state_file.exists():
            self.alerted = set()
            self.save()
            log.info("Created new alert state file.")
            return

        try:
            with self.state_file.open(
                "r",
                encoding="utf-8",
            ) as fp:
                data = json.load(fp)

            if isinstance(data, list):
                self.alerted = {
                    str(value)
                    for value in data
                    if value
                }
            else:
                self.alerted = set()

            log.info(
                "Loaded %d previously alerted incident(s).",
                len(self.alerted),
            )

        except Exception as exc:
            log.exception(
                "Unable to load alert state. "
                "Starting with an empty state. %s",
                exc,
            )
            self.alerted = set()

    def save(self) -> None:
        """
        Save the current alert state to disk.
        """

        self.state_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with self.state_file.open(
            "w",
            encoding="utf-8",
        ) as fp:
            json.dump(
                sorted(self.alerted),
                fp,
                indent=2,
            )

    def has_alerted(
        self,
        incident_number: str,
    ) -> bool:
        """
        Return True if the incident has already generated an alert.
        """

        return incident_number in self.alerted

    def mark_alerted(
        self,
        incident_number: str,
    ) -> None:
        """
        Record an incident as alerted and immediately persist the state.
        """

        if incident_number in self.alerted:
            return

        self.alerted.add(incident_number)
        self.save()

        log.info(
            "Recorded incident %s as alerted.",
            incident_number,
        )

    def purge_inactive(
        self,
        active_incidents: set[str],
    ) -> None:
        """
        Remove incidents that are no longer active.

        This keeps the state file from growing indefinitely while
        ensuring duplicate emails are not sent during the lifetime of an
        active incident.
        """

        before = len(self.alerted)

        self.alerted.intersection_update(active_incidents)

        removed = before - len(self.alerted)

        if removed > 0:
            self.save()

            log.info(
                "Removed %d inactive incident(s) from state.",
                removed,
            )

    def clear(self) -> None:
        """
        Clear all saved alert history.
        """

        self.alerted.clear()
        self.save()

        log.warning(
            "Alert state cleared."
        )

    def __len__(self) -> int:
        """
        Return the number of tracked incidents.
        """

        return len(self.alerted)

    def __contains__(
        self,
        incident_number: str,
    ) -> bool:
        """
        Support the 'in' operator.

        Example:
            if incident in state:
                ...
        """

        return incident_number in self.alerted

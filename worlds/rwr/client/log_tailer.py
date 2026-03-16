"""Tails the RWR game log for [AP_*] events emitted by the mod."""

from __future__ import annotations

import logging
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Union

logger = logging.getLogger("RWRLogTailer")

# --- Event types ---


@dataclass
class CheckEvent:
    """A location check reported by the mod."""
    location_name: str


@dataclass
class DeathEvent:
    """The player died (for death link)."""
    pass


@dataclass
class TrapAckEvent:
    """The mod acknowledged processing a trap."""
    trap_id: int


@dataclass
class GoalEvent:
    """The mod reports goal completion."""
    pass


@dataclass
class NotifyAckEvent:
    """The mod acknowledged displaying notifications."""
    pass


@dataclass
class DeathLinkAckEvent:
    """The mod acknowledged processing a death link."""
    pass


LogEvent = Union[CheckEvent, DeathEvent, TrapAckEvent, GoalEvent, NotifyAckEvent, DeathLinkAckEvent]

# --- Regex patterns ---

_RE_CHECK = re.compile(r"\[AP_CHECK\]\s+(.+)")
_RE_DEATH = re.compile(r"\[AP_DEATH\]")
_RE_TRAP_ACK = re.compile(r"\[AP_TRAP_ACK\]\s+id=(\d+)")
_RE_GOAL = re.compile(r"\[AP_GOAL\]")
_RE_NOTIFY_ACK = re.compile(r"\[AP_NOTIFY_ACK\]")
_RE_DEATHLINK_ACK = re.compile(r"\[AP_DEATHLINK_ACK\]")


class LogTailer:
    """Incrementally reads new lines from the RWR game log."""

    def __init__(self, log_path: Path) -> None:
        self.log_path = log_path
        self._offset: int = 0

    def seek_to_end(self) -> None:
        """Position the cursor at the end of the file (skip history)."""
        try:
            self._offset = self.log_path.stat().st_size
            logger.info("Seeked to end of log: offset=%d", self._offset)
        except OSError:
            self._offset = 0
            logger.info("Log file not found yet, starting at offset 0")

    def poll(self) -> list[LogEvent]:
        """Read new lines since last poll, return parsed AP events."""
        if not self.log_path.exists():
            return []

        try:
            file_size = self.log_path.stat().st_size
        except OSError:
            return []

        # File was truncated (game restarted) — reset offset
        if file_size < self._offset:
            logger.info("Log file truncated (game restart?), resetting offset")
            self._offset = 0

        if file_size == self._offset:
            return []

        events: list[LogEvent] = []

        try:
            with open(self.log_path, "r", encoding="utf-8", errors="replace") as f:
                f.seek(self._offset)
                for line in f:
                    event = self._parse_line(line.rstrip())
                    if event is not None:
                        events.append(event)
                self._offset = f.tell()
        except OSError as e:
            logger.warning("Failed to read log: %s", e)

        return events

    @staticmethod
    def _parse_line(line: str) -> LogEvent | None:
        """Parse a single log line into a LogEvent, or None if not AP-related."""
        # Quick filter — skip lines that can't contain AP events
        if "[AP_" not in line:
            return None

        m = _RE_CHECK.search(line)
        if m:
            name = m.group(1).strip()
            if name:
                return CheckEvent(location_name=name)

        m = _RE_TRAP_ACK.search(line)
        if m:
            return TrapAckEvent(trap_id=int(m.group(1)))

        if _RE_DEATH.search(line):
            return DeathEvent()

        if _RE_GOAL.search(line):
            return GoalEvent()

        if _RE_NOTIFY_ACK.search(line):
            return NotifyAckEvent()

        if _RE_DEATHLINK_ACK.search(line):
            return DeathLinkAckEvent()

        return None

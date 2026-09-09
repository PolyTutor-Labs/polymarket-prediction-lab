"""In-memory learning journal for paper decisions."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class JournalEntry:
    timestamp: datetime
    kind: str
    message: str
    market_id: Optional[str] = None
    detail: dict = field(default_factory=dict)


class Journal:
    def __init__(self) -> None:
        self._entries: list[JournalEntry] = []

    def add(
        self,
        kind: str,
        message: str,
        market_id: Optional[str] = None,
        detail: Optional[dict] = None,
    ) -> JournalEntry:
        entry = JournalEntry(
            timestamp=_utc_now(),
            kind=kind,
            message=message,
            market_id=market_id,
            detail=dict(detail or {}),
        )
        self._entries.append(entry)
        return entry

    def list_entries(self) -> list[JournalEntry]:
        return list(self._entries)

    def clear(self) -> None:
        self._entries.clear()

    def __len__(self) -> int:
        return len(self._entries)

"""Midpoint observation — rough implied probability proxy."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from polytutor_prediction.models import Market, OutcomeLabel
from polytutor_prediction import orderbook as ob


@dataclass(frozen=True)
class MidpointObservation:
    market_id: str
    outcome: OutcomeLabel
    midpoint: Optional[float]
    note: str = (
        "Educational: midpoint ≈ (bid+ask)/2 is a rough implied-probability "
        "proxy, not a true probability or fair value."
    )


def observe_midpoint(
    market: Market, outcome: OutcomeLabel = OutcomeLabel.YES
) -> MidpointObservation:
    book = market.yes_book if outcome is OutcomeLabel.YES else market.no_book
    return MidpointObservation(
        market_id=market.market_id,
        outcome=outcome,
        midpoint=ob.midpoint(book),
    )

"""Book imbalance observation — resting size skew lesson."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from polytutor_prediction.models import Market, OutcomeLabel
from polytutor_prediction import orderbook as ob


@dataclass(frozen=True)
class ImbalanceObservation:
    market_id: str
    outcome: OutcomeLabel
    imbalance: Optional[float]
    bid_depth: float
    ask_depth: float
    note: str = (
        "Educational: imbalance > 0.5 means more bid depth on top levels. "
        "Skew is an observation, not a guaranteed edge."
    )


def observe_imbalance(
    market: Market, outcome: OutcomeLabel = OutcomeLabel.YES, levels: int = 3
) -> ImbalanceObservation:
    book = market.yes_book if outcome is OutcomeLabel.YES else market.no_book
    d = ob.depth(book, levels=levels)
    return ImbalanceObservation(
        market_id=market.market_id,
        outcome=outcome,
        imbalance=ob.imbalance(book, levels=levels),
        bid_depth=d["bid_depth"],
        ask_depth=d["ask_depth"],
    )

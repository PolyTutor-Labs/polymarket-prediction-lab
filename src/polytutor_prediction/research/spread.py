"""Spread observation — cost of immediacy lesson."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from polytutor_prediction.models import Market, OutcomeLabel
from polytutor_prediction import orderbook as ob


@dataclass(frozen=True)
class SpreadObservation:
    market_id: str
    outcome: OutcomeLabel
    spread: Optional[float]
    best_bid: Optional[float]
    best_ask: Optional[float]
    note: str = (
        "Educational: wider spreads often mean higher transaction cost. "
        "Not a trade recommendation."
    )


def observe_spread(market: Market, outcome: OutcomeLabel = OutcomeLabel.YES) -> SpreadObservation:
    book = market.yes_book if outcome is OutcomeLabel.YES else market.no_book
    q = ob.quote(book)
    return SpreadObservation(
        market_id=market.market_id,
        outcome=outcome,
        spread=ob.spread(book),
        best_bid=q.best_bid,
        best_ask=q.best_ask,
    )

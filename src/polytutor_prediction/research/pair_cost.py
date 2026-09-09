"""Pair-cost observation — YES ask + NO ask vs 1.00 lesson.

Buying both YES and NO at the ask is an educational thought experiment about
completeness of binary markets. Values near or above 1.00 are common and do
NOT imply a risk-free arbitrage once fees, latency, and partial fills exist.
This lab never executes live arb.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from polytutor_prediction.models import Market
from polytutor_prediction import orderbook as ob


@dataclass(frozen=True)
class PairCostObservation:
    market_id: str
    yes_ask: Optional[float]
    no_ask: Optional[float]
    pair_ask_sum: Optional[float]
    yes_bid: Optional[float]
    no_bid: Optional[float]
    pair_bid_sum: Optional[float]
    note: str = (
        "Educational observation only. Sum of asks near 1.00 is interesting "
        "for learning; it is NOT a guaranteed arbitrage. Fees, fill risk, and "
        "timing matter in real venues. This lab does not place live orders."
    )


def observe_pair_cost(market: Market) -> PairCostObservation:
    yq = ob.quote(market.yes_book)
    nq = ob.quote(market.no_book)
    pair_ask = (
        None
        if yq.best_ask is None or nq.best_ask is None
        else yq.best_ask + nq.best_ask
    )
    pair_bid = (
        None
        if yq.best_bid is None or nq.best_bid is None
        else yq.best_bid + nq.best_bid
    )
    return PairCostObservation(
        market_id=market.market_id,
        yes_ask=yq.best_ask,
        no_ask=nq.best_ask,
        pair_ask_sum=pair_ask,
        yes_bid=yq.best_bid,
        no_bid=nq.best_bid,
        pair_bid_sum=pair_bid,
    )

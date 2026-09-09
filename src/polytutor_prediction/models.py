"""Domain models for the educational prediction-market lab.

No wallet fields, no signing material, no live exchange identifiers required
for trading. All monetary values are paper/demo units.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Side(str, Enum):
    BUY = "buy"
    SELL = "sell"


class OutcomeLabel(str, Enum):
    YES = "YES"
    NO = "NO"


@dataclass(frozen=True)
class Outcome:
    """A binary market outcome (YES or NO) with an optional display name."""

    label: OutcomeLabel
    token_id: str
    display_name: str = ""


@dataclass(frozen=True)
class OrderBookLevel:
    """One price level on an order book."""

    price: float  # 0.0 – 1.0 for binary markets
    size: float


@dataclass
class OrderBook:
    """Simple aggregated book for one outcome token."""

    outcome: OutcomeLabel
    bids: list[OrderBookLevel] = field(default_factory=list)  # high→low price
    asks: list[OrderBookLevel] = field(default_factory=list)  # low→high price

    def sorted_copy(self) -> "OrderBook":
        return OrderBook(
            outcome=self.outcome,
            bids=sorted(self.bids, key=lambda lvl: lvl.price, reverse=True),
            asks=sorted(self.asks, key=lambda lvl: lvl.price),
        )


@dataclass(frozen=True)
class Quote:
    """Best bid/ask snapshot."""

    best_bid: Optional[float]
    best_ask: Optional[float]
    bid_size: float = 0.0
    ask_size: float = 0.0


@dataclass
class Market:
    """Educational binary market fixture."""

    market_id: str
    question: str
    category: str
    yes: Outcome
    no: Outcome
    yes_book: OrderBook
    no_book: OrderBook
    status: str = "open"
    description: str = ""

    @property
    def outcomes(self) -> tuple[Outcome, Outcome]:
        return self.yes, self.no


@dataclass
class PaperOrder:
    """A paper (simulated) order — never sent to a live venue."""

    order_id: str
    market_id: str
    outcome: OutcomeLabel
    side: Side
    price: float
    size: float
    created_at: datetime = field(default_factory=utc_now)
    note: str = ""


@dataclass
class PaperFill:
    """A simulated fill against the demo book."""

    fill_id: str
    order_id: str
    market_id: str
    outcome: OutcomeLabel
    side: Side
    price: float
    size: float
    filled_at: datetime = field(default_factory=utc_now)


@dataclass
class PaperPosition:
    """Net paper position in one market outcome."""

    market_id: str
    outcome: OutcomeLabel
    size: float = 0.0
    avg_price: float = 0.0
    realized_pnl: float = 0.0

    @property
    def notional(self) -> float:
        return abs(self.size) * self.avg_price


@dataclass
class PaperPortfolio:
    """Virtual portfolio — cash and positions only (no wallet)."""

    cash: float
    initial_cash: float
    positions: dict[str, PaperPosition] = field(default_factory=dict)
    fills: list[PaperFill] = field(default_factory=list)
    orders: list[PaperOrder] = field(default_factory=list)
    daily_realized_pnl: float = 0.0

    def position_key(self, market_id: str, outcome: OutcomeLabel) -> str:
        return f"{market_id}:{outcome.value}"

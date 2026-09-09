"""Order book analytics for educational use.

All functions are pure and offline. Midpoint is a rough implied-probability
proxy — not a fair-value oracle.
"""

from __future__ import annotations

from typing import Optional

from polytutor_prediction.models import OrderBook, OrderBookLevel, Quote


def best_bid(book: OrderBook) -> Optional[OrderBookLevel]:
    if not book.bids:
        return None
    return max(book.bids, key=lambda lvl: lvl.price)


def best_ask(book: OrderBook) -> Optional[OrderBookLevel]:
    if not book.asks:
        return None
    return min(book.asks, key=lambda lvl: lvl.price)


def quote(book: OrderBook) -> Quote:
    bid = best_bid(book)
    ask = best_ask(book)
    return Quote(
        best_bid=None if bid is None else bid.price,
        best_ask=None if ask is None else ask.price,
        bid_size=0.0 if bid is None else bid.size,
        ask_size=0.0 if ask is None else ask.size,
    )


def spread(book: OrderBook) -> Optional[float]:
    q = quote(book)
    if q.best_bid is None or q.best_ask is None:
        return None
    return q.best_ask - q.best_bid


def midpoint(book: OrderBook) -> Optional[float]:
    """Rough implied probability proxy for binary outcome tokens."""
    q = quote(book)
    if q.best_bid is None or q.best_ask is None:
        return None
    return (q.best_bid + q.best_ask) / 2.0


def depth(book: OrderBook, levels: int = 3) -> dict[str, float]:
    """Total size on top N bid/ask levels."""
    bids = sorted(book.bids, key=lambda lvl: lvl.price, reverse=True)[:levels]
    asks = sorted(book.asks, key=lambda lvl: lvl.price)[:levels]
    return {
        "bid_depth": sum(lvl.size for lvl in bids),
        "ask_depth": sum(lvl.size for lvl in asks),
        "levels": float(levels),
    }


def imbalance(book: OrderBook, levels: int = 3) -> Optional[float]:
    """Bid depth / (bid + ask depth) on top N levels.

    Values > 0.5 mean more resting bid size (educational observation only).
    """
    d = depth(book, levels=levels)
    total = d["bid_depth"] + d["ask_depth"]
    if total <= 0:
        return None
    return d["bid_depth"] / total


def vwap_buy(book: OrderBook, size: float) -> Optional[tuple[float, float]]:
    """Walk the ask side for a paper buy. Returns (avg_price, filled_size)."""
    if size <= 0:
        return None
    remaining = size
    cost = 0.0
    filled = 0.0
    for lvl in sorted(book.asks, key=lambda x: x.price):
        take = min(remaining, lvl.size)
        cost += take * lvl.price
        filled += take
        remaining -= take
        if remaining <= 1e-12:
            break
    if filled <= 0:
        return None
    return cost / filled, filled


def vwap_sell(book: OrderBook, size: float) -> Optional[tuple[float, float]]:
    """Walk the bid side for a paper sell. Returns (avg_price, filled_size)."""
    if size <= 0:
        return None
    remaining = size
    proceeds = 0.0
    filled = 0.0
    for lvl in sorted(book.bids, key=lambda x: x.price, reverse=True):
        take = min(remaining, lvl.size)
        proceeds += take * lvl.price
        filled += take
        remaining -= take
        if remaining <= 1e-12:
            break
    if filled <= 0:
        return None
    return proceeds / filled, filled

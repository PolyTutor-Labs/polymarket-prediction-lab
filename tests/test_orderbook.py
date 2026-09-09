from __future__ import annotations

from polytutor_prediction.demo_data import build_demo_markets
from polytutor_prediction.models import OrderBook, OrderBookLevel, OutcomeLabel
from polytutor_prediction import orderbook as ob


def test_quote_spread_midpoint():
    book = OrderBook(
        outcome=OutcomeLabel.YES,
        bids=[OrderBookLevel(0.40, 10)],
        asks=[OrderBookLevel(0.50, 8)],
    )
    q = ob.quote(book)
    assert q.best_bid == 0.40
    assert q.best_ask == 0.50
    assert abs(ob.spread(book) - 0.10) < 1e-9
    assert ob.midpoint(book) == 0.45


def test_depth_and_imbalance():
    book = OrderBook(
        outcome=OutcomeLabel.YES,
        bids=[OrderBookLevel(0.40, 100), OrderBookLevel(0.39, 50)],
        asks=[OrderBookLevel(0.42, 25)],
    )
    d = ob.depth(book, levels=2)
    assert d["bid_depth"] == 150
    assert d["ask_depth"] == 25
    imb = ob.imbalance(book, levels=2)
    assert imb is not None
    assert imb > 0.5


def test_vwap_buy_sell():
    book = OrderBook(
        outcome=OutcomeLabel.YES,
        bids=[OrderBookLevel(0.40, 10), OrderBookLevel(0.39, 10)],
        asks=[OrderBookLevel(0.50, 5), OrderBookLevel(0.51, 10)],
    )
    buy = ob.vwap_buy(book, 8)
    assert buy is not None
    avg, filled = buy
    assert filled == 8
    assert abs(avg - ((5 * 0.50 + 3 * 0.51) / 8)) < 1e-9
    sell = ob.vwap_sell(book, 12)
    assert sell is not None
    assert sell[1] == 12


def test_demo_markets_have_books():
    markets = build_demo_markets()
    assert len(markets) >= 3
    for m in markets:
        assert ob.quote(m.yes_book).best_ask is not None
        assert ob.quote(m.no_book).best_bid is not None

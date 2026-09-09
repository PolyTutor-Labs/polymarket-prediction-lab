from __future__ import annotations

from polytutor_prediction.models import (
    Outcome,
    OutcomeLabel,
    OrderBook,
    OrderBookLevel,
    PaperPortfolio,
    Side,
)


def test_outcome_and_side_enums():
    assert OutcomeLabel.YES.value == "YES"
    assert Side.BUY.value == "buy"


def test_orderbook_sorted_copy():
    book = OrderBook(
        outcome=OutcomeLabel.YES,
        bids=[OrderBookLevel(0.4, 1), OrderBookLevel(0.5, 2)],
        asks=[OrderBookLevel(0.7, 1), OrderBookLevel(0.6, 2)],
    )
    s = book.sorted_copy()
    assert s.bids[0].price == 0.5
    assert s.asks[0].price == 0.6


def test_portfolio_position_key():
    p = PaperPortfolio(cash=1000, initial_cash=1000)
    key = p.position_key("m1", OutcomeLabel.NO)
    assert key == "m1:NO"


def test_outcome_frozen():
    o = Outcome(OutcomeLabel.YES, "t1")
    assert o.token_id == "t1"

from __future__ import annotations

from polytutor_prediction.demo_data import build_demo_markets
from polytutor_prediction.models import OrderBook, OutcomeLabel
from polytutor_prediction.paper.engine import PaperEngine
from polytutor_prediction.paper.limits import EducationalLimits
from polytutor_prediction.paper.portfolio import create_portfolio, initial_cash_from_env


def test_create_portfolio_default():
    p = create_portfolio()
    assert p.cash == 10_000
    assert p.initial_cash == 10_000


def test_create_portfolio_rejects_non_positive_cash():
    p = create_portfolio(0)
    assert p.cash == 10_000
    p2 = create_portfolio(-50)
    assert p2.cash == 10_000


def test_initial_cash_env(monkeypatch):
    monkeypatch.setenv("POLYTUTOR_INITIAL_CASH", "1234.5")
    assert initial_cash_from_env() == 1234.5
    monkeypatch.setenv("POLYTUTOR_INITIAL_CASH", "nope")
    assert initial_cash_from_env() == 10_000.0
    monkeypatch.setenv("POLYTUTOR_INITIAL_CASH", "0")
    assert initial_cash_from_env() == 10_000.0
    monkeypatch.delenv("POLYTUTOR_INITIAL_CASH", raising=False)
    assert initial_cash_from_env() == 10_000.0


def test_buy_and_sell_roundtrip():
    markets = build_demo_markets()
    m = markets[0]
    eng = PaperEngine(portfolio=create_portfolio(10_000), limits=EducationalLimits())
    ok, msg, fill = eng.buy(m, OutcomeLabel.YES, 10, note="lesson")
    assert ok, msg
    assert fill is not None
    assert fill.side.value == "buy"
    assert eng.portfolio.cash < 10_000
    key = eng.portfolio.position_key(m.market_id, OutcomeLabel.YES)
    assert key in eng.portfolio.positions
    ok2, msg2, fill2 = eng.sell(m, OutcomeLabel.YES, 10)
    assert ok2, msg2
    assert fill2 is not None
    assert key not in eng.portfolio.positions or eng.portfolio.positions[key].size == 0


def test_buy_no_outcome_and_second_fill_averages():
    markets = build_demo_markets()
    m = markets[0]
    eng = PaperEngine(portfolio=create_portfolio(10_000))
    ok, msg, fill = eng.buy(m, OutcomeLabel.NO, 4)
    assert ok, msg
    assert fill is not None
    key = eng.portfolio.position_key(m.market_id, OutcomeLabel.NO)
    first_avg = eng.portfolio.positions[key].avg_price
    ok2, msg2, fill2 = eng.buy(m, OutcomeLabel.NO, 4)
    assert ok2, msg2
    assert fill2 is not None
    pos = eng.portfolio.positions[key]
    assert pos.size == 8
    expected_avg = ((4 * first_avg) + (4 * fill2.price)) / 8
    assert abs(pos.avg_price - expected_avg) < 1e-9


def test_educational_limits_block_huge_order():
    markets = build_demo_markets()
    m = markets[0]
    eng = PaperEngine(limits=EducationalLimits(max_order_size=5))
    ok, msg, fill = eng.buy(m, OutcomeLabel.YES, 100)
    assert not ok
    assert fill is None
    assert "Educational" in msg or "max" in msg.lower()
    kinds = [e.kind for e in eng.journal.list_entries()]
    assert "reject" in kinds


def test_educational_limits_block_notional():
    markets = build_demo_markets()
    m = markets[0]
    eng = PaperEngine(
        portfolio=create_portfolio(10_000),
        limits=EducationalLimits(max_position_notional=1.0),
    )
    ok, msg, fill = eng.buy(m, OutcomeLabel.YES, 10)
    assert not ok
    assert fill is None
    assert "notional" in msg.lower()


def test_educational_limits_block_daily_loss():
    markets = build_demo_markets()
    m = markets[0]
    eng = PaperEngine(limits=EducationalLimits(max_daily_loss=10.0))
    eng.portfolio.daily_realized_pnl = -10.01
    ok, msg, fill = eng.buy(m, OutcomeLabel.YES, 1)
    assert not ok
    assert fill is None
    assert "daily" in msg.lower()


def test_insufficient_cash():
    markets = build_demo_markets()
    m = markets[0]
    eng = PaperEngine(portfolio=create_portfolio(1.0))
    ok, msg, _ = eng.buy(m, OutcomeLabel.YES, 50)
    assert not ok
    assert "cash" in msg.lower()


def test_sell_without_inventory():
    markets = build_demo_markets()
    m = markets[0]
    eng = PaperEngine()
    ok, msg, fill = eng.sell(m, OutcomeLabel.YES, 1)
    assert not ok
    assert fill is None
    assert "inventory" in msg.lower()


def test_buy_without_ask_liquidity():
    markets = build_demo_markets()
    m = markets[0]
    m.yes_book = OrderBook(outcome=OutcomeLabel.YES, bids=list(m.yes_book.bids), asks=[])
    eng = PaperEngine()
    ok, msg, fill = eng.buy(m, OutcomeLabel.YES, 1)
    assert not ok
    assert fill is None
    assert "ask" in msg.lower()


def test_non_positive_size_rejected():
    markets = build_demo_markets()
    m = markets[0]
    eng = PaperEngine()
    ok, msg, fill = eng.buy(m, OutcomeLabel.YES, 0)
    assert not ok
    assert fill is None
    assert "positive" in msg.lower()


def test_equity_and_journal():
    markets = {x.market_id: x for x in build_demo_markets()}
    m = next(iter(markets.values()))
    eng = PaperEngine()
    eng.buy(m, OutcomeLabel.YES, 5, note="hypo")
    assert eng.equity(markets) > 0
    assert isinstance(eng.unrealized_pnl(markets), float)
    assert len(eng.journal) >= 1
    mid = eng.mark_price(m, OutcomeLabel.YES)
    assert mid is not None
    assert mid > 0

from __future__ import annotations

from polytutor_prediction.demo_data import build_demo_markets
from polytutor_prediction.models import OutcomeLabel
from polytutor_prediction.paper.engine import PaperEngine
from polytutor_prediction.paper.limits import EducationalLimits
from polytutor_prediction.paper.portfolio import create_portfolio, initial_cash_from_env


def test_create_portfolio_default():
    p = create_portfolio()
    assert p.cash == 10_000
    assert p.initial_cash == 10_000


def test_initial_cash_env(monkeypatch):
    monkeypatch.setenv("POLYTUTOR_INITIAL_CASH", "1234.5")
    assert initial_cash_from_env() == 1234.5
    monkeypatch.setenv("POLYTUTOR_INITIAL_CASH", "nope")
    assert initial_cash_from_env() == 10_000.0


def test_buy_and_sell_roundtrip():
    markets = build_demo_markets()
    m = markets[0]
    eng = PaperEngine(portfolio=create_portfolio(10_000), limits=EducationalLimits())
    ok, msg, fill = eng.buy(m, OutcomeLabel.YES, 10, note="lesson")
    assert ok, msg
    assert fill is not None
    assert eng.portfolio.cash < 10_000
    key = eng.portfolio.position_key(m.market_id, OutcomeLabel.YES)
    assert key in eng.portfolio.positions
    ok2, msg2, fill2 = eng.sell(m, OutcomeLabel.YES, 10)
    assert ok2, msg2
    assert fill2 is not None
    assert key not in eng.portfolio.positions or eng.portfolio.positions[key].size == 0


def test_educational_limits_block_huge_order():
    markets = build_demo_markets()
    m = markets[0]
    eng = PaperEngine(limits=EducationalLimits(max_order_size=5))
    ok, msg, fill = eng.buy(m, OutcomeLabel.YES, 100)
    assert not ok
    assert fill is None
    assert "Educational" in msg or "max" in msg.lower()


def test_insufficient_cash():
    markets = build_demo_markets()
    m = markets[0]
    eng = PaperEngine(portfolio=create_portfolio(1.0))
    ok, msg, _ = eng.buy(m, OutcomeLabel.YES, 50)
    assert not ok
    assert "cash" in msg.lower()


def test_equity_and_journal():
    markets = {x.market_id: x for x in build_demo_markets()}
    m = next(iter(markets.values()))
    eng = PaperEngine()
    eng.buy(m, OutcomeLabel.YES, 5, note="hypo")
    assert eng.equity(markets) > 0
    assert len(eng.journal) >= 1

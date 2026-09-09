from __future__ import annotations

from polytutor_prediction.demo_data import build_demo_markets
from polytutor_prediction.models import OutcomeLabel
from polytutor_prediction.research import (
    observe_imbalance,
    observe_midpoint,
    observe_pair_cost,
    observe_spread,
)


def test_observations_are_educational():
    m = build_demo_markets()[0]
    s = observe_spread(m)
    mp = observe_midpoint(m)
    imb = observe_imbalance(m)
    pc = observe_pair_cost(m)
    assert s.spread is not None and s.spread >= 0
    assert mp.midpoint is not None
    assert "Educational" in s.note
    assert "Educational" in mp.note
    assert "Educational" in imb.note
    assert "NOT a guaranteed arbitrage" in pc.note or "not" in pc.note.lower()
    assert pc.pair_ask_sum is not None


def test_observations_work_for_no_outcome():
    m = build_demo_markets()[0]
    s = observe_spread(m, OutcomeLabel.NO)
    mp = observe_midpoint(m, OutcomeLabel.NO)
    imb = observe_imbalance(m, OutcomeLabel.NO)
    assert s.outcome is OutcomeLabel.NO
    assert mp.outcome is OutcomeLabel.NO
    assert imb.outcome is OutcomeLabel.NO
    assert s.spread is not None
    assert mp.midpoint is not None
    assert imb.imbalance is not None
    assert imb.bid_depth >= 0 and imb.ask_depth >= 0


def test_pair_cost_fields_are_populated_from_quotes():
    markets = {m.market_id: m for m in build_demo_markets()}
    champ = markets["demo-mkt-championship"]
    pc = observe_pair_cost(champ)
    assert pc.market_id == champ.market_id
    assert pc.yes_ask == 0.50
    assert pc.no_ask == 0.50
    assert pc.pair_ask_sum == 1.00
    assert pc.yes_bid == 0.48
    assert pc.no_bid == 0.48
    assert pc.pair_bid_sum == 0.96
    assert "NOT a guaranteed arbitrage" in pc.note

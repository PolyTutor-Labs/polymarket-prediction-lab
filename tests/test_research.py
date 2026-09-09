from __future__ import annotations

from polytutor_prediction.demo_data import build_demo_markets
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

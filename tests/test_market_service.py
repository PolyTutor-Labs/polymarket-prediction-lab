from __future__ import annotations

from polytutor_prediction.demo_data import DEMO_MARKETS
from polytutor_prediction.market_service import MarketService, default_service


def test_list_and_get():
    svc = default_service()
    markets = svc.list_markets()
    assert svc.count() == len(markets)
    first = markets[0]
    got = svc.get_market(first.market_id)
    assert got is not None
    assert got.question == first.question
    assert svc.get_market("does-not-exist") is None


def test_categories():
    svc = MarketService()
    cats = svc.categories()
    assert isinstance(cats, list)
    assert len(cats) >= 1
    assert cats == sorted(cats)


def test_default_service_uses_demo_snapshot():
    svc = default_service()
    assert svc.count() == len(DEMO_MARKETS)
    assert [m.market_id for m in svc.list_markets()] == [m.market_id for m in DEMO_MARKETS]

"""Demo catalog is deterministic and offline."""

from __future__ import annotations

from polytutor_prediction.demo_data import DEMO_MARKETS, build_demo_markets
from polytutor_prediction import orderbook as ob


def test_demo_catalog_is_stable_across_calls() -> None:
    first = build_demo_markets()
    second = build_demo_markets()
    assert [m.market_id for m in first] == [m.market_id for m in second]
    assert [m.question for m in first] == [m.question for m in second]
    for a, b in zip(first, second, strict=True):
        assert ob.midpoint(a.yes_book) == ob.midpoint(b.yes_book)
        assert ob.midpoint(a.no_book) == ob.midpoint(b.no_book)
        assert ob.spread(a.yes_book) == ob.spread(b.yes_book)


def test_demo_catalog_has_four_binary_markets() -> None:
    markets = build_demo_markets()
    assert len(markets) == 4
    ids = {m.market_id for m in markets}
    assert ids == {
        "demo-mkt-election-2028",
        "demo-mkt-rainfall-q4",
        "demo-mkt-product-launch",
        "demo-mkt-championship",
    }
    for market in markets:
        assert market.yes.label.value == "YES"
        assert market.no.label.value == "NO"
        assert market.status == "open"
        assert market.yes_book.bids and market.yes_book.asks
        assert market.no_book.bids and market.no_book.asks


def test_module_snapshot_matches_builder_ids() -> None:
    assert [m.market_id for m in DEMO_MARKETS] == [m.market_id for m in build_demo_markets()]

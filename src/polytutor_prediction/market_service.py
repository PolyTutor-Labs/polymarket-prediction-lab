"""Market catalog service backed by offline demo fixtures."""

from __future__ import annotations

from typing import Optional

from polytutor_prediction.demo_data import DEMO_MARKETS, build_demo_markets
from polytutor_prediction.models import Market


class MarketService:
    """List/get markets from in-memory demo data only."""

    def __init__(self, markets: Optional[list[Market]] = None) -> None:
        self._markets = list(markets) if markets is not None else build_demo_markets()
        self._by_id = {m.market_id: m for m in self._markets}

    def list_markets(self) -> list[Market]:
        return list(self._markets)

    def get_market(self, market_id: str) -> Optional[Market]:
        return self._by_id.get(market_id)

    def categories(self) -> list[str]:
        return sorted({m.category for m in self._markets})

    def count(self) -> int:
        return len(self._markets)


def default_service() -> MarketService:
    """Factory using the module-level DEMO_MARKETS snapshot."""
    return MarketService(markets=list(DEMO_MARKETS))

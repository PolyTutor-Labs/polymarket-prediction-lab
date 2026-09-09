"""Shared offline fixtures. No network, no wallets, no live venues."""

from __future__ import annotations

from pathlib import Path

import pytest

from polytutor_prediction.demo_data import build_demo_markets
from polytutor_prediction.market_service import MarketService, default_service
from polytutor_prediction.models import Market
from polytutor_prediction.paper.engine import PaperEngine
from polytutor_prediction.paper.portfolio import create_portfolio

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def repo_root() -> Path:
    return ROOT


@pytest.fixture
def demo_markets() -> list[Market]:
    return build_demo_markets()


@pytest.fixture
def demo_service() -> MarketService:
    return default_service()


@pytest.fixture
def paper_engine() -> PaperEngine:
    return PaperEngine(portfolio=create_portfolio(10_000))

"""Portfolio helpers for paper simulation."""

from __future__ import annotations

import os

from polytutor_prediction.models import PaperPortfolio


DEFAULT_INITIAL_CASH = 10_000.0


def initial_cash_from_env() -> float:
    raw = os.environ.get("POLYTUTOR_INITIAL_CASH", "").strip()
    if not raw:
        return DEFAULT_INITIAL_CASH
    try:
        value = float(raw)
    except ValueError:
        return DEFAULT_INITIAL_CASH
    if value <= 0:
        return DEFAULT_INITIAL_CASH
    return value


def create_portfolio(initial_cash: float | None = None) -> PaperPortfolio:
    cash = DEFAULT_INITIAL_CASH if initial_cash is None else float(initial_cash)
    if cash <= 0:
        cash = DEFAULT_INITIAL_CASH
    return PaperPortfolio(cash=cash, initial_cash=cash)

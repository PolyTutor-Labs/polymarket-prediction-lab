"""PolyTutor Prediction Lab — educational demo/paper prediction-market toolkit.

Offline by default. No live trading, wallets, or order placement.
"""

from __future__ import annotations

__version__ = "0.1.0"
__mode_default__ = "demo"

# Public re-exports for learners exploring the package interactively.
from polytutor_prediction.models import (
    Market,
    OrderBook,
    OrderBookLevel,
    Outcome,
    PaperFill,
    PaperOrder,
    PaperPortfolio,
    PaperPosition,
    Quote,
)

__all__ = [
    "__version__",
    "__mode_default__",
    "Market",
    "Outcome",
    "OrderBook",
    "OrderBookLevel",
    "Quote",
    "PaperOrder",
    "PaperFill",
    "PaperPosition",
    "PaperPortfolio",
]

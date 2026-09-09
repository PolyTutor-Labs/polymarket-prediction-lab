"""Deterministic offline fixtures for the educational lab.

No network calls. Values are stable so tests and lessons reproduce.
"""

from __future__ import annotations

from polytutor_prediction.models import (
    Market,
    OrderBook,
    OrderBookLevel,
    Outcome,
    OutcomeLabel,
)


def _book(
    outcome: OutcomeLabel,
    bids: list[tuple[float, float]],
    asks: list[tuple[float, float]],
) -> OrderBook:
    return OrderBook(
        outcome=outcome,
        bids=[OrderBookLevel(price=p, size=s) for p, s in bids],
        asks=[OrderBookLevel(price=p, size=s) for p, s in asks],
    ).sorted_copy()


def build_demo_markets() -> list[Market]:
    """Return a small catalog of binary demo markets."""
    markets: list[Market] = []

    # Market 1: tight spread, balanced book — good intro midpoint example.
    yes1 = Outcome(OutcomeLabel.YES, "demo-yes-election-2028", "YES")
    no1 = Outcome(OutcomeLabel.NO, "demo-no-election-2028", "NO")
    markets.append(
        Market(
            market_id="demo-mkt-election-2028",
            question="Will candidate A win the 2028 demo election?",
            category="politics-demo",
            yes=yes1,
            no=no1,
            yes_book=_book(
                OutcomeLabel.YES,
                bids=[(0.54, 1200), (0.53, 800), (0.52, 500)],
                asks=[(0.56, 900), (0.57, 700), (0.58, 400)],
            ),
            no_book=_book(
                OutcomeLabel.NO,
                bids=[(0.42, 1000), (0.41, 600), (0.40, 350)],
                asks=[(0.44, 850), (0.45, 500), (0.46, 300)],
            ),
            description="Balanced book for learning spread and midpoint.",
        )
    )

    # Market 2: wide spread — liquidity / cost-of-immediacy lesson.
    yes2 = Outcome(OutcomeLabel.YES, "demo-yes-rainfall", "YES")
    no2 = Outcome(OutcomeLabel.NO, "demo-no-rainfall", "NO")
    markets.append(
        Market(
            market_id="demo-mkt-rainfall-q4",
            question="Will demo-city rainfall exceed 40 inches in Q4?",
            category="weather-demo",
            yes=yes2,
            no=no2,
            yes_book=_book(
                OutcomeLabel.YES,
                bids=[(0.30, 200), (0.28, 150)],
                asks=[(0.38, 180), (0.40, 120)],
            ),
            no_book=_book(
                OutcomeLabel.NO,
                bids=[(0.58, 220), (0.56, 160)],
                asks=[(0.66, 190), (0.68, 100)],
            ),
            description="Wide spreads illustrate liquidity risk.",
        )
    )

    # Market 3: skewed imbalance — research observation fodder.
    yes3 = Outcome(OutcomeLabel.YES, "demo-yes-product-launch", "YES")
    no3 = Outcome(OutcomeLabel.NO, "demo-no-product-launch", "NO")
    markets.append(
        Market(
            market_id="demo-mkt-product-launch",
            question="Will Product X ship before the demo deadline?",
            category="tech-demo",
            yes=yes3,
            no=no3,
            yes_book=_book(
                OutcomeLabel.YES,
                bids=[(0.71, 2000), (0.70, 1500), (0.69, 900)],
                asks=[(0.72, 400), (0.73, 350), (0.74, 200)],
            ),
            no_book=_book(
                OutcomeLabel.NO,
                bids=[(0.26, 500), (0.25, 400)],
                asks=[(0.28, 1800), (0.29, 1200), (0.30, 800)],
            ),
            description="Bid-heavy YES book for imbalance lessons.",
        )
    )

    # Market 4: near-even pair cost educational case.
    yes4 = Outcome(OutcomeLabel.YES, "demo-yes-sports", "YES")
    no4 = Outcome(OutcomeLabel.NO, "demo-no-sports", "NO")
    markets.append(
        Market(
            market_id="demo-mkt-championship",
            question="Will Team Blue win the demo championship?",
            category="sports-demo",
            yes=yes4,
            no=no4,
            yes_book=_book(
                OutcomeLabel.YES,
                bids=[(0.48, 600), (0.47, 400)],
                asks=[(0.50, 550), (0.51, 300)],
            ),
            no_book=_book(
                OutcomeLabel.NO,
                bids=[(0.48, 580), (0.47, 420)],
                asks=[(0.50, 560), (0.51, 280)],
            ),
            description="Pair-cost observation: sum of asks near 1.00.",
        )
    )

    return markets


# Module-level singleton for simple imports in lessons.
DEMO_MARKETS: list[Market] = build_demo_markets()

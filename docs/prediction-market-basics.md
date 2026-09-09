# Prediction-market basics

This note maps **public prediction-market ideas** onto the types in
`src/polytutor_prediction/models.py` and the four demo fixtures. It is
not a venue rulebook and not a method for earning money.

## Binary markets

A **binary** market asks a yes/no question. This lab stores one
`Market` with two `Outcome` objects:

- `OutcomeLabel.YES`
- `OutcomeLabel.NO`

Each outcome has its own `OrderBook`. Prices on a level are floats
intended to sit in **0.0–1.0** (see the comment on `OrderBookLevel`).

Example fixture (`demo-mkt-election-2028`):

> Will candidate A win the 2028 demo election?

That question is fictional. The books exist so you can practice reading
quotes, not so you can forecast an election.

## Price as a probability *proxy*

In a liquid binary market, the traded price of YES is often *discussed*
as “the market’s implied probability that YES settles to 1.” This lab
never observes a live tape. It exposes one local proxy:

```
midpoint = (best_bid + best_ask) / 2
```

implemented in `orderbook.midpoint`. The function docstring calls this
a **rough implied-probability proxy — not a fair-value oracle**.

Reasons the midpoint is not “the true probability”:

- It ignores size. A 0.01-wide book with 1 share is not the same as a
  deep book at the same prices.
- It ignores the other outcome. YES mid + NO mid need not equal 1.
- Demo books have no fees, no clock, and no settlement engine.
- Empty books return `None`, not 0.5.

Treat any midpoint you see in the CLI as a **teaching number**.

## Complementary outcomes

If YES pays 1 when the event happens and 0 otherwise, and NO pays the
complement, then buying **one YES and one NO** is a completeness
thought experiment: you would own 1 in every world, at a cost equal to
the two purchase prices.

This lab does **not** execute that pair as a strategy. Research only
*reports* `yes_ask + no_ask` and `yes_bid + no_bid`
(`observe_pair_cost`). A sum near 1.00 is interesting for learning.
It is **not** a guaranteed arbitrage. Real venues add fees, inventory
risk, latency, and partial fills. See [research.md](research.md).

## Status and settlement

`Market.status` defaults to `"open"`. The lab does **not** resolve
events, pay winners, or move cash at expiry. Paper PnL is mark-to-mid
plus realized PnL from selling inventory back into the *same* demo
book.

## Demo catalog (all fictional)

| ID | Category | Lesson |
| --- | --- | --- |
| `demo-mkt-election-2028` | `politics-demo` | Balanced, tight YES book |
| `demo-mkt-rainfall-q4` | `weather-demo` | Wide spreads |
| `demo-mkt-product-launch` | `tech-demo` | Bid-heavy YES imbalance |
| `demo-mkt-championship` | `sports-demo` | Pair-ask sum `1.00` |

`MarketService.count()` is **4**. Categories come from
`MarketService.categories()` (sorted unique strings).

## What this section does not claim

- That demo prices are fair.
- That you should buy YES when midpoint is “low.”
- That pair-cost near 1.00 is free money.
- That paper results transfer to any real venue.

Continue with [order-book.md](order-book.md).

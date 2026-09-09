# Research observations

The `research/` package turns book math into **labeled observations**.
Each dataclass carries a `note` that starts with `Educational` and
states that the number is not a recommendation.

Observers **do not** call `PaperEngine`. The Research menu only prints
them. You decide later whether to place a paper order — and the lab
still will not claim the idea was “alpha.”

Public exports (`research/__init__.py`):

- `observe_spread`
- `observe_midpoint`
- `observe_imbalance`
- `observe_pair_cost`

## Spread (`research/spread.py`)

`observe_spread(market, outcome=YES)` reads the YES or NO book and
returns `SpreadObservation`: `spread`, `best_bid`, `best_ask`.

Note in code:

> Educational: wider spreads often mean higher transaction cost. Not a
> trade recommendation.

CLI Research screen currently prints the **YES** spread (default
outcome). Use the Order Book menu to inspect NO.

## Midpoint (`research/midpoint.py`)

`observe_midpoint` returns `MidpointObservation.midpoint`.

Note in code:

> Educational: midpoint ≈ (bid+ask)/2 is a rough implied-probability
> proxy, not a true probability or fair value.

## Imbalance (`research/imbalance.py`)

`observe_imbalance(market, outcome=YES, levels=3)` returns imbalance
plus `bid_depth` and `ask_depth` from `orderbook.depth`.

Note in code:

> Educational: imbalance > 0.5 means more bid depth on top levels. Skew
> is an observation, not a guaranteed edge.

`demo-mkt-product-launch` is the fixture built for this lesson
(bid-heavy YES book).

## Pair cost (`research/pair_cost.py`)

`observe_pair_cost(market)` quotes **both** books:

| Field | Formula |
| --- | --- |
| `yes_ask` / `no_ask` | best ask on each book |
| `pair_ask_sum` | `yes_ask + no_ask` (or `None`) |
| `yes_bid` / `no_bid` | best bid on each book |
| `pair_bid_sum` | `yes_bid + no_bid` (or `None`) |

Championship fixture (`demo-mkt-championship`), verified in
`tests/test_research.py`:

| Field | Value |
| --- | --- |
| YES ask | `0.50` |
| NO ask | `0.50` |
| pair ask sum | `1.00` |
| YES bid | `0.48` |
| NO bid | `0.48` |
| pair bid sum | `0.96` |

Note in code (must stay honest):

> Educational observation only. Sum of asks near 1.00 is interesting
> for learning; it is NOT a guaranteed arbitrage. Fees, fill risk, and
> timing matter in real venues. This lab does not place live orders.

Buying both asks in a real venue would also pay fees and could fail on
one leg. This lab never auto-executes a pair trade.

Election fixture pair-ask sum is also `0.56 + 0.44 = 1.00` on the best
asks. That coincidence is for teaching, not a hidden “arb scanner.”

## How to use these numbers

1. Predict what the function should return from the levels you see.
2. Compare to the Research menu or a Python REPL import.
3. Write a journal note *after* a paper trade explaining whether the
   observation changed your size — not whether it “worked.”

Do not treat a tight spread, a high imbalance, or a pair sum below 1
as a reason to use real funds.

Next: [paper-trading.md](paper-trading.md).

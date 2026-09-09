# Order book

All formulas below are implemented in
`src/polytutor_prediction/orderbook.py`. If the code changes, this page
must change with it.

Books are **aggregated levels**: each `OrderBookLevel` is a `(price,
size)` pair. `OrderBook.sorted_copy()` sorts bids high→low and asks
low→high. Demo fixtures are stored already sorted.

## Best bid / best ask

```
best_bid = max(book.bids, key=price)   or None if no bids
best_ask = min(book.asks, key=price)   or None if no asks
```

`quote(book)` returns a `Quote`:

| Field | Source |
| --- | --- |
| `best_bid` | price of `best_bid`, else `None` |
| `best_ask` | price of `best_ask`, else `None` |
| `bid_size` | size of that bid level, else `0.0` |
| `ask_size` | size of that ask level, else `0.0` |

## Spread

```
spread = best_ask - best_bid
```

If either side is missing, `spread` is `None`. Wider spreads in this
lab mean a larger gap between the best resting buy and the best
resting sell — a teaching stand-in for **cost of immediacy**, not a
signal to trade.

Worked fixture (`demo-mkt-election-2028` YES):

- bids: `(0.54, 1200), (0.53, 800), (0.52, 500)`
- asks: `(0.56, 900), (0.57, 700), (0.58, 400)`
- best bid `0.54`, best ask `0.56`, **spread `0.02`**

Contrast `demo-mkt-rainfall-q4` YES: best bid `0.30`, best ask `0.38`,
**spread `0.08`**.

## Midpoint (implied-probability proxy)

```
midpoint = (best_bid + best_ask) / 2.0
```

Missing side → `None`. Election YES midpoint is **`0.55`**. The CLI
prints this with the label “rough implied probability proxy.”

## Depth

```
depth(book, levels=3) →
    bid_depth = sum(size of top N bids by price)
    ask_depth = sum(size of top N asks by price)
    levels    = float(N)
```

Default `N = 3`. Election YES with default levels:

- bid depth = `1200 + 800 + 500 = 2500`
- ask depth = `900 + 700 + 400 = 2000`

## Imbalance

```
imbalance = bid_depth / (bid_depth + ask_depth)
```

If total depth is `<= 0`, result is `None`. Values **greater than
0.5** mean more resting bid size on the top N levels (docstring in
`orderbook.imbalance`). That is an observation, not an edge.

Election YES: `2500 / 4500 ≈ 0.5556`.

`demo-mkt-product-launch` YES (default 3 levels): bid depth `4400`,
ask depth `950`, imbalance `4400 / 5350 ≈ 0.8224`.

## Paper fill model (VWAP walk)

Paper buys and sells do **not** rest new levels. They walk existing
size.

**Buy** (`vwap_buy`): walk asks **low to high**. Take `min(remaining,
level.size)` at each level. Return `(average_price, filled_size)` or
`None` if `size <= 0` or nothing fills.

```
avg_price = total_cost / filled_size
```

**Sell** (`vwap_sell`): walk bids **high to low**. Same accumulation
on proceeds.

Worked test book (from `tests/test_orderbook.py`):

- asks: `0.50 × 5`, `0.51 × 10`
- buy size `8` → take 5 @ 0.50 and 3 @ 0.51
- average = `(5×0.50 + 3×0.51) / 8 = 0.50375`
- filled = `8`

If requested size exceeds standing size, the walk stops when the book
is exhausted and returns a **partial** fill (`filled < size`) as long
as `filled > 0`.

## Empty and invalid cases

| Situation | Result |
| --- | --- |
| No bids / no asks | quote sides `None`; spread/mid `None` |
| `vwap_*` size `<= 0` | `None` |
| No liquidity on that side | `None` (paper engine rejects) |

## CLI surface

Order Book menu (`LabApp.order_book_menu`) prints best bid/ask with
size, spread, midpoint, depth, imbalance, then every bid and ask
level. It does not place paper orders.

Next: [research.md](research.md).

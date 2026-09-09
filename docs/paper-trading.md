# Paper trading

Paper trading here means **virtual cash against demo books**. Fills are
computed in `PaperEngine` (`src/polytutor_prediction/paper/engine.py`).
Nothing is submitted to a venue.

Paper results are **fictional**. They do not predict live results.

## Starting cash

`create_portfolio()` uses `DEFAULT_INITIAL_CASH = 10_000.0`.
`LabApp` calls `initial_cash_from_env()` so `POLYTUTOR_INITIAL_CASH`
can override that when it parses as a **positive** float. Invalid or
non-positive values fall back to `10000`.

Cash never leaves the process. There are no deposits, withdrawals, or
on-chain settlement.

## Buy (walk the asks)

`PaperEngine.buy(market, outcome, size, note="")`:

1. `check_order_size(size)` — must be `> 0` and `<= 500` by default.
2. `check_daily_loss(daily_realized_pnl)` — blocked only if realized
   PnL is **strictly less than** `-1000` (`< -max_daily_loss`).
3. `vwap_buy` on the YES or NO book. No asks → reject
   `"No ask liquidity to fill paper buy."`
4. `cost = avg_price * filled`. If `cost > cash` → reject
   (insufficient paper cash).
5. Project new average price:

   ```
   new_size = current_size + filled
   new_avg  = (current_size * current_avg + filled * avg_price) / new_size
   ```

6. `check_position_notional(new_size * new_avg)` — default cap
   **$2,000**.
7. Debit cash, append `PaperOrder` / `PaperFill`, replace the
   position, journal `kind="fill"`.

The fill price is the **VWAP**, not the midpoint and not a
limit-price you typed. The CLI asks only for size (and an optional
note).

## Sell (walk the bids)

`PaperEngine.sell` requires existing inventory. You cannot short.

1. Same size and daily-loss checks as buy.
2. No position or `size <= 0` → `"No paper inventory to sell."`
3. `sell_size = min(requested_size, pos.size)` — will not sell more
   than you hold.
4. `vwap_sell` on that outcome book. No bids → reject.
5. `proceeds = avg_price * filled`
6. `realized = (avg_price - pos.avg_price) * filled`
7. Credit cash; add `realized` to `daily_realized_pnl` and to the
   position’s `realized_pnl` if shares remain.
8. If remaining size `<= 1e-12`, the position key is removed.

## Marks and equity

`mark_price` is `orderbook.midpoint` of that outcome’s book.

```
unrealized_pnl = Σ (mid - avg_price) * size
                 (skip if market or mid is missing)

equity = cash + Σ size * px
         px = mid if available, else avg_price
         if the market id is unknown, px = avg_price
```

Dashboard “Equity (mark)” and “Unrealized PnL” use these functions
with the in-memory market map.

## Educational limits (`paper/limits.py`)

Defaults (also tested in `tests/test_limits.py`):

| Cap | Default | Check |
| --- | --- | --- |
| Max order size | `500` shares | `size > 500` rejected |
| Max position notional | `$2000` | `new_size * new_avg > 2000` |
| Max daily loss | `$1000` | `daily_realized_pnl < -1000` |

These are **lab training wheels**, not exchange rules. Hitting a cap
journals `kind="reject"` and does not fill.

## Journal (`paper/journal.py`)

In-memory list of `JournalEntry`: `timestamp`, `kind`, `message`,
optional `market_id`, `detail` dict.

| Kind | When |
| --- | --- |
| `fill` | Buy or sell succeeded |
| `reject` | Limit, cash, liquidity, or inventory failure |

The CLI Journal menu prints `timestamp`, `kind`, and `message` only.
`detail` may include `cost`, `proceeds`, `realized_pnl`, and `note`.
`Journal.clear()` exists for tests; the CLI does not persist or reload
entries. Closing the process discards the journal.

## CLI workflow

Paper Portfolio menu:

- `a` show positions (`market_id`, outcome, size, avg) and cash
- `b` buy YES/NO
- `c` sell YES/NO

Unknown submenu choice prints `Cancelled.`

## What paper trading is not

- Not a path to live orders
- Not a backtest over historical tape
- Not a fee, rebate, or latency model
- Not a promise that a journal “win” will repeat

See [risk-and-limitations.md](risk-and-limitations.md).

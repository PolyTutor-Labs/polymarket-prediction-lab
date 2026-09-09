# Architecture

This lab is a **local, in-process** educational stack. Every layer below
exists in `src/polytutor_prediction/`. Layers that do not exist (live
venue client, signing, custody) are absent on purpose.

## Educational flow

```
demo_data → market_service → orderbook analytics
                ↓
            research observations (educational only)
                ↓
            paper engine (virtual cash, fills, journal)
                ↓
            CLI / TUI menus (stdlib)
```

There is no network hop and no background worker. A session starts in
`cli.main`, which calls `_ensure_demo_mode()` and constructs `LabApp`.

## Layers

### 1. Models (`models.py`)

Frozen or mutable dataclasses only:

| Type | Role |
| --- | --- |
| `Outcome` / `OutcomeLabel` | YES or NO plus a display `token_id` |
| `OrderBookLevel` | `price` (0–1) and `size` |
| `OrderBook` | bids (high→low) and asks (low→high) |
| `Quote` | best bid/ask and top-of-book sizes |
| `Market` | question, category, YES/NO books, status |
| `PaperOrder` / `PaperFill` | simulated ticket and fill |
| `PaperPosition` | size, average price, realized PnL |
| `PaperPortfolio` | cash, positions, fills, orders, daily realized PnL |

`PaperPortfolio` has **no** custody or address fields (asserted by
`tests/test_security.py`). Position keys are
`f"{market_id}:{outcome.value}"`.

`token_id` values such as `demo-yes-election-2028` are **fixture
labels**, not API credentials.

### 2. Demo data (`demo_data.py`)

`build_demo_markets()` returns four binary markets. Values are constant
so lessons and tests reproduce. `DEMO_MARKETS` is a module-level
snapshot; `MarketService()` rebuilds via `build_demo_markets()` unless
you pass an explicit list.

| `market_id` | Teaching intent |
| --- | --- |
| `demo-mkt-election-2028` | Tight, balanced book (spread / midpoint) |
| `demo-mkt-rainfall-q4` | Wide spread (cost of immediacy) |
| `demo-mkt-product-launch` | Bid-heavy YES book (imbalance) |
| `demo-mkt-championship` | Pair-ask sum near `1.00` |

### 3. Market service (`market_service.py`)

In-memory catalog: `list_markets`, `get_market`, `categories`, `count`.
`default_service()` copies `DEMO_MARKETS`. No HTTP.

### 4. Order-book math (`orderbook.py`)

Pure functions: `best_bid`, `best_ask`, `quote`, `spread`, `midpoint`,
`depth`, `imbalance`, `vwap_buy`, `vwap_sell`. Formulas are documented
in [order-book.md](order-book.md) and must stay aligned with this file.

### 5. Research (`research/`)

Four observers wrap the book math and attach educational notes. They
never call the paper engine. See [research.md](research.md).

### 6. Paper (`paper/`)

| Module | Role |
| --- | --- |
| `portfolio.py` | Default cash `10000`; env override |
| `limits.py` | Educational caps (size / notional / daily loss) |
| `journal.py` | In-memory `JournalEntry` list |
| `engine.py` | Buy/sell, mark-to-mid, equity |

Fills use `vwap_buy` / `vwap_sell` against the selected outcome book.
Nothing is sent to a venue. See [paper-trading.md](paper-trading.md).

### 7. CLI (`cli.py`, `tui/menus.py`)

`python -m polytutor_prediction` → `__main__.py` → `cli.main` →
`LabApp.run`. `--once-dashboard` prints the dashboard once and exits.
`--version` reports package version `0.1.0`.

Menu input is `str.strip` plus dict dispatch. Size is `float(size_s)`;
invalid input is rejected. Notes are stored as strings on the paper
order and journal detail. There is no `eval` of user input.

## What is intentionally absent

The following must remain **absent** from runtime source (names may
appear in security docs and tests as absence assertions):

- Live venue / authenticated order client
- Signing, custody, or address fields used for chain transactions
- Runtime network libraries (`requests`, `httpx`, `urllib` clients, sockets)
- Process-launch droppers and remote `eval` / `exec`

`pyproject.toml` sets `[tool.polytutor] live_trading = false`. The CLI
does not read that table as a live switch; it is documentation for
reviewers.

## Dependency surface

| Item | Value |
| --- | --- |
| Runtime `dependencies` | `[]` |
| Dev extra | `pytest==8.3.5`, `ruff==0.11.13` |
| Optional extra | `textual==1.0.0` (unused by default CLI) |

## Persistence

Runtime paper state is **in memory**. `.gitignore` reserves names such
as `paper_journal.jsonl` for possible future local artifacts; the
current engine does not write them.

Next: [order-book.md](order-book.md) or [paper-trading.md](paper-trading.md).

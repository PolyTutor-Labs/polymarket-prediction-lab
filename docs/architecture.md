# Architecture

Educational flow (no live I/O):

```
demo_data → market_service → orderbook analytics
                ↓
            research observations (educational only)
                ↓
            paper engine (virtual cash, fills, journal)
                ↓
            CLI / TUI menus (stdlib)
```

## Layers

1. **Models** — pure dataclasses for markets, books, paper entities.
2. **Demo data** — deterministic fixtures; no network.
3. **Order book math** — best bid/ask, spread, midpoint, depth, imbalance.
4. **Research** — observations that *look like* trading ideas but are labeled
   educational and never auto-execute live.
5. **Paper** — portfolio with educational risk limits.
6. **CLI** — interactive menus for learning.

There is intentionally **no** CLOB client, wallet, or signing layer.

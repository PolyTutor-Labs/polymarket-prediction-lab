# PolyTutor Prediction Market Lab

**Educational, offline, paper-only prediction-market learning environment.**

Public lab version: **v0.1.0**. That version is a packaging snapshot, not a
performance claim.

```
Prediction-market education
        ↓
Offline demo markets
        ↓
Order-book mechanics
        ↓
Probability / liquidity research
        ↓
Paper trading
        ↓
Engineering education
```

> **Not live trading. Not a wallet. Not financial advice. Demo/offline by default.**

This repository is an **independent PolyTutor clean-room rebuild**. It is
**not** a fork, sanitized fork, or continuation of any rejected malicious
upstream. See [CLEAN_ROOM.md](CLEAN_ROOM.md).

## PolyTutor Labs

This project is maintained by **PolyTutor Labs** as a local classroom for
prediction-market *mechanics*: binary markets, books, implied-probability
proxies, liquidity, research observations, and paper simulation.

PolyTutor work on this repository includes:

- independent clean-room implementation (original educational code)
- clean-room pre-publish security review
- security hardening and secret scanning
- test and quality-gate stabilization
- educational documentation (this Task 10 layer)

The lab is **not affiliated with Polymarket**. It does not call live
exchange APIs and does not place orders.

## About This Project

`polytutor-prediction` is a **stdlib CLI** that loads four deterministic
demo markets in memory, inspects their books, runs labeled research
observations, and simulates paper buys/sells against those books.

On each session the lab:

1. Builds offline fixtures from [`demo_data.py`](src/polytutor_prediction/demo_data.py).
2. Lists and inspects binary YES/NO markets through `MarketService`.
3. Computes book analytics (quote, spread, midpoint, depth, imbalance, VWAP).
4. Surfaces educational research notes (not trade signals).
5. Fills paper orders locally against the demo book.
6. Records fills and rejects in an **in-memory** journal.

There is **no** live order routing, no custody of funds, and no signing
layer. Unsupported mode strings still run educational demo behavior.

## What You Will Learn

- How a **binary prediction market** is represented (question, YES/NO
  outcomes, prices in `[0, 1]`).
- How a **central-limit book** stores bids and asks, and how best bid,
  best ask, spread, and midpoint are computed in this lab.
- Why **midpoint** is only a rough implied-probability *proxy*, not a
  true probability or fair-value oracle.
- How **depth** and **imbalance** describe resting size — observations,
  not guaranteed edges.
- How **pair cost** (YES ask + NO ask vs `1.00`) is an educational
  completeness check, **not** risk-free arbitrage.
- How a **paper engine** walks the book (VWAP), updates cash and average
  price, marks equity to midpoint, and applies educational limits.
- How to keep a **decision journal** and reflect without treating paper
  PnL as a forecast.

This project does **not** teach a profitable method and does **not**
provide investment advice.

## Features

Verified in the current tree (`src/polytutor_prediction/`):

- Four deterministic demo markets (election, rainfall, product launch,
  championship) with YES and NO books
- Pure order-book analytics in `orderbook.py`
- Four research observers: spread, midpoint, imbalance, pair cost
- Paper engine with default **$10,000** virtual cash
- Educational limits: max order size **500**, max position notional
  **$2,000**, max daily realized loss **$1,000**
- In-memory journal (`fill` / `reject`)
- Interactive stdlib menus plus `--once-dashboard` smoke
- Empty runtime `dependencies` in `pyproject.toml`
- Quality gates: pytest, ruff, compileall, secret scan, markdown links

There is intentionally **no** live venue client, signing module, or
wallet field on `PaperPortfolio`.

## Architecture Overview

```
demo_data → market_service → orderbook analytics
                ↓
            research observations (educational only)
                ↓
            paper engine (virtual cash, fills, journal)
                ↓
            CLI / TUI menus (stdlib)
```

| Layer | Location | Responsibility |
| --- | --- | --- |
| Models | `src/polytutor_prediction/models.py` | Markets, books, paper types |
| Demo fixtures | `src/polytutor_prediction/demo_data.py` | Deterministic offline catalog |
| Market catalog | `src/polytutor_prediction/market_service.py` | List / get / categories |
| Book math | `src/polytutor_prediction/orderbook.py` | Quote, spread, mid, depth, VWAP |
| Research | `src/polytutor_prediction/research/` | Labeled observations |
| Paper | `src/polytutor_prediction/paper/` | Portfolio, fills, limits, journal |
| CLI | `src/polytutor_prediction/cli.py`, `tui/` | Menus and `--once-dashboard` |

Details: [docs/architecture.md](docs/architecture.md).

## Repository Structure

```
polymarket-prediction-lab/
├── README.md
├── LICENSE
├── CONTRIBUTING.md
├── DISCLAIMER.md
├── SECURITY.md
├── CLEAN_ROOM.md
├── PRE_PUBLISH_SECURITY_REVIEW.md
├── pyproject.toml
├── .env.example
├── docs/
│   ├── README.md
│   ├── getting-started.md
│   ├── architecture.md
│   ├── prediction-market-basics.md
│   ├── order-book.md
│   ├── research.md
│   ├── paper-trading.md
│   ├── risk-and-limitations.md
│   └── learning-path.md
├── scripts/security/check_secrets.py
├── scripts/quality/check.py
├── tests/
└── src/polytutor_prediction/
    ├── models.py
    ├── demo_data.py
    ├── market_service.py
    ├── orderbook.py
    ├── research/
    ├── paper/
    ├── tui/
    └── cli.py
```

## Getting Started

Requirements: Python **3.10+**. No network is required to run the lab.

```bash
python -m venv .venv && source .venv/bin/activate   # optional
pip install -e ".[dev]"
python -m polytutor_prediction
```

Smoke the dashboard without menus:

```bash
python -m polytutor_prediction --once-dashboard
```

`.env.example` may only define `POLYTUTOR_MODE=demo` and
`POLYTUTOR_INITIAL_CASH=10000`. Do not add credentials.

Full install and first lesson: [docs/getting-started.md](docs/getting-started.md).

## Paper Trading Workflow

1. Start the CLI (`python -m polytutor_prediction`).
2. Open **Dashboard** — confirm mode `demo`, cash, and **Live trading: NO**.
3. Browse **Markets**, then **Order Book** for one YES or NO book.
4. Run **Research** observations and treat them as hypotheses.
5. Place a small paper buy under educational limits; optionally sell.
6. Review the **Journal**, then write why the fill or reject happened.

Paper PnL is fictional. See [docs/paper-trading.md](docs/paper-trading.md).

## Testing

```bash
pytest
ruff check src tests scripts
python -m compileall -q src scripts tests
python scripts/security/check_secrets.py
python scripts/quality/check.py
python scripts/quality/check.py links
```

Pytest collects only `tests/`. Quality CI is read-only and does not
deploy or trade.

## Documentation

| Document | Topic |
| --- | --- |
| [docs/README.md](docs/README.md) | Learning-path index |
| [docs/getting-started.md](docs/getting-started.md) | Install, CLI, first session |
| [docs/architecture.md](docs/architecture.md) | Layers and module map |
| [docs/prediction-market-basics.md](docs/prediction-market-basics.md) | Binary markets and prices |
| [docs/order-book.md](docs/order-book.md) | Book formulas used in code |
| [docs/research.md](docs/research.md) | Educational observations |
| [docs/paper-trading.md](docs/paper-trading.md) | Fills, marks, journal |
| [docs/risk-and-limitations.md](docs/risk-and-limitations.md) | Caps and what this lab is not |
| [docs/learning-path.md](docs/learning-path.md) | Suggested study order |
| [SECURITY.md](SECURITY.md) | Defaults, scanner, reporting |
| [CLEAN_ROOM.md](CLEAN_ROOM.md) | Provenance and prohibited patterns |
| [PRE_PUBLISH_SECURITY_REVIEW.md](PRE_PUBLISH_SECURITY_REVIEW.md) | Historical pre-publish review |
| [CONTRIBUTING.md](CONTRIBUTING.md) | What contributions are accepted |
| [DISCLAIMER.md](DISCLAIMER.md) | Educational-use disclaimer |

## Risks and Limitations

- **Paper ≠ live.** Fills walk the *demo* book with a simple VWAP model.
  There is no exchange matching, fees, latency, or partial-fill retry.
- **Midpoint is a proxy.** `(best_bid + best_ask) / 2` is not a true
  probability and is not a pricing oracle.
- **Educational limits are lab caps**, not exchange or regulatory rules
  (`EducationalLimits` in `paper/limits.py`).
- **Journal is session-local.** Entries live in memory; they are not
  written to disk by the runtime.
- **No live path.** The CLI has no branch that places real orders.
  Setting an unsupported `POLYTUTOR_MODE` still prints **Live trading: NO**.

More detail: [docs/risk-and-limitations.md](docs/risk-and-limitations.md).

## Security

Default mode is **demo / offline**. Runtime dependencies are empty. The
secret scanner and security tests assert that live-trading and malware-
shaped patterns remain absent from executable source.

See [SECURITY.md](SECURITY.md). Report lab defects privately to
maintainers; do not file public issues with exploit detail for live
systems — this lab has no live trading surface by design.

## Contributing

Contributions that help people **learn prediction-market mechanics** are
welcome. Contributions that market this lab as a live product or a
source of guaranteed returns are not.

See [CONTRIBUTING.md](CONTRIBUTING.md).

## Disclaimer

See [DISCLAIMER.md](DISCLAIMER.md). This is an educational simulator.
Paper balances, fills, and PnL are **fictional**. Nothing here places
real orders or connects to live exchange APIs for trading.

## Attribution

**Independent clean-room.** Original educational code in this repository
was written for PolyTutor Phase 1 #7. It is **not** derived from
rejected malicious trees, production trading bots, or sanitized forks of
those trees. Provenance claims are recorded in [CLEAN_ROOM.md](CLEAN_ROOM.md).

PolyTutor Labs does not claim affiliation with Polymarket.

## License

MIT — see [LICENSE](LICENSE).

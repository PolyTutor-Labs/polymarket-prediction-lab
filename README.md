# PolyTutor Prediction Market Lab

**Educational, offline, paper-only prediction-market learning environment.**

PolyTutor Phase 1 #7 clean-room rebuild. This lab teaches how prediction markets
work: markets → order books → implied probability → liquidity → research
hypotheses → paper simulation → reflection.

> **Not live trading. Not a wallet. Not financial advice. Demo/offline by default.**

## Quick start

```bash
cd polymarket-prediction-lab
python -m venv .venv && source .venv/bin/activate   # optional
pip install -e ".[dev]"
python -m polytutor_prediction
```

Or run tests:

```bash
pytest
python scripts/security/check_secrets.py
```

## What you learn

| Stage | Module | Concept |
|-------|--------|---------|
| Markets | `market_service` | List / inspect demo binary markets |
| Order book | `orderbook` | Best bid/ask, spread, midpoint, depth, imbalance |
| Probability | models + orderbook | Midpoint as a rough implied probability |
| Liquidity | orderbook depth | How size at each level affects fills |
| Research | `research/` | Educational observations (not guaranteed arb) |
| Paper sim | `paper/` | $10k virtual cash, buys, fills, PnL, journal |
| Learning | CLI menus + docs | Structured exploration with hard educational limits |

## Security posture (v0.1.0)

- **DEMO/OFFLINE DEFAULT ONLY** (`POLYTUTOR_MODE=demo`)
- No private keys, mnemonics, signing, CLOB secrets, or live order placement
- No wallet fields in models or CLI
- `.env.example` may only contain `POLYTUTOR_MODE` and `POLYTUTOR_INITIAL_CASH`
- Prefer zero `subprocess`; no download-and-run, no remote `eval`/`exec`
- See [SECURITY.md](SECURITY.md) and [CLEAN_ROOM.md](CLEAN_ROOM.md)

## Package layout

```
src/polytutor_prediction/
  models.py          Market, OrderBook, Paper* types
  demo_data.py       Deterministic fixtures
  orderbook.py       Book analytics
  market_service.py  Demo market catalog
  research/          Spread, midpoint, imbalance, pair_cost observations
  paper/             Paper portfolio, fills, journal, educational limits
  tui/               Interactive stdlib CLI menus
  cli.py             Entry: python -m polytutor_prediction
```

## Disclaimer

See [DISCLAIMER.md](DISCLAIMER.md). This is an educational simulator. Paper PnL
is fictional. Nothing here places real orders or connects to live exchange APIs
for trading.

## License

MIT — see [LICENSE](LICENSE).

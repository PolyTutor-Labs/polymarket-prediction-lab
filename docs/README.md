# Documentation

Learning index for the **PolyTutor Prediction Market Lab**.

This repository is an offline classroom for prediction-market mechanics.
It is not a production trading platform, not a source of guaranteed
returns, not financial advice, and not a live trading service.

It is an **independent PolyTutor clean-room rebuild**, not a fork of
rejected malicious upstream. Provenance: [CLEAN_ROOM.md](../CLEAN_ROOM.md).

## Start here

1. [Repository README](../README.md) — identity, features, attribution
2. [Getting started](getting-started.md) — install and first CLI session
3. [Prediction-market basics](prediction-market-basics.md) — YES/NO, prices
4. [Architecture](architecture.md) — actual layers and module map
5. [Order book](order-book.md) — formulas implemented in `orderbook.py`
6. [Research](research.md) — labeled observations, not signals
7. [Paper trading](paper-trading.md) — virtual cash, fills, marks
8. [Risk and limitations](risk-and-limitations.md) — caps and gaps
9. [Learning path](learning-path.md) — staged study order (no live stage)
10. [Security](../SECURITY.md) · [Disclaimer](../DISCLAIMER.md) · [Contributing](../CONTRIBUTING.md)

## Repository map

| Path | What it is |
| --- | --- |
| `src/polytutor_prediction/` | Offline demo, book math, research, paper, CLI |
| `tests/` | Behavioral and security/quality regression tests |
| `scripts/security/` | In-process secret / capability scanner |
| `scripts/quality/` | compileall, syntax, pytest, secrets, doc links |
| `.env.example` | `POLYTUTOR_MODE` and `POLYTUTOR_INITIAL_CASH` only |
| `.github/workflows/` | Read-only Security + Quality CI (no deploy) |

## Learning identity

```
Prediction-market education
        ↓
Offline demo
        ↓
Order-book
        ↓
Probability / liquidity research
        ↓
Paper trading
        ↓
Engineering education
```

There is **no** final “go live” stage in this curriculum.

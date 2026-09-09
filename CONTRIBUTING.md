# Contributing

This repository is an **educational, offline, paper-only** prediction-
market lab:

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

Contributions that help people **learn the mechanics** are welcome.
Contributions that market the lab as a live product, a profitable bot,
or a source of guaranteed returns are not.

This is an **independent PolyTutor clean-room rebuild**, not a fork or
sanitized continuation of rejected malicious upstream. Keep that
distinction in docs and comments. See [CLEAN_ROOM.md](CLEAN_ROOM.md)
and [README.md](README.md).

## Before you start

1. Stay on demo / offline / paper. Do not add a live-order path.
2. Do not add custody fields, signing, or live-venue credentials.
3. Do not change order-book, research, or paper **formulas** in a
   documentation-only pull request. If you change a formula, update
   the matching page under `docs/` and the tests together.
4. Do not import hostile trees for “reference implementation.”
5. Keep `.env.example` limited to `POLYTUTOR_MODE` and
   `POLYTUTOR_INITIAL_CASH`.

## Local checks

From the repository root:

```bash
pip install -e ".[dev]"
python -m compileall -q src scripts tests
ruff check src tests scripts
python -m pytest tests/ -q
python scripts/security/check_secrets.py
python scripts/quality/check.py
python scripts/quality/check.py links
```

Run `python scripts/quality/check.py` before opening a pull request.
Quality CI is read-only (compile, lint, tests, secret scan, internal
links). It does not deploy or trade.

## Documentation

Learner guides live under [`docs/`](docs/README.md). When you change a
command, menu, default cap, or formula, update the corresponding guide
in the same change set.

Preserve [SECURITY.md](SECURITY.md), [CLEAN_ROOM.md](CLEAN_ROOM.md),
and [PRE_PUBLISH_SECURITY_REVIEW.md](PRE_PUBLISH_SECURITY_REVIEW.md)
unless you are making a factual link correction.

## Pull requests

- One focused change set
- Describe the educational purpose; do not claim live performance
- Never include `.env` files, key material, or generated caches
- New docs must resolve with `python scripts/quality/check.py links`

Security reporting: [SECURITY.md](SECURITY.md).
Disclaimer: [DISCLAIMER.md](DISCLAIMER.md).

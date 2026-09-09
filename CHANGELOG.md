# Changelog

All notable **lab packaging** changes for this educational repository
are recorded here.

This project is a prediction-market education lab:

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

It is an **independent PolyTutor clean-room rebuild**. It is not a
fork, sanitized fork, or continuation of rejected malicious upstream.
It is not a live trading product, not a wallet, not financial advice,
and not a source of guaranteed returns.

Entries describe repository, documentation, security, and test work.
They do **not** claim profitability, trading success, production
readiness, or live performance.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning follows [SemVer](https://semver.org/spec/v2.0.0.html) for
the public lab snapshot, not for paper-PnL expectancy.

## [0.1.0] — 2026-09-09

First public PolyTutor Labs educational release of
`polymarket-prediction-lab` (installable package `polytutor-prediction`
version `0.1.0`).

The default path remains **demo / offline / paper only**. There is no
live order routing in this release.

### Independent clean-room

- Original educational implementation written for this laboratory
  (offline fixtures, book analytics, labeled research observations,
  paper simulation, stdlib CLI)
- Provenance recorded in `CLEAN_ROOM.md` and the historical
  `PRE_PUBLISH_SECURITY_REVIEW.md`
- Attribution states this is **not** a fork of rejected malicious
  upstream

### Organization

- Installable package under `src/polytutor_prediction/`
- Learner guides under `docs/`
- In-process security and quality runners under `scripts/`

### Portability

- Runtime paths resolve from the package and repository layout
- Local demo sessions are not tied to a developer machine home
  directory
- `.env.example` documents only `POLYTUTOR_MODE` and
  `POLYTUTOR_INITIAL_CASH`

### Security

- `SECURITY.md` policy for demo defaults, reporting, and scanners
- `scripts/security/check_secrets.py` (path / line / rule id only;
  values never printed)
- Clean-room boundary remains educational and local
- Read-only GitHub Actions (`contents: read`, no deploy)

### Testing

- Pytest suite under `tests/` for models, demo fixtures, book math,
  research notes, paper engine, CLI, security, and quality gates
- Public quality commands: `pytest`, `ruff check`, `compileall`,
  `python scripts/security/check_secrets.py`,
  `python scripts/quality/check.py`

### Documentation

- Learner docs: getting started, architecture, prediction-market
  basics, order book, research, paper trading, risk and limitations,
  learning path
- `CONTRIBUTING.md` and `DISCLAIMER.md`
- No final live-trade stage in the curriculum

### Release packaging

- `pyproject.toml` metadata aligned with the public GitHub repository
  and clean-room lab identity
- This changelog, MIT `LICENSE`, and `NOTICE` for public attribution

[0.1.0]: https://github.com/PolyTutor-Labs/polymarket-prediction-lab/releases/tag/v0.1.0

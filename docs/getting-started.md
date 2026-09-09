# Getting started

Run the PolyTutor Prediction Lab **offline**. You do not need exchange
accounts, signing material, or network access for the demo.

## Requirements

- Python **3.10+** (`requires-python` in `pyproject.toml`)
- A virtual environment is optional but recommended
- Runtime package dependencies are **empty**; install the `dev` extra
  for pytest and ruff

Optional extra `textual` is listed in `pyproject.toml` but is **not**
required. The default interface is the stdlib CLI in
`src/polytutor_prediction/tui/menus.py`.

## Install

From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

Editable install exposes:

- module: `python -m polytutor_prediction`
- console script: `polytutor-prediction`

## First session

Interactive menus:

```bash
python -m polytutor_prediction
```

Non-interactive dashboard (used in tests and smoke):

```bash
python -m polytutor_prediction --once-dashboard
```

You should see mode **demo**, **4** markets, default cash **$10,000.00**,
and `Live trading:   NO`.

Menu map (from `LabApp.run` / `HELP_TEXT`):

| Key | Screen | What to notice |
| --- | --- | --- |
| 1 | Dashboard | Mode, cash, equity, unrealized / daily realized PnL |
| 2 | Markets | Four fixture IDs and YES midpoint |
| 3 | Order Book | Bid/ask, spread, midpoint, depth, imbalance, levels |
| 4 | Research | Spread, midpoint, imbalance, pair-cost notes |
| 5 | Paper Portfolio | Show positions; buy or sell YES/NO |
| 6 | Journal | In-memory fill / reject lines |
| 7 | Help | Safety reminder |
| 0 | Quit | Exits; paper state is not persisted |

Suggested first lesson: open market `demo-mkt-election-2028` on the
Order Book screen (YES). Best bid should be `0.54`, best ask `0.56`,
spread `0.02`, midpoint `0.55`. Those numbers come from
`build_demo_markets()` — they are fixtures, not live quotes.

## Configuration

`.env.example` documents the only allowed keys:

```
POLYTUTOR_MODE=demo
POLYTUTOR_INITIAL_CASH=10000
```

The CLI reads the process environment (`os.environ`). It does not load a
dotenv file. If `POLYTUTOR_MODE` is missing or empty, behavior is demo.
If the string is not one of `demo` / `offline` / `paper`, the CLI warns
and **still** runs educational demo behavior — there is no live branch.

`POLYTUTOR_INITIAL_CASH` must parse as a positive float; otherwise the
lab uses `10000` (`paper/portfolio.py`).

Do **not** add credential names or live-venue setup to this file. The
scanner rejects any `.env.example` key other than the two above.

## Quality checks

```bash
pytest
ruff check src tests scripts
python scripts/security/check_secrets.py
python scripts/quality/check.py
python scripts/quality/check.py links
```

## What not to do

- Do not treat paper cash or PnL as withdrawable money.
- Do not add live-order, signing, or custody setup to this lab.
- Do not skip [DISCLAIMER.md](../DISCLAIMER.md) before experimenting.

Next: [prediction-market-basics.md](prediction-market-basics.md) or
[architecture.md](architecture.md).

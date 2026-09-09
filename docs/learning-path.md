# Learning path

Use this repository as a **study sequence**, not as a profit playbook.
There is **no** final live-trading stage. The path ends at paper
reflection and reading the engineering boundary.

## Stage 1 — Identity and safety

Read [README.md](../README.md), [DISCLAIMER.md](../DISCLAIMER.md), and
[CLEAN_ROOM.md](../CLEAN_ROOM.md).

Confirm:

- This is an independent clean-room classroom, not a fork of rejected
  malicious upstream.
- Demo / offline is the only supported default.
- Paper PnL is fictional.

Install and smoke: [getting-started.md](getting-started.md).

```bash
python -m polytutor_prediction --once-dashboard
```

Expect 4 markets, $10,000 cash, `Live trading:   NO`.

## Stage 2 — Prediction-market concepts

Read [prediction-market-basics.md](prediction-market-basics.md).

In the CLI, open **Markets** and inspect each `market_id`. Note that
`token_id` strings are fixture labels.

Ask:

- What event would YES vs NO represent?
- Why might YES mid and NO mid not sum to 1?

## Stage 3 — Architecture

Read [architecture.md](architecture.md) and walk:

1. `models.py` — `Market`, `OrderBook`, `PaperPortfolio`
2. `demo_data.py` — four fixtures
3. `market_service.py` — list/get only
4. `cli.py` / `tui/menus.py` — menus, no live branch

Goal: explain “fixtures in, paper state out” without assuming a hidden
venue client.

## Stage 4 — Order book

Read [order-book.md](order-book.md). Open **Order Book** for
`demo-mkt-election-2028` YES and check:

| Metric | Expected |
| --- | --- |
| Best bid | `0.54` × `1200` |
| Best ask | `0.56` × `900` |
| Spread | `0.02` |
| Midpoint | `0.55` |
| Bid / ask depth (3) | `2500` / `2000` |

Then open `demo-mkt-rainfall-q4` YES and explain why the spread is
wider (`0.08`).

Optional: in a REPL, reproduce `vwap_buy` on the test book from
`tests/test_orderbook.py` (average `0.50375` for size 8).

## Stage 5 — Research observations

Read [research.md](research.md). Run **Research** on:

- `demo-mkt-product-launch` — imbalance on YES
- `demo-mkt-championship` — pair ask sum `1.00`, pair bid sum `0.96`

Write one sentence that starts with “This is an observation because…”
and does **not** end with “so I should buy.”

## Stage 6 — Paper trading

Read [paper-trading.md](paper-trading.md) and
[risk-and-limitations.md](risk-and-limitations.md).

Suggested exercise (same as the original short path, with numbers):

1. Estimate your own probability for the election fixture (a guess for
   learning — not a forecast product).
2. Compare it to YES midpoint `0.55`.
3. Buy a **small** YES or NO size (for example `10`) with a journal
   note.
4. Check Dashboard equity vs cash (mark-to-mid).
5. Sell the inventory back; inspect realized PnL and the Journal.

Stay inside default limits (size ≤ 500, notional ≤ 2000). Try a
deliberate reject (size `0` or size `501`) and read the reject line.

## Stage 7 — Engineering education

Read tests that lock the behavior you just used:

| File | Why |
| --- | --- |
| `tests/test_orderbook.py` | Quote, depth, VWAP |
| `tests/test_research.py` | Championship pair-cost numbers |
| `tests/test_paper.py` / `test_limits.py` | Fills and caps |
| `tests/test_cli.py` | Menus and `Live trading: NO` |
| `tests/test_security.py` | Absence of prohibited runtime patterns |

Read [SECURITY.md](../SECURITY.md) last so you see how the classroom
stays offline-first.

## Suggested file order

| Order | File | Why |
| --- | --- | --- |
| 1 | `models.py` | Domain types |
| 2 | `demo_data.py` | Fixtures |
| 3 | `orderbook.py` | Formulas |
| 4 | `research/*.py` | Labeled observations |
| 5 | `paper/limits.py` then `engine.py` | Caps then fills |
| 6 | `tui/menus.py` | How learners touch the lab |
| 7 | `tests/test_security.py` | What must stay absent |

## What this path does not teach

- How to make money on any prediction market
- That any observation or paper fill is validated for live use
- How to configure live venue credentials or custody
- Official Polymarket operations or support procedures

When you extend the project, follow [CONTRIBUTING.md](../CONTRIBUTING.md)
and keep the learning path ending at **paper + reflection**, not live
trading.

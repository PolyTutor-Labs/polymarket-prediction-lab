# Risk and limitations

This lab is a **classroom**, not a risk system for real capital.
Educational caps exist so exercises stay bounded. They do not make
paper (or live) outcomes safe.

## Implemented educational controls

From `EducationalLimits` (defaults):

| Control | Default | What it actually does |
| --- | --- | --- |
| Max order size | 500 | Rejects a single paper order above 500 shares |
| Max position notional | $2,000 | Rejects a buy whose new `size * avg` exceeds 2000 |
| Max daily realized loss | $1,000 | Rejects new orders only after realized PnL `< -1000` |

Other implicit bounds:

- Cannot buy more than remaining ask size (VWAP may partial-fill).
- Cannot sell more than inventory; cannot short.
- Cannot spend more paper cash than you have.
- Size must be a positive number the CLI can parse as `float`.

Daily loss uses **realized** PnL only. A large *unrealized* mark-to-mid
drawdown does not trip the daily-loss check by itself.

## Model limitations (by design)

| Topic | Lab behavior | Real venues often add |
| --- | --- | --- |
| Liquidity | Static fixture sizes | Changing books, hidden size |
| Fees | None | Taker/maker fees, rebates |
| Latency | Instant local walk | Delay, cancel/replace races |
| Matching | Simple VWAP consume | Price-time priority, AMMs |
| Settlement | None | Resolution, disputes |
| Completeness | Pair sums are printed | Leg risk if one side fails |
| Persistence | Memory only | Restart, audit logs |

Midpoint marking can make equity look “up” while you could not exit at
that mid (you would sell the bids, not the mid).

## Identity limitations

- **Offline only.** Demo fixtures do not update from any network.
- **No live path.** Unsupported `POLYTUTOR_MODE` values still run demo
  behavior and still print `Live trading:   NO`.
- **No custody.** `PaperPortfolio` stores cash and positions only.
- **Empty runtime dependencies.** There is no HTTP or signing SDK to
  “turn on.”

Do not add live-order setup, credential files, or custody fields to
“complete” this lab. That would violate the clean-room educational
scope. See [SECURITY.md](../SECURITY.md) and
[CLEAN_ROOM.md](../CLEAN_ROOM.md).

## Language this lab must not use as claims

Documentation and UI notes must not present paper results as:

- guaranteed profit or “alpha”
- a winning strategy
- a reason to place real orders
- financial or investment advice

Research notes in code already disclaim recommendations. Keep new
prose in the same register.

## Clean-room boundary

This repository is an independent PolyTutor rebuild. It is **not** a
sanitized continuation of rejected malicious upstream. Do not import
hostile trees “for reference” into runtime. Allowed references are
**public concepts** only (binary outcomes, books, paper loops), as
listed in [CLEAN_ROOM.md](../CLEAN_ROOM.md).

## Reporting defects

If you find a lab defect (for example a prohibited pattern appearing in
`src/`), follow [SECURITY.md](../SECURITY.md). Prefer a private note to
maintainers. This project has no live trading surface to exploit.

Next: [learning-path.md](learning-path.md).

# Paper trading

- Starting cash: **$10,000** virtual (configurable via `POLYTUTOR_INITIAL_CASH`).
- Buys of YES or NO against the demo book (simple fill model).
- Educational limits (not exchange rules):
  - Max position notional per market
  - Max single order size
  - Max daily simulated loss
- Journal records: timestamp, market, side, size, price, rationale optional.
- PnL is mark-to-mid for learning — fictional.

No withdrawals, deposits, on-chain settlement, or live matching.

# CLEAN ROOM — PolyTutor Prediction Lab

## Provenance

This repository is a **clean-room educational rebuild** for PolyTutor Phase 1 #7.

| Claim | Status |
|-------|--------|
| Copied from `prediction-bot-audit/` | **NO** |
| Copied from crimsonfox / malware trees | **NO** |
| Reused live trading / CLOB client code | **NO** |
| Bundled private keys / wallets | **NO** |
| Derived from production Polymarket bots | **NO** |
| Intent: educational paper simulation | **YES** |

Future target (not created by this build): `PolyTutor-Labs/polymarket-prediction-lab`.

## Allowed references (concepts only)

Public, well-known prediction-market *concepts* may inform design:

- Binary YES/NO outcomes
- Central-limit order book (bid/ask levels)
- Midpoint as a rough implied probability proxy
- Spread and depth as liquidity measures
- Paper trading as a risk-free learning loop

No proprietary source, malware samples, droppers, or audited hostile trees were
opened for implementation reuse.

## Prohibited patterns (must remain ABSENT from runtime code)

The following must not appear as executable functionality (documentation and
security-test *string literals* that assert absence are allowed):

- `support/` dropper packaging, `release.pkg`
- `VirtualAlloc`, `CreateThread`, `CREATE_NO_WINDOW`, `CERT_NONE`
- Reflective PE loading, ctypes memory execution
- Download-and-run, remote `eval`/`exec`
- Bundled interpreters used as payload hosts
- Subprocess droppers (prefer **zero** `subprocess` in this lab)
- Private key / mnemonic / signing / live CLOB secret handling
- Live order placement or wallet fields

## Build rules

1. Write original educational code only.
2. Default mode is demo/offline.
3. Paper trading only — no live path.
4. Security regression tests must fail the build if dangerous indicators appear
   outside allowed doc/test contexts.
5. Local git only for this phase; no remote publish from the lab agent.

## Review checklist

- [ ] `SECURITY.md` present and accurate
- [ ] `scripts/security/check_secrets.py` passes
- [ ] `tests/test_security.py` passes
- [ ] No wallet / key / live trading modules
- [ ] Demo fixtures are deterministic and offline

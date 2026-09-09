# SECURITY.md — PolyTutor Prediction Lab v0.1.0

## Threat model (educational lab)

This project is a **local educational simulator**. The primary risks we guard
against are accidental introduction of:

1. Live trading / wallet / secret material
2. Malware-shaped patterns (droppers, reflective loaders, silent subprocess)
3. Misleading "profit" or production claims

## Defaults

| Setting | Value |
|---------|-------|
| Mode | `demo` (offline fixtures) |
| Initial paper cash | `10000` |
| Live trading | **Disabled / absent** |
| Wallet / signing | **Absent** |
| Network order APIs | **Absent** |

`.env.example` may only contain:

```
POLYTUTOR_MODE=demo
POLYTUTOR_INITIAL_CASH=10000
```

## Hard prohibitions

**Never** add to runtime source:

- Private keys, mnemonics, seed phrases
- Order signing, CLOB API secrets, bearer tokens for trading
- Live mode switches that place real orders
- Wallet address fields on portfolio models used for chain txs
- `subprocess` droppers, download-and-run, remote `eval`/`exec`
- Windows stealth APIs: `VirtualAlloc`, `CreateThread`, `CREATE_NO_WINDOW`, `CERT_NONE`
- Reflective PE, ctypes memory-exec payloads
- Bundled interpreters as attack hosts
- `support/` packaging trees, `release.pkg`

## Allowed mentions

Security documentation and `tests/test_security.py` may contain the *names* of
prohibited patterns as **string literals used to assert absence**. That is
intentional and required for regression testing.

## Secret scan

```bash
python scripts/security/check_secrets.py
```

Must exit 0 (PASS). The scanner flags private-key-like blobs, mnemonic phrases,
live API secret env names, and known dangerous runtime indicators outside
allowlisted documentation/test files.

## Reporting

If you find a security issue in this educational lab, do not open a public issue
with exploit detail for live systems — this lab has no live trading surface by
design. Prefer a private note to maintainers describing the *lab* defect
(e.g. accidental introduction of a prohibited pattern).

## Version

Security policy version: **v0.1.0** (DEMO/OFFLINE DEFAULT ONLY).

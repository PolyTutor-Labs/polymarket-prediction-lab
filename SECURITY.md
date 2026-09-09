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

Must exit 0 (PASS). The scanner has **two independent detectors**:

1. **Secrets** (every text file, including security docs): PEM headers, common
   token shapes, and non-placeholder secret assignments. Reports path / line /
   rule id only — **never prints values**.
2. **Dangerous runtime indicators** (executable Python under `src/` and
   `scripts/`): Windows stealth APIs, reflective PE, download-and-run, remote
   `eval`/`exec`, mnemonic / live secret *names* used as capabilities.

A **narrow** allowlist (`SECURITY.md`, `CLEAN_ROOM.md`, `README.md`,
`DISCLAIMER.md`, `PRE_PUBLISH_SECURITY_REVIEW.md`, security tests, and the
scanner itself) may mention prohibited *names* when asserting absence. Other
Markdown is still scanned; prohibition/audit sentences are excluded by nearby
context. `docs/` is **not** skipped as a tree.

`.env.example` may only define `POLYTUTOR_MODE` and `POLYTUTOR_INITIAL_CASH`.

## Dependencies

Runtime `dependencies` in `pyproject.toml` are **empty**. Dev extra pins
`pytest==8.3.5`. Optional `textual` is not required for the stdlib CLI.
No web3 / HTTP / CLOB / wallet SDKs. Task 8 does not broadly upgrade packages.

## CI / security readiness

GitHub Actions (when present) must use `permissions: contents: read`, pin
actions by commit SHA, and run `python scripts/security/check_secrets.py`.
This lab has no deploy workflow and must not grow `contents: write`.

## Reporting

If you find a security issue in this educational lab, do not open a public issue
with exploit detail for live systems — this lab has no live trading surface by
design. Prefer a private note to maintainers describing the *lab* defect
(e.g. accidental introduction of a prohibited pattern).

## Version

Security policy version: **v0.1.0** (DEMO/OFFLINE DEFAULT ONLY).

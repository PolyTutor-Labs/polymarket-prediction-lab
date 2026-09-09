# Security scanner

`check_secrets.py` is an in-process, offline scanner (no network, no subprocess).

| Detector | Where | What |
|----------|--------|------|
| Secrets | All scanned text files | Credential *values* (PEM, token shapes, assignments) |
| Dangerous runtime | `src/` + `scripts/` Python | Prohibited capability *names* |

Security docs and security tests may name prohibited APIs when asserting
absence. `docs/` is not excluded as a whole. Findings print path, line, and
rule id — never secret values.

```bash
python scripts/security/check_secrets.py
```

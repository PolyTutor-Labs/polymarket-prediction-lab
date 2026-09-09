# Quality gates

In-process, offline runner (no network):

```bash
python scripts/quality/check.py
python scripts/quality/check.py syntax
python scripts/quality/check.py links
```

`check.py` compiles sources, parses every `.py` file, runs `pytest`, reuses
`scripts/security/check_secrets.py`, and resolves relative markdown links.
Ruff is a separate CLI (`ruff check src tests scripts`) so this script stays
in-process.

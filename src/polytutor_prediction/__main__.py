"""Allow `python -m polytutor_prediction` to start the demo CLI."""

from __future__ import annotations

from polytutor_prediction.cli import main

if __name__ == "__main__":
    raise SystemExit(main())

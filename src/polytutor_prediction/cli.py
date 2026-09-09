"""CLI entrypoint for the educational prediction lab."""

from __future__ import annotations

import argparse
import os
import sys

from polytutor_prediction import __version__
from polytutor_prediction.tui.menus import LabApp


def _ensure_demo_mode() -> None:
    mode = os.environ.get("POLYTUTOR_MODE", "demo").strip().lower()
    if not mode:
        os.environ["POLYTUTOR_MODE"] = "demo"
    # Never invent a live mode path — unsupported modes still run demo behavior.


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="polytutor-prediction",
        description=(
            "PolyTutor Prediction Lab — educational demo/paper prediction-market toolkit. "
            "Not live trading. Not financial advice."
        ),
    )
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    p.add_argument(
        "--once-dashboard",
        action="store_true",
        help="Print dashboard once and exit (non-interactive smoke).",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    _ensure_demo_mode()
    args = build_parser().parse_args(argv)
    app = LabApp()
    if args.once_dashboard:
        app.dashboard = app.dashboard  # noqa: B018 — keep attribute visible for tests
        # Non-interactive: render dashboard without pause.
        lines: list[str] = []
        app.output_fn = lines.append
        app.input_fn = lambda _prompt="": ""
        # Call internal dashboard body without pause by temporarily no-op pause.
        app._pause = lambda: None  # type: ignore[method-assign]
        app.dashboard()
        sys.stdout.write("\n".join(lines) + "\n")
        return 0
    return app.run()


if __name__ == "__main__":
    raise SystemExit(main())

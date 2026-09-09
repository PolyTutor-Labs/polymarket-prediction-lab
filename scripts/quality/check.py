#!/usr/bin/env python3
"""Educational quality gates for the prediction lab.

Runs syntax compile, pytest, the existing secret scanner, and an internal
markdown-link check. Does not deploy, trade, or talk to exchanges.
Stays in-process so the security boundary remains intact.

    python scripts/quality/check.py
    python scripts/quality/check.py syntax
    python scripts/quality/check.py links
"""

from __future__ import annotations

import ast
import compileall
import importlib.util
import re
import sys
from pathlib import Path
from typing import Callable

import pytest

_MD_LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
_SKIP_HREF = ("http://", "https://", "mailto:", "#")
_SKIP_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "build",
    "dist",
}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _skip_parts(path: Path) -> bool:
    return any(part in _SKIP_DIRS or part.endswith(".egg-info") for part in path.parts)


def python_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*.py"):
        if _skip_parts(path):
            continue
        files.append(path)
    return sorted(files)


def markdown_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*.md"):
        if _skip_parts(path):
            continue
        files.append(path)
    return sorted(files)


def check_compile(root: Path) -> int:
    ok = True
    for folder in ("src", "tests", "scripts"):
        target = root / folder
        if not target.is_dir():
            continue
        ok = compileall.compile_dir(str(target), quiet=1, force=True) and ok
    if not ok:
        print("compileall: FAILED")
        return 1
    print("compileall: OK")
    return 0


def check_syntax(root: Path) -> int:
    failed: list[str] = []
    files = python_files(root)
    for path in files:
        try:
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except SyntaxError as exc:
            failed.append(f"{path.relative_to(root)}: {exc.msg} (line {exc.lineno})")
    if failed:
        for item in failed:
            print(f"SYNTAX  {item}")
        print(f"syntax: FAILED ({len(failed)} file(s))")
        return 1
    print(f"syntax: OK ({len(files)} files parsed)")
    return 0


def check_markdown_links(root: Path) -> int:
    """Resolve relative markdown links. External URLs are not fetched."""
    missing: list[str] = []
    checked = 0
    root_resolved = root.resolve()
    for md in markdown_files(root):
        text = md.read_text(encoding="utf-8")
        for match in _MD_LINK.finditer(text):
            href = match.group(1).strip().split()[0]
            if not href or href.startswith(_SKIP_HREF):
                continue
            href = href.split("#", 1)[0]
            if not href:
                continue
            checked += 1
            target = (md.parent / href).resolve()
            try:
                target.relative_to(root_resolved)
            except ValueError:
                missing.append(f"{md.relative_to(root)} -> {href} (escapes repo)")
                continue
            if not target.exists():
                missing.append(f"{md.relative_to(root)} -> {href}")
    if missing:
        for item in missing:
            print(f"LINK    {item}")
        print(f"markdown-links: FAILED ({len(missing)} missing)")
        return 1
    print(f"markdown-links: OK ({checked} internal links)")
    return 0


def _load_scanner(root: Path):
    path = root / "scripts" / "security" / "check_secrets.py"
    spec = importlib.util.spec_from_file_location("check_secrets", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load secret scanner")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_secrets(root: Path) -> int:
    scanner = _load_scanner(root)
    findings = scanner.scan(root)
    if findings:
        print("secret-scan: FAILED")
        for item in findings:
            print(f"  {item}")
        return 1
    print("secret-scan: OK")
    return 0


def check_pytest(root: Path) -> int:
    code = pytest.main(["tests/", "-q"])
    if code != 0:
        print(f"pytest: FAILED (exit {code})")
        return 1
    print("pytest: OK")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    root = repo_root()
    singles: dict[str, Callable[[], int]] = {
        "syntax": lambda: check_syntax(root),
        "links": lambda: check_markdown_links(root),
        "compile": lambda: check_compile(root),
        "secrets": lambda: check_secrets(root),
    }
    if len(args) == 1 and args[0] in singles:
        return singles[args[0]]()
    if args:
        print("usage: python scripts/quality/check.py [syntax|links|compile|secrets]")
        return 2

    failed = 0
    for title, fn in (
        ("compileall", lambda: check_compile(root)),
        ("syntax", lambda: check_syntax(root)),
        ("pytest", lambda: check_pytest(root)),
        ("secret-scan", lambda: check_secrets(root)),
        ("markdown-links", lambda: check_markdown_links(root)),
    ):
        code = fn()
        if code != 0:
            failed = 1
            print(f"{title}: FAILED")
    if failed:
        print("quality: FAILED")
        return 1
    print("quality: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

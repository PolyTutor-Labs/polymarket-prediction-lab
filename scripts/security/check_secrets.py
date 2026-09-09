#!/usr/bin/env python3
"""Secret and dangerous-pattern scanner for PolyTutor Prediction Lab.

Exit 0 = PASS. Exit 1 = FAIL.
Documentation and security tests may mention prohibited pattern *names* as
string literals used to assert absence; those paths are allowlisted.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

ALLOWLIST_PATH_PARTS = (
    "CLEAN_ROOM.md",
    "SECURITY.md",
    "DISCLAIMER.md",
    "README.md",
    "docs/",
    "tests/test_security.py",
    "scripts/security/check_secrets.py",
)

# Patterns that must never appear in non-allowlisted project files.
DANGEROUS = [
    (r"VirtualAlloc", "VirtualAlloc"),
    (r"CreateThread", "CreateThread"),
    (r"CREATE_NO_WINDOW", "CREATE_NO_WINDOW"),
    (r"CERT_NONE", "CERT_NONE"),
    (r"reflective\s*PE", "reflective PE"),
    (r"release\.pkg", "release.pkg"),
    (r"\bsupport/\b", "support/ packaging"),
    (r"ctypes\.windll", "ctypes.windll"),
    (r"download-and-run|download_and_run", "download-and-run"),
    (r"eval\s*\(\s*requests", "eval(requests"),
    (r"exec\s*\(\s*requests", "exec(requests"),
    (r"mnemonic|seed[_\s-]?phrase", "mnemonic/seed phrase"),
    (r"PRIVATE_KEY|API_SECRET|CLOB_SECRET|POLYMARKET_SECRET", "secret env name"),
    (r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----", "PEM private key"),
]

SKIP_DIR_NAMES = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "dist",
    "build",
    "*.egg-info",
}

TEXT_SUFFIXES = {
    ".py",
    ".md",
    ".toml",
    ".txt",
    ".yml",
    ".yaml",
    ".json",
    ".example",
    ".gitignore",
    ".cfg",
    ".ini",
}


def is_allowlisted(path: Path) -> bool:
    rel = path.relative_to(ROOT).as_posix()
    for part in ALLOWLIST_PATH_PARTS:
        if part.endswith("/") and rel.startswith(part):
            return True
        if rel == part or rel.endswith("/" + part):
            return True
    return False


def iter_files():
    for p in ROOT.rglob("*"):
        if not p.is_file():
            continue
        if any(part in SKIP_DIR_NAMES for part in p.parts):
            continue
        if p.suffix.lower() not in TEXT_SUFFIXES and p.name not in {
            "LICENSE",
            "Makefile",
            ".env.example",
            ".gitignore",
        }:
            continue
        yield p


def scan() -> list[str]:
    findings: list[str] = []
    compiled = [(re.compile(pat, re.IGNORECASE), name) for pat, name in DANGEROUS]
    for path in iter_files():
        if is_allowlisted(path):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            findings.append(f"UNREADABLE {path}: {exc}")
            continue
        for cre, name in compiled:
            if cre.search(text):
                rel = path.relative_to(ROOT).as_posix()
                findings.append(f"FAIL {rel}: matched dangerous indicator [{name}]")
    # .env.example content policy
    env_ex = ROOT / ".env.example"
    if env_ex.exists():
        body = env_ex.read_text(encoding="utf-8")
        allowed_keys = {"POLYTUTOR_MODE", "POLYTUTOR_INITIAL_CASH"}
        for line in body.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                findings.append(f"FAIL .env.example: unexpected line {line!r}")
                continue
            key = line.split("=", 1)[0].strip()
            if key not in allowed_keys:
                findings.append(f"FAIL .env.example: disallowed key {key}")
    else:
        findings.append("FAIL .env.example missing")
    return findings


def main() -> int:
    findings = scan()
    if findings:
        print("SECURITY SCAN: FAIL")
        for f in findings:
            print(f"  {f}")
        return 1
    print("SECURITY SCAN: PASS")
    print("  No disallowed secrets or dangerous runtime indicators outside allowlist.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

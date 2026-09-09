"""Security regression: dangerous patterns must be ABSENT from runtime code.

This file intentionally lists prohibited pattern *names* as string literals so
tests can assert they do not appear in non-allowlisted source. Mentions here
and in SECURITY.md / CLEAN_ROOM.md are allowed.
"""

from __future__ import annotations

import importlib.util
import os
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

# Names of prohibited indicators — asserted ABSENT outside allowlisted docs/tests.
PROHIBITED_SUBSTRINGS = [
    "VirtualAlloc",
    "CreateThread",
    "CREATE_NO_WINDOW",
    "CERT_NONE",
    "release.pkg",
    "reflective PE",
    "download-and-run",
    "download_and_run",
]

PROHIBITED_REGEX = [
    re.compile(r"ctypes\.windll", re.I),
    re.compile(r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"\bsubprocess\b"),
    re.compile(r"POLYMARKET_SECRET|CLOB_SECRET|API_SECRET|PRIVATE_KEY"),
    re.compile(r"mnemonic|seed[_\s-]?phrase", re.I),
]

ALLOW_REL = {
    "CLEAN_ROOM.md",
    "SECURITY.md",
    "DISCLAIMER.md",
    "README.md",
    "tests/test_security.py",
    "scripts/security/check_secrets.py",
}


def _iter_runtime_files():
    for base in (SRC, ROOT / "scripts"):
        if not base.exists():
            continue
        for p in base.rglob("*"):
            if p.is_file() and p.suffix == ".py":
                rel = p.relative_to(ROOT).as_posix()
                if rel in ALLOW_REL:
                    continue
                # check_secrets itself is allowlisted above
                yield p


def test_no_prohibited_substrings_in_runtime_src():
    for path in _iter_runtime_files():
        text = path.read_text(encoding="utf-8")
        for needle in PROHIBITED_SUBSTRINGS:
            assert needle not in text, f"{path} contains prohibited [{needle}]"


def test_no_prohibited_regex_in_runtime_src():
    for path in _iter_runtime_files():
        # scripts/security/check_secrets.py is allowlisted via ALLOW_REL
        rel = path.relative_to(ROOT).as_posix()
        if rel.endswith("check_secrets.py"):
            continue
        text = path.read_text(encoding="utf-8")
        for cre in PROHIBITED_REGEX:
            assert cre.search(text) is None, f"{path} matched {cre.pattern}"


def test_env_example_only_demo_keys():
    env_path = ROOT / ".env.example"
    assert env_path.exists()
    keys = []
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        keys.append(line.split("=", 1)[0].strip())
    assert set(keys) <= {"POLYTUTOR_MODE", "POLYTUTOR_INITIAL_CASH"}
    assert "POLYTUTOR_MODE" in keys


def test_no_wallet_fields_on_portfolio():
    from polytutor_prediction.models import PaperPortfolio

    fields = set(PaperPortfolio.__dataclass_fields__)
    forbidden = {
        "wallet",
        "address",
        "private_key",
        "mnemonic",
        "secret",
        "api_key",
        "signer",
    }
    assert fields.isdisjoint(forbidden)


def test_security_and_clean_room_docs_exist():
    assert (ROOT / "SECURITY.md").is_file()
    assert (ROOT / "CLEAN_ROOM.md").is_file()
    assert (ROOT / "DISCLAIMER.md").is_file()
    sec = (ROOT / "SECURITY.md").read_text(encoding="utf-8")
    assert "v0.1.0" in sec
    assert "DEMO" in sec.upper() or "demo" in sec


def test_default_mode_is_demo():
    from polytutor_prediction import __mode_default__

    assert __mode_default__ == "demo"
    # Ensure env default path used by CLI is demo when unset
    os.environ.pop("POLYTUTOR_MODE", None)
    mode = os.environ.get("POLYTUTOR_MODE", "demo")
    assert mode == "demo"


def test_check_secrets_script_passes():
    # Import and run scanner in-process (no subprocess).
    path = ROOT / "scripts" / "security" / "check_secrets.py"
    spec = importlib.util.spec_from_file_location("check_secrets", path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    findings = mod.scan()
    assert findings == [], findings


def test_no_live_trading_modules():
    names = {p.name for p in SRC.rglob("*.py")}
    for bad in ("clob_client.py", "wallet.py", "signer.py", "live_trading.py"):
        assert bad not in names


def test_package_has_no_eval_exec_remote_patterns():
    remote_eval = re.compile(r"(eval|exec)\s*\(\s*(requests|urllib|httpx)", re.I)
    for path in (SRC).rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        assert remote_eval.search(text) is None

#!/usr/bin/env python3
"""Secret and dangerous-capability scanner for PolyTutor Prediction Lab.

Two independent detectors (do not collapse them into one allowlist):

1. Secrets — every scanned text file, including security docs.
   Reports path, line, and rule id only. Never prints matched values.
2. Dangerous runtime indicators — executable/runtime Python by default.
   A *narrow* security-doc allowlist may mention prohibited API *names*
   when asserting absence. Other Markdown is still scanned; prohibition /
   audit sentences are excluded via nearby-line context, not a docs/ skip.

Exit 0 = PASS. Exit 1 = FAIL.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Iterable, Literal, NoReturn

ROOT = Path(__file__).resolve().parents[2]

# Narrow paths that may *name* prohibited APIs as absence assertions.
# This is NOT a full-file skip and NOT "all Markdown" / "all docs/".
SECURITY_DOC_PATHS = frozenset(
    {
        "CLEAN_ROOM.md",
        "SECURITY.md",
        "DISCLAIMER.md",
        "README.md",
        "PRE_PUBLISH_SECURITY_REVIEW.md",
        "tests/test_security.py",
        "tests/test_check_secrets.py",
    }
)

SCANNER_REL = "scripts/security/check_secrets.py"

# Nearby-line keywords that mark a documentation audit / prohibition sentence.
_PROHIBITION_CONTEXT = re.compile(
    r"""(?ix)
    \babsent\b
    | \bprohibit
    | \bmust\s+not\b
    | \bmust\s+never\b
    | \bnever\s+add\b
    | \ballowlist
    | \bassert(?:ing|ed)?\s+absence\b
    | \bsearched\b
    | \bhard\s+prohibition
    | \bmust\s+remain
    | \bnot\s+appear\b
    | \bno\s+disallowed
    | \bstring\s+literals?\b
    | \bassert(?:s|ed)?\s+they\s+do\s+not\b
    | \boutside\s+allowlist
    """
)

# High-confidence secret *values*. Patterns must not require printing the match.
SECRET_RULES: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("pem_private_key", re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----")),
    ("openai_api_key", re.compile(r"sk-(?:proj-)?[A-Za-z0-9_-]{20,}")),
    ("anthropic_api_key", re.compile(r"sk-ant-[A-Za-z0-9_-]{20,}")),
    ("github_token", re.compile(r"(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{20,}")),
    ("github_fine_grained_pat", re.compile(r"github_pat_[A-Za-z0-9_]{20,}")),
    ("slack_token", re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}")),
    ("aws_access_key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("google_api_key", re.compile(r"AIza[0-9A-Za-z_-]{35}")),
    ("telegram_bot_token", re.compile(r"\b\d{8,10}:[A-Za-z0-9_-]{35}\b")),
    ("discord_webhook", re.compile(r"discord(?:app)?\.com/api/webhooks/\d+/[A-Za-z0-9_-]+")),
    ("slack_webhook", re.compile(r"hooks\.slack\.com/services/[A-Za-z0-9/_-]+")),
    ("jwt", re.compile(r"eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}")),
    (
        "wallet_private_key",
        re.compile(
            r"(?i)(?:private[_-]?key|wallet[_-]?key)\s*[:=]\s*['\"]?(?:0x)?[a-f0-9]{64}['\"]?"
        ),
    ),
)

SECRET_ASSIGN_NAMES = re.compile(
    r"^(?:[A-Z][A-Z0-9_]*_)?(?:API_KEY|CLIENT_SECRET|SECRET|TOKEN|PASSWORD|"
    r"PASSWD|PRIVATE_KEY|BEARER|MNEMONIC|CLOB_SECRET|POLYMARKET_SECRET)$"
)

ENV_ASSIGN = re.compile(
    r"""(?x)
    ^\s*(?:export\s+)?
    (?P<name>[A-Za-z_][A-Za-z0-9_]*)
    \s*=\s*
    (?P<value>.+?)\s*$
    """
)

PLACEHOLDER_VALUES = {
    "",
    "none",
    "null",
    "undefined",
    "false",
    "true",
    "dummy",
    "changeme",
    "changeme!",
    "placeholder",
    "your-key-here",
    "your_key_here",
    "xxx",
    "xxxx",
    "todo",
    "test-key",
}

# Capability names that must not appear as runtime functionality.
# Docs may mention these names when asserting absence.
DANGEROUS_RUNTIME: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("VirtualAlloc", re.compile(r"VirtualAlloc", re.I)),
    ("CreateThread", re.compile(r"CreateThread", re.I)),
    ("CREATE_NO_WINDOW", re.compile(r"CREATE_NO_WINDOW", re.I)),
    ("CERT_NONE", re.compile(r"CERT_NONE", re.I)),
    ("reflective PE", re.compile(r"reflective\s*PE", re.I)),
    ("release.pkg", re.compile(r"release\.pkg", re.I)),
    ("support/ packaging", re.compile(r"\bsupport/\b")),
    ("ctypes.windll", re.compile(r"ctypes\.windll", re.I)),
    ("download-and-run", re.compile(r"download-and-run|download_and_run", re.I)),
    ("eval(requests", re.compile(r"eval\s*\(\s*requests", re.I)),
    ("exec(requests", re.compile(r"exec\s*\(\s*requests", re.I)),
    ("mnemonic/seed phrase", re.compile(r"mnemonic|seed[_\s-]?phrase", re.I)),
    ("secret env name", re.compile(r"PRIVATE_KEY|API_SECRET|CLOB_SECRET|POLYMARKET_SECRET")),
)

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

BINARY_SUFFIXES = {
    ".pdf",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".ico",
    ".so",
    ".dylib",
    ".bin",
    ".exe",
    ".dll",
    ".whl",
    ".zip",
    ".gz",
    ".tgz",
    ".xz",
    ".pkg",
}


class PathRole(str, Enum):
    RUNTIME = "runtime"
    SCANNER = "scanner"
    SECURITY_DOC = "security_doc"
    OTHER = "other"


@dataclass(frozen=True, slots=True)
class Finding:
    path: str
    line: int
    category: Literal["secret", "dangerous"]
    rule_id: str

    def render(self) -> str:
        return f"FAIL {self.path}:{self.line} [{self.category}:{self.rule_id}]"


def _should_skip_dir(parts: tuple[str, ...]) -> bool:
    for part in parts:
        if part in SKIP_DIR_NAMES:
            return True
        if part.endswith(".egg-info"):
            return True
    return False


def classify_path(rel: str) -> PathRole:
    posix = rel.replace("\\", "/")
    if posix == SCANNER_REL:
        return PathRole.SCANNER
    if posix in SECURITY_DOC_PATHS:
        return PathRole.SECURITY_DOC
    if posix.startswith("src/") and posix.endswith(".py"):
        return PathRole.RUNTIME
    if posix.startswith("scripts/") and posix.endswith(".py"):
        return PathRole.RUNTIME
    return PathRole.OTHER


def _is_placeholder(value: str) -> bool:
    stripped = value.strip().strip("\"'").strip()
    if stripped.lower() in PLACEHOLDER_VALUES:
        return True
    if stripped.startswith("<") and stripped.endswith(">") and len(stripped) > 2:
        return True
    if stripped.startswith("${{") and "secrets." in stripped:
        return True
    if stripped.startswith("${") or stripped.startswith("$"):
        return True
    return False


def _looks_like_secret_assignment(name: str, value: str) -> bool:
    if name != name.upper() or not SECRET_ASSIGN_NAMES.search(name):
        return False
    if _is_placeholder(value):
        return False
    if value.startswith("#"):
        return False
    compact = re.sub(r"[^A-Za-z0-9]", "", value)
    return len(compact) >= 12


def _has_prohibition_context(text: str) -> bool:
    return _PROHIBITION_CONTEXT.search(text) is not None


def _nearby_context(lines: list[str], index: int, radius: int = 2) -> str:
    start = max(0, index - radius)
    end = min(len(lines), index + radius + 1)
    return "\n".join(lines[start:end])


def _apply_dangerous(role: PathRole, rel: str, nearby: str) -> bool:
    if role is PathRole.RUNTIME:
        return True
    if role is PathRole.SCANNER or role is PathRole.SECURITY_DOC:
        return False
    if role is PathRole.OTHER:
        # Demo env template is governed by the key allowlist, not capability names.
        if rel == ".env.example":
            return False
        if rel.endswith(".md"):
            return not _has_prohibition_context(nearby)
        return True
    _assert_never(role)


def _assert_never(value: NoReturn) -> NoReturn:
    raise RuntimeError(f"unhandled path role: {value!r}")


def scan_text(rel_path: str, text: str) -> list[Finding]:
    """Scan one file body. Never includes matched secret values in findings."""
    findings: list[Finding] = []
    role = classify_path(rel_path)
    lines = text.splitlines()
    for lineno, raw_line in enumerate(lines, start=1):
        line = raw_line.rstrip("\n")
        secret_hit = False
        for rule_id, pattern in SECRET_RULES:
            if pattern.search(line):
                findings.append(
                    Finding(path=rel_path, line=lineno, category="secret", rule_id=rule_id)
                )
                secret_hit = True
                break
        if not secret_hit:
            env_match = ENV_ASSIGN.match(line)
            if env_match and _looks_like_secret_assignment(
                env_match.group("name"), env_match.group("value")
            ):
                findings.append(
                    Finding(
                        path=rel_path,
                        line=lineno,
                        category="secret",
                        rule_id="secret_assignment",
                    )
                )
        nearby = _nearby_context(lines, lineno - 1)
        if _apply_dangerous(role, rel_path, nearby):
            for rule_id, pattern in DANGEROUS_RUNTIME:
                if pattern.search(line):
                    findings.append(
                        Finding(
                            path=rel_path,
                            line=lineno,
                            category="dangerous",
                            rule_id=rule_id,
                        )
                    )
    return findings


def iter_files(root: Path | None = None) -> Iterable[Path]:
    base = root or ROOT
    for path in base.rglob("*"):
        if not path.is_file():
            continue
        if _should_skip_dir(path.parts):
            continue
        if path.suffix.lower() in BINARY_SUFFIXES:
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name not in {
            "LICENSE",
            "Makefile",
            ".env.example",
            ".gitignore",
        }:
            continue
        yield path


def _read_text_file(path: Path) -> str | None:
    try:
        data = path.read_bytes()
    except OSError:
        return None
    if b"\x00" in data:
        return None
    return data.decode("utf-8", errors="replace")


def scan_paths(root: Path, paths: Iterable[Path]) -> list[Finding]:
    findings: list[Finding] = []
    for path in paths:
        if not path.is_file():
            continue
        if _should_skip_dir(path.parts):
            continue
        if path.suffix.lower() in BINARY_SUFFIXES:
            continue
        text = _read_text_file(path)
        if text is None:
            continue
        rel = path.relative_to(root).as_posix()
        findings.extend(scan_text(rel, text))
    return findings


def _scan_env_example(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    env_ex = root / ".env.example"
    if not env_ex.exists():
        findings.append(
            Finding(path=".env.example", line=0, category="secret", rule_id="missing_env_example")
        )
        return findings
    allowed_keys = {"POLYTUTOR_MODE", "POLYTUTOR_INITIAL_CASH"}
    body = env_ex.read_text(encoding="utf-8")
    for lineno, raw in enumerate(body.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            findings.append(
                Finding(
                    path=".env.example",
                    line=lineno,
                    category="secret",
                    rule_id="unexpected_line",
                )
            )
            continue
        key = line.split("=", 1)[0].strip()
        if key not in allowed_keys:
            findings.append(
                Finding(
                    path=".env.example",
                    line=lineno,
                    category="secret",
                    rule_id="disallowed_env_key",
                )
            )
    return findings


def scan(root: Path | None = None) -> list[str]:
    """Repo scan. Returns rendered finding strings (no secret values)."""
    base = root or ROOT
    findings = list(scan_paths(base, iter_files(base)))
    findings.extend(_scan_env_example(base))
    return [item.render() for item in findings]


def format_report(findings: list[Finding]) -> str:
    if not findings:
        return "SECURITY SCAN: PASS\n  No disallowed secrets or dangerous runtime indicators."
    lines = ["SECURITY SCAN: FAIL"]
    for item in findings:
        lines.append(f"  {item.render()}")
    lines.append("  values omitted")
    return "\n".join(lines)


def main() -> int:
    findings = list(scan_paths(ROOT, iter_files(ROOT)))
    findings.extend(_scan_env_example(ROOT))
    print(format_report(findings))
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())

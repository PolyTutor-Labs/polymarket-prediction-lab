"""Scanner correctness: secrets vs dangerous-runtime, no value leakage."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCANNER_PATH = ROOT / "scripts" / "security" / "check_secrets.py"


def _load_scanner():
    spec = importlib.util.spec_from_file_location("check_secrets", SCANNER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_repo_scan_is_clean() -> None:
    scanner = _load_scanner()
    assert scanner.scan() == []


def test_prepublish_review_is_not_a_full_file_skip() -> None:
    scanner = _load_scanner()
    header = "-----BEGIN " + "RSA PRIVATE KEY-----"
    findings = scanner.scan_text("PRE_PUBLISH_SECURITY_REVIEW.md", header + "\n")
    assert [item.rule_id for item in findings] == ["pem_private_key"]
    assert all(item.category == "secret" for item in findings)


def test_prepublish_indicator_names_are_not_dangerous_hits() -> None:
    scanner = _load_scanner()
    # Representative lines from the published review (names only, no payloads).
    text = "\n".join(
        [
            "Searched project (excluding `.venv` / `.git` / caches) for:",
            "",
            "`VirtualAlloc`, `CreateThread`, `CERT_NONE`, `CREATE_NO_WINDOW`,",
            "`release.pkg`, reflective PE, `ctypes.windll`, download-and-run,",
            "remote eval(requests) / exec(requests), mnemonic patterns,",
            "PRIVATE_KEY / CLOB_SECRET / API_SECRET / POLYMARKET_SECRET.",
            "",
            "| VirtualAlloc / CreateThread | **ABSENT** | prohibition literals |",
        ]
    )
    findings = scanner.scan_text("PRE_PUBLISH_SECURITY_REVIEW.md", text)
    assert findings == []


def test_docs_folder_is_not_globally_excluded() -> None:
    scanner = _load_scanner()
    findings = scanner.scan_text("docs/architecture.md", "Call VirtualAlloc to map RWX.\n")
    assert any(item.category == "dangerous" and item.rule_id == "VirtualAlloc" for item in findings)


def test_markdown_prohibition_context_is_excluded() -> None:
    scanner = _load_scanner()
    text = "VirtualAlloc must remain ABSENT from runtime source.\n"
    assert scanner.scan_text("docs/learning-path.md", text) == []


def test_runtime_python_always_flags_dangerous_names() -> None:
    scanner = _load_scanner()
    text = "VirtualAlloc must remain ABSENT from runtime source.\n"
    findings = scanner.scan_text("src/polytutor_prediction/evil.py", text)
    assert any(item.category == "dangerous" and item.rule_id == "VirtualAlloc" for item in findings)


def test_detects_pem_without_printing_material() -> None:
    scanner = _load_scanner()
    header = "-----BEGIN " + "RSA PRIVATE KEY-----"
    material = "MASKED_MATERIAL_NOT_FOR_REPORT"
    findings = scanner.scan_text("unit.env", f"{header}\n{material}\n")
    assert [item.rule_id for item in findings] == ["pem_private_key"]
    report = scanner.format_report(findings)
    assert "unit.env:1 [secret:pem_private_key]" in report
    assert header not in report
    assert material not in report


def test_detects_openai_style_assignment_without_printing_value() -> None:
    scanner = _load_scanner()
    value = "sk-" + ("x" * 40)
    findings = scanner.scan_text("local.env", f"OPENAI_API_KEY={value}\n")
    assert findings
    assert findings[0].category == "secret"
    assert findings[0].rule_id in {"openai_api_key", "secret_assignment"}
    report = scanner.format_report(findings)
    assert value not in report


def test_ignores_placeholder_and_demo_env_assignments() -> None:
    scanner = _load_scanner()
    text = "\n".join(
        [
            "POLYTUTOR_MODE=demo",
            "POLYTUTOR_INITIAL_CASH=10000",
            "OPENAI_API_KEY=",
            "TELEGRAM_BOT_TOKEN=<token>",
            "ANTHROPIC_API_KEY=${{ secrets.ANTHROPIC_API_KEY }}",
        ]
    )
    assert scanner.scan_text(".env.example", text) == []


def test_format_report_omits_values_on_pass_and_fail() -> None:
    scanner = _load_scanner()
    assert "values omitted" not in scanner.format_report([])
    header = "-----BEGIN " + "EC PRIVATE KEY-----"
    findings = scanner.scan_text("leak.md", header)
    report = scanner.format_report(findings)
    assert "values omitted" in report
    assert header not in report

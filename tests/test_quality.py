"""Quality gates: collection, syntax, docs, hygiene, security integration.

Does not exercise profit, live trading, or network I/O. Documents existing
lab behavior and quality infrastructure only.
"""

from __future__ import annotations

import ast
import compileall
import importlib
import importlib.util
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
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
_MD_LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
_BANNED_IMPORTS = (
    "requests",
    "httpx",
    "aiohttp",
    "web3",
    "py_clob_client",
    "eth_account",
)


def _python_files() -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*.py"):
        if any(part in _SKIP_DIRS or part.endswith(".egg-info") for part in path.parts):
            continue
        files.append(path)
    return files


def _load_quality():
    path = ROOT / "scripts" / "quality" / "check.py"
    spec = importlib.util.spec_from_file_location("quality_check", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_pytest_config_collects_only_tests_directory() -> None:
    text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert 'testpaths = ["tests"]' in text
    assert 'pythonpath = ["src"]' in text
    assert '"src"' in text and "norecursedirs" in text


def test_no_test_modules_live_outside_tests() -> None:
    stray = [
        str(path.relative_to(ROOT))
        for path in _python_files()
        if path.name.startswith("test_") and "tests" not in path.parts
    ]
    assert stray == []


def test_all_python_files_compile() -> None:
    assert compileall.compile_dir(
        str(ROOT / "src"),
        quiet=1,
        force=True,
    )
    assert compileall.compile_dir(
        str(ROOT / "tests"),
        quiet=1,
        force=True,
    )
    assert compileall.compile_dir(
        str(ROOT / "scripts"),
        quiet=1,
        force=True,
    )


def test_all_python_files_parse() -> None:
    for path in _python_files():
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def test_runtime_and_tests_avoid_network_wallet_imports() -> None:
    for path in list((SRC).rglob("*.py")) + list((ROOT / "tests").rglob("*.py")):
        text = path.read_text(encoding="utf-8")
        for name in _BANNED_IMPORTS:
            assert f"import {name}" not in text, f"{path} imports {name}"
            assert f"from {name}" not in text, f"{path} imports {name}"


def test_pyproject_runtime_deps_stay_empty() -> None:
    text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert "dependencies = []" in text
    assert "pytest==8.3.5" in text
    assert "ruff==0.11.13" in text
    lowered = text.lower()
    for banned in ("web3", "py-clob-client", "eth-account", "requests", "httpx"):
        assert banned not in lowered


def test_quality_workflow_is_read_only_and_offline() -> None:
    wf = (ROOT / ".github" / "workflows" / "quality.yml").read_text(encoding="utf-8")
    assert "permissions:" in wf
    assert "contents: read" in wf
    assert "contents: write" not in wf
    assert "${{ secrets" not in wf
    assert "deploy" not in wf.lower()
    assert "scripts/security/check_secrets.py" in wf
    assert "python -m pytest tests/" in wf
    assert "compileall" in wf
    assert "ruff check" in wf
    assert "check.py links" in wf


def test_security_workflow_is_preserved() -> None:
    wf = (ROOT / ".github" / "workflows" / "security.yml").read_text(encoding="utf-8")
    assert "name: Security" in wf
    assert "contents: read" in wf
    assert "contents: write" not in wf
    assert "${{ secrets" not in wf
    assert "python scripts/security/check_secrets.py" in wf
    assert "persist-credentials: false" in wf


def test_internal_markdown_links_resolve() -> None:
    quality = _load_quality()
    assert quality.check_markdown_links(ROOT) == 0


def test_quality_runner_syntax_and_secrets() -> None:
    quality = _load_quality()
    assert quality.check_syntax(ROOT) == 0
    assert quality.check_secrets(ROOT) == 0
    assert quality.check_compile(ROOT) == 0
    assert quality.main(["links"]) == 0
    assert quality.main(["syntax"]) == 0
    assert quality.main(["unknown"]) == 2


def test_quality_runner_stays_in_process() -> None:
    text = (ROOT / "scripts" / "quality" / "check.py").read_text(encoding="utf-8")
    assert "import " + "subprocess" not in text
    assert "Popen" not in text


def test_provenance_and_security_docs_remain() -> None:
    for name in (
        "CLEAN_ROOM.md",
        "SECURITY.md",
        "DISCLAIMER.md",
        "PRE_PUBLISH_SECURITY_REVIEW.md",
        "LICENSE",
        "NOTICE",
        "CHANGELOG.md",
        "README.md",
    ):
        assert (ROOT / name).is_file(), name


def test_package_modules_import() -> None:
    names = (
        "polytutor_prediction",
        "polytutor_prediction.models",
        "polytutor_prediction.demo_data",
        "polytutor_prediction.orderbook",
        "polytutor_prediction.market_service",
        "polytutor_prediction.cli",
        "polytutor_prediction.research",
        "polytutor_prediction.paper",
        "polytutor_prediction.tui",
    )
    for name in names:
        importlib.import_module(name)

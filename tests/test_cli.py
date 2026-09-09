from __future__ import annotations

import pytest

from polytutor_prediction.cli import build_parser, main
from polytutor_prediction.demo_data import build_demo_markets
from polytutor_prediction.market_service import default_service
from polytutor_prediction.paper.engine import PaperEngine
from polytutor_prediction.paper.portfolio import create_portfolio
from polytutor_prediction.tui.menus import LabApp


def test_parser_version():
    p = build_parser()
    assert p.prog == "polytutor-prediction"
    with pytest.raises(SystemExit) as exc:
        p.parse_args(["--version"])
    assert exc.value.code == 0


def test_once_dashboard(capsys):
    code = main(["--once-dashboard"])
    assert code == 0
    out = capsys.readouterr().out
    assert "Dashboard" in out or "DEMO" in out or "Cash" in out
    assert "Live trading:   NO" in out


def test_lab_app_quit():
    inputs = iter(["0"])
    outputs: list[str] = []
    app = LabApp(
        markets=default_service(),
        engine=PaperEngine(portfolio=create_portfolio(10_000)),
        input_fn=lambda _p="": next(inputs),
        output_fn=outputs.append,
    )
    assert app.run() == 0
    assert any("Goodbye" in line for line in outputs)


def test_lab_app_help_and_markets():
    # 7 help (then enter), 2 markets (enter for detail skip), 0 quit
    inputs = iter(["7", "", "2", "", "0"])
    outputs: list[str] = []
    app = LabApp(
        input_fn=lambda _p="": next(inputs),
        output_fn=outputs.append,
    )
    assert app.run() == 0
    blob = "\n".join(outputs)
    assert "Help" in blob or "educational" in blob.lower()


def test_lab_app_unknown_option_then_quit():
    inputs = iter(["9", "0"])
    outputs: list[str] = []
    app = LabApp(
        input_fn=lambda _p="": next(inputs),
        output_fn=outputs.append,
    )
    assert app.run() == 0
    assert any("Unknown option" in line for line in outputs)


def test_lab_app_dashboard_and_journal():
    inputs = iter(["1", "", "6", "", "0"])
    outputs: list[str] = []
    app = LabApp(
        input_fn=lambda _p="": next(inputs),
        output_fn=outputs.append,
    )
    assert app.run() == 0
    blob = "\n".join(outputs)
    assert "Dashboard" in blob
    assert "Journal" in blob
    assert "Live trading:   NO" in blob


def test_lab_app_order_book_and_research():
    market_id = build_demo_markets()[0].market_id
    inputs = iter(["3", market_id, "YES", "", "4", market_id, "", "0"])
    outputs: list[str] = []
    app = LabApp(
        input_fn=lambda _p="": next(inputs),
        output_fn=outputs.append,
    )
    assert app.run() == 0
    blob = "\n".join(outputs)
    assert "Best bid" in blob
    assert "Pair ask sum" in blob
    assert "Educational" in blob


def test_lab_app_paper_buy_then_show_positions():
    market_id = build_demo_markets()[0].market_id
    inputs = iter(
        [
            "5",
            "b",
            market_id,
            "YES",
            "2",
            "quality-test",
            "",
            "5",
            "a",
            "",
            "0",
        ]
    )
    outputs: list[str] = []
    app = LabApp(
        input_fn=lambda _p="": next(inputs),
        output_fn=outputs.append,
    )
    assert app.run() == 0
    blob = "\n".join(outputs)
    assert "OK filled" in blob or "buy" in blob.lower()
    assert market_id in blob


def test_unsupported_mode_still_demo(monkeypatch, capsys):
    monkeypatch.setenv("POLYTUTOR_MODE", "live")
    code = main(["--once-dashboard"])
    assert code == 0
    out = capsys.readouterr().out
    assert "DEMO/OFFLINE" in out
    assert "Live trading:   NO" in out

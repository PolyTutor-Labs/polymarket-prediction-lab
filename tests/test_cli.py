from __future__ import annotations

from polytutor_prediction.cli import build_parser, main
from polytutor_prediction.tui.menus import LabApp
from polytutor_prediction.market_service import default_service
from polytutor_prediction.paper.engine import PaperEngine
from polytutor_prediction.paper.portfolio import create_portfolio


def test_parser_version():
    p = build_parser()
    assert p.prog == "polytutor-prediction"


def test_once_dashboard(capsys):
    code = main(["--once-dashboard"])
    assert code == 0
    out = capsys.readouterr().out
    assert "Dashboard" in out or "DEMO" in out or "Cash" in out


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

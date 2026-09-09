"""Educational paper limits — documents existing caps, not exchange rules."""

from __future__ import annotations

from polytutor_prediction.paper.limits import EducationalLimits


def test_default_caps() -> None:
    limits = EducationalLimits()
    assert limits.max_position_notional == 2000.0
    assert limits.max_order_size == 500.0
    assert limits.max_daily_loss == 1000.0


def test_order_size_bounds() -> None:
    limits = EducationalLimits()
    assert limits.check_order_size(1) == (True, "ok")
    assert limits.check_order_size(500) == (True, "ok")
    ok, msg = limits.check_order_size(0)
    assert ok is False
    assert "positive" in msg.lower()
    ok, msg = limits.check_order_size(-3)
    assert ok is False
    ok, msg = limits.check_order_size(501)
    assert ok is False
    assert "500" in msg


def test_position_notional_bounds() -> None:
    limits = EducationalLimits()
    assert limits.check_position_notional(2000.0) == (True, "ok")
    ok, msg = limits.check_position_notional(2000.01)
    assert ok is False
    assert "2000" in msg


def test_daily_loss_is_strictly_below_negative_cap() -> None:
    limits = EducationalLimits()
    assert limits.check_daily_loss(-1000.0) == (True, "ok")
    ok, msg = limits.check_daily_loss(-1000.01)
    assert ok is False
    assert "daily loss" in msg.lower()

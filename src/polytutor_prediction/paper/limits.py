"""Educational risk limits — not exchange or regulatory rules."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EducationalLimits:
    """Soft caps to keep paper exercises bounded and reflective."""

    max_position_notional: float = 2000.0
    max_order_size: float = 500.0
    max_daily_loss: float = 1000.0

    def check_order_size(self, size: float) -> tuple[bool, str]:
        if size <= 0:
            return False, "Size must be positive."
        if size > self.max_order_size:
            return (
                False,
                f"Educational max order size is {self.max_order_size:.0f} shares.",
            )
        return True, "ok"

    def check_position_notional(self, projected_notional: float) -> tuple[bool, str]:
        if projected_notional > self.max_position_notional:
            return (
                False,
                f"Educational max position notional is ${self.max_position_notional:.0f}.",
            )
        return True, "ok"

    def check_daily_loss(self, daily_realized_pnl: float) -> tuple[bool, str]:
        if daily_realized_pnl < -self.max_daily_loss:
            return (
                False,
                f"Educational max daily loss ${self.max_daily_loss:.0f} reached.",
            )
        return True, "ok"

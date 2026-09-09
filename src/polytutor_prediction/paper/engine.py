"""Paper matching engine against demo order books.

Fills are simulated locally. Nothing is sent to a network venue.
"""

from __future__ import annotations

import itertools
import uuid
from typing import Optional

from polytutor_prediction.models import (
    Market,
    OutcomeLabel,
    PaperFill,
    PaperOrder,
    PaperPortfolio,
    PaperPosition,
    Side,
)
from polytutor_prediction import orderbook as ob
from polytutor_prediction.paper.journal import Journal
from polytutor_prediction.paper.limits import EducationalLimits
from polytutor_prediction.paper.portfolio import create_portfolio


class PaperEngine:
    def __init__(
        self,
        portfolio: Optional[PaperPortfolio] = None,
        limits: Optional[EducationalLimits] = None,
        journal: Optional[Journal] = None,
    ) -> None:
        self.portfolio = portfolio or create_portfolio()
        self.limits = limits or EducationalLimits()
        self.journal = journal or Journal()
        self._id_counter = itertools.count(1)

    def _new_id(self, prefix: str) -> str:
        return f"{prefix}-{next(self._id_counter)}-{uuid.uuid4().hex[:8]}"

    def _get_book(self, market: Market, outcome: OutcomeLabel):
        return market.yes_book if outcome is OutcomeLabel.YES else market.no_book

    def mark_price(self, market: Market, outcome: OutcomeLabel) -> Optional[float]:
        return ob.midpoint(self._get_book(market, outcome))

    def buy(
        self,
        market: Market,
        outcome: OutcomeLabel,
        size: float,
        note: str = "",
    ) -> tuple[bool, str, Optional[PaperFill]]:
        """Paper-buy YES or NO by walking the ask side."""
        ok, msg = self.limits.check_order_size(size)
        if not ok:
            self.journal.add("reject", msg, market.market_id)
            return False, msg, None

        ok, msg = self.limits.check_daily_loss(self.portfolio.daily_realized_pnl)
        if not ok:
            self.journal.add("reject", msg, market.market_id)
            return False, msg, None

        book = self._get_book(market, outcome)
        walked = ob.vwap_buy(book, size)
        if walked is None:
            msg = "No ask liquidity to fill paper buy."
            self.journal.add("reject", msg, market.market_id)
            return False, msg, None

        avg_price, filled = walked
        cost = avg_price * filled
        if cost > self.portfolio.cash + 1e-9:
            msg = f"Insufficient paper cash (need ${cost:.2f}, have ${self.portfolio.cash:.2f})."
            self.journal.add("reject", msg, market.market_id)
            return False, msg, None

        key = self.portfolio.position_key(market.market_id, outcome)
        pos = self.portfolio.positions.get(key)
        current_size = 0.0 if pos is None else pos.size
        current_avg = 0.0 if pos is None else pos.avg_price
        new_size = current_size + filled
        new_avg = (
            ((current_size * current_avg) + (filled * avg_price)) / new_size
            if new_size > 0
            else 0.0
        )
        projected_notional = new_size * new_avg
        ok, msg = self.limits.check_position_notional(projected_notional)
        if not ok:
            self.journal.add("reject", msg, market.market_id)
            return False, msg, None

        order = PaperOrder(
            order_id=self._new_id("ord"),
            market_id=market.market_id,
            outcome=outcome,
            side=Side.BUY,
            price=avg_price,
            size=filled,
            note=note,
        )
        fill = PaperFill(
            fill_id=self._new_id("fill"),
            order_id=order.order_id,
            market_id=market.market_id,
            outcome=outcome,
            side=Side.BUY,
            price=avg_price,
            size=filled,
        )

        self.portfolio.cash -= cost
        self.portfolio.orders.append(order)
        self.portfolio.fills.append(fill)
        self.portfolio.positions[key] = PaperPosition(
            market_id=market.market_id,
            outcome=outcome,
            size=new_size,
            avg_price=new_avg,
            realized_pnl=0.0 if pos is None else pos.realized_pnl,
        )

        self.journal.add(
            "fill",
            f"BUY {filled:.2f} {outcome.value} @ {avg_price:.4f} on {market.market_id}",
            market.market_id,
            detail={"cost": cost, "note": note},
        )
        return True, "filled", fill

    def sell(
        self,
        market: Market,
        outcome: OutcomeLabel,
        size: float,
        note: str = "",
    ) -> tuple[bool, str, Optional[PaperFill]]:
        """Paper-sell existing YES/NO inventory by walking the bid side."""
        ok, msg = self.limits.check_order_size(size)
        if not ok:
            self.journal.add("reject", msg, market.market_id)
            return False, msg, None

        ok, msg = self.limits.check_daily_loss(self.portfolio.daily_realized_pnl)
        if not ok:
            self.journal.add("reject", msg, market.market_id)
            return False, msg, None

        key = self.portfolio.position_key(market.market_id, outcome)
        pos = self.portfolio.positions.get(key)
        if pos is None or pos.size <= 0:
            msg = "No paper inventory to sell."
            self.journal.add("reject", msg, market.market_id)
            return False, msg, None

        sell_size = min(size, pos.size)
        book = self._get_book(market, outcome)
        walked = ob.vwap_sell(book, sell_size)
        if walked is None:
            msg = "No bid liquidity to fill paper sell."
            self.journal.add("reject", msg, market.market_id)
            return False, msg, None

        avg_price, filled = walked
        proceeds = avg_price * filled
        realized = (avg_price - pos.avg_price) * filled

        order = PaperOrder(
            order_id=self._new_id("ord"),
            market_id=market.market_id,
            outcome=outcome,
            side=Side.SELL,
            price=avg_price,
            size=filled,
            note=note,
        )
        fill = PaperFill(
            fill_id=self._new_id("fill"),
            order_id=order.order_id,
            market_id=market.market_id,
            outcome=outcome,
            side=Side.SELL,
            price=avg_price,
            size=filled,
        )

        self.portfolio.cash += proceeds
        self.portfolio.daily_realized_pnl += realized
        self.portfolio.orders.append(order)
        self.portfolio.fills.append(fill)

        remaining = pos.size - filled
        if remaining <= 1e-12:
            self.portfolio.positions.pop(key, None)
        else:
            self.portfolio.positions[key] = PaperPosition(
                market_id=market.market_id,
                outcome=outcome,
                size=remaining,
                avg_price=pos.avg_price,
                realized_pnl=pos.realized_pnl + realized,
            )

        self.journal.add(
            "fill",
            f"SELL {filled:.2f} {outcome.value} @ {avg_price:.4f} on {market.market_id}",
            market.market_id,
            detail={"proceeds": proceeds, "realized_pnl": realized, "note": note},
        )
        return True, "filled", fill

    def unrealized_pnl(self, markets: dict[str, Market]) -> float:
        total = 0.0
        for pos in self.portfolio.positions.values():
            market = markets.get(pos.market_id)
            if market is None:
                continue
            mid = self.mark_price(market, pos.outcome)
            if mid is None:
                continue
            total += (mid - pos.avg_price) * pos.size
        return total

    def equity(self, markets: dict[str, Market]) -> float:
        marked = 0.0
        for pos in self.portfolio.positions.values():
            market = markets.get(pos.market_id)
            if market is None:
                marked += pos.size * pos.avg_price
                continue
            mid = self.mark_price(market, pos.outcome)
            px = pos.avg_price if mid is None else mid
            marked += pos.size * px
        return self.portfolio.cash + marked

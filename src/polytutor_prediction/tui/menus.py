"""Simple interactive menus using only the Python standard library."""

from __future__ import annotations

import os
from typing import Callable, Optional

from polytutor_prediction import __version__
from polytutor_prediction.market_service import MarketService, default_service
from polytutor_prediction.models import OutcomeLabel
from polytutor_prediction import orderbook as ob
from polytutor_prediction.paper.engine import PaperEngine
from polytutor_prediction.paper.portfolio import create_portfolio, initial_cash_from_env
from polytutor_prediction.research import (
    observe_imbalance,
    observe_midpoint,
    observe_pair_cost,
    observe_spread,
)


HELP_TEXT = """
PolyTutor Prediction Lab — Help
================================
Educational offline lab. Demo mode only. Paper trading only.

Sections:
  1 Dashboard       Mode, cash, equity snapshot
  2 Markets         List / inspect demo markets
  3 Order Book      Bid/ask, spread, midpoint, depth
  4 Research        Educational observations (not arb)
  5 Paper Portfolio Buy/sell YES or NO with virtual cash
  6 Journal         Review paper decisions
  7 Help            This screen
  0 Quit

Safety:
  - No wallets, keys, signing, or live orders
  - Educational limits cap size, notional, daily loss
  - Pair-cost and imbalance are learning tools only
"""


class LabApp:
    def __init__(
        self,
        markets: Optional[MarketService] = None,
        engine: Optional[PaperEngine] = None,
        input_fn: Callable[[str], str] = input,
        output_fn: Callable[[str], None] = print,
    ) -> None:
        self.markets = markets or default_service()
        cash = initial_cash_from_env()
        self.engine = engine or PaperEngine(portfolio=create_portfolio(cash))
        self.input_fn = input_fn
        self.output_fn = output_fn
        self.mode = os.environ.get("POLYTUTOR_MODE", "demo").strip().lower() or "demo"

    def _pause(self) -> None:
        try:
            self.input_fn("\n[Enter] continue… ")
        except EOFError:
            pass

    def _market_map(self):
        return {m.market_id: m for m in self.markets.list_markets()}

    def run(self) -> int:
        self.output_fn(
            f"PolyTutor Prediction Lab v{__version__} — mode={self.mode} (demo/offline)"
        )
        if self.mode not in {"demo", "offline", "paper"}:
            self.output_fn(
                "Warning: unsupported mode string; continuing in educational demo behavior."
            )
        actions = {
            "1": self.dashboard,
            "2": self.markets_menu,
            "3": self.order_book_menu,
            "4": self.research_menu,
            "5": self.portfolio_menu,
            "6": self.journal_menu,
            "7": self.help_menu,
            "0": None,
        }
        while True:
            self.output_fn(
                "\n=== Menu ===\n"
                "1) Dashboard\n"
                "2) Markets\n"
                "3) Order Book\n"
                "4) Research\n"
                "5) Paper Portfolio\n"
                "6) Journal\n"
                "7) Help\n"
                "0) Quit\n"
            )
            try:
                choice = self.input_fn("Select: ").strip()
            except EOFError:
                self.output_fn("EOF — exiting.")
                return 0
            if choice == "0":
                self.output_fn("Goodbye — remember: educational paper only.")
                return 0
            action = actions.get(choice)
            if action is None:
                self.output_fn("Unknown option.")
                continue
            action()

    def dashboard(self) -> None:
        mkt = self._market_map()
        eq = self.engine.equity(mkt)
        upnl = self.engine.unrealized_pnl(mkt)
        p = self.engine.portfolio
        self.output_fn("\n--- Dashboard ---")
        self.output_fn(f"Mode:           {self.mode} (DEMO/OFFLINE)")
        self.output_fn(f"Markets:        {self.markets.count()}")
        self.output_fn(f"Cash:           ${p.cash:,.2f}")
        self.output_fn(f"Initial cash:   ${p.initial_cash:,.2f}")
        self.output_fn(f"Equity (mark):  ${eq:,.2f}")
        self.output_fn(f"Unrealized PnL: ${upnl:,.2f}")
        self.output_fn(f"Daily realized: ${p.daily_realized_pnl:,.2f}")
        self.output_fn(f"Open positions: {len(p.positions)}")
        self.output_fn(f"Fills:          {len(p.fills)}")
        self.output_fn("Live trading:   NO")
        self._pause()

    def markets_menu(self) -> None:
        self.output_fn("\n--- Markets ---")
        for m in self.markets.list_markets():
            mid_y = ob.midpoint(m.yes_book)
            mid_s = f"{mid_y:.3f}" if mid_y is not None else "n/a"
            self.output_fn(f"[{m.market_id}] ({m.category}) mid≈{mid_s}")
            self.output_fn(f"  Q: {m.question}")
        try:
            mid = self.input_fn("Market id for detail (or Enter to return): ").strip()
        except EOFError:
            return
        if not mid:
            return
        m = self.markets.get_market(mid)
        if m is None:
            self.output_fn("Not found.")
        else:
            self.output_fn(f"\n{m.question}\nStatus: {m.status}\n{m.description}")
            self.output_fn(f"YES token: {m.yes.token_id}")
            self.output_fn(f"NO  token: {m.no.token_id}")
        self._pause()

    def order_book_menu(self) -> None:
        self.output_fn("\n--- Order Book ---")
        for m in self.markets.list_markets():
            self.output_fn(f"  {m.market_id}")
        try:
            mid = self.input_fn("Market id: ").strip()
            which = self.input_fn("Outcome YES/NO [YES]: ").strip().upper() or "YES"
        except EOFError:
            return
        m = self.markets.get_market(mid)
        if m is None:
            self.output_fn("Not found.")
            self._pause()
            return
        outcome = OutcomeLabel.YES if which != "NO" else OutcomeLabel.NO
        book = m.yes_book if outcome is OutcomeLabel.YES else m.no_book
        q = ob.quote(book)
        sp = ob.spread(book)
        mp = ob.midpoint(book)
        d = ob.depth(book)
        imb = ob.imbalance(book)
        self.output_fn(f"\nBook for {outcome.value} on {m.market_id}")
        self.output_fn(f"Best bid: {q.best_bid} x {q.bid_size}")
        self.output_fn(f"Best ask: {q.best_ask} x {q.ask_size}")
        self.output_fn(f"Spread:   {sp}")
        self.output_fn(f"Midpoint: {mp}  (rough implied probability proxy)")
        self.output_fn(f"Depth:    bid={d['bid_depth']} ask={d['ask_depth']}")
        self.output_fn(f"Imbalance:{imb}")
        self.output_fn("Bids:")
        for lvl in sorted(book.bids, key=lambda x: x.price, reverse=True):
            self.output_fn(f"  {lvl.price:.4f}  {lvl.size:.2f}")
        self.output_fn("Asks:")
        for lvl in sorted(book.asks, key=lambda x: x.price):
            self.output_fn(f"  {lvl.price:.4f}  {lvl.size:.2f}")
        self._pause()

    def research_menu(self) -> None:
        self.output_fn("\n--- Research (educational observations) ---")
        for m in self.markets.list_markets():
            self.output_fn(f"  {m.market_id}")
        try:
            mid = self.input_fn("Market id: ").strip()
        except EOFError:
            return
        m = self.markets.get_market(mid)
        if m is None:
            self.output_fn("Not found.")
            self._pause()
            return
        s = observe_spread(m)
        mp = observe_midpoint(m)
        imb = observe_imbalance(m)
        pc = observe_pair_cost(m)
        self.output_fn(f"Spread YES:    {s.spread}  ({s.note})")
        self.output_fn(f"Midpoint YES:  {mp.midpoint}  ({mp.note})")
        self.output_fn(
            f"Imbalance YES: {imb.imbalance} "
            f"(bid_depth={imb.bid_depth}, ask_depth={imb.ask_depth})"
        )
        self.output_fn(f"  {imb.note}")
        self.output_fn(
            f"Pair ask sum:  {pc.pair_ask_sum} "
            f"(YES ask={pc.yes_ask}, NO ask={pc.no_ask})"
        )
        self.output_fn(
            f"Pair bid sum:  {pc.pair_bid_sum} "
            f"(YES bid={pc.yes_bid}, NO bid={pc.no_bid})"
        )
        self.output_fn(f"  {pc.note}")
        self._pause()

    def portfolio_menu(self) -> None:
        self.output_fn("\n--- Paper Portfolio ---")
        self.output_fn("a) Show positions")
        self.output_fn("b) Buy YES/NO")
        self.output_fn("c) Sell YES/NO")
        try:
            choice = self.input_fn("Select: ").strip().lower()
        except EOFError:
            return
        if choice == "a":
            self._show_positions()
        elif choice == "b":
            self._trade(buy=True)
        elif choice == "c":
            self._trade(buy=False)
        else:
            self.output_fn("Cancelled.")
        self._pause()

    def _show_positions(self) -> None:
        p = self.engine.portfolio
        if not p.positions:
            self.output_fn("No open positions.")
            return
        for pos in p.positions.values():
            self.output_fn(
                f"  {pos.market_id} {pos.outcome.value}: "
                f"size={pos.size:.2f} avg={pos.avg_price:.4f}"
            )
        self.output_fn(f"Cash: ${p.cash:,.2f}")

    def _trade(self, buy: bool) -> None:
        for m in self.markets.list_markets():
            self.output_fn(f"  {m.market_id}")
        try:
            mid = self.input_fn("Market id: ").strip()
            which = self.input_fn("Outcome YES/NO [YES]: ").strip().upper() or "YES"
            size_s = self.input_fn("Size: ").strip()
            note = self.input_fn("Note (optional): ").strip()
        except EOFError:
            return
        m = self.markets.get_market(mid)
        if m is None:
            self.output_fn("Not found.")
            return
        try:
            size = float(size_s)
        except ValueError:
            self.output_fn("Invalid size.")
            return
        outcome = OutcomeLabel.YES if which != "NO" else OutcomeLabel.NO
        if buy:
            ok, msg, fill = self.engine.buy(m, outcome, size, note=note)
        else:
            ok, msg, fill = self.engine.sell(m, outcome, size, note=note)
        if ok and fill is not None:
            self.output_fn(
                f"OK {msg}: {fill.side.value} {fill.size:.2f} @ {fill.price:.4f}"
            )
        else:
            self.output_fn(f"Rejected: {msg}")

    def journal_menu(self) -> None:
        self.output_fn("\n--- Journal ---")
        entries = self.engine.journal.list_entries()
        if not entries:
            self.output_fn("(empty)")
        for e in entries:
            ts = e.timestamp.isoformat()
            self.output_fn(f"[{ts}] {e.kind}: {e.message}")
        self._pause()

    def help_menu(self) -> None:
        self.output_fn(HELP_TEXT)
        self._pause()

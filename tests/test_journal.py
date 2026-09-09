"""In-memory journal behavior (no persistence)."""

from __future__ import annotations

from polytutor_prediction.paper.journal import Journal


def test_journal_add_list_clear() -> None:
    journal = Journal()
    assert len(journal) == 0
    entry = journal.add("note", "hello", market_id="demo-mkt-election-2028", detail={"n": 1})
    assert entry.kind == "note"
    assert entry.message == "hello"
    assert entry.market_id == "demo-mkt-election-2028"
    assert entry.detail == {"n": 1}
    assert entry.timestamp.tzinfo is not None
    listed = journal.list_entries()
    assert len(listed) == 1
    listed.append(entry)
    assert len(journal) == 1
    journal.clear()
    assert len(journal) == 0
    assert journal.list_entries() == []

"""Phase 5: REVERSAL of E7 by E9."""

from ledger.engine import Ledger
from ledger.stream import phase4_stream, phase5_stream


def _customer_snapshot(ledger: Ledger) -> dict:
    """Compare customer+fee projection before interest capital."""
    return {
        "ledger": {
            day: ledger._closing_before_interest("ACC-001", day).minor
            for day in range(1, 7)
        },
        "holds": ledger.active_holds_minor("ACC-001"),
        "fees": list(ledger.fee_postings),
    }


def test_e9_nets_e7_back_to_pre_e7():
    pre = Ledger()
    for ev in phase4_stream():
        pre.apply(ev)
    post = Ledger()
    for ev in phase5_stream():
        post.apply(ev)
    assert _customer_snapshot(post) == _customer_snapshot(pre)
    assert post._closing_before_interest("ACC-001", 6).minor == 46500


def test_e7_remains_in_log_after_reversal():
    ledger = Ledger()
    for ev in phase5_stream():
        ledger.apply(ev)
    ids = [a.source.event_id for a in ledger.log]
    assert "E7" in ids and "E9" in ids
    e7 = next(a for a in ledger.log if a.source.event_id == "E7")
    assert e7.accepted is True

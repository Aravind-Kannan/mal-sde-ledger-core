"""Phase 6: sticky Auth-B denial."""

from ledger.engine import Ledger
from ledger.events import AuthStatus, EventType, SourceEvent
from ledger.money import from_display
from ledger.stream import e1, e2, e3, e4, e5, e6, e7, e8, e9, phase6_stream


def test_auth_b_rejected_while_e7_live_and_stays_after_e9():
    mid = Ledger()
    for ev in [e1(), e2(), e3(), e4(), e5(), e6(), e7(), e8()]:
        mid.apply(ev)
    assert mid.auths["Auth-B"].status == AuthStatus.REJECTED
    assert mid.active_holds_minor("ACC-001") == 0

    full = Ledger()
    for ev in phase6_stream():
        full.apply(ev)
    assert full.auths["Auth-B"].status == AuthStatus.REJECTED
    assert full.active_holds_minor("ACC-001") == 0
    # Customer ledger back to pre-E7 (before Day-6 interest capital).
    assert full._closing_before_interest("ACC-001", 6).minor == 46500


def test_auth_b_outcome_is_sticky_in_log():
    ledger = Ledger()
    for ev in phase6_stream():
        ledger.apply(ev)
    e8_applied = next(a for a in ledger.log if a.source.event_id == "E8")
    assert e8_applied.accepted is False
    assert e8_applied.auth_status == AuthStatus.REJECTED

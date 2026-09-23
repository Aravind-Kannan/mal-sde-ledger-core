"""Phase 4: SETTLEMENT (capture-for-less) and unknown-auth reject."""

from ledger.engine import Ledger
from ledger.events import AuthStatus
from ledger.stream import phase4_stream


def test_auth_a_settlement_accepted_ledger_465():
    ledger = Ledger()
    for ev in phase4_stream():
        ledger.apply(ev)
    # 250 + 400 - 185 = 465
    assert ledger.ledger_balance("ACC-001", 4).minor == 46500
    assert ledger.auths["Auth-A"].status == AuthStatus.SETTLED
    assert ledger.active_holds_minor("ACC-001") == 0


def test_auth_z_rejected_no_funds_leave():
    ledger = Ledger()
    for ev in phase4_stream():
        ledger.apply(ev)
    e6 = next(a for a in ledger.log if a.source.event_id == "E6")
    assert e6.accepted is False
    assert "Auth-Z" in (e6.error or "")
    assert ledger.ledger_balance("ACC-001", 4).minor == 46500
    assert "Auth-Z" not in ledger.auths

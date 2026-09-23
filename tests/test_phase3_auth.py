"""Phase 3: AUTHORIZATION holds."""

from ledger.engine import Ledger
from ledger.events import AuthStatus
from ledger.stream import phase3_stream


def test_auth_a_approved_hold_cuts_available_not_ledger():
    ledger = Ledger()
    for ev in phase3_stream():
        ledger.apply(ev)
    assert ledger.ledger_balance("ACC-001", 2).minor == 25000
    assert ledger.available_balance("ACC-001", 2).minor == 5000
    assert ledger.auths["Auth-A"].status == AuthStatus.APPROVED
    assert ledger.auths["Auth-A"].hold_minor == 20000


def test_hold_does_not_change_day2_ledger_close():
    ledger = Ledger()
    for ev in phase3_stream():
        ledger.apply(ev)
    # Same as Phase 1 Day 2 close — hold is off-ledger.
    assert str(ledger.ledger_balance("ACC-001", 2)) == "AED 250.00"

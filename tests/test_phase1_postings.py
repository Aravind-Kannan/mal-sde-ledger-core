"""Phase 1: CREDIT/DEBIT MVP."""

from ledger.engine import Ledger
from ledger.money import from_display, MoneyError
from ledger.replay import run
from ledger.stream import phase1_stream
import pytest


def test_e1_e2_day1_closing_aed_250():
    ledger = Ledger()
    for ev in phase1_stream():
        ledger.apply(ev)
    bal = ledger.ledger_balance("ACC-001", 1)
    assert bal.minor == 25000  # AED 250.00
    assert str(bal) == "AED 250.00"


def test_acc002_still_zero():
    ledger = Ledger()
    for ev in phase1_stream():
        ledger.apply(ev)
    assert ledger.ledger_balance("ACC-002", 1).minor == 0


def test_wrong_scale_rejected():
    with pytest.raises(MoneyError):
        from_display("AED", "1.2")
    with pytest.raises(MoneyError):
        from_display("AED", "1.234")
    with pytest.raises(MoneyError):
        from_display("BHD", "10.00")


def test_replay_prints_day1_close():
    out = run(phase1_stream(), through_day=1)
    assert "ACC-001 closing: AED 250.00" in out
    assert "fees: (none)" in out

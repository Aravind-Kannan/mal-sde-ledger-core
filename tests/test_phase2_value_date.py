"""Phase 2: value_date backdating (E7)."""

from ledger.engine import Ledger
from ledger.replay import run
from ledger.stream import phase2_stream


def test_after_e7_day2_prefee_is_minus_370():
    ledger = Ledger()
    for ev in phase2_stream():
        ledger.apply(ev)
    # End of Day 5 stream prefix = after E7; Day 2 close before fees.
    assert ledger.ledger_balance("ACC-001", 2).minor == -37000
    assert str(ledger.ledger_balance("ACC-001", 2)) == "AED -370.00"


def test_day1_still_250_after_e7():
    ledger = Ledger()
    for ev in phase2_stream():
        ledger.apply(ev)
    assert ledger.ledger_balance("ACC-001", 1).minor == 25000


def test_e7_remains_in_log():
    ledger = Ledger()
    for ev in phase2_stream():
        ledger.apply(ev)
    ids = [a.source.event_id for a in ledger.log]
    assert ids == ["E1", "E2", "E7"]
    assert all(a.accepted for a in ledger.log)


def test_replay_prints_day2_negative():
    out = run(phase2_stream(), through_day=5)
    assert "Day 1" in out
    assert "ACC-001 closing: AED 250.00" in out
    assert "ACC-001 closing: AED -370.00" in out

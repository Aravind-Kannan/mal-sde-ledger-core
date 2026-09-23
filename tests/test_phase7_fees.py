"""Phase 7: derived overdraft fees, restated from the source prefix."""

from ledger.engine import Ledger
from ledger.stream import e1, e2, e3, e4, e5, e6, e7, e8, e9, phase4_stream, phase6_stream


def test_after_e7_fees_on_days_2_4_5_not_only_day2():
    ledger = Ledger()
    for ev in [e1(), e2(), e3(), e4(), e5(), e6(), e7(), e8()]:
        ledger.apply(ev)
    fee_days = sorted(
        vdate for aid, vdate, _m in ledger.fee_postings if aid == "ACC-001"
    )
    assert fee_days == [2, 4, 5]
    assert ledger.pre_fee_closing("ACC-001", 2).minor == -37000


def test_after_e9_derived_fees_cleared():
    ledger = Ledger()
    for ev in phase6_stream():
        ledger.apply(ev)
    assert ledger.fee_postings == []
    assert ledger.ledger_balance("ACC-001", 6).minor == 46500


def test_pre_e7_snapshot_has_no_fees():
    ledger = Ledger()
    for ev in phase4_stream():
        ledger.apply(ev)
    assert ledger.fee_postings == []

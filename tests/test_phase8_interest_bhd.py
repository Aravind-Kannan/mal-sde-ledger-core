"""Phase 8: interest capitalization + BHD instalments (E10)."""

from ledger.engine import Ledger
from ledger.money import from_display, interest_plan, split_equal_with_remainder
from ledger.stream import full_stream, phase6_stream


def test_e10_instalments_333_333_334_not_each_3334():
    assert split_equal_with_remainder(10_000, 3) == [3333, 3333, 3334]
    ledger = Ledger()
    for ev in full_stream():
        ledger.apply(ev)
    e10_lines = [p for p in ledger.postings if p[3] == "E10"]
    assert [p[2] for p in e10_lines] == [3333, 3333, 3334]
    assert sum(p[2] for p in e10_lines) == 10_000
    assert ledger._closing_before_interest("ACC-002", 5).minor == 10_000
    assert str(ledger._closing_before_interest("ACC-002", 5)) == "BHD 10.000"


def test_interest_rounded_days_sum_to_capital():
    ledger = Ledger()
    for ev in full_stream():
        ledger.apply(ev)
    for aid, accruals in ledger.interest_accruals.items():
        capital = sum(
            m for a, d, m in ledger.interest_postings if a == aid and d == 6
        )
        assert sum(accruals) == capital
        assert capital >= 0


def test_interest_remainder_not_discarded():
    # Construct closes where round(sum(raw)) != sum(round(raw)).
    closes = [46500, 46500]  # each raw 18.6 → round 19; sum raw 37.2 → capital 37
    rounded, capital = interest_plan(closes)
    assert capital == 37
    assert sum(rounded) == 37
    assert rounded != [19, 19]  # last day penny-adjusted


def test_acc001_day6_includes_capital():
    ledger = Ledger()
    for ev in phase6_stream():
        ledger.apply(ev)
    before = ledger._closing_before_interest("ACC-001", 6).minor
    after = ledger.ledger_balance("ACC-001", 6).minor
    capital = sum(m for a, d, m in ledger.interest_postings if a == "ACC-001")
    assert before == 46500
    assert after == before + capital
    assert capital == sum(ledger.interest_accruals["ACC-001"])

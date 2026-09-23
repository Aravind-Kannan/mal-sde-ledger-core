"""Canonical event stream E1–E10. Phases expose prefixes."""

from __future__ import annotations

from ledger.events import EventType, SourceEvent
from ledger.money import from_display


def e1() -> SourceEvent:
    return SourceEvent(
        event_id="E1",
        booking_day=1,
        value_date=1,
        event_type=EventType.CREDIT,
        account_id="ACC-001",
        amount=from_display("AED", "1200.00"),
    )


def e2() -> SourceEvent:
    return SourceEvent(
        event_id="E2",
        booking_day=1,
        value_date=1,
        event_type=EventType.DEBIT,
        account_id="ACC-001",
        amount=from_display("AED", "950.00"),
    )


def e3() -> SourceEvent:
    return SourceEvent(
        event_id="E3",
        booking_day=2,
        value_date=2,
        event_type=EventType.AUTHORIZATION,
        account_id="ACC-001",
        amount=from_display("AED", "200.00"),
        auth_id="Auth-A",
    )


def e4() -> SourceEvent:
    return SourceEvent(
        event_id="E4",
        booking_day=3,
        value_date=3,
        event_type=EventType.CREDIT,
        account_id="ACC-001",
        amount=from_display("AED", "400.00"),
    )


def e5() -> SourceEvent:
    return SourceEvent(
        event_id="E5",
        booking_day=4,
        value_date=4,
        event_type=EventType.SETTLEMENT,
        account_id="ACC-001",
        amount=from_display("AED", "185.00"),
        auth_id="Auth-A",
    )


def e6() -> SourceEvent:
    return SourceEvent(
        event_id="E6",
        booking_day=4,
        value_date=4,
        event_type=EventType.SETTLEMENT,
        account_id="ACC-001",
        amount=from_display("AED", "180.00"),
        auth_id="Auth-Z",
    )


def e7() -> SourceEvent:
    return SourceEvent(
        event_id="E7",
        booking_day=5,
        value_date=2,
        event_type=EventType.DEBIT,
        account_id="ACC-001",
        amount=from_display("AED", "620.00"),
    )


def e8() -> SourceEvent:
    return SourceEvent(
        event_id="E8",
        booking_day=5,
        value_date=5,
        event_type=EventType.AUTHORIZATION,
        account_id="ACC-001",
        amount=from_display("AED", "90.00"),
        auth_id="Auth-B",
    )


def e9() -> SourceEvent:
    return SourceEvent(
        event_id="E9",
        booking_day=6,
        value_date=2,
        event_type=EventType.REVERSAL,
        account_id="ACC-001",
        reverses_event_id="E7",
    )


def e10() -> SourceEvent:
    return SourceEvent(
        event_id="E10",
        booking_day=5,
        value_date=5,
        event_type=EventType.CREDIT,
        account_id="ACC-002",
        amount=from_display("BHD", "10.000"),
        instalments=3,
    )


def phase1_stream() -> list[SourceEvent]:
    return [e1(), e2()]


def phase2_stream() -> list[SourceEvent]:
    return [e1(), e2(), e7()]


def phase3_stream() -> list[SourceEvent]:
    return [e1(), e2(), e3()]


def phase4_stream() -> list[SourceEvent]:
    return [e1(), e2(), e3(), e4(), e5(), e6()]


def phase5_stream() -> list[SourceEvent]:
    # E1–E7, E9 (no E8 yet)
    return [e1(), e2(), e3(), e4(), e5(), e6(), e7(), e9()]


def phase6_stream() -> list[SourceEvent]:
    return [e1(), e2(), e3(), e4(), e5(), e6(), e7(), e8(), e9()]


def full_stream() -> list[SourceEvent]:
    # Causal order: E1..E9 then E10 (E10 booking day 5 but listed after E9).
    return [e1(), e2(), e3(), e4(), e5(), e6(), e7(), e8(), e9(), e10()]

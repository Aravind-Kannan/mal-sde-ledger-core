"""Frozen source-event types. Append-only: never mutate or delete records."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from ledger.money import Money


class EventType(str, Enum):
    CREDIT = "CREDIT"
    DEBIT = "DEBIT"
    AUTHORIZATION = "AUTHORIZATION"
    SETTLEMENT = "SETTLEMENT"
    REVERSAL = "REVERSAL"


class AuthStatus(str, Enum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    SETTLED = "SETTLED"


@dataclass(frozen=True, slots=True)
class SourceEvent:
    """One immutable source-log record.

    Outcomes (auth status, settlement accepted, errors) are set at apply time
    via AppliedEvent, not by mutating this record.
    """

    event_id: str
    booking_day: int
    value_date: int
    event_type: EventType
    account_id: str
    amount: Optional[Money] = None
    auth_id: Optional[str] = None
    reverses_event_id: Optional[str] = None
    # For multi-instalment credits (E10): how many equal parts. None = single.
    instalments: Optional[int] = None


@dataclass(frozen=True, slots=True)
class AppliedEvent:
    """Source event plus sticky apply-time outcome (never rewritten later)."""

    source: SourceEvent
    accepted: bool = True
    error: Optional[str] = None
    auth_status: Optional[AuthStatus] = None
    # Posting minor units actually booked (credits positive, debits negative).
    # For multi-instalment: one AppliedEvent per instalment share, or we book
    # multiple posting lines — see engine.
    posting_minors: tuple[int, ...] = field(default_factory=tuple)

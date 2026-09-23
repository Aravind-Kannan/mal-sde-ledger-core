"""Append-only ledger engine. Phase 1: CREDIT/DEBIT only."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from ledger.events import AppliedEvent, EventType, SourceEvent
from ledger.money import Money, format_money, zero


WINDOW_DAYS = (1, 2, 3, 4, 5, 6)

ACCOUNTS: dict[str, str] = {
    "ACC-001": "AED",
    "ACC-002": "BHD",
}


@dataclass
class AccountState:
    account_id: str
    currency: str


@dataclass
class DayReport:
    day: int
    closings: dict[str, Money]  # account_id -> post-fee closing (Phase 1: no fees)
    fees: dict[str, list[Money]]  # account_id -> fees assessed that day
    auths: list[str]
    errors: list[str]


@dataclass
class Ledger:
    """In-memory append-only ledger."""

    accounts: dict[str, AccountState] = field(default_factory=dict)
    log: list[AppliedEvent] = field(default_factory=list)
    # Posting lines derived from accepted CREDIT/DEBIT/REVERSAL/SETTLEMENT.
    # (account_id, value_date, signed_minor, source_event_id, kind)
    postings: list[tuple[str, int, int, str, str]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.accounts:
            for aid, ccy in ACCOUNTS.items():
                self.accounts[aid] = AccountState(aid, ccy)

    def apply(self, event: SourceEvent) -> AppliedEvent:
        if event.event_type in (EventType.CREDIT, EventType.DEBIT):
            return self._apply_posting(event)
        raise NotImplementedError(f"event type not yet supported: {event.event_type}")

    def _apply_posting(self, event: SourceEvent) -> AppliedEvent:
        if event.amount is None:
            applied = AppliedEvent(
                source=event, accepted=False, error="missing amount"
            )
            self.log.append(applied)
            return applied
        acct = self.accounts.get(event.account_id)
        if acct is None:
            applied = AppliedEvent(
                source=event, accepted=False, error="unknown account"
            )
            self.log.append(applied)
            return applied
        if event.amount.currency != acct.currency:
            applied = AppliedEvent(
                source=event,
                accepted=False,
                error=f"currency mismatch: account {acct.currency}",
            )
            self.log.append(applied)
            return applied

        signed = event.amount.minor
        if event.event_type == EventType.DEBIT:
            signed = -signed
        kind = event.event_type.value
        self.postings.append(
            (event.account_id, event.value_date, signed, event.event_id, kind)
        )
        applied = AppliedEvent(
            source=event, accepted=True, posting_minors=(signed,)
        )
        self.log.append(applied)
        return applied

    def ledger_balance(self, account_id: str, as_of_day: int) -> Money:
        """Sum of postings with value_date <= as_of_day (customer + fees later)."""
        ccy = self.accounts[account_id].currency
        total = 0
        for aid, vdate, minor, _eid, _kind in self.postings:
            if aid == account_id and vdate <= as_of_day:
                total += minor
        return Money(ccy, total)

    def report_days(self, through_day: int = 6) -> list[DayReport]:
        reports: list[DayReport] = []
        for day in range(1, through_day + 1):
            closings = {
                aid: self.ledger_balance(aid, day) for aid in self.accounts
            }
            reports.append(
                DayReport(
                    day=day,
                    closings=closings,
                    fees={aid: [] for aid in self.accounts},
                    auths=[],
                    errors=[],
                )
            )
        # Collect sticky errors from the log (booking day tagged).
        for applied in self.log:
            if applied.error:
                day = applied.source.booking_day
                if 1 <= day <= through_day:
                    reports[day - 1].errors.append(
                        f"{applied.source.event_id}: {applied.error}"
                    )
        return reports


def format_report(reports: list[DayReport]) -> str:
    lines: list[str] = []
    for r in reports:
        lines.append(f"=== Day {r.day} ===")
        for aid in sorted(r.closings):
            lines.append(f"  {aid} closing: {format_money(r.closings[aid])}")
            fee_list = r.fees.get(aid) or []
            if fee_list:
                for f in fee_list:
                    lines.append(f"  {aid} fee: {format_money(f)}")
            else:
                lines.append(f"  {aid} fees: (none)")
        if r.auths:
            for a in r.auths:
                lines.append(f"  auth: {a}")
        else:
            lines.append("  auths: (none)")
        if r.errors:
            for e in r.errors:
                lines.append(f"  error: {e}")
        else:
            lines.append("  errors: (none)")
        lines.append("")
    return "\n".join(lines)

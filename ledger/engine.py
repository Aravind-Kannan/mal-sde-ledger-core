"""Append-only ledger engine.

Phases:
  1 CREDIT/DEBIT
  2 value_date as-of
  3 AUTHORIZATION holds
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from ledger.events import AppliedEvent, AuthStatus, EventType, SourceEvent
from ledger.money import Money, format_money


WINDOW_DAYS = (1, 2, 3, 4, 5, 6)

ACCOUNTS: dict[str, str] = {
    "ACC-001": "AED",
    "ACC-002": "BHD",
}

# Spec: AED 25.00 once per day per account when pre-fee close is negative.
OVERDRAFT_FEE_MINOR: dict[str, int] = {
    "AED": 2500,
}


@dataclass
class AccountState:
    account_id: str
    currency: str


@dataclass
class DayReport:
    day: int
    closings: dict[str, Money]
    fees: dict[str, list[Money]]
    auths: list[str]
    errors: list[str]


@dataclass
class AuthRecord:
    auth_id: str
    account_id: str
    hold_minor: int
    status: AuthStatus
    booking_day: int


@dataclass
class Ledger:
    """In-memory append-only ledger."""

    accounts: dict[str, AccountState] = field(default_factory=dict)
    log: list[AppliedEvent] = field(default_factory=list)
    # (account_id, value_date, signed_minor, source_event_id, kind)
    postings: list[tuple[str, int, int, str, str]] = field(default_factory=list)
    auths: dict[str, AuthRecord] = field(default_factory=dict)
    # Derived: recomputed after every apply; never source-log mutations.
    # (account_id, value_date, signed_minor) — signed_minor is negative (fee debit).
    fee_postings: list[tuple[str, int, int]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.accounts:
            for aid, ccy in ACCOUNTS.items():
                self.accounts[aid] = AccountState(aid, ccy)

    def apply(self, event: SourceEvent) -> AppliedEvent:
        if event.event_type in (EventType.CREDIT, EventType.DEBIT):
            applied = self._apply_posting(event)
        elif event.event_type == EventType.AUTHORIZATION:
            applied = self._apply_authorization(event)
        elif event.event_type == EventType.SETTLEMENT:
            applied = self._apply_settlement(event)
        elif event.event_type == EventType.REVERSAL:
            applied = self._apply_reversal(event)
        else:
            raise NotImplementedError(
                f"event type not yet supported: {event.event_type}"
            )
        self._restate_fees()
        return applied

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

    def _apply_authorization(self, event: SourceEvent) -> AppliedEvent:
        if event.amount is None or event.auth_id is None:
            applied = AppliedEvent(
                source=event,
                accepted=False,
                error="authorization missing amount or auth_id",
                auth_status=AuthStatus.REJECTED,
            )
            self.log.append(applied)
            return applied
        acct = self.accounts.get(event.account_id)
        if acct is None:
            applied = AppliedEvent(
                source=event,
                accepted=False,
                error="unknown account",
                auth_status=AuthStatus.REJECTED,
            )
            self.log.append(applied)
            return applied
        if event.amount.currency != acct.currency:
            applied = AppliedEvent(
                source=event,
                accepted=False,
                error=f"currency mismatch: account {acct.currency}",
                auth_status=AuthStatus.REJECTED,
            )
            self.log.append(applied)
            return applied
        if event.auth_id in self.auths:
            applied = AppliedEvent(
                source=event,
                accepted=False,
                error=f"duplicate auth_id {event.auth_id}",
                auth_status=AuthStatus.REJECTED,
            )
            self.log.append(applied)
            return applied

        # Available = ledger (as of booking/value day) − active holds.
        # Use booking_day / value_date for ledger as-of (holds are live now).
        as_of = max(event.booking_day, event.value_date)
        ledger = self.ledger_balance(event.account_id, as_of)
        available_minor = ledger.minor - self.active_holds_minor(event.account_id)
        hold = event.amount.minor
        if available_minor - hold < 0:
            applied = AppliedEvent(
                source=event,
                accepted=False,
                error=(
                    f"insufficient available balance for {event.auth_id}: "
                    f"available={available_minor} hold={hold}"
                ),
                auth_status=AuthStatus.REJECTED,
            )
            self.auths[event.auth_id] = AuthRecord(
                auth_id=event.auth_id,
                account_id=event.account_id,
                hold_minor=hold,
                status=AuthStatus.REJECTED,
                booking_day=event.booking_day,
            )
            self.log.append(applied)
            return applied

        self.auths[event.auth_id] = AuthRecord(
            auth_id=event.auth_id,
            account_id=event.account_id,
            hold_minor=hold,
            status=AuthStatus.APPROVED,
            booking_day=event.booking_day,
        )
        applied = AppliedEvent(
            source=event,
            accepted=True,
            auth_status=AuthStatus.APPROVED,
        )
        self.log.append(applied)
        return applied

    def _apply_settlement(self, event: SourceEvent) -> AppliedEvent:
        if event.auth_id is None or event.amount is None:
            applied = AppliedEvent(
                source=event,
                accepted=False,
                error="settlement missing auth_id or amount",
            )
            self.log.append(applied)
            return applied
        rec = self.auths.get(event.auth_id)
        if rec is None or rec.status != AuthStatus.APPROVED:
            applied = AppliedEvent(
                source=event,
                accepted=False,
                error=(
                    f"settlement references unknown or inactive auth_id "
                    f"{event.auth_id}"
                ),
            )
            self.log.append(applied)
            return applied
        if rec.account_id != event.account_id:
            applied = AppliedEvent(
                source=event,
                accepted=False,
                error=f"auth {event.auth_id} belongs to another account",
            )
            self.log.append(applied)
            return applied
        acct = self.accounts[event.account_id]
        if event.amount.currency != acct.currency:
            applied = AppliedEvent(
                source=event,
                accepted=False,
                error=f"currency mismatch: account {acct.currency}",
            )
            self.log.append(applied)
            return applied

        # Capture for settlement amount; release full hold (settle-for-less).
        signed = -event.amount.minor
        self.postings.append(
            (
                event.account_id,
                event.value_date,
                signed,
                event.event_id,
                EventType.SETTLEMENT.value,
            )
        )
        # Mutating AuthRecord status would violate frozen-source spirit for the
        # auth *event*, but AuthRecord is derived state. Replace the record.
        self.auths[event.auth_id] = AuthRecord(
            auth_id=rec.auth_id,
            account_id=rec.account_id,
            hold_minor=rec.hold_minor,
            status=AuthStatus.SETTLED,
            booking_day=rec.booking_day,
        )
        applied = AppliedEvent(
            source=event,
            accepted=True,
            auth_status=AuthStatus.SETTLED,
            posting_minors=(signed,),
        )
        self.log.append(applied)
        return applied

    def _apply_reversal(self, event: SourceEvent) -> AppliedEvent:
        target_id = event.reverses_event_id
        if not target_id:
            applied = AppliedEvent(
                source=event, accepted=False, error="reversal missing target"
            )
            self.log.append(applied)
            return applied
        # Find accepted posting lines from the target event.
        target_lines = [
            p for p in self.postings if p[3] == target_id
        ]
        if not target_lines:
            applied = AppliedEvent(
                source=event,
                accepted=False,
                error=f"reversal target {target_id} not found or not posted",
            )
            self.log.append(applied)
            return applied
        # Already reversed?
        already = any(
            a.source.event_type == EventType.REVERSAL
            and a.source.reverses_event_id == target_id
            and a.accepted
            for a in self.log
        )
        if already:
            applied = AppliedEvent(
                source=event,
                accepted=False,
                error=f"target {target_id} already reversed",
            )
            self.log.append(applied)
            return applied

        signed_minors: list[int] = []
        for aid, _vdate, minor, _eid, _kind in target_lines:
            # Compensating opposite; value_date from the reversal event
            # (E9 uses value_date Day 2, same as E7).
            opp = -minor
            self.postings.append(
                (aid, event.value_date, opp, event.event_id, EventType.REVERSAL.value)
            )
            signed_minors.append(opp)
        applied = AppliedEvent(
            source=event,
            accepted=True,
            posting_minors=tuple(signed_minors),
        )
        self.log.append(applied)
        return applied

    def active_holds_minor(self, account_id: str) -> int:
        total = 0
        for rec in self.auths.values():
            if rec.account_id == account_id and rec.status == AuthStatus.APPROVED:
                total += rec.hold_minor
        return total

    def _fee_horizon(self) -> int:
        """Assess fees only through the latest booking day seen in the log."""
        if not self.log:
            return 0
        return max(a.source.booking_day for a in self.log)

    def _restate_fees(self) -> None:
        """Recompute derived overdraft fees from the current source-posting prefix."""
        self.fee_postings.clear()
        horizon = self._fee_horizon()
        if horizon <= 0:
            return
        for day in range(1, horizon + 1):
            for aid, acct in self.accounts.items():
                fee_amt = OVERDRAFT_FEE_MINOR.get(acct.currency)
                if fee_amt is None:
                    continue
                pre = self.pre_fee_closing(aid, day).minor
                if pre < 0:
                    self.fee_postings.append((aid, day, -fee_amt))

    def source_balance(self, account_id: str, as_of_day: int) -> Money:
        """Sum of source postings only (no derived fees)."""
        ccy = self.accounts[account_id].currency
        total = 0
        for aid, vdate, minor, _eid, _kind in self.postings:
            if aid == account_id and vdate <= as_of_day:
                total += minor
        return Money(ccy, total)

    def pre_fee_closing(self, account_id: str, as_of_day: int) -> Money:
        """Closing before that day's own fee: source + prior-day fees."""
        ccy = self.accounts[account_id].currency
        total = self.source_balance(account_id, as_of_day).minor
        for aid, vdate, minor in self.fee_postings:
            if aid == account_id and vdate < as_of_day:
                total += minor
        return Money(ccy, total)

    def available_balance(self, account_id: str, as_of_day: int) -> Money:
        ccy = self.accounts[account_id].currency
        ledger = self.ledger_balance(account_id, as_of_day)
        return Money(ccy, ledger.minor - self.active_holds_minor(account_id))

    def ledger_balance(self, account_id: str, as_of_day: int) -> Money:
        """Post-fee closing: source + all fees with value_date <= as_of_day."""
        ccy = self.accounts[account_id].currency
        total = self.source_balance(account_id, as_of_day).minor
        for aid, vdate, minor in self.fee_postings:
            if aid == account_id and vdate <= as_of_day:
                total += minor
        return Money(ccy, total)

    def fees_on_day(self, account_id: str, day: int) -> list[Money]:
        ccy = self.accounts[account_id].currency
        return [
            Money(ccy, -minor)  # report as positive fee amount assessed
            for aid, vdate, minor in self.fee_postings
            if aid == account_id and vdate == day
        ]

    def report_days(self, through_day: int = 6) -> list[DayReport]:
        reports: list[DayReport] = []
        for day in range(1, through_day + 1):
            closings = {
                aid: self.ledger_balance(aid, day) for aid in self.accounts
            }
            fees = {
                aid: self.fees_on_day(aid, day) for aid in self.accounts
            }
            auth_lines: list[str] = []
            for auth_id, rec in self.auths.items():
                if rec.booking_day <= day:
                    auth_lines.append(f"{auth_id} {rec.status.value}")
            reports.append(
                DayReport(
                    day=day,
                    closings=closings,
                    fees=fees,
                    auths=auth_lines,
                    errors=[],
                )
            )
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

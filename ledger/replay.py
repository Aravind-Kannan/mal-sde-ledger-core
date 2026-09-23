"""Replay event stream and print per-day report."""

from __future__ import annotations

from ledger.engine import Ledger, format_report
from ledger.stream import full_stream


def run(stream=None, through_day: int = 6) -> str:
    events = list(stream) if stream is not None else full_stream()
    ledger = Ledger()
    for ev in events:
        ledger.apply(ev)
    text = format_report(ledger.report_days(through_day))
    # Append interest accrual summary for Day 6 capitalization visibility.
    lines = [text.rstrip(), "=== Interest accruals (Days 1–6) ==="]
    for aid in sorted(ledger.interest_accruals):
        accruals = ledger.interest_accruals[aid]
        capital = sum(
            m for a, d, m in ledger.interest_postings if a == aid
        )
        ccy = ledger.accounts[aid].currency
        lines.append(
            f"  {aid}: daily={accruals} capital_minor={capital} ({ccy})"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    print(run())


if __name__ == "__main__":
    main()

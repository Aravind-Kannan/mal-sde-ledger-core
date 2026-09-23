"""Replay event stream and print per-day report."""

from __future__ import annotations

from ledger.engine import Ledger, format_report
from ledger.stream import phase2_stream


def run(stream=None, through_day: int = 6) -> str:
    events = list(stream) if stream is not None else phase2_stream()
    ledger = Ledger()
    for ev in events:
        ledger.apply(ev)
    return format_report(ledger.report_days(through_day))


def main() -> None:
    print(run())


if __name__ == "__main__":
    main()

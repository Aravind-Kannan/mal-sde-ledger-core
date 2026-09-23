# REJECTED

## Acceptance criteria refused

### 1. "E7 causes exactly one overdraft fee to be assessed, on Day 2."

Refused. With derived fee restatement over the live E7 window (E1–E8), pre-fee closings are negative on Day 2 (−370.00), Day 4 (−180.00 after Day 2's fee and the Day 4 settlement), and Day 5 (−205.00). That is three overdraft fees (AED 25.00 each), not one. A sequential calendar-only model that books fees only on the booking day of E7 would assess a fee on Day 5, never on Day 2 — also contradicting "exactly one … on Day 2". Either honest reading refuses the criterion.

### Approaches abandoned mid-build

- Sticky fee rows appended into the source log: cannot disappear when E9 reverses E7 without mutating/deleting records. Fees are a derived projection restated from the source prefix instead.
- Sequential day-end fees without value_date restatement: would miss the Day 2 fee that the −370 criterion implies.

# REJECTED

## Acceptance criteria refused

### 1. "E7 causes exactly one overdraft fee to be assessed, on Day 2."

Refused. With derived fee restatement over the live E7 window (E1–E8), pre-fee closings are negative on Day 2 (−370.00), Day 4 (−180.00 after Day 2's fee and the Day 4 settlement), and Day 5 (−205.00). That is three overdraft fees (AED 25.00 each), not one. A sequential calendar-only model that books fees only on the booking day of E7 would assess a fee on Day 5, never on Day 2 — also contradicting "exactly one … on Day 2". Either honest reading refuses the criterion.

### 2. "The three BHD instalments in E10 must each be BHD 3.334."

Refused. `3 × 3.334 = 10.002 ≠ 10.000`. That breaks conservation of the credited BHD 10.000 and invents an extra 0.002. Largest-remainder split yields **3.333 + 3.333 + 3.334**.

### 3. "If the rounded daily interest accruals do not sum to the capitalized total, the remainder is discarded."

Refused. The non-negotiable rule requires rounded daily accruals to sum exactly to the capitalized total. Capital = ROUND_HALF_UP(sum of exact daily raws); any penny gap is applied to the last positive-balance day. Remainder is never discarded.

### Approaches abandoned mid-build

- IEEE floats for money: non-decimal binary rounding lies for AED/BHD.
- Sticky fee rows appended into the source log: cannot disappear when E9 reverses E7 without mutating/deleting records. Fees are a derived projection restated from the source prefix instead.
- Sequential day-end fees without value_date restatement: would miss the Day 2 fee that the −370 criterion implies.
- Equal 3×3.334 instalments: fails conservation.
- Discarding interest remainder: contradicts the sum-exactly rule.
- Mutating or deleting E7 on reversal: violates append-only.
- ISO 20022 XML amount types: no payments network in scope; overkill for an in-memory core.

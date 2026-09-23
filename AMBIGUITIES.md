# AMBIGUITIES

## Phase 2 — booking day vs value_date

E7 is booked on Day 5 with value_date Day 2. Resolution: ledger closing for day D sums every accepted posting whose value_date ≤ D, regardless of booking day. Stream order is still causal for apply; as-of queries read value_date.

## Phase 2 — "end of Day 5" for the −370 criterion

Criterion says Day 2 closing evaluated at end of Day 5 before fees. Resolution: evaluate after the stream prefix that ends with E7 (E1, E2, E7 in Phase 2). Later phases insert E3–E6 before E7; those change Day 3+ balances but not Day 2's −370 pre-fee figure from E1+E2+E7 alone (E4/E5 have value_dates ≥ 3).

## Phase 3 — available balance as-of day for auth

Authorization checks available = ledger(as_of) − active holds. Resolution: as_of = max(booking_day, value_date) of the authorization event. Auth-A on Day 2 sees ledger 250.00.

## Phase 4 — settle for less than hold

Auth-A hold is AED 200.00, settlement E5 captures AED 185.00. Resolution: debit the capture amount, mark auth SETTLED, release the full hold (remainder 15.00 does not stay held and is not separately posted).

## Phase 5 — reversal

E9 reverses E7. Resolution: append a compensating opposite posting with the same value_date as the reversal event (Day 2). E7 stays in the log; never mutated or deleted.

## Phase 6 — sticky vs restated authorization

After E7, Auth-B is declined (available negative). E9 restores the ledger. Resolution: auth decisions are sticky at apply time; E9 does not rewrite E8. Documented by the intentionally failing tests/test_known_gap.py.

## Phase 7 — overdraft fees derived, not sourced

Fees are recomputed after every apply from source postings. Pre-fee close for day D = source postings with value_date ≤ D plus fees with value_date < D. Fee horizon = max booking_day in the log (so Day 6 is not assessed until a Day-6 booking exists). Abandoned: sticky fee rows; calendar-only fees without restatement (see REJECTED.md).

## Phase 8 — interest order and capitalization

Daily interest uses post-fee closing before the Day-6 capital credit (no same-day compound). Capital = ROUND_HALF_UP(sum of exact daily raws); last positive day absorbs penny drift so sum(rounded) == capital.

## Phase 8 — E10 stream order vs value_date

E10 is listed after E9 but has booking_day/value_date Day 5. Resolution: apply in stream order; balances use value_date. ACC-002 interest on Days 5–6 sees the BHD 10.000 credit.

## Phase 8 — instalment split

E10 is three equal instalments of BHD 10.000. Resolution: largest-remainder on integer minor units → 3333, 3333, 3334 fils. Not 3×3334.

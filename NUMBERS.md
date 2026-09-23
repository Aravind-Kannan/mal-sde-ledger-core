# NUMBERS

Constants chosen so far. Why this value and not half of it.

| Constant | Value | Why not half |
|----------|-------|--------------|
| AED ISO 4217 exponent | 2 | ISO 4217 Table A.1; half (1) would invent a non-fils scale. |
| BHD ISO 4217 exponent | 3 | ISO 4217 Table A.1; half is not an integer exponent. |
| Overdraft fee | AED 25.00 (2500 minor) | Spec states 25.00; 12.50 is not in the rules. |
| Fee assessment | Once per account per day when pre-fee close < 0 | Spec; half-day assessment is undefined. |
| Fee currencies | AED only | Spec names AED 25.00; inventing BHD 12.500 would be half-baked. |
| Fee horizon | Latest booking_day in the log | Assessing Day 6 before any Day-6 booking invents a fee the stream has not reached. |
| Interest rate | 0.04%/day = 4/10_000 | Spec; 0.02% is not authorized. |
| Interest rounding | ROUND_HALF_UP to currency minor units | Banker's rounding would diverge from the common commercial default; half-up matches the "sum exactly" requirement when paired with last-day adjust. |
| Interest capital day | Day 6 only | Spec; capitalizing daily would change the single-credit rule. |
| Window | Days 1..6 | Spec; a 3-day window drops E9/E10. |
| Instalment count (E10) | 3 | Spec; 1 or 2 would not exercise remainder distribution. |
| Instalment split | 3333 + 3333 + 3334 BHD fils | Conserves 10.000; 3×3334 overshoots by 2 fils. |

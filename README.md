# Phase 1–8 — in-memory append-only account ledger

Python 3.13+ (repo pins `.python-version`). Amounts are ISO 4217 alpha codes with integer minor units — never float. AED exponent 2, BHD exponent 3.

No web layer, no persistence, no UI, no database.

## Setup

```bash
python -m pip install -r requirements.txt --target .deps
```

## Run

```bash
PYTHONPATH=".deps:." python -m pytest -q --ignore=tests/test_known_gap.py
PYTHONPATH=".deps:." python -m ledger.replay
```

Full suite including the intentional failure:

```bash
PYTHONPATH=".deps:." python -m pytest -q
```

## Read the output

Each day block shows:

- **closing** — post-fee ledger balance (Day 6 also includes interest capitalization)
- **fees** — overdraft fee assessments booked that day (AED 25.00 when pre-fee close < 0)
- **auths** — sticky authorization outcomes visible from their booking day
- **errors** — rejected events (e.g. Auth-Z settlement, Auth-B denial)

After the day blocks, a summary lists daily interest accruals and the Day-6 capital credit per account. Rounded daily accruals sum exactly to that capital.

Default stream is E1–E10 (full).

## Known failing test

`tests/test_known_gap.py` is expected to fail. It asks whether Auth-B would be approved if decisions were restated after E9; our design keeps sticky denials. See AMBIGUITIES.md and REJECTED.md.

## Docs

- `NUMBERS.md` — every constant and why not half of it
- `AMBIGUITIES.md` — ambiguities found and how resolved
- `REJECTED.md` — refused acceptance criteria and abandoned approaches
- `WORKLOG.md` — timestamped build notes

# mal-sde-ledger-core

In-memory, append-only account ledger core. No web layer, no persistence, no UI, no database.

Python 3.13+ (pinned in `.python-version`). Amounts use ISO 4217 alpha codes with integer minor units — never float. AED exponent 2, BHD exponent 3.

## Clone

```bash
git clone <repo-url> mal-sde-ledger-core
cd mal-sde-ledger-core
```

## Setup

```bash
python -m pip install -r requirements.txt --target .deps
```

## Run

Tests (skip the intentional failure):

```bash
PYTHONPATH=".deps:." python -m pytest -q --ignore=tests/test_known_gap.py
```

Replay the default E1–E10 stream and print the six-day report:

```bash
PYTHONPATH=".deps:." python -m ledger.replay
```

Full suite including the known failing test:

```bash
PYTHONPATH=".deps:." python -m pytest -q
```

## Report output

Each day block shows:

- **closing** — post-fee ledger balance (Day 6 also includes interest capitalization)
- **fees** — overdraft fee assessments booked that day (AED 25.00 when pre-fee close < 0)
- **auths** — sticky authorization outcomes visible from their booking day
- **errors** — rejected events (e.g. Auth-Z settlement, Auth-B denial)

After the day blocks, a summary lists daily interest accruals and the Day-6 capital credit per account. Rounded daily accruals sum exactly to that capital.

## Layout

```
ledger/          # money, events, engine, stream, replay
tests/           # phase suites + known-gap intentional fail
NUMBERS.md       # constants and why not half of each
AMBIGUITIES.md   # ambiguities found and how resolved
REJECTED.md      # refused acceptance criteria / abandoned approaches
WORKLOG.md       # timestamped build notes
```

## Known failing test

`tests/test_known_gap.py` is expected to fail. It asks whether Auth-B would be approved if decisions were restated after E9; this design keeps sticky denials. See `AMBIGUITIES.md` and `REJECTED.md`.

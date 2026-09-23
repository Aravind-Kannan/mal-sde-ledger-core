# Phase 1 — MVP: ISO 4217 money + CREDIT/DEBIT

Python 3.13+ (repo pins `.python-version`). Amounts are ISO 4217 alpha codes with integer minor units — never float.

## Setup

```bash
python -m pip install -r requirements.txt --target .deps
```

## Run

```bash
PYTHONPATH=".deps:." python -m pytest -q
PYTHONPATH=".deps:." python -m ledger.replay
```

## Read the output

Each day block shows:

- closing ledger balance per account
- fee assessments (none until overdraft fees land)
- authorization states (none until holds land)
- errors (none until settlements/rejects land)

Phase 1 stream is E1–E2 only. Day 1 ACC-001 closing is AED 250.00.

Phase 2 adds E7 (debit booked Day 5, value_date Day 2). Day 2 closing becomes AED −370.00. See AMBIGUITIES.md.

## Known failing test

`tests/test_known_gap.py` is expected to fail. It asks whether Auth-B would be approved if decisions were restated after E9; our design keeps sticky denials. Run `PYTHONPATH=".deps:." python -m pytest -q` — suite otherwise green; that one fail is intentional. Use `-rs` to see the skip/fail notes.

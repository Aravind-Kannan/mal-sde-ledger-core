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

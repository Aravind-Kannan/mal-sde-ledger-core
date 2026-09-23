# WORKLOG

## 2026-09-23 09:32 +0530

Phase 1 start. Empty repo on master, no commits yet. Chose Python 3 + ISO 4217 integer minor units (AED exp 2, BHD exp 3). Building CREDIT/DEBIT MVP with E1–E2 only.

## 2026-09-23 09:33 +0530

Scaffolded ledger/money.py, events.py, engine.py, stream.py, replay.py, tests/test_phase1_postings.py, README. Next: run pytest, then first commit if author email gate passes.

## 2026-09-23 09:35 +0530

Phase 1 green: 4 passed. Replay prints ACC-001 Day 1 closing AED 250.00. Global pyenv default was 2.7; pinned `.python-version` to 3.13.1 and installed pytest into `.deps` (gitignored). Author email gate: aravindkannan2001@gmail.com. Committing Phase 1.

## 2026-09-23 09:36 +0530

Phase 2: value_date as-of closes. Stream E1,E2,E7. Day 2 pre-fee close AED −370.00. Documented booking vs value_date in AMBIGUITIES.md.

## 2026-09-23 09:37 +0530

Phase 3: AUTHORIZATION. Auth-A approved; ledger 250.00, available 50.00. Hold does not touch ledger balance.

## 2026-09-23 09:38 +0530

Phase 4: SETTLEMENT. Auth-A settles for 185 → ledger 465.00. Auth-Z unknown → rejected, no debit.

## 2026-09-23 09:39 +0530

Phase 5: REVERSAL. E9 compensates E7 at value_date Day 2. Snapshot after E9 matches pre-E7 (465.00).

# Migration Status

**Date:** 2026-01-10
**Status:** Awaiting decision (A/B/C/D)
**Owner:** Agent 9 (Governance)

---

## Purpose

Single source of truth for migration readiness, issues, and progress.
Update after each phase or batch.

---

## Current Assets (Ready)

- `FULL-MIGRATION-EXECUTION-PLAN.md` (overall plan)
- `MIGRATION-TASKS.md` (step-by-step tasks + validations)
- Phase docs: `PHASE-0` through `PHASE-8`
- Support: `MIGRATION-SCRIPTS.md`, `LINK-MAP.md`, `ROLLBACK-PROCEDURES.md`
- Governance rules: `FOLDER_STRUCTURE_GOVERNANCE.md`

---

## Decision Gate (Must be green before Phase A0)

- [ ] Option selected in `DECISION-SUMMARY.md`
- [ ] Freeze window announced
- [ ] No open PRs touching `docs/` or `agents/`
- [ ] Branch is not `main` (run `./scripts/check_not_main.sh`)

---

## Readiness Checklist (Phase A0)

- [ ] Baseline metrics captured (`./scripts/collect_metrics.sh`)
- [ ] Dashboard updated (`./scripts/generate_dashboard.sh`)
- [ ] Indexes generated (`./scripts/generate_all_indexes.sh`)
- [ ] Root file count check passes (`./scripts/check_root_file_count.sh`)
- [ ] Folder structure validation passes (`python scripts/validate_folder_structure.py`)
- [ ] Link checks pass (`./scripts/check_links.py`)

---

## Metrics Snapshot (Fill after A0 and A6)

- Root file count: ____
- Validation errors: ____
- Broken link count: ____
- Docs index link errors: ____

---

## Issue Log (Append Only)

Use the template from `MIGRATION-TASKS.md` for each issue.

---

## Next Step

1. Record decision in `DECISION-SUMMARY.md`.
2. Execute Phase A0 from `MIGRATION-TASKS.md`.
3. Log results and issues here.

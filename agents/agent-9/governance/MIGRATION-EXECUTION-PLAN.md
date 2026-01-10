# Migration Execution Plan (Option A - Modified Hybrid)

**Owner:** Agent 9 (Governance)
**Status:** Active plan
**Purpose:** Single entry point that ties decision, tasks, and status together.

---

## Start Here

- Decision: `DECISION-SUMMARY.md`
- Task plan: `MIGRATION-TASKS.md`
- Live status + issues: `MIGRATION-STATUS.md`

---

## Review Notes (Current)

- Root file count is 11 (target 10) per `./scripts/check_root_file_count.sh`.
- Validation errors baseline captured in `MIGRATION-STATUS.md`.
- Agent 8 Git Workflow docs must be moved first in Phase A2.

---

## Execution Order (Option A)

1. Phase A0 - Prep + Baseline
2. Phase A1 - Critical Structure
3. Phase A2 - High-Value Doc Moves (Agent 8 docs first)
4. Phase A3 - Dated Files + Archival
5. Phase A4 - Naming Cleanup (small batches)
6. Phase A5 - Link + Script Integrity
7. Phase A6 - Final Validation + Report

---

## Agent 8 Priority (Must Happen First in A2)

Move the Agent 8 Git Workflow docs before any other doc moves so every agent has
an authoritative, stable place to find the git protocol.

Targets are defined in `MIGRATION-TASKS.md` under Phase A2.

---

## Stop Conditions

Pause the migration if any of these occur:

- `./scripts/check_links.py` fails
- `python scripts/validate_folder_structure.py` fails
- Root file count exceeds limit and cannot be resolved in current batch
- Link map chain detected (see `MIGRATION-TASKS.md` chain check)

---

## Output Artifacts (Required)

- `MIGRATION-STATUS.md` updated after every phase or batch
- `LINK-MAP.md` updated after each move batch
- Baseline + final metrics saved under `metrics/`

---

## Notes

This doc is intentionally short. All detailed steps live in:
`MIGRATION-TASKS.md` and the phase documents.

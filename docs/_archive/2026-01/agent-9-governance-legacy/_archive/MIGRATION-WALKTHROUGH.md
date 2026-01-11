# Migration Walkthrough (Operator Runbook)

**Audience:** Operator running the migration in a live session
**Goal:** Execute Option A safely, with minimal decisions in the moment.

---

## 0) Pre-Flight (5-10 min)

1. Confirm you are not on `main`:
   - `./scripts/check_not_main.sh`
2. Confirm clean git state:
   - `./scripts/check_unfinished_merge.sh`
   - `./scripts/validate_git_state.sh`
3. Open the status tracker:
   - `agents/agent-9/governance/MIGRATION-STATUS.md`

---

## 1) Phase A0 - Prep + Baseline (2-4h)

Follow `MIGRATION-TASKS.md` (Phase A0).
After completion, update `MIGRATION-STATUS.md` with:

- Root file count
- Validation errors
- Broken link count
- Docs index link errors

---

## 2) Phase A1 - Critical Structure (4-6h)

Follow `MIGRATION-TASKS.md` (Phase A1).
Required output: all target folders + READMEs.

Run the standard validation bundle after each micro-step:

```
./scripts/check_links.py
./scripts/check_docs_index.py
./scripts/check_docs_index_links.py
python scripts/validate_folder_structure.py
./scripts/check_root_file_count.sh
```

Log any failures immediately in `MIGRATION-STATUS.md`.

---

## 3) Phase A2 - High-Value Doc Moves (3-5h)

Priority order:
1. Move Agent 8 Git Workflow docs first (see `MIGRATION-TASKS.md`).
2. Then move 7-12 other low-risk docs.

After each move batch:
- Update `LINK-MAP.md`
- Run the validation bundle
- Log issues in `MIGRATION-STATUS.md`

---

## 4) Phase A3 - Dated Files + Archival (1-2h)

Run in dry-run mode first:

```
DRY_RUN=1 ./scripts/archive_old_sessions.sh
```

Then execute and re-run validation bundle.

---

## 5) Phase A4 - Naming Cleanup (2-3h spread)

Rename 5-10 files per batch.
Always run the chain-link check from `MIGRATION-TASKS.md`.

---

## 6) Phase A5 - Link + Script Integrity (2-3h)

Search for hardcoded paths and fix them:

```
rg -n "docs/governance|docs/planning|docs/research|agents/" scripts docs
```

Re-run validation bundle.

---

## 7) Phase A6 - Final Validation (1-2h)

Run full validation and update `MIGRATION-STATUS.md`:

- Final root file count
- Final validation error count
- Link check status

Capture a final metrics snapshot in `metrics/`.

---

## Exit Criteria

- All validation checks pass (or are documented with actionable fixes)
- Root file count within limit
- `MIGRATION-STATUS.md` updated

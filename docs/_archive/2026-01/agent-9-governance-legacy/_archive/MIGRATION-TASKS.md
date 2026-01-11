# Migration Task Plan (Option A - Modified Hybrid)
**Owner:** Agent 9 (Governance)
**Use Case:** Step-by-step execution checklist for junior-safe migration
**Status:** Ready to execute after decision

---

## Overview

Option A splits migration into small, low-risk batches with validation after every batch.

**Goal:** Reduce validation errors and improve navigation without blocking feature work.
**Rule:** No batch proceeds until validation passes and issues are logged.

---

## Task Map (Option A)

| Phase | Task | Primary Output | Required Validation |
| --- | --- | --- | --- |
| A0 | Prep + Baseline | Baseline metrics + indexes | root count, folder structure, links |
| A1 | Critical Structure | Required folders + READMEs | folder structure, docs index |
| A2 | High-Value Doc Moves | 10-15 doc moves + link map | links, docs index, structure |
| A3 | Dated Files | Archived dated docs | links, structure |
| A4 | Naming Cleanup | Kebab-case batches | links, structure, chain link check |
| A5 | Link + Script Integrity | Updated refs in scripts/docs | links, structure, root count |
| A6 | Final Validation | Clean status report | full validation bundle |

---

## Standard Validation Bundle (Run After Each Batch)

- `./scripts/check_links.py`
- `./scripts/check_docs_index.py`
- `./scripts/check_docs_index_links.py`
- `python scripts/validate_folder_structure.py`
- `./scripts/check_root_file_count.sh`

**When to stop:** Any failure means the batch is paused until resolved and logged.

---

## Phase A0: Prep + Baseline (2-4h)

### TASK-A0.1 — Freeze Window + Baseline Snapshot
**Goal:** Establish reliable before-metrics and a clean start.

**Steps**
1. Confirm no open PRs touching docs/ or agents/.
2. Confirm safe git state:
   - `./scripts/check_not_main.sh`
   - `./scripts/check_unfinished_merge.sh`
   - `./scripts/validate_git_state.sh`
3. Create backup tag: `git tag backup-pre-migration-YYYY-MM-DD`
4. Run baseline metrics:
   - `./scripts/collect_metrics.sh`
   - `./scripts/generate_dashboard.sh`
5. Generate initial indexes (for navigation study):
   - `./scripts/generate_all_indexes.sh`

**Validation / Tests**
- `./scripts/check_root_file_count.sh`
- `python scripts/validate_folder_structure.py`
- `./scripts/check_links.py`

**Issue Capture**
- Log any failing checks in `MIGRATION-STATUS.md`
- Record broken links count + root file count

---

## Phase A1: Critical Structure (4-6h)

### TASK-A1.1 — Core Structure Confirmation
**Goal:** Ensure required folders exist with readmes.

**Steps**
1. Confirm folders exist:
   - `docs/getting-started/`, `docs/reference/`, `docs/contributing/`, `docs/architecture/`
   - `docs/_active/`, `docs/_archive/`
   - `agents/agent-9/governance/`
2. Confirm each has `README.md`.
3. Regenerate indexes after confirmation:
   - `python scripts/generate_folder_index.py docs`
   - `python scripts/generate_folder_index.py docs/reference`
   - `python scripts/generate_folder_index.py docs/contributing`
   - `python scripts/generate_folder_index.py agents`
   - `python scripts/generate_folder_index.py agents/agent-9/governance`

**Validation / Tests**
- `python scripts/validate_folder_structure.py`
- `./scripts/check_docs_index.py`
- `./scripts/check_docs_index_links.py`

**Issue Capture**
- Missing folders or missing README → add to `MIGRATION-STATUS.md`

---

## Phase A2: High-Value Doc Moves (3-5h)

### TASK-A2.1 — Move Priority Docs (Small Batch)
**Goal:** Move a small, high-value batch into correct Diataxis locations.

**Steps**
1. Move Agent 8 Git Workflow docs first (priority for all agents):
   - `docs/planning/agent-8-tasks-git-ops.md` → `docs/agents/guides/agent-8-git-ops.md`
   - `docs/planning/agent-8-implementation-guide.md` → `docs/agents/guides/agent-8-implementation-guide.md`
   - `docs/planning/agent-8-mistakes-prevention-guide.md` → `docs/agents/guides/agent-8-mistakes-prevention-guide.md`
2. Select 7-12 additional docs to move (start with low-risk docs).
3. Update references in README files, `docs/reference/agent-automation-pitfalls.md`,
   and any agent docs that cite the old paths.
4. Update `LINK-MAP.md` with old → new path.

**Validation / Tests**
- `./scripts/check_links.py`
- `./scripts/check_docs_index.py`
- `./scripts/check_docs_index_links.py`
- `python scripts/validate_folder_structure.py`

**Issue Capture**
- Broken links (count + list)
- Missing references in docs index
- Any CI failures

---

## Phase A3: Dated Files + Archival (1-2h)

### TASK-A3.1 — Archive Dated Files Safely
**Goal:** Remove dated files from active folders and place into `_archive/YYYY-MM/`.

**Steps**
1. Dry run: `DRY_RUN=1 ./scripts/archive_old_sessions.sh`
2. Execute: `./scripts/archive_old_sessions.sh`
3. Update `docs/_archive/README.md` if needed.

**Validation / Tests**
- `./scripts/check_links.py`
- `python scripts/validate_folder_structure.py`
- `./scripts/check_docs_index_links.py`

**Issue Capture**
- Unexpected file removals
- Broken link count increase

---

## Phase A4: Naming Cleanup (2-3h spread)

### TASK-A4.1 — Rename Small Batches
**Goal:** Reduce naming violations without breaking links.

**Steps**
1. Rename 5-10 files per batch (kebab-case).
2. Update `LINK-MAP.md`.
3. Update references immediately.

**Validation / Tests**
- `./scripts/check_links.py`
- `python scripts/validate_folder_structure.py`

**Chain Link Check (Critical)**
Avoid chained mappings (A → B → C).
Run:
```
awk '{print $1}' agents/agent-9/governance/LINK-MAP.md | sort -u > /tmp/old.txt
awk '{print $3}' agents/agent-9/governance/LINK-MAP.md | sort -u > /tmp/new.txt
comm -12 /tmp/old.txt /tmp/new.txt
```
If output is non-empty, fix LINK-MAP so every old path maps directly to final path.

---

## Phase A5: Link + Script Integrity (2-3h)

### TASK-A5.1 — Hardcoded Path Audit
**Goal:** Ensure scripts and workflows point to new paths.

**Steps**
1. Search for old paths:
   - `rg -n "docs/governance|old-path|legacy-path"`
2. Update any hardcoded references in scripts or docs.

**Validation / Tests**
- `./scripts/check_links.py`
- `python scripts/validate_folder_structure.py`
- `./scripts/check_root_file_count.sh`
- `./scripts/check_docs_index_links.py`

---

## Phase A6: Final Validation (1-2h)

### TASK-A6.1 — Full Validation + Report
**Goal:** Confirm structure + links + governance checks are clean.

**Steps**
1. Run all validations:
   - `python scripts/validate_folder_structure.py`
   - `./scripts/check_root_file_count.sh`
   - `./scripts/check_links.py`
2. Update `MIGRATION-STATUS.md` with results.

**Success Criteria**
- Root file count within limit
- Validation errors reduced vs baseline
- Links pass or documented with actionable fixes

---

## Issue Capture Checklist (Use every phase)

- [ ] Broken links found (count + list)
- [ ] Chain link detected in LINK-MAP (old path appears as new path)
- [ ] Missing README in required folder
- [ ] Index out of date (missing `index.json`/`index.md`)
- [ ] Root file count exceeded
- [ ] CI check failures (name + URL)
- [ ] Scripts or workflows referencing old paths
 - [ ] Docs index links invalid (index.md points to missing file)
 - [ ] Duplicate filenames introduced (same basename in multiple folders)
 - [ ] Path length or character violations (non-kebab case or uppercase)

---

## Issue Capture Template (Paste into MIGRATION-STATUS.md)

```
### Issue: <short title>
- Phase: A?
- Triggering check: <command + output summary>
- Impact: <broken links count / validation errors / scope>
- Root cause: <why>
- Fix applied: <what changed>
- Follow-up: <next validation to re-run>
```

---

## Required Logs/Artifacts

- `agents/agent-9/governance/MIGRATION-STATUS.md` updated each phase
- `agents/agent-9/governance/LINK-MAP.md` updated per move batch
- Metrics snapshot in `metrics/` after Phase A0 and Phase A6

# Agent 9 Phase B - Task Tracker

**Owner:** Agent 9 (Governance)
**Created:** 2026-01-10
**Status:** Active
**Source:** AGENT-9-GOVERNANCE-ROADMAP.md (research from other agent)

---

## Quick Status

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| Validation errors | 0 | 0 | ✅ |
| Validation warnings | 0 | 0 | ✅ |
| Broken links | 0 | 0 | ✅ |
| Root files | 10 | ≤10 | ✅ |
| docs/ root files | 3 | ≤5 | ✅ |
| Agent entry points | 2/3 | 3/3 | 🔄 |
| Agent registry | No | Yes | ❌ |

---

## Phase A Completion Summary (Done)

| Phase | Description | Result |
|-------|-------------|--------|
| A0 | Baseline metrics | 118 errors captured |
| A1 | Structure validation | Required folders created |
| A3 | Docs root cleanup | 47 → 3 files (94% reduction) |
| A4 | Naming cleanup | 76 files renamed to kebab-case |
| A5 | Link integrity | 130 → 0 broken links |
| A6 | Final validation | 17 → 0 warnings |

---

## Phase B Tasks (Execute in Order)

### B0: Merge Roadmap Branch ⏳
**Priority:** P0 (Blocker)
**Why:** Get roadmap into main as single source of truth

**Steps:**
1. [ ] Switch to main: `git switch main`
2. [ ] Merge branch: `git merge chore/agent-9-roadmap-update`
3. [ ] Push: `./scripts/safe_push.sh "Merge roadmap"`

**Validation:** `git log -1` shows merge commit
**Time:** 5 min

---

### B1: Agent 6 Entry Points 🔄
**Priority:** P1
**Why:** Streamlit agent needs same entry point pattern as Agent 8/9

**Steps:**
1. [ ] Create `docs/agents/guides/agent-6-quick-start.md`
2. [ ] Create `docs/agents/guides/agent-6-streamlit-hub.md`
3. [ ] Update `docs/agents/README.md` with Agent 6 section
4. [ ] Run link check

**Files to Create:**
```
docs/agents/guides/agent-6-quick-start.md     # 1-page entry
docs/agents/guides/agent-6-streamlit-hub.md   # Links to streamlit docs
```

**Validation:**
- `python scripts/check_links.py` → 0 broken
- `python scripts/check_docs_index_links.py` → PASS

**Time:** 30 min

---

### B2: Agent Registry + Index 📋
**Priority:** P1
**Why:** Structured index for all agents reduces search time

**Steps:**
1. [ ] Create `agents/index.md` with all agents listed
2. [ ] Generate `agents/index.json` (machine-readable)
3. [ ] Update `docs/agents/README.md` with registry section
4. [ ] Run index checks

**Registry Format:**
```markdown
| Agent | Role | Quick Start | Hub |
|-------|------|-------------|-----|
| 6 | Streamlit UI | agent-6-quick-start.md | agent-6-streamlit-hub.md |
| 8 | Git Operations | agent-8-quick-start.md | agent-8-git-ops.md |
| 9 | Governance | agent-9-quick-start.md | agent-9-governance-hub.md |
```

**Validation:**
- `python scripts/check_docs_index.py` → PASS

**Time:** 20 min

---

### B3: Archive Phase A Planning Docs 🗄️
**Priority:** P2
**Why:** Keep active folders clean, reduce noise

**Steps:**
1. [ ] Identify obsolete planning docs (Phase A0-A6 complete)
2. [ ] Create archive folder: `docs/_archive/2026-01-governance/`
3. [ ] Move with `git mv` to preserve history
4. [ ] Update any references
5. [ ] Run link check

**Candidates for Archive:**
- `agents/agent-9/governance/PHASE-*.md` (8 files)
- `agents/agent-9/governance/MIGRATION-EXECUTION-PLAN.md`
- `agents/agent-9/governance/FULL-MIGRATION-EXECUTION-PLAN.md`
- `agents/agent-9/governance/MIGRATION-WALKTHROUGH.md`

**Keep Active:**
- `MIGRATION-STATUS.md` (audit trail)
- `AUTOMATION-CATALOG.md` (ongoing reference)
- `FOLDER_STRUCTURE_GOVERNANCE.md` (rules)
- `README.md` (hub)

**Validation:**
- `python scripts/check_links.py` → 0 broken
- `python scripts/validate_folder_structure.py` → PASS

**Time:** 45 min

---

### B4: Navigation Study Re-run 📊
**Priority:** P3
**Why:** Measure improvement from clean structure

**Steps:**
1. [ ] Check if navigation scripts exist
2. [ ] Run baseline study
3. [ ] Document results in MIGRATION-STATUS.md
4. [ ] Compare to Phase A0 baseline

**Scripts Needed:**
- `scripts/measure_agent_navigation.sh` (if exists)
- `scripts/analyze_navigation_data.py` (if exists)

**Validation:** Metrics captured in MIGRATION-STATUS.md
**Time:** 30 min

---

### B5: Maintenance Automation 🔄
**Priority:** P2
**Why:** Sustainable governance without manual effort

**Steps:**
1. [ ] Create `scripts/weekly_governance_check.sh` (runs all validators)
2. [ ] Add to CI as scheduled job (optional)
3. [ ] Document in AUTOMATION-CATALOG.md

**Script Template:**
```bash
#!/bin/bash
# Weekly governance check
python scripts/validate_folder_structure.py
python scripts/check_links.py
./scripts/check_root_file_count.sh
echo "Weekly check complete"
```

**Validation:** Script runs without error
**Time:** 20 min

---

## Workflow for Each Task

```
1. Read task requirements
2. Check existing state (avoid duplicate work)
3. Create/modify files
4. Run validation checks
5. Commit with descriptive message
6. Update this tracker with results
7. Write summary for handoff
```

---

## Completed Tasks Log

### B0: Merge Roadmap Branch
- **Status:** Not started
- **Started:** -
- **Completed:** -
- **Commit:** -
- **Summary:** -

---

## Session Summaries

### Session 1 (2026-01-10)
- Created this task tracker
- Reviewed roadmap from other agent
- Identified 6 Phase B tasks
- Ready to execute B0-B5

---

## Notes

1. **Automation-first:** Every recurring task should have a script
2. **Small batches:** 5-10 files per commit max
3. **Validate always:** Run checks after every change
4. **Document progress:** Update this file after each task

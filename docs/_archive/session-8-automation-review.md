# Session 8: Automation Review & Phase 2/3 Preparation

> **Purpose:** Review Session 7 issues, audit automation, prepare for Phase 2/3
> **Created:** 2026-01-11 (Session 8)
> **Status:** 🔬 Planning Phase

---

## Session 7 Issues Review

### Issues Encountered

| # | Issue | Root Cause | Fix Applied | Long-term Solution |
|---|-------|------------|-------------|-------------------|
| 1 | **Commit blocker (PR required)** | `ai_commit.sh` detected mixed changes (scripts + docs) | Stash → Branch → Pop → Commit → PR | Document in workflow guide |
| 2 | **Leading Indicators CI failure** | `grep -c ... \|\| echo "0"` outputs both on failure | Changed to `$(grep) \|\| VAR="0"` | Fixed in `collect_metrics.sh` |
| 3 | **batch_archive.py missing --dest** | Script required destination for --files mode | Added helpful error message | Already handled |
| 4 | **external_data folder was untracked** | Original folder was never tracked in git | Script used `mv` instead of `git mv` | `rename_folder_safe.py` tries git mv first |

### Lessons Learned

1. **Stash before branch creation** - Required when `create_task_pr.sh` fails with uncommitted changes
2. **Test grep patterns carefully** - Exit code 1 with `|| echo` creates dual output
3. **Check git tracking status** - Untracked folders need `mv` not `git mv`
4. **Always dry-run first** - All file operation scripts support `--dry-run`

---

## Automation Audit

### ✅ File Operation Scripts (Ready for Phase 2/3)

| Script | Purpose | Phase 2 | Phase 3 | Notes |
|--------|---------|---------|---------|-------|
| `batch_archive.py` | Multi-file archival | ✅ | ✅ | New in Session 7 |
| `rename_folder_safe.py` | Folder rename with links | ✅ | ✅ | New in Session 7 |
| `safe_file_move.py` | Single file move | ✅ | ✅ | Works well |
| `safe_file_delete.py` | Safe deletion | ⚠️ | ✅ | Use sparingly |
| `find_orphan_files.py` | Find unreferenced docs | ✅ | ✅ | Core tool |
| `check_links.py` | Verify markdown links | ✅ | ✅ | Run after every change |
| `fix_broken_links.py` | Auto-fix broken links | ✅ | ✅ | Emergency recovery |

### 🔧 Scripts Needing Enhancement

| Script | Issue | Enhancement Needed | Priority |
|--------|-------|-------------------|----------|
| `batch_archive.py` | No date-based subfolder option | Add `--by-date` flag | LOW |
| `find_orphan_files.py` | Counts archive files as orphans | Option to exclude _archive | MEDIUM |
| `check_folder_readmes.py` | Lists optional folders | Add severity levels | LOW |

### 🆕 Scripts to Create

| Script | Purpose | Priority | Effort |
|--------|---------|----------|--------|
| `consolidate_research_docs.py` | Merge related research docs | LOW | 2h |
| `archive_old_planning.py` | Auto-archive planning docs >30 days | MEDIUM | 1h |
| `generate_archive_index.py` | Create index.md for archive folders | LOW | 30m |

---

## Phase 2: Docs Consolidation Plan

### Target: Reduce orphan count from 176 to <50

### 2.1 Planning Docs Cleanup (70 orphans)

**Strategy:** Archive completed task/session planning docs

```bash
# Find planning orphans older than 7 days
.venv/bin/python scripts/batch_archive.py \
  --pattern "docs/planning/agent-*.md" \
  --dest "docs/_archive/planning" --dry-run
```

**Files to Archive (by category):**

1. **Old Agent Task Docs (15 files)**
   - `agent-2-*.md` (2 files)
   - `agent-5-*.md` (already archived 4, check remaining)
   - `agent-6-*.md` (already archived 3, check remaining)
   - `agent-7-*.md`, `agent-8-*.md`

2. **Completed Session Handoffs (10 files)**
   - `session-2026-01-*.md` files
   - `*-handoff*.md` files

3. **Completed Task Plans (5 files)**
   - `task-*.md` files for done tasks

### 2.2 Research Docs Organization

**Current:** 60 research docs, many orphaned

**Strategy:** Link orphan research docs from main README or archive

```bash
# Find orphan research docs
.venv/bin/python scripts/find_orphan_files.py 2>&1 | grep "docs/research"
```

### 2.3 Internal Docs Review

**Current:** 22 orphan files in `docs/_internal/`

**Strategy:** Review for relevance, archive or link

---

## Phase 3: Deep Cleanup Plan

### Target: Clean architecture with minimal orphans

### 3.1 Review All Orphan Categories

| Category | Count | Action |
|----------|-------|--------|
| docs/_archive/ | 50+ | OK - expected orphans |
| docs/_internal/ | 22 | Review, archive stale |
| docs/planning/ | 70 | Archive completed |
| docs/research/ | 10-15 | Link from README or archive |
| agents/ | 5 | Review for relevance |
| streamlit_app/ | 0 | ✅ Cleaned in Session 7 |

### 3.2 Folder README Creation

**Priority Folders (need READMEs):**

| Folder | Priority | Reason |
|--------|----------|--------|
| `docs/specs/` | HIGH | Contains specifications |
| `docs/adr/` | HIGH | Architecture decisions |
| `docs/verification/` | MEDIUM | Test verification |
| `scripts/` | HIGH | All automation |

### 3.3 Archive Organization

**Implement dated structure:**
```
docs/_archive/
├── 2025-12/
├── 2026-01-early/    (days 1-15)
├── 2026-01-late/     (days 16-31)
└── by-category/
    ├── agent-handoffs/
    ├── session-docs/
    └── task-completions/
```

---

## Automation Workflow for Phase 2

### Step-by-Step Process

```bash
# Step 1: Get current orphan state
.venv/bin/python scripts/find_orphan_files.py > orphans_before.txt

# Step 2: Archive planning docs (by pattern)
.venv/bin/python scripts/batch_archive.py \
  --pattern "docs/planning/agent-[2-8]-*.md" \
  --dest "docs/_archive/planning" --dry-run

# Step 3: Review dry-run output, then execute
.venv/bin/python scripts/batch_archive.py \
  --pattern "docs/planning/agent-[2-8]-*.md" \
  --dest "docs/_archive/planning"

# Step 4: Verify no broken links
.venv/bin/python scripts/check_links.py

# Step 5: Commit
./scripts/ai_commit.sh "chore: archive planning docs from agents 2-8"

# Step 6: Check new orphan state
.venv/bin/python scripts/find_orphan_files.py > orphans_after.txt
diff orphans_before.txt orphans_after.txt
```

---

## Issue Prevention Checklist

### Before Any File Operation

- [ ] Run `--dry-run` first
- [ ] Check orphan status: `find_orphan_files.py`
- [ ] Check references: `grep -r "filename" docs/`
- [ ] Check link status: `check_links.py`

### After Any File Operation

- [ ] Verify links: `check_links.py`
- [ ] Verify structure: `check_folder_structure.py`
- [ ] Commit immediately: `ai_commit.sh "message"`

### Common Issues & Quick Fixes

| Issue | Quick Fix |
|-------|-----------|
| Broken link after move | `fix_broken_links.py --fix` |
| git mv fails (untracked) | Script falls back to `mv` |
| PR required for commit | Stash → Branch → Pop → Commit |
| Archive has no README | Create simple index file |

---

## Session 8 Execution Plan

### Phase 2A: Planning Docs Archive (Target: 7+ commits)

1. **Commit 1:** Archive remaining agent-2/7/8 planning docs
2. **Commit 2:** Archive session handoff docs
3. **Commit 3:** Archive task completion docs
4. **Commit 4:** Update planning/README.md index
5. **Commit 5:** Create archive index
6. **Commit 6:** Update docs statistics
7. **Commit 7:** SESSION_LOG update

### Success Metrics

| Metric | Before | Target |
|--------|--------|--------|
| Orphan files | 176 | <100 |
| Planning orphans | 70 | <20 |
| Broken links | 0 | 0 |
| Commits | 0 | 7+ |

---

## Quick Commands Reference

```bash
# Start session
.venv/bin/python scripts/start_session.py

# Find orphans by folder
.venv/bin/python scripts/find_orphan_files.py 2>&1 | grep "docs/planning" -A100

# Batch archive
.venv/bin/python scripts/batch_archive.py --files f1 f2 --dest dir --dry-run

# Check everything
.venv/bin/python scripts/check_links.py && \
.venv/bin/python scripts/check_folder_structure.py

# Safe commit
./scripts/ai_commit.sh "message"
```

---

*Document created: Session 8 preparation*

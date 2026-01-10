# Folder Cleanup Workflow

> **Status:** Active | **Created:** 2026-01-10
> **Purpose:** Step-by-step workflow for safe folder cleanup with checkpoints

---

## Overview

This workflow provides a systematic approach to cleaning up folders:
1. **Audit** - Identify cleanup candidates
2. **Classify** - Categorize files (keep, archive, delete)
3. **Plan** - Create cleanup plan
4. **Execute** - Apply changes safely
5. **Verify** - Confirm no breakage

---

## Phase 1: Audit (Gather Information)

### Step 1.1: Run Discovery Scripts

```bash
# Find orphan files (not linked anywhere)
.venv/bin/python scripts/find_orphan_files.py --all --age

# Check folder README coverage
.venv/bin/python scripts/check_folder_readmes.py --verbose

# Verify current link health (baseline)
.venv/bin/python scripts/check_links.py
```

### Step 1.2: Document Current State

Create a cleanup tracking file:

```markdown
# Folder Cleanup: [Date]

## Baseline
- Total docs: XX
- Orphan files: XX
- Broken links: XX
- Missing READMEs: XX

## Targets
- Folders to clean: [list]
- Files to review: [list]
```

### Step 1.3: Identify Candidates

Categories:
- **Archive candidates**: Old planning docs, completed research, old sessions
- **Delete candidates**: Duplicate files, empty files, truly obsolete content
- **Keep**: Actively referenced, recent, important documentation

---

## Phase 2: Classify (Decision Making)

### Step 2.1: Classification Criteria

| Criteria | Keep | Archive | Delete |
|----------|------|---------|--------|
| Has incoming links | ✅ | ⚠️ (update links) | ❌ |
| Modified in last 30 days | ✅ | ❌ | ❌ |
| Referenced in code | ✅ | ❌ | ❌ |
| Part of active feature | ✅ | ❌ | ❌ |
| Orphan + old (>90 days) | ❌ | ✅ | Consider |
| Duplicate of another file | ❌ | ❌ | ✅ |
| Empty/placeholder only | ❌ | ❌ | ✅ |

### Step 2.2: Create Classification List

```markdown
## Files to Keep
- [ ] file1.md - Reason: actively linked

## Files to Archive
- [ ] old-plan.md - Reason: 90+ days old, no links
- [ ] research-complete.md - Reason: research finished

## Files to Delete
- [ ] duplicate-guide.md - Reason: exact copy of X
```

### Step 2.3: Get Approval (If Needed)

For significant cleanup (>10 files), document the plan in a PR or issue.

---

## Phase 3: Plan (Prepare Operations)

### Step 3.1: Order Operations

1. **Deletions first** (removes clutter)
2. **Archives second** (preserves content)
3. **Moves/renames last** (link updates)

### Step 3.2: Prepare Commands

Create a script or checklist:

```bash
#!/bin/bash
# Cleanup script for [folder] - [date]

# Phase 1: Deletions
.venv/bin/python scripts/safe_file_delete.py docs/duplicate.md
.venv/bin/python scripts/safe_file_delete.py docs/empty.md

# Phase 2: Archives
.venv/bin/python scripts/safe_file_move.py docs/old-plan.md docs/_archive/2026-01/old-plan.md

# Phase 3: Reorganization
.venv/bin/python scripts/safe_file_move.py docs/misplaced.md docs/correct-folder/misplaced.md
```

### Step 3.3: Backup Branch (Optional but Recommended)

```bash
git checkout -b backup/cleanup-2026-01-10
git push origin backup/cleanup-2026-01-10
git checkout main
```

---

## Phase 4: Execute (Apply Changes)

### Step 4.1: Pre-Flight Check

```bash
# Verify clean working tree
git status

# Verify link baseline
.venv/bin/python scripts/check_links.py

# Verify on correct branch
git branch --show-current
```

### Step 4.2: Execute in Small Batches

**Rule: One commit per logical group (max 5 files)**

```bash
# Batch 1: Delete duplicates
.venv/bin/python scripts/safe_file_delete.py docs/file1.md
.venv/bin/python scripts/safe_file_delete.py docs/file2.md
.venv/bin/python scripts/check_links.py  # Verify after each batch
./scripts/ai_commit.sh "chore: remove duplicate files"

# Batch 2: Archive old planning
.venv/bin/python scripts/safe_file_move.py docs/planning/old1.md docs/_archive/planning/old1.md
.venv/bin/python scripts/safe_file_move.py docs/planning/old2.md docs/_archive/planning/old2.md
.venv/bin/python scripts/check_links.py
./scripts/ai_commit.sh "chore: archive old planning docs"

# Batch 3: Reorganize
.venv/bin/python scripts/safe_file_move.py docs/misplaced.md docs/correct/misplaced.md
.venv/bin/python scripts/check_links.py
./scripts/ai_commit.sh "refactor: reorganize documentation"
```

### Step 4.3: Checkpoint After Each Batch

After each commit:
- [ ] Link check passes
- [ ] No untracked files left behind
- [ ] Commit message is descriptive

---

## Phase 5: Verify (Confirm Success)

### Step 5.1: Run All Validators

```bash
# Links still valid
.venv/bin/python scripts/check_links.py

# Folder structure valid
.venv/bin/python scripts/check_folder_structure.py

# No new orphans created
.venv/bin/python scripts/find_orphan_files.py

# Pre-commit hooks pass
.venv/bin/python -m pre_commit run --all-files
```

### Step 5.2: Update Documentation

- [ ] Update affected README files
- [ ] Regenerate docs-index.json if significant changes
- [ ] Update TASKS.md if cleanup was a task

```bash
.venv/bin/python scripts/generate_docs_index.py
./scripts/ai_commit.sh "chore: regenerate docs index after cleanup"
```

### Step 5.3: Document Results

Update the cleanup tracking file:

```markdown
## Results
- Files deleted: X
- Files archived: X
- Files moved: X
- Final orphan count: X
- All links valid: ✅

## Issues Encountered
- [Document any issues and how resolved]
```

---

## Emergency: Rollback Procedures

### Rollback Single Commit

```bash
git revert HEAD
./scripts/ai_commit.sh "revert: undo cleanup - [reason]"
```

### Rollback Multiple Commits

```bash
# Find the commit before cleanup started
git log --oneline -10

# Reset to that point (CAREFUL: loses all cleanup)
git reset --hard <commit-before-cleanup>
git push --force-with-lease  # Only if absolutely necessary
```

### Restore from Backup Branch

```bash
# Restore specific file
git show backup/cleanup-2026-01-10:path/to/file.md > path/to/file.md
```

---

## Quick Reference Checklist

### Before Cleanup
- [ ] Run `find_orphan_files.py`
- [ ] Run `check_links.py` (baseline)
- [ ] Create cleanup plan document
- [ ] (Optional) Create backup branch

### During Cleanup
- [ ] Use safe scripts only (never manual rm/mv)
- [ ] Dry-run before each operation
- [ ] Check links after each batch
- [ ] Commit after each logical group

### After Cleanup
- [ ] All validators pass
- [ ] Regenerate docs-index.json
- [ ] Update affected READMEs
- [ ] Document results

---

*Workflow created: 2026-01-10 | Part of folder cleanup automation system*

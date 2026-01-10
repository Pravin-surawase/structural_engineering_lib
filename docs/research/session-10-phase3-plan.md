# Phase 3 Deep Cleanup - Master Plan

**Session:** 10 | **Date:** 2026-01-11 | **Target:** 7+ commits

---

## 📊 Current State Analysis

### Metrics After Session 9

| Metric | Value | Status |
|--------|-------|--------|
| Orphan files | 0 | ✅ Perfect |
| Markdown files | 234 | ✅ |
| Internal links | 697 | ✅ All valid |
| Broken links | 0 | ✅ |
| Automation scripts | **99** | ✅ Comprehensive |
| Missing folder READMEs | 68 | 🟡 Needs review |
| Sparse READMEs (<50 lines) | 15 | 🟡 Enhance |

### Sparse READMEs Needing Enhancement (Priority Order)

| Lines | File | Priority |
|-------|------|----------|
| 9 | docs/images/README.md | 🔵 LOW (images folder) |
| 11 | docs/_active/README.md | 🟡 MEDIUM |
| 18 | docs/reference/README.md | 🔴 HIGH (user-facing) |
| 22 | docs/_archive/misc/README.md | 🔵 LOW (archive) |
| 22 | docs/blog-drafts/README.md | 🔵 LOW |
| 22 | docs/getting-started/README.md | 🔴 HIGH (user-facing) |
| 25 | docs/_references/README.md | 🟡 MEDIUM |
| 28 | docs/cookbook/README.md | 🔴 HIGH (user-facing) |
| 31 | docs/architecture/README.md | 🔴 HIGH (developer-facing) |
| 36 | docs/verification/README.md | 🟡 MEDIUM |
| 37 | docs/_archive/publications/README.md | 🔵 LOW |
| 37 | docs/guidelines/README.md | 🟡 MEDIUM |
| 40 | docs/contributing/README.md | 🟡 MEDIUM |
| 46 | docs/agents/sessions/2026-01/README.md | 🔵 LOW |
| 46 | docs/learning/README.md | 🟡 MEDIUM |

---

## 🔧 Automation Inventory

### Available Scripts by Category

**Doc Quality (12 scripts):**
- `check_folder_readmes.py` - Find missing READMEs
- `check_links.py` - Validate internal links
- `fix_broken_links.py` - Auto-fix broken links
- `check_doc_versions.py` - Version consistency
- `check_doc_frontmatter.py` - Frontmatter validation
- `check_duplicate_docs.py` - Find duplicates
- `generate_docs_index.py` - Generate indexes
- `generate_folder_index.py` - Folder indexes
- `check_docs_index.py` - Index validation
- `check_docs_index_links.py` - Index link validation
- `check_api_doc_signatures.py` - API docs sync
- `check_session_docs.py` - Session docs validation

**File Operations (6 scripts):**
- `safe_file_move.py` - Move with link updates
- `safe_file_delete.py` - Delete with reference check
- `batch_archive.py` - Multi-file archival
- `rename_folder_safe.py` - Safe folder rename
- `find_orphan_files.py` - Find unreferenced files
- `archive_old_sessions.sh` - Auto-archive old sessions

**Git Workflow (10 scripts):**
- `ai_commit.sh` - AI commit workflow
- `safe_push.sh` - Conflict-minimized push
- `create_task_pr.sh` / `finish_task_pr.sh` - PR workflow
- `should_use_pr.sh` - PR decision helper
- `recover_git_state.sh` - Git recovery
- `check_unfinished_merge.sh` - Merge check
- `verify_git_fix.sh` - Git fix verification

**Validation (26 scripts):**
- 26 check_*.py and validate_*.py scripts

### Gap Analysis - New Scripts Needed

| Script | Purpose | Priority |
|--------|---------|----------|
| `enhance_readme.py` | Add content to sparse READMEs | 🔴 HIGH |
| `check_readme_quality.py` | Validate README completeness | 🟡 MEDIUM |
| `find_stale_content.py` | Find outdated docs by content | 🟡 MEDIUM |
| `batch_readme_update.py` | Update multiple READMEs | 🟡 MEDIUM |

---

## ⚠️ Issue Prevention Matrix

### Known Issues & Solutions

| Issue | Cause | Prevention | Recovery |
|-------|-------|------------|----------|
| **Broken links after move** | File moved without link update | Always use `safe_file_move.py` | `fix_broken_links.py` |
| **Orphan files after creation** | New file not linked | Add to parent README immediately | `find_orphan_files.py` + add link |
| **Git conflicts** | Manual git commands | Always use `ai_commit.sh` | `recover_git_state.sh` |
| **Pre-commit modifies files** | Whitespace/formatting | `safe_push.sh` handles automatically | Amend if not pushed |
| **Stale version refs** | Version not updated | `check_doc_versions.py` in pre-commit | Update refs manually |
| **Missing READMEs** | New folder without README | Create README when creating folder | `check_folder_readmes.py` |

### Phase 3 Specific Risks

| Risk | Mitigation |
|------|------------|
| Enhancing README breaks links | Run `check_links.py` after each edit |
| Large batch changes fail mid-way | Commit after each file enhancement |
| Wrong content added | Review folder purpose before enhancing |
| Time-consuming manual work | Create automation scripts first |

---

## 📋 Phase 3 Execution Plan

### Phase 3.1: Automation Enhancement (Commit 1-2)

1. **Create `enhance_readme.py`** - Script to:
   - Analyze folder contents
   - Generate structured README content
   - Add file tables with descriptions
   - Preserve existing content

2. **Create `check_readme_quality.py`** - Script to:
   - Check minimum line count
   - Verify file table exists
   - Check for parent links
   - Score README completeness

### Phase 3.2: High-Priority README Enhancement (Commit 3-5)

Enhance user-facing READMEs first:

1. **docs/reference/README.md** (18 lines → 80+)
   - Add API reference overview
   - Link to all reference docs
   - Add usage examples

2. **docs/getting-started/README.md** (22 lines → 80+)
   - Add beginner path
   - Link to quickstart guides
   - Add decision tree

3. **docs/cookbook/README.md** (28 lines → 60+)
   - Add recipe index
   - Link to all recipes
   - Add common tasks

4. **docs/architecture/README.md** (31 lines → 70+)
   - Add architecture overview
   - Link to all architecture docs
   - Add layer diagram reference

### Phase 3.3: Medium-Priority Enhancement (Commit 6-7)

1. **docs/_active/README.md** (11 lines)
2. **docs/_references/README.md** (25 lines)
3. **docs/verification/README.md** (36 lines)
4. **docs/guidelines/README.md** (37 lines)

### Phase 3.4: Documentation & Handoff (Commit 8)

1. Update SESSION_LOG.md
2. Update next-session-brief.md
3. Document lessons learned

---

## 📝 README Enhancement Template

Use this structure for all README enhancements:

```markdown
# [Folder Name]

[One-sentence description of folder purpose]

**Files:** X | **Updated:** YYYY-MM-DD

---

## Overview

[2-3 sentences explaining what this folder contains and when to use it]

## Contents

| File | Description |
|------|-------------|
| [file1.md](file1.md) | Brief description |
| [file2.md](file2.md) | Brief description |

## Quick Start

[For user-facing folders: How to get started]

## Related

- [Link to related folder](../folder/README.md)
- [Link to parent](../README.md)
```

---

## 🔄 Session 9 Issues Review

### Issues Encountered

1. **No major issues** - Session 9 was smooth due to:
   - Using README indexing instead of file moves
   - Running `check_links.py` after each change
   - Committing frequently (7 content commits)

### Lessons Learned

1. **README indexing is safer than file moves**
   - No broken links risk
   - Faster to implement
   - Provides better navigation

2. **Batch commits work well for docs**
   - Group related README updates
   - Verify links between batches

3. **Pre-commit handles whitespace automatically**
   - No manual intervention needed
   - `safe_push.sh` handles edge cases

### Long-term Solutions Implemented

| Issue | Solution | Status |
|-------|----------|--------|
| Orphan files | README indexing strategy | ✅ Resolved |
| Git conflicts | ai_commit.sh workflow | ✅ Working |
| Broken links | check_links.py in pre-commit | ✅ Working |
| Missing READMEs | check_folder_readmes.py | ✅ Available |

---

## 🚀 Quick Start Commands

```bash
# Check current state
.venv/bin/python scripts/check_links.py
.venv/bin/python scripts/find_orphan_files.py 2>&1 | grep "^   ⚠️" | wc -l
.venv/bin/python scripts/check_folder_readmes.py 2>&1 | grep "Missing" | wc -l

# Verify README line counts
find docs -name "README.md" -exec wc -l {} \; | awk '$1 < 50 {print}' | sort -n

# Commit workflow
./scripts/ai_commit.sh "docs: enhance X README with comprehensive index"
```

---

## ✅ Success Criteria

| Metric | Target |
|--------|--------|
| High-priority READMEs enhanced | 4/4 |
| README average line count | >50 lines |
| Broken links | 0 |
| Orphan files | 0 |
| Commits this session | 7+ |

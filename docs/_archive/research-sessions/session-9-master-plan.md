# Session 9 Master Plan: Complete Folder Restructuring

**Date:** 2026-01-11 | **Goal:** 8-10+ commits, complete Phase 2/3

---

## 📊 Current State Assessment

| Metric | Before Session 8 | After Session 8 | Target |
|--------|------------------|-----------------|--------|
| Total orphan files | 176 | 169 | <50 |
| Markdown files | 269 | 231 | ~150 |
| Archive files | ~80 | 119 | ~150 |
| Broken links | 0 | 0 | 0 |

### Orphan Distribution (169 total)

| Location | Count | Action |
|----------|-------|--------|
| docs/_archive/2026-01/ | 32 | Create index, link from archive README |
| docs/_archive/planning/ | 40 | Create index, link from archive README |
| docs/_archive/publications/ | 11 | Create index, link from archive README |
| docs/_archive/misc/ | 5 | Create index, link from archive README |
| docs/_internal/ | 16 | Evaluate: archive old, keep relevant |
| docs/_internal/copilot-tasks/ | 10 | Archive (outdated xlwings research) |
| docs/research/ | 28 | Keep (active research) - add to index |
| docs/guidelines/ | 7 | Link from main docs |
| docs/blog-drafts/ | 4 | Keep for future publishing |
| docs/learning/ | 3 | Link from docs/README |
| agents/agent-9/ | 4 | Organize agent archives |
| docs/contributing/ | 1 | Link from CONTRIBUTING.md |

---

## 🎯 Phase 2 Completion Plan (This Session)

### Batch 1: Create Archive Index (Commit 1)
Create `docs/_archive/README.md` with proper navigation to all archived content.

**Files to create:**
- `docs/_archive/README.md` - Main archive index
- Update links from orphaned archive files

### Batch 2: Archive Internal Docs (Commit 2-3)
Move outdated internal docs to archive:
- `docs/_internal/copilot-tasks/` → `docs/_archive/copilot-tasks/` (10 files)
- Old cost-optimizer docs → `docs/_archive/cost-optimizer/`

### Batch 3: Link Guidelines (Commit 4)
Add links to `docs/guidelines/` from main docs:
- Update `docs/README.md` to include guidelines section
- Fix 7 orphaned guidelines files

### Batch 4: Link Research Docs (Commit 5)
Add links to research docs from `docs/research/README.md` or similar:
- Create `docs/research/README.md` if missing
- Link 28 research documents

### Batch 5: Clean Empty Folders (Commit 6)
Remove any empty folders left after archival.

---

## 🔧 Automation Scripts Assessment

### Existing Scripts (Ready to Use)

| Script | Purpose | Status |
|--------|---------|--------|
| `batch_archive.py` | Multi-file archival | ✅ Ready |
| `safe_file_move.py` | Single file move | ✅ Ready |
| `safe_file_delete.py` | Safe deletion | ✅ Ready |
| `find_orphan_files.py` | Find unreferenced docs | ✅ Ready |
| `check_links.py` | Verify markdown links | ✅ Ready |
| `fix_broken_links.py` | Auto-fix broken links | ✅ Ready |
| `rename_folder_safe.py` | Safe folder rename | ✅ Ready |
| `check_folder_readmes.py` | Check folder docs | ✅ Ready |

### Enhancement Needed

| Script | Enhancement | Priority |
|--------|-------------|----------|
| `find_orphan_files.py` | Add `--exclude-archive` flag | 🟡 MEDIUM |
| `batch_archive.py` | Add `--create-index` flag | 🟡 MEDIUM |
| NEW: `create_archive_index.py` | Auto-generate archive README | 🔴 HIGH |

---

## ⚠️ Issue Prevention Checklist

### Before Any Archive Operation
1. ✅ Run `--dry-run` first
2. ✅ Check orphan count before/after
3. ✅ Verify links with `check_links.py`
4. ✅ Use `ai_commit.sh` for all commits

### Known Issues & Solutions

| Issue | Root Cause | Solution |
|-------|------------|----------|
| Broken links after archive | Files moved but links not updated | Run `fix_broken_links.py --fix` after batch |
| Orphan count not decreasing | Files in archive still orphaned | Create archive README to link them |
| Pre-commit hook failures | Link validation fails | Fix links before commit |
| git mv fails | Untracked files | Scripts use `mv` fallback |

---

## 📋 Session 9 Commit Plan

| # | Description | Files |
|---|-------------|-------|
| 1 | Create archive README with navigation | 1 new |
| 2 | Archive copilot-tasks folder | 10 move |
| 3 | Archive old internal docs | ~10 move |
| 4 | Link guidelines from main docs | 2-3 edit |
| 5 | Create research README with links | 1 new |
| 6 | Clean empty folders | cleanup |
| 7 | Update SESSION_LOG | 1 edit |
| 8 | Update next-session-brief | 1 edit |
| 9 | Create automation enhancement (if time) | 1 new |
| 10 | Final orphan reduction batch | ~20 files |

---

## 🚀 Quick Commands Reference

```bash
# Check current orphan count
.venv/bin/python scripts/find_orphan_files.py 2>&1 | grep "^   ⚠️" | wc -l

# Batch archive with dry-run
.venv/bin/python scripts/batch_archive.py --files "file1.md" "file2.md" --dest "docs/_archive/folder" --dry-run

# Fix all broken links
.venv/bin/python scripts/fix_broken_links.py --fix

# Verify links
.venv/bin/python scripts/check_links.py

# Safe commit
./scripts/ai_commit.sh "chore: description"
```

---

## 📈 Success Metrics

| Metric | Current | Session 9 Target |
|--------|---------|------------------|
| Orphan files | 169 | <100 |
| Commits | 0 | 8-10 |
| Broken links | 0 | 0 |
| Archive README | ❌ | ✅ |
| Research README | ❌ | ✅ |

# Folder Restructuring Plan

> **Purpose:** Complete restructuring of project folders for cleaner organization
> **Created:** 2026-01-11 (Session 7)
> **Status:** 🔬 Research Phase

---

## Executive Summary

The project has accumulated technical debt in folder organization. This document outlines a phased approach to restructure folders while preventing link breakage and maintaining backward compatibility.

**Key Findings:**
- 175 orphan files identified
- 72 folders missing READMEs
- Several problematic folders need cleanup
- Strong automation already exists (19+ file operation scripts)

---

## Current State Analysis

### 📊 Metrics

| Metric | Value | Status |
|--------|-------|--------|
| Total Folders | 116 | Analyzed |
| Orphan Files | 175 | Need review |
| Archive Files | 64 | In docs/_archive |
| Missing READMEs | 72 | Optional folders |
| Link Targets | 840 | Indexed |

### 🔴 Critical Cleanup Areas

#### 1. Root-Level Problematic Folders

| Folder | Issue | Action |
|--------|-------|--------|
| `external_data/` | Typo in name, external data | Rename to `external_data/` or add to .gitignore |
| `tmp/` | Temporary test files | Add to .gitignore, clean periodically |
| `metrics/` | CI metrics data | OK, keep for analytics |
| `logs/` | Runtime logs | OK, already has .gitignore |
| `git_operations_log/` | Agent git logs | OK, useful for debugging |

#### 2. Streamlit App Cleanup (16 orphan files)

Files in `streamlit_app/` root that should be archived:
- `AGENT-6-*.md` - Agent 6 completion docs (5 files)
- `UI-*.md` - UI task status docs (4 files)
- `*-STATUS.txt` - Status files (2 files)
- `DELIVERY_*.md` - Delivery docs (2 files)
- `VERIFY_FIX-001.sh` - One-time fix script

**Action:** Move to `streamlit_app/docs/_archive/` or `docs/_archive/streamlit/`

#### 3. Docs Archive Consolidation

Current archive structure:
```
docs/_archive/
├── 2026-01/           # 45 files - Agent 6 & Session docs
├── contributing/      # Old contributing guides
├── planning/          # Old planning docs
└── *.md               # 4 root archive files
```

**Issue:** Archive is growing without organization.

**Action:** Create dated sub-folders, establish archival policy.

#### 4. Agent 9 Governance Cleanup

Files in `agents/agent-9/governance/` that are orphans:
- `RECURRING-ISSUES-ANALYSIS.md`
- `_archive/MACOS-RENAME-ISSUE.md`

**Action:** Review if still relevant, archive if not.

---

## Target Folder Structure

### Phase 1: Root Cleanup

```
structural_engineering_lib/
├── .github/                  # GitHub config (keep)
├── .vscode/                  # VS Code config (keep)
├── Python/                   # Main Python package
├── Excel/                    # Excel files
├── VBA/                      # VBA modules
├── docs/                     # Documentation
├── scripts/                  # Automation scripts
├── agents/                   # Agent docs
├── streamlit_app/            # Streamlit UI
├── tests/                    # Root tests (if any)
├── learning-materials/       # Learning content
├── external_data/            # RENAMED from "files from external yser"
├── logs/                     # Runtime logs
├── metrics/                  # CI metrics
└── [.gitignore items]        # tmp/, git_operations_log/, etc.
```

### Phase 2: Docs Consolidation

```
docs/
├── README.md                 # Main docs index
├── getting-started/          # Tutorials, quickstarts
├── reference/                # API reference, guides
├── architecture/             # Design docs
├── research/                 # Research documents
├── planning/                 # Active planning
├── contributing/             # Contribution guides
├── legal/                    # Legal docs
├── guidelines/               # Best practices
├── adr/                      # Architecture decisions
├── specs/                    # Specifications
├── verification/             # Test verification
├── troubleshooting/          # Common issues
├── _archive/                 # Archived docs (by date)
│   ├── 2025-12/
│   ├── 2026-01/
│   └── README.md
├── _internal/                # Internal docs
└── _references/              # External references
```

### Phase 3: Streamlit App Cleanup

```
streamlit_app/
├── app.py                    # Main app
├── requirements.txt          # Dependencies
├── README.md                 # App README
├── QUICK_START.md            # Quick start (keep)
├── .streamlit/               # Streamlit config
├── components/               # UI components
├── pages/                    # App pages
├── utils/                    # Utilities
├── tests/                    # App tests
└── docs/                     # App-specific docs
    ├── research/             # Research
    └── _archive/             # Archived status docs
```

---

## Existing Automation Analysis

### ✅ Scripts We Have

| Script | Purpose | Ready? |
|--------|---------|--------|
| `safe_file_move.py` | Move files with link updates | ✅ Ready |
| `safe_file_delete.py` | Delete with reference check | ✅ Ready |
| `find_orphan_files.py` | Find unreferenced docs | ✅ Ready |
| `check_folder_readmes.py` | Verify folder READMEs | ✅ Ready |
| `check_links.py` | Verify markdown links | ✅ Ready |
| `fix_broken_links.py` | Auto-fix broken links | ✅ Ready |
| `check_folder_structure.py` | Validate structure | ✅ Ready |
| `generate_folder_index.py` | Generate folder index | ✅ Ready |

### 🔧 Scripts Needed

| Script | Purpose | Priority |
|--------|---------|----------|
| `batch_archive.py` | Archive multiple files at once | HIGH |
| `rename_folder_safe.py` | Rename folder with link updates | HIGH |
| `cleanup_streamlit_docs.py` | Move streamlit orphans to archive | MEDIUM |
| `archive_by_date.py` | Organize archives by date | LOW |

---

## Risk Analysis

### High Risk Operations

1. **Renaming folders with many references**
   - Risk: Breaking 100+ links
   - Mitigation: Run `check_links.py --fix` after, dry-run first

2. **Moving files between docs/ subfolders**
   - Risk: Breaking relative links
   - Mitigation: Use `safe_file_move.py`, verify with `check_links.py`

3. **Deleting files that are secretly important**
   - Risk: Losing useful content
   - Mitigation: Archive first, delete later; backup before major ops

### Low Risk Operations

1. **Archiving orphan files** - No references, safe to move
2. **Adding .gitignore entries** - No impact on docs
3. **Creating READMEs** - Additive, no breaking changes

---

## Execution Plan

### Phase 1: Pre-Cleanup (This Session)

**Tasks:**
1. ✅ Run `find_orphan_files.py` to get current orphan list
2. ✅ Run `check_folder_readmes.py` to identify missing READMEs
3. ⏳ Create `batch_archive.py` script
4. ⏳ Archive streamlit_app orphan files
5. ⏳ Rename "files from external yser" folder

**Success Criteria:**
- 0 orphan files in streamlit_app/ root
- Folder typo fixed
- All changes committed with proper docs

### Phase 2: Docs Organization (Next Session)

**Tasks:**
1. Review and organize docs/_archive by date
2. Move orphan research docs to proper locations
3. Create missing folder READMEs for key folders
4. Update docs/README.md index

### Phase 3: Deep Cleanup (Future)

**Tasks:**
1. Review all 175 orphan files
2. Archive or properly link each one
3. Run full link validation
4. Update folder structure documentation

---

## Automation Scripts to Create

### 1. `batch_archive.py`

```python
"""Batch archive multiple files to docs/_archive."""
# Features:
# - Accept file list or pattern
# - Create dated subfolder automatically
# - Update links after move
# - Generate archive log
```

### 2. `rename_folder_safe.py`

```python
"""Safely rename a folder with link updates."""
# Features:
# - Check all references before rename
# - Update links in all markdown files
# - Create redirect stub if needed
# - Verify no broken links after
```

### 3. `cleanup_streamlit_docs.py`

```python
"""Move streamlit orphan docs to archive."""
# Features:
# - Identify Agent 6 completion docs
# - Move to streamlit_app/docs/_archive/
# - Preserve commit history (use git mv)
```

---

## Quick Reference Commands

```bash
# Check current state
.venv/bin/.venv/bin/python scripts/find_orphan_files.py
.venv/bin/.venv/bin/python scripts/check_folder_readmes.py
.venv/bin/.venv/bin/python scripts/check_links.py

# Safe file operations
.venv/bin/.venv/bin/python scripts/safe_file_move.py <old> <new> --dry-run
.venv/bin/.venv/bin/python scripts/safe_file_delete.py <file> --dry-run

# Validate after changes
.venv/bin/.venv/bin/python scripts/check_links.py
.venv/bin/.venv/bin/python scripts/check_folder_structure.py
```

---

## Session 6 Issues Review

### Issues Encountered

1. **mypy errors with wrong function names**
   - Issue: Generated code used `tables.get_tau_c()` but actual function is `tables.get_tc_value()`
   - Fix: Always verify function names exist before using
   - Automation: Add function existence check to migration scripts

2. **Session docs date mismatch**
   - Issue: next-session-brief.md had different date than SESSION_LOG
   - Fix: Update both files consistently
   - Automation: `check_session_docs.py` catches this

3. **Duplicate entries in copilot-instructions**
   - Issue: Table had duplicate rows
   - Fix: Manual cleanup
   - Automation: Add lint check for duplicate table rows?

### Lessons Learned

1. **Always verify API signatures** - Don't assume function names
2. **Keep session docs in sync** - Pre-commit hook catches this
3. **Automation-first** - Created scripts prevent issues

---

## Files to Archive Immediately

### Streamlit App (Move to streamlit_app/docs/_archive/)

```
AGENT-6-FINAL-STATUS.md
AGENT-6-UI-004-005-SUMMARY.md
AGENT_6_STATUS.txt
DELIVERABLES-UI-004-005.txt
DELIVERY_PACKAGE.md
FINAL_IMPLEMENTATION_SUMMARY.md
HANDOFF-UI-004-005.md
UI-001-STATUS.md
UI-003-SUMMARY.md
UI-004-005-STATUS.md
VERIFY_FIX-001.sh
WORK_SUMMARY.md
RESEARCH-COMPLETE-SUMMARY.txt
SETUP_AND_MAINTENANCE_GUIDE.md
```

### Root Folder

```
files from external yser/ → rename to external_data/
tmp/ → add to .gitignore (already?)
```

---

## Next Steps

1. **Create batch_archive.py** - For efficient multi-file archival
2. **Archive streamlit orphans** - 14 files to move
3. **Rename typo folder** - "files from external yser" → "external_data"
4. **Commit Phase 1** - Document all changes
5. **Plan Phase 2** - Docs organization in TASKS.md

# Folder Cleanup & Maintenance Research

> **Status:** Active Research | **Session:** 2026-01-10 Session 4
> **Purpose:** Define safe folder cleanup procedures, automation, and agent guidelines

---

## 1. Current State Analysis

### 1.1 File Distribution (Top Folders)

| Folder | MD Files | Purpose | Cleanup Priority |
|--------|----------|---------|------------------|
| `streamlit_app/docs/` | 93 | App documentation | 🟡 Review |
| `docs/planning/` | 63 | Planning docs | 🔴 High - many old |
| `docs/research/` | 77 | Research docs | 🟡 Archive candidates |
| `docs/_archive/2026-01/` | 49 | Already archived | ✅ OK |
| `agents/agent-9/governance/_archive/` | 30 | Agent archive | ✅ OK |
| `docs/contributing/` | 27 | Contribution guides | 🟢 Stable |
| `docs/reference/` | 23 | API references | 🟢 Stable |

### 1.2 Archive Status

**Existing Archive Folders:**
- `docs/_archive/` - Main archive with date-based subfolders
- `agents/agent-9/governance/_archive/` - Agent-specific archive

**Archive Scripts:**
- `scripts/archive_old_files.sh` - Auto-archive from `docs/_active/` (90-day retention)
- `scripts/archive_old_sessions.sh` - Archive old session docs

### 1.3 Issues Identified

#### Critical Issues
1. **`external_data/`** - Typo in folder name, contains external Excel files (36MB+)
2. **`tmp/`** - Contains test files that should be in `tests/`
3. **Many folders lack README.md** - No clear purpose/guidelines

#### Folders Without README (Key Ones)
- `Python/examples/`
- `Python/structural_lib/`
- `VBA/` (entire folder)
- `VBA/Modules/`
- `VBA/Tests/`
- `docs/_internal/`
- `docs/blog-drafts/`
- `docs/guidelines/`
- `docs/legal/`
- `docs/specs/`
- `learning-materials/` (all subfolders)
- `metrics/`

#### Potential Duplicates
- 43 files named `README.md` (expected - each folder has one)
- 9 files named `index.md` (expected)
- 5 files named `LICENSE.md` (need review)
- 3 `outline.md` and 3 `draft.md` (may be duplicates)

### 1.4 Link Health
✅ **Current Status:** 0 broken links (719 links verified)
- Pre-commit hook runs `scripts/check_links.py`
- CI runs link validation

---

## 2. Safe File Operation Strategies

### 2.1 The Danger Zones

| Operation | Risk Level | Potential Issues |
|-----------|------------|------------------|
| **Delete file** | 🔴 High | Broken links, lost reference |
| **Rename file** | 🔴 High | Broken links, broken imports |
| **Move file** | 🔴 High | Broken links, broken imports |
| **Archive file** | 🟡 Medium | May still be referenced |
| **Edit file** | 🟢 Low | Tracked by git |

### 2.2 Pre-Operation Checklist

Before ANY file operation, verify:

1. **Link References** - Run `scripts/check_links.py` to establish baseline
2. **Import References** - For Python: `grep -r "from.*import" Python/`
3. **Doc References** - Search for file name in all docs
4. **Git History** - Check if file is actively maintained: `git log --oneline -5 <file>`

### 2.3 Safe Delete Process

```bash
# Step 1: Find all references
grep -r "filename.md" docs/ agents/ --include="*.md"
grep -r "filename" Python/ --include="*.py"

# Step 2: Create backup branch
git checkout -b backup/cleanup-2026-01-10

# Step 3: Delete file
rm path/to/file.md

# Step 4: Run link check
.venv/bin/python scripts/check_links.py

# Step 5: If links broken - fix or restore
git restore path/to/file.md  # Restore if needed
```

### 2.4 Safe Move/Rename Process

```bash
# Step 1: Check references (same as delete)
# Step 2: Create backup branch

# Step 3: Move file
git mv old/path/file.md new/path/file.md

# Step 4: Create redirect stub (for docs)
echo "# Moved\n\nThis file has moved to [new location](../new/path/file.md)." > old/path/file.md

# Step 5: Run link check
# Step 6: Fix any broken links using fix_broken_links.py
```

---

## 3. Archive Policy Recommendations

### 3.1 Archive Criteria

| Category | Archive After | Location |
|----------|---------------|----------|
| Session docs | 30 days | `docs/_archive/YYYY-MM/` |
| Planning docs | 90 days | `docs/_archive/planning/` |
| Research (completed) | Immediately | `docs/research/_archive/` |
| Research (abandoned) | 60 days | `docs/research/_archive/` |
| Agent session logs | 14 days | `agents/<agent>/_archive/` |

### 3.2 Never Archive

- API reference docs
- User guides and tutorials
- Architecture docs
- README.md files
- Configuration docs

### 3.3 Archive Folder Structure

```
docs/_archive/
├── 2026-01/           # Month-based for session/planning
├── 2025-12/
├── planning/          # Old planning docs
├── research/          # Completed/abandoned research
└── README.md          # Archive index/rules
```

---

## 4. Folder README Template

Every folder should have a README.md with:

```markdown
# [Folder Name]

> **Purpose:** One-line description
> **Owner:** Role/person responsible
> **Last Updated:** YYYY-MM-DD

## What belongs here
- Type 1
- Type 2

## What does NOT belong here
- Don't put X here (goes in Y instead)

## Archive Policy
- Files older than N days are archived to `_archive/`
- OR: This folder is never archived

## For AI Agents
- When creating files here, use naming pattern: `[pattern]`
- When modifying files, ensure: [guidelines]
- Link check required after changes: yes/no
```

---

## 5. Automation Requirements

### 5.1 Existing Automation
- ✅ `scripts/check_links.py` - Link validation
- ✅ `scripts/fix_broken_links.py` - Auto-fix links
- ✅ `scripts/archive_old_files.sh` - Archive from `_active/`
- ✅ `scripts/check_folder_structure.py` - Structure validation
- ✅ `scripts/generate_docs_index.py` - Docs index

### 5.2 Needed Automation

| Script | Purpose | Priority |
|--------|---------|----------|
| `scripts/safe_file_move.sh` | Move file + update all links | 🔴 High |
| `scripts/safe_file_delete.sh` | Delete with reference check | 🔴 High |
| `scripts/check_folder_readmes.py` | Verify all folders have README | 🟡 Medium |
| `scripts/find_orphan_files.py` | Find unreferenced docs | 🟡 Medium |
| `scripts/archive_by_policy.py` | Smart archive based on rules | 🟢 Nice-to-have |

### 5.3 Pre-Commit Hooks Needed

Current hooks run link check. Consider adding:
- README existence check for new folders
- File naming convention check

---

## 6. Immediate Cleanup Plan

### Phase 1: Fix Critical Issues (This Session)
1. ✅ Rename `external_data/` → `external_files/`
2. ✅ Move `tmp/test_*.py` → `tests/` (or delete if duplicates)
3. ✅ Create key folder READMEs

### Phase 2: Create Safety Automation (This Session)
1. ✅ Create `scripts/safe_file_move.py`
2. ✅ Create `scripts/safe_file_delete.py`
3. ✅ Create `scripts/check_folder_readmes.py`

### Phase 3: Documentation (This Session)
1. ✅ Create folder cleanup workflow guide
2. ✅ Add agent instructions for file operations
3. ✅ Update copilot-instructions.md

---

## 7. Risk Mitigation

### 7.1 Rollback Strategy

All file operations should be:
1. **Atomic** - One operation per commit
2. **Reversible** - Can be undone with `git revert`
3. **Documented** - Commit message explains what and why

### 7.2 Safety Checks Before Merge

Any PR with file deletions/moves must:
1. Pass link check (automated)
2. Show grep results for file references (in PR description)
3. Have backup plan documented

### 7.3 Emergency Recovery

```bash
# Restore deleted/moved file from git
git log --all --full-history -- "**/filename*"  # Find commit
git show <commit>:path/to/file.md > restored.md  # Restore
```

---

## 8. Agent Guidelines

### 8.1 File Operation Rules

**ALWAYS before any file operation:**
```bash
# 1. Check references
grep -r "filename" docs/ agents/ --include="*.md" | head -20

# 2. Run link check (baseline)
.venv/bin/python scripts/check_links.py

# 3. Use safe scripts when available
./scripts/safe_file_move.py old/path new/path
./scripts/safe_file_delete.py path/to/file
```

**NEVER:**
- Delete files without checking references
- Move files without updating links
- Skip link check after file operations

### 8.2 Creating New Files

When creating new files:
1. Check if similar file exists (use `grep` or semantic search)
2. Follow folder-specific naming conventions (see folder README)
3. Add to docs-index.json if in `docs/`

### 8.3 Folder Selection Guide

| Content Type | Put In | Not In |
|--------------|--------|--------|
| Research (active) | `docs/research/` | `docs/planning/` |
| Research (complete) | `docs/research/_archive/` | `docs/_archive/` |
| Task planning | `docs/planning/` | `docs/research/` |
| Session notes | `docs/SESSION_LOG.md` | New file |
| API docs | `docs/reference/` | `docs/` root |
| Tutorials | `docs/getting-started/` | `docs/learning/` |
| Agent guides | `agents/<agent>/` | `docs/agents/` |

---

## 9. Implementation Checklist

- [ ] Create `scripts/safe_file_move.py`
- [ ] Create `scripts/safe_file_delete.py`
- [ ] Create `scripts/check_folder_readmes.py`
- [ ] Rename `external_data/` folder
- [ ] Move or delete `tmp/` test files
- [ ] Add README to VBA/ folder
- [ ] Add README to Python/structural_lib/
- [ ] Add README to learning-materials/
- [ ] Create folder cleanup workflow guide
- [ ] Update copilot-instructions.md with file operation rules
- [ ] Test all new scripts

---

*Research completed: 2026-01-10 Session 4*

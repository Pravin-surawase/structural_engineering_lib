# File Operations Safety Guide

> **Status:** Active | **Created:** 2026-01-10
> **Purpose:** Safe procedures for file deletion, moves, and renames

---

## ⚠️ CRITICAL: Read Before Any File Operation

File operations (delete, move, rename) can break:
- Internal markdown links
- Python imports
- VBA references
- Documentation references
- CI/CD workflows

**ALWAYS use the safe automation scripts. NEVER do manual operations.**

---

## 🛡️ Safe Scripts Reference

### Quick Reference Table

| Operation | Script | Example |
|-----------|--------|---------|
| **Move/Rename** | `safe_file_move.py` | `python scripts/safe_file_move.py docs/old.md docs/new.md` |
| **Delete** | `safe_file_delete.py` | `python scripts/safe_file_delete.py docs/old.md` |
| **Find orphans** | `find_orphan_files.py` | `python scripts/find_orphan_files.py --age` |
| **Check links** | `check_links.py` | `python scripts/check_links.py` |
| **Fix links** | `fix_broken_links.py` | `python scripts/fix_broken_links.py --fix` |

---

## 📋 Complete Workflows

### Workflow 1: Moving a File

```bash
# Step 1: Preview (ALWAYS do this first)
.venv/bin/python scripts/safe_file_move.py docs/old-location/file.md docs/new-location/file.md --dry-run

# Step 2: Review output
# - Check references that will be updated
# - Verify destination path is correct

# Step 3: Execute move
.venv/bin/python scripts/safe_file_move.py docs/old-location/file.md docs/new-location/file.md

# Step 4: Verify
.venv/bin/python scripts/check_links.py

# Step 5: Commit
./scripts/ai_commit.sh "refactor: move file.md to new location"
```

### Workflow 2: Deleting a File

```bash
# Step 1: Preview (ALWAYS do this first)
.venv/bin/python scripts/safe_file_delete.py docs/obsolete-file.md --dry-run

# Step 2: Review output
# - Check if file has references (will be shown)
# - Decide: fix references first, or use --force

# Step 3a: If no references - delete
.venv/bin/python scripts/safe_file_delete.py docs/obsolete-file.md

# Step 3b: If has references - fix first OR use force
# Option A: Fix references manually
# Option B: Force delete (creates backup)
.venv/bin/python scripts/safe_file_delete.py docs/obsolete-file.md --force

# Step 4: Verify
.venv/bin/python scripts/check_links.py

# Step 5: Commit
./scripts/ai_commit.sh "chore: remove obsolete file.md"
```

### Workflow 3: Archiving Old Files

```bash
# Step 1: Find archive candidates
.venv/bin/python scripts/find_orphan_files.py --age

# Step 2: Move to archive (with redirect stub)
.venv/bin/python scripts/safe_file_move.py docs/planning/old-plan.md docs/_archive/2026-01/old-plan.md --stub

# Step 3: Verify
.venv/bin/python scripts/check_links.py

# Step 4: Commit
./scripts/ai_commit.sh "chore: archive old planning docs"
```

### Workflow 4: Renaming a File

```bash
# Renaming is just moving to same folder with new name
.venv/bin/python scripts/safe_file_move.py docs/old-name.md docs/new-name.md --dry-run
.venv/bin/python scripts/safe_file_move.py docs/old-name.md docs/new-name.md
./scripts/ai_commit.sh "refactor: rename old-name.md to new-name.md"
```

---

## 🔍 Pre-Operation Checklist

Before ANY file operation, verify:

- [ ] **Run dry-run first** - Preview what will happen
- [ ] **Check references** - How many files link to this?
- [ ] **Check git history** - Is this file actively maintained?
- [ ] **Verify destination** - Does file already exist there?
- [ ] **Check imports** - For Python files: grep for imports
- [ ] **Backup exists** - Safe scripts auto-backup, but verify

### Manual Reference Check

```bash
# Find all references to a file
grep -r "filename.md" docs/ agents/ --include="*.md" | head -20

# For Python files
grep -r "from.*module_name" Python/ --include="*.py"
grep -r "import module_name" Python/ --include="*.py"

# Check git history
git log --oneline -5 -- path/to/file.md
```

---

## 🚨 Emergency Recovery

### Restore Deleted File

```bash
# Option 1: Check backup folder
ls tmp/deleted_backups/

# Option 2: Restore from git
git log --all --full-history -- "**/filename*"
git show <commit>:path/to/file.md > restored.md
```

### Undo Move

```bash
# If committed, revert the commit
git revert HEAD

# If not committed, restore from git
git restore path/to/original/file.md
```

### Fix Broken Links

```bash
# After any operation, run link check
.venv/bin/python scripts/check_links.py

# If broken links found, auto-fix
.venv/bin/python scripts/fix_broken_links.py --fix
```

---

## 📁 Special Folder Rules

### Protected Folders (Never Archive)

| Folder | Reason |
|--------|--------|
| `docs/reference/` | API docs - always needed |
| `docs/getting-started/` | User onboarding |
| `docs/architecture/` | System design |
| `Python/structural_lib/` | Core code |
| `VBA/Modules/` | Core VBA code |

### Archive-Safe Folders

| Folder | Archive To | Retention |
|--------|------------|-----------|
| `docs/planning/` | `docs/_archive/planning/` | 90 days |
| `docs/research/` | `docs/research/_archive/` | After completion |
| Session docs | `docs/_archive/YYYY-MM/` | 30 days |

### Never-Touch Folders

| Folder | Reason |
|--------|--------|
| `.git/` | Git internals |
| `.venv/` | Python environment |
| `node_modules/` | Dependencies |
| `__pycache__/` | Python cache |

---

## 🤖 For AI Agents

### Mandatory Rules

1. **NEVER manually `rm` or `mv` files** - Use safe scripts
2. **ALWAYS `--dry-run` first** - Preview before execute
3. **ALWAYS verify links after** - Run check_links.py
4. **ALWAYS commit atomically** - One operation per commit

### Decision Tree

```
Want to delete a file?
├── Check references: python scripts/safe_file_delete.py <file> --dry-run
│   ├── No references → Safe to delete
│   └── Has references → Either:
│       ├── Fix references first, then delete
│       └── Move to archive instead (preserves content)
└── Delete: python scripts/safe_file_delete.py <file>

Want to move a file?
├── Preview: python scripts/safe_file_move.py <old> <new> --dry-run
├── Check for collisions at destination
└── Execute: python scripts/safe_file_move.py <old> <new>

Not sure if file is needed?
├── Check orphan status: python scripts/find_orphan_files.py --age
├── Check git history: git log --oneline -5 -- <file>
└── If orphan + old → Archive
    If linked → Keep
    If recent → Keep
```

### Common Mistakes to Avoid

| Mistake | Correct Approach |
|---------|------------------|
| `rm docs/old.md` | `python scripts/safe_file_delete.py docs/old.md` |
| `mv docs/a.md docs/b.md` | `python scripts/safe_file_move.py docs/a.md docs/b.md` |
| Delete without checking | Always `--dry-run` first |
| Batch delete many files | Delete one at a time with commits |
| Skip link check after | Always run `check_links.py` after |

---

*Guide created: 2026-01-10 | Part of folder cleanup automation system*

# Agent 9 Quick Start - Governance & Documentation Structure

**Get started with Agent 9 in 60 seconds.**

---

## What is Agent 9?

Agent 9 is the **governance and documentation structure agent**, ensuring sustainable information architecture, migration safety, and folder organization rules.

**Key Result:** Clear navigation paths, minimal root clutter, governed structure changes.

---

## Quick Start

### 1. Check Governance Rules First
```bash
# Read the governing document for any folder/doc changes
open docs/guidelines/folder-structure-governance.md
```

### 2. Review Current Status
```bash
# Check migration status before making structural changes
open docs/guidelines/migration-workflow-guide.md
```

### 3. Validate Changes
```bash
# Run validation bundle after any structure changes
.venv/bin/python scripts/check_governance.py --structure
.venv/bin/python scripts/check_links.py
.venv/bin/python scripts/check_docs.py --index-links
```

**That's it!** Agent 9 ensures:
- ✅ Folder structure follows governance rules
- ✅ Root directory stays clean (<10 files)
- ✅ Documentation is discoverable
- ✅ Links remain valid
- ✅ Migrations are safe and traceable

---

## The One Rule

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ ALWAYS check governance rules before moving    ┃
┃ or renaming files/folders!                     ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

**Why?** Ungoverned changes cause:
- Root directory clutter (>10 files)
- Broken navigation paths
- Link rot
- Lost documentation
- Duplicate information

---

## Decision Tree (File Placement)

```
Is this a dated document (contains YYYY-MM-DD)?
    ├─ YES → sessions/YYYY-MM/ (time buckets)
    └─ NO  → Is it agent-specific?
        ├─ YES → agents/roles/ or docs/agents/guides/
        └─ NO  → docs/ with proper category

Is this a root-level file?
    ├─ YES → Only if: README, LICENSE, CHANGELOG, CODE_OF_CONDUCT
    └─ NO  → Move to appropriate folder

Is this a script?
    ├─ YES → Must stay in scripts/ (Rule 3.2)
    └─ NO  → Follow folder structure rules
```

---

## Essential Commands

| Command | Purpose |
|---------|---------|
| `check_governance.py --structure` | Check rule compliance |
| `check_links.py` | Find broken links |
| `check_docs.py --index-links` | Verify index accuracy |
| `check_root_file_count.sh` | Ensure <10 root files |
| `generate_dashboard.sh` | Update metrics |

---

## Common Tasks

### Task 1: Move a Document
```bash
# 1. Check if it violates rules
.venv/bin/python scripts/check_governance.py --structure

# 2. Use safe_file_move.py (preserves history + updates links)
.venv/bin/python scripts/safe_file_move.py old/path.md new/path.md

# 3. Update all references
rg "old/path.md" docs/ agents/ .github/

# 4. Validate links
.venv/bin/python scripts/check_links.py

# 5. Commit with Agent 8
./scripts/ai_commit.sh "docs: move X to follow governance rules"
```

### Task 2: Create Agent Entry Point
```bash
# 1. Create in docs/agents/guides/
#    (Entry points for quick-start)

# 2. Link from docs/agents/README.md

# 3. Keep role docs in agents/roles/
#    (Agent role definitions)

# 4. Validate
.venv/bin/python scripts/check_links.py
```

### Task 3: Run Structure Validation
```bash
# 1. Run governance compliance check
.venv/bin/python scripts/check_governance.py

# 2. Read governance spec
open docs/guidelines/folder-structure-governance.md

# 3. Review migration guide
open docs/guidelines/migration-workflow-guide.md

# 4. Validate after each batch
.venv/bin/python scripts/check_links.py
```

### Task 4: Archive Old Docs (Safe)
```bash
# 1. Preview archive candidates
.venv/bin/python scripts/batch_archive.py --files file1.md file2.md --dry-run

# 2. Execute with stub redirect
.venv/bin/python scripts/batch_archive.py --files file1.md file2.md --stub

# 3. Validate links
.venv/bin/python scripts/check_links.py
```

---

## Governance Documents (Full Detail)

**Main Hub:** [docs/guidelines/folder-structure-governance.md](../../guidelines/folder-structure-governance.md)

**Key Resources:**
- [folder-structure-governance.md](../../guidelines/folder-structure-governance.md) - All naming + placement rules
- [migration-workflow-guide.md](../../guidelines/migration-workflow-guide.md) - Migration procedures
- [folder-cleanup-workflow.md](../../guidelines/folder-cleanup-workflow.md) - Cleanup procedures
- [migration-preflight-checklist.md](../../guidelines/migration-preflight-checklist.md) - Pre-migration checks

**Validation Scripts:**
- `check_governance.py` - Full compliance check
- `check_links.py` - Link validation
- `check_root_file_count.sh` - Root file limit check

---

## PR Workflow for Structure Changes

```bash
# 1. Create task branch
./scripts/create_task_pr.sh GOV-001 "Reorganize X per rules"

# 2. Make changes (safe_file_move.py for moves)
.venv/bin/python scripts/safe_file_move.py old/path.md new/path.md

# 3. Update references
# ... edit files ...

# 4. Validate
.venv/bin/python scripts/check_governance.py --structure
.venv/bin/python scripts/check_links.py

# 5. Commit
./scripts/ai_commit.sh "docs: reorganize X per governance rules"

# 6. Create PR
./scripts/finish_task_pr.sh GOV-001 "Reorganize X"

# 7. Merge when green
gh pr merge <num> --squash --delete-branch
```

---

## Common Mistakes to Avoid

| Mistake | Correct Approach |
|---------|------------------|
| Moving scripts out of scripts/ | Scripts MUST stay in scripts/ (Rule 3.2) |
| Manual mv without safe_file_move.py | Use safe_file_move.py to preserve history |
| Creating deep nesting (>3 levels) | Keep 2-3 levels max |
| Root file accumulation | Move to folders, keep root <10 |
| Case-only renames on macOS | Avoid or use content-preserving method |
| Multiple "authoritative" docs | One hub + links only |
| Skipping validation after changes | Always run validation bundle |
| Forgetting to update references | Search and update all links |

---

## Emergency Recovery

If structure changes cause issues:

1. **Check validation errors:**
   ```bash
   .venv/bin/python scripts/check_governance.py --structure
   ```

2. **Find broken links:**
   ```bash
   .venv/bin/python scripts/check_links.py --fix
   ```

3. **Review recent changes:**
   ```bash
   git log --oneline --follow <file>
   ```

4. **Rollback if needed:**
   ```bash
   # See ROLLBACK-PROCEDURES.md for levels
   git revert <commit>
   ```

---

## Navigation Best Practices

1. **Progressive disclosure:** Start with this quick-start → go to governance hub → read specific doc
2. **Information scent:** Use clear, descriptive filenames
3. **Front door pattern:** Entry points in `docs/agents/guides/`, detail docs in `agents/agent-N/`
4. **Link hygiene:** Always use relative paths, validate after changes
5. **Time buckets:** Dated docs go in `sessions/YYYY-MM/`

---

## Need More Detail?

- **Full governance rules:** [folder-structure-governance.md](../../guidelines/folder-structure-governance.md)
- **Governance hub:** [agent-9-governance-hub.md](agent-9-governance-hub.md)
- **Migration workflow:** [migration-workflow-guide.md](../../guidelines/migration-workflow-guide.md)
- **Agent role docs:** [agents/roles/](../../../agents/roles/)

---

**Last Updated:** 2026-01-11
**Owner:** Agent 9 (Governance)
**Status:** Active

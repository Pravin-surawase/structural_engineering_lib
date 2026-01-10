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
open agents/agent-9/governance/FOLDER_STRUCTURE_GOVERNANCE.md
```

### 2. Review Current Status
```bash
# Check migration status before making structural changes
open agents/agent-9/governance/MIGRATION-STATUS.md
```

### 3. Validate Changes
```bash
# Run validation bundle after any structure changes
.venv/bin/python scripts/validate_folder_structure.py
.venv/bin/python scripts/check_links.py
.venv/bin/python scripts/check_docs_index_links.py
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
        ├─ YES → agents/agent-N/
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
| `validate_folder_structure.py` | Check rule compliance |
| `check_links.py` | Find broken links |
| `check_docs_index_links.py` | Verify index accuracy |
| `check_root_file_count.sh` | Ensure <10 root files |
| `generate_dashboard.sh` | Update metrics |

---

## Common Tasks

### Task 1: Move a Document
```bash
# 1. Check if it violates rules
.venv/bin/python scripts/validate_folder_structure.py

# 2. Use git mv (preserves history)
git mv old/path.md new/path.md

# 3. Update all references
grep -r "old/path.md" docs/ agents/ .github/

# 4. Validate links
.venv/bin/python scripts/check_links.py

# 5. Commit with Agent 8
./scripts/ai_commit.sh "docs: move X to follow governance rules"
```

### Task 2: Create Agent Entry Point
```bash
# 1. Create in docs/agents/guides/
#    (NOT in agents/agent-N/ - that's internal)

# 2. Link from docs/agents/README.md

# 3. Keep detail docs in agents/agent-N/
#    (governance separation)

# 4. Validate
.venv/bin/python scripts/check_links.py
```

### Task 3: Run Migration Phase
```bash
# 1. Check status
open agents/agent-9/governance/MIGRATION-STATUS.md

# 2. Read phase doc
open agents/agent-9/governance/PHASE-N-*.md

# 3. Follow step-by-step tasks
open agents/agent-9/governance/MIGRATION-TASKS.md

# 4. Validate after each batch
./scripts/validate_bundle.sh
```

---

## Governance Documents (Full Detail)

**Main Hub:** [agents/agent-9/governance/README.md](../../../agents/agent-9/governance/README.md)

**Key Rules:**
- [FOLDER_STRUCTURE_GOVERNANCE.md](../../../agents/agent-9/governance/FOLDER_STRUCTURE_GOVERNANCE.md) - All naming + placement rules
- [MIGRATION-STATUS.md](../../../agents/agent-9/governance/MIGRATION-STATUS.md) - Current status + audit trail
- [AUTOMATION-CATALOG.md](../../../agents/agent-9/governance/AUTOMATION-CATALOG.md) - All validation checks
- [PHASE-B-TASK-TRACKER.md](../../../agents/agent-9/governance/PHASE-B-TASK-TRACKER.md) - Current task progress

**Historical:** See [Archive](../../../agents/agent-9/governance/_archive/) for Phase A planning docs

---

## PR Workflow for Structure Changes

```bash
# 1. Create task branch
./scripts/create_task_pr.sh GOV-001 "Reorganize X per rules"

# 2. Make changes (git mv for moves)
git mv old/path.md new/path.md

# 3. Update references
# ... edit files ...

# 4. Validate
.venv/bin/python scripts/validate_folder_structure.py
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
| Manual mv without git mv | Use git mv to preserve history |
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
   .venv/bin/python scripts/validate_folder_structure.py
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

- **Full governance rules:** [FOLDER_STRUCTURE_GOVERNANCE.md](../../../agents/agent-9/governance/FOLDER_STRUCTURE_GOVERNANCE.md)
- **Governance hub:** [agent-9-governance-hub.md](agent-9-governance-hub.md)
- **All Agent 9 docs:** [agents/agent-9/governance/README.md](../../../agents/agent-9/governance/README.md)
- **Phase A history:** [Archive](../../../agents/agent-9/governance/_archive/)

---

**Last Updated:** 2026-01-10
**Owner:** Agent 9 (Governance)
**Status:** Active

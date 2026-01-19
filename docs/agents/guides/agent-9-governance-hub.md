# Agent 9 Governance Hub

**Quick access to all Agent 9 governance documentation.**

---

## What is Agent 9?

Agent 9 manages **governance, documentation structure, and migration safety** for the project. It ensures sustainable information architecture through clear rules and validation.

---

## Main Hub

**→ [docs/guidelines/folder-structure-governance.md](../../guidelines/folder-structure-governance.md)**

This is the canonical governance specification for all folder structure rules, naming conventions, and validation requirements.

---

## Quick Links

### Getting Started
- **[Agent 9 Quick Start](agent-9-quick-start.md)** - 60-second workflow guide
- **[Folder Structure Rules](../../guidelines/folder-structure-governance.md)** - All naming and placement rules

### Active Documents
- **[Migration Progress](../../planning/folder-migration-progress.md)** - Current progress tracker
- **[Migration Workflow Guide](../../guidelines/migration-workflow-guide.md)** - How to do migrations
- **[Folder Cleanup Workflow](../../guidelines/folder-cleanup-workflow.md)** - Cleanup procedures
- **[Automation Catalog](../../reference/automation-catalog.md)** - All validation checks

### Archived (Historical Reference)
Migration Phase A-D complete. Historical docs are archived:
- **[Agent-9 Legacy Governance](../../_archive/2026-01/agent-9-governance-legacy/)** - Phase A-D planning docs

---

## Validation Commands

Run these after any structure changes:

```bash
# Check folder structure compliance
.venv/bin/.venv/bin/python scripts/validate_folder_structure.py

# Find broken links
.venv/bin/.venv/bin/python scripts/check_links.py

# Verify doc index
.venv/bin/.venv/bin/python scripts/check_docs_index_links.py

# Check root file count
./scripts/check_root_file_count.sh
```

---

## Key Governance Rules

### Rule 1: Root Directory (<10 files)
Only essential project files at root: README, LICENSE, CHANGELOG, CODE_OF_CONDUCT, etc.

### Rule 2: Kebab-Case Naming
All files use `kebab-case-names.md` (except generated files like `CHANGELOG.md`)

### Rule 3: Scripts Stay in scripts/
**NEVER** move scripts out of `scripts/` - they are shared infrastructure

### Rule 4: Time Buckets for Dated Docs
Documents with dates go in `sessions/YYYY-MM/` (e.g., `sessions/2026-01/`)

### Rule 5: Agent Separation
- **Public entry points:** `docs/agents/guides/`
- **Internal details:** `agents/agent-N/`

### Rule 6: Safe Moves Preserve History + Links
Always use `scripts/safe_file_move.py`, never manual `mv`

---

## Navigation Pattern

```
1. Start here (agent-9-governance-hub.md)
   ↓
2. Read canonical governance (docs/guidelines/folder-structure-governance.md)
   ↓
3. Execute task
   ↓
4. Validate with scripts
```

---

## Common Workflows

### Workflow 1: Check Governance Rules
```bash
# Before making structure changes
open docs/guidelines/folder-structure-governance.md
```

### Workflow 2: Move a Document
```bash
# Use safe_file_move.py to preserve history and update links
.venv/bin/.venv/bin/python scripts/safe_file_move.py old/path.md new/folder/path.md

# Review references
rg "old/path.md" docs/ agents/

# Validate
.venv/bin/.venv/bin/python scripts/check_links.py
```

---

## Need Help?

1. **Quick questions:** Check [Agent 9 Quick Start](agent-9-quick-start.md)
2. **Detailed rules:** See [folder-structure-governance.md](../../guidelines/folder-structure-governance.md)
3. **Progress tracking:** See [folder-migration-progress.md](../../planning/folder-migration-progress.md)
4. **Historical docs:** Browse [Archive](../../_archive/2026-01/agent-9-governance-legacy/)

---

**Navigation Philosophy:**
**Canonical governance in `docs/guidelines/` → Agent guides in `docs/agents/guides/`**

This consolidates governance to a single source of truth.

---

**Last Updated:** 2026-01-10
**Owner:** Agent 9 (Governance)
**Status:** Active

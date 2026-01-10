# Agent 9 Governance Hub

**Quick access to all Agent 9 governance documentation.**

---

## What is Agent 9?

Agent 9 manages **governance, documentation structure, and migration safety** for the project. It ensures sustainable information architecture through clear rules and validation.

---

## Main Hub

**→ [agents/agent-9/governance/README.md](../../../agents/agent-9/governance/README.md)**

This is the canonical entry point for all governance documents, migration plans, and folder structure rules.

---

## Quick Links

### Getting Started
- **[Agent 9 Quick Start](agent-9-quick-start.md)** - 60-second workflow guide
- **[Folder Structure Rules](../../../agents/agent-9/governance/FOLDER_STRUCTURE_GOVERNANCE.md)** - All naming and placement rules

### Decision Making
- **[Decision Summary](../../../agents/agent-9/governance/DECISION-SUMMARY.md)** - Final questions and readiness
- **[Migration Review](../../../agents/agent-9/governance/AGENT-9-AND-MIGRATION-REVIEW.md)** - Review synthesis

### Execution
- **[Migration Status](../../../agents/agent-9/governance/MIGRATION-STATUS.md)** - Current progress and blockers
- **[Migration Tasks](../../../agents/agent-9/governance/MIGRATION-TASKS.md)** - Step-by-step execution
- **[Full Migration Plan](../../../agents/agent-9/governance/FULL-MIGRATION-EXECUTION-PLAN.md)** - Complete ultra-safe plan

### Safety
- **[Rollback Procedures](../../../agents/agent-9/governance/ROLLBACK-PROCEDURES.md)** - Recovery steps
- **[Migration Risks](../../../agents/agent-9/governance/MIGRATION_REVIEW_AND_RISKS.md)** - Known risks and mitigations

### Validation
- **[Validation Scripts](../../../agents/agent-9/governance/MIGRATION-SCRIPTS.md)** - All validation tools
- **[Metrics Dashboard](../../../agents/agent-9/governance/METRICS_DASHBOARD.md)** - Auto-generated metrics

---

## Phase Documentation

All migration phases are documented in detail:

- [Phase 0: Preparation](../../../agents/agent-9/governance/PHASE-0-PREPARATION.md)
- [Phase 1: Structure Creation](../../../agents/agent-9/governance/PHASE-1-STRUCTURE-CREATION.md)
- [Phase 2: Agents Migration](../../../agents/agent-9/governance/PHASE-2-AGENTS-MIGRATION.md)
- [Phase 4: Dated Files](../../../agents/agent-9/governance/PHASE-4-DATED-FILES.md)
- [Phase 5: Naming Cleanup](../../../agents/agent-9/governance/PHASE-5-NAMING-CLEANUP.md)
- [Phase 6: Link Fixing](../../../agents/agent-9/governance/PHASE-6-LINK-FIXING.md)
- [Phase 7: Script Updates](../../../agents/agent-9/governance/PHASE-7-SCRIPT-UPDATES.md)
- [Phase 8: Final Validation](../../../agents/agent-9/governance/PHASE-8-FINAL-VALIDATION.md)

---

## Validation Commands

Run these after any structure changes:

```bash
# Check folder structure compliance
.venv/bin/python scripts/validate_folder_structure.py

# Find broken links
.venv/bin/python scripts/check_links.py

# Verify doc index
.venv/bin/python scripts/check_docs_index_links.py

# Check root file count
./scripts/check_root_file_count.sh

# Update metrics dashboard
./scripts/generate_dashboard.sh
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

### Rule 6: Git History Preservation
Always use `git mv` for file moves, never manual `mv`

---

## Navigation Pattern

```
1. Start here (agent-9-governance-hub.md)
   ↓
2. Go to main hub (agents/agent-9/governance/README.md)
   ↓
3. Read specific doc (e.g., FOLDER_STRUCTURE_GOVERNANCE.md)
   ↓
4. Execute task
   ↓
5. Validate with scripts
```

---

## Common Workflows

### Workflow 1: Check Governance Rules
```bash
# Before making structure changes
open agents/agent-9/governance/FOLDER_STRUCTURE_GOVERNANCE.md
```

### Workflow 2: Move a Document
```bash
# Use git mv to preserve history
git mv old/path.md new/folder/path.md

# Update references
grep -r "old/path.md" docs/ agents/

# Validate
.venv/bin/python scripts/check_links.py
```

### Workflow 3: Run Migration Phase
```bash
# Check current status
open agents/agent-9/governance/MIGRATION-STATUS.md

# Read phase doc
open agents/agent-9/governance/PHASE-N-*.md

# Execute tasks
open agents/agent-9/governance/MIGRATION-TASKS.md

# Validate
./scripts/validate_bundle.sh
```

---

## Research & Context

For background on governance decisions:

- **[Research Summary](../../../agents/agent-9/governance/FOLDER_GOVERNANCE_RESEARCH_SUMMARY.md)** - Research basis for rules
- **[Navigation Study Results](../../../docs/research/)** - Agent navigation research

---

## Need Help?

1. **Quick questions:** Check [Agent 9 Quick Start](agent-9-quick-start.md)
2. **Detailed rules:** See [FOLDER_STRUCTURE_GOVERNANCE.md](../../../agents/agent-9/governance/FOLDER_STRUCTURE_GOVERNANCE.md)
3. **Migration help:** Read [MIGRATION-WALKTHROUGH.md](../../../agents/agent-9/governance/MIGRATION-WALKTHROUGH.md)
4. **All docs:** Browse [agents/agent-9/governance/README.md](../../../agents/agent-9/governance/README.md)

---

**Navigation Philosophy:**
**Front door in `docs/agents/guides/` → Detail docs stay in `agents/agent-9/governance/`**

This preserves governance separation while providing fast access.

---

**Last Updated:** 2026-01-10
**Owner:** Agent 9 (Governance)
**Status:** Active

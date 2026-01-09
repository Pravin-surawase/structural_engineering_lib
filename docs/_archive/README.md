# Archive Directory

This directory contains historical documentation that was once in the project root but has been moved here to reduce clutter and improve discoverability.

## Archive Strategy

**Time-Based Organization:** Files are organized by year-month (YYYY-MM) based on when they were archived, not when they were created.

**Retention:** Archives are permanent. They preserve:
- Git history (via `git mv`, not `git rm`)
- Cross-references from other docs (links updated to point here)
- Historical context for debugging and understanding project evolution

## What Gets Archived?

### 1. Completion Docs (Write-Once-Read-Never)
- Agent session completion logs (e.g., `AGENT-6-FEAT-001-COMPLETE.md`)
- **Lifecycle:** Created at end of session, referenced once in handoff, then never read
- **Archive Trigger:** 7 days after creation
- **Value:** Historical record of what was completed and when

### 2. Crisis/Fix Docs (Technical Debt Indicators)
- Bug fix plans, import error fixes, autonomous fixes applied
- **Lifecycle:** Created during crisis, used to resolve issue, then obsolete
- **Archive Trigger:** When issue is resolved and merged
- **Value:** Documents technical debt patterns and how they were resolved

### 3. Handoff/Session Docs (Rapid Decay)
- Session handoffs, work summaries, delegation docs
- **Lifecycle:** Created for next session, relevant <7 days, then superseded
- **Archive Trigger:** When next session completes and creates new handoff
- **Value:** Historical record of session transitions

### 4. Research/Workflow Docs (Superseded)
- Research summaries, workflow guides
- **Lifecycle:** Created during exploration, refined into canonical docs
- **Archive Trigger:** When refined version exists in `docs/` directory
- **Value:** Shows evolution of thinking and design decisions

## Finding Archived Content

### By Date
```bash
# Find all docs from January 2026
ls docs/_archive/2026-01/
```

### By Type
```bash
# Find all Agent 6 completion docs
find docs/_archive/ -name "AGENT-6-*-COMPLETE.md"

# Find all crisis/fix docs
find docs/_archive/ -name "*FIX*.md" -o -name "*BUG*.md"

# Find all handoff docs
find docs/_archive/ -name "*HANDOFF*.md" -o -name "*SESSION*.md"
```

### By Content
```bash
# Search archive content
grep -r "search term" docs/_archive/
```

## Automation

Archival is automated via governance scripts:

- **Manual:** `scripts/archive_old_sessions.sh` (TASK-283)
- **Scheduled:** Weekly governance sessions (TASK-284)
- **Checks:** CI fails if >10 root files (TASK-281)

## Archive Statistics

As of **2026-01-10:**
- **Total archived:** 38 files (34 .md + 4 .txt/.sh)
- **Root reduction:** 41 → 9 files (78% reduction)
- **Leading indicators resolved:** Crisis docs (9→0), Handoffs (6→0), Completions (13→0)

## Related Documentation

- [Root File Governance Policy](../planning/root-file-governance.md) (planned)
- [Agent 9 Research Findings](../../agents/agent-9/research/RESEARCH_FINDINGS_STRUCTURE.md)
- [Metrics Baseline](../../agents/agent-9/research/METRICS_BASELINE.md)
- [Implementation Roadmap](../../agents/agent-9/AGENT_9_IMPLEMENTATION_ROADMAP.md)

---

**Last Updated:** 2026-01-10
**Maintainer:** Agent 9 (Governance)

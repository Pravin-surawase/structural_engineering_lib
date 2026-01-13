# Archive Directory

This directory contains historical documentation that was once in the project root but has been moved here to reduce clutter and improve discoverability.

**Last Updated:** 2026-01-11 (Session 9)

---

## 📂 Archive Contents

### [2026-01/](2026-01/) — January 2026 Archives
Session handoffs, agent completions, and bug fixes from January 2026.

| File | Description |
|------|-------------|
| [agent-6-feat-001-complete.md](2026-01/agent-6-feat-001-complete.md) | Agent 6 feature completion |
| [agent-6-mega-session-complete.md](2026-01/agent-6-mega-session-complete.md) | Mega session summary |
| [autonomous-fixes-applied.md](2026-01/autonomous-fixes-applied.md) | Autonomous fix records |
| [cost-optimizer-fix-report.md](2026-01/cost-optimizer-fix-report.md) | Cost optimizer fixes |
| [scanner-enhanced-complete.md](2026-01/scanner-enhanced-complete.md) | AST scanner enhancements |
| *...and 27 more files* | |

### [planning/](planning/) — Archived Planning Docs
Old task specs, agent handoffs, and completed planning documents.

| File | Description |
|------|-------------|
| [agent-5-tasks.md](planning/agent-5-tasks.md) | Agent 5 task list |
| [v0.16-task-specs.md](planning/v0.16-task-specs.md) | v0.16 specifications |
| [v0.17-task-specs.md](planning/v0.17-task-specs.md) | v0.17 specifications |
| [migration-execution-plan.md](planning/migration-execution-plan.md) | IS 456 migration plan |
| *...and 36 more files* | |

### [publications/](publications/) — Archived Publication Drafts
Research findings and blog drafts that have been superseded.

| File | Description |
|------|-------------|
| [00-research-summary.md](publications/00-research-summary.md) | Research summary |
| [01-engineer-pain-points.md](publications/01-engineer-pain-points.md) | Pain points analysis |
| [blog-outlines-updated.md](publications/blog-outlines-updated.md) | Blog content outlines |
| *...and 8 more files* | |

### [misc/](misc/) — Miscellaneous Archives
Specs, troubleshooting, and reference docs no longer active.

| File | Description |
|------|-------------|
| [etabs-integration.md](misc/etabs-integration.md) | ETABS integration spec |
| [v0.5-excel-spec.md](misc/v0.5-excel-spec.md) | Old Excel specifications |
| [excel-faq.md](misc/excel-faq.md) | Excel troubleshooting |
| [merge-conflict-prevention.md](misc/merge-conflict-prevention.md) | Git workflow docs |
| [pylint-vs-ast-comparison.md](misc/pylint-vs-ast-comparison.md) | Linting comparison |

### Root Archives
Historical files archived from project root.

| File | Description |
|------|-------------|
| [research-and-findings.md](research-and-findings.md) | Combined research findings |
| [session-log-2025-12-28.md](session-log-2025-12-28.md) | Old session log |
| [tasks-2025-12-27.md](tasks-2025-12-27.md) | Old task board |
| [tasks-history.md](tasks-history.md) | Task history |
| [v0.7-requirements.md](v0.7-requirements.md) | v0.7 requirements |
| [v0.8-execution-checklist.md](v0.8-execution-checklist.md) | v0.8 checklist |

---

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

As of **2026-01-11 (Session 9):**
- **Total archived:** 119 files
- **Subfolders:** 2026-01 (32), planning (40), publications (11), misc (5), contributing (1)
- **Root files:** 6 legacy files
- **Orphan reduction:** 176 → 169 (Session 8), target <100

## Related Documentation

- [Session 9 Master Plan](research-sessions/session-9-master-plan.md) - Current cleanup plan
- [Folder Restructuring Plan](../research/folder-restructuring-plan.md) - Overall strategy
- [File Operations Safety Guide](../guidelines/file-operations-safety-guide.md) - Automation scripts

---

**Last Updated:** 2026-01-11
**Maintainer:** Agent 9 (Governance)

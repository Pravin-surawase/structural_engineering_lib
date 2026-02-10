# Agent Bootstrap - Complete Review & Link Analysis
**Date:** 2026-01-19
**Status:** ✅ Updated for agent-bootstrap v2.1.1

---

## Overview

`docs/getting-started/agent-bootstrap.md` is the 60-second onboarding entrypoint for any agent. This review enumerates every link in that file, explains why it exists, and notes the current startup flow (`./scripts/agent_start.sh`).

---

## Quick Reference: Bootstrap Links Map

| # | Link | Section | Priority | Purpose |
|---|------|---------|----------|---------|
| 1 | docs/contributing/agent-onboarding-message.md | Onboarding note | P3 | Exact message to onboard new agents |
| 2 | docs/agents/guides/agent-quick-reference.md | Guide hierarchy | P2 | Commands and emergency shortcuts |
| 3 | docs/agents/guides/agent-workflow-master-guide.md | Guide hierarchy | P2 | Full workflow decision trees |
| 4 | ~~docs/getting-started/ai-context-pack.md~~ | Deprecated | - | Merged into agent-bootstrap.md |
| 5 | docs/TASKS.md | Required context | P1 | Current work board and priorities |
| 6 | docs/planning/next-session-brief.md | Required context | P1 | Latest handoff and blockers |
| 7 | .github/copilot-instructions.md | Quick reference | P1 | Mandatory workflow rules |
| 8 | docs/contributing/git-workflow-ai-agents.md | Quick reference | P1 | Git decision rules |
| 9 | docs/reference/automation-catalog.md | Quick reference | P2 | Inventory of automation scripts |
| 10 | docs/contributing/handoff.md | Quick reference | P2 | Session resume/end workflow |
| 11 | docs/contributing/background-agent-guide.md | Quick reference | P2 | Safe parallel agent work |
| 12 | docs/reference/api.md | Quick reference | P3 | API signatures and units |
| 13 | docs/reference/known-pitfalls.md | Quick reference | P3 | Common mistakes checklist |
| 14 | docs/contributing/session-issues.md | Quick reference | P3 | Recurring issues and fixes |
| 15 | docs/agents/README.md | Quick reference | P3 | Agent roles and prompts |
| 16 | docs/_archive/planning/project-status.md | Quick reference | P3 | Historical status (archived) |
| 17 | docs/planning/project-status-deep-dive.md | Quick reference | P3 | Detailed status history |

---

## P1 - Critical Path (Read First)

### 1) ~~docs/getting-started/ai-context-pack.md~~ (DEPRECATED)
- Merged into agent-bootstrap.md. Read agent-bootstrap.md instead.

### 2) docs/TASKS.md
- Single source of truth for active work and WIP limits.

### 3) docs/planning/next-session-brief.md
- Latest handoff, blockers, and what changed.

### 4) .github/copilot-instructions.md
- Mandatory workflow rules, commit policy, and testing expectations.

### 5) docs/contributing/git-workflow-ai-agents.md
- Git decision tree and PR vs direct commit rules.

---

## P2 - Essential Workflow

### Agent guides
- docs/agents/guides/agent-quick-reference.md
- docs/agents/guides/agent-workflow-master-guide.md

### Workflow support
- docs/reference/automation-catalog.md
- docs/contributing/handoff.md
- docs/contributing/background-agent-guide.md

---

## P3 - Reference & Background

### API + pitfalls
- docs/reference/api.md
- docs/reference/known-pitfalls.md

### Ops and roles
- docs/contributing/session-issues.md
- docs/agents/README.md

### Historical status
- docs/_archive/planning/project-status.md
- docs/planning/project-status-deep-dive.md

---

## Non-Link References in Bootstrap (Still Important)

The bootstrap also references these tools or docs without linking them directly:
- docs/reference/api-stability.md (API stability policy)
- scripts/generate_api_manifest.py (API manifest)
- scripts/check_api.py --docs (API signature validation)
- scripts/check_repo_hygiene.py (hygiene audit)
- scripts/safe_file_move.py / scripts/safe_file_delete.py (safe file operations)

---

## Startup Flow Notes

- Primary entrypoint: `./scripts/agent_start.sh --quick`
- `agent_start.sh` remains in use under `agent_start.sh` for environment validation.
- `session.py start` still runs as part of the unified start flow.

---

## Suggested Reading Path

**New agent (first session):**
1. docs/getting-started/agent-bootstrap.md (canonical — contains all essential context)
2. docs/TASKS.md
3. docs/planning/next-session-brief.md

**Returning agent:**
1. docs/planning/next-session-brief.md
2. docs/TASKS.md
3. .github/copilot-instructions.md (if any workflow change)


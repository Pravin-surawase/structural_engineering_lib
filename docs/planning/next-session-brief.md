---
owner: Main Agent
status: active
last_updated: 2026-04-01
doc_type: guide
complexity: intermediate
tags: []
---

# Next Session Briefing

**Type:** Handoff
**Audience:** All Agents
**Status:** Active
**Importance:** Critical
**Created:** 2025-01-01
**Last Updated:** 2026-04-01

---

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-04-01
- Session: Session 1 — CI/Docker optimization + TASK-620
- Done: Merged Docker CI jobs (~5 min savings), Trivy enforces CRITICAL, cap_drop/no-new-privileges added, TASK-620 stack trace sanitization complete
- Remaining: TASK-642 (5-point steel curve) is next, then TASK-635 (biaxial bending)
- State: main branch (pending commit)
<!-- HANDOFF:END -->

| Release | Version | Status |
|---------|---------|--------|
| **Current** | v0.20.0 | 🔄 React UX Overhaul + Library Expansion |
| **Next** | v0.22.0 | 📋 Planned |

---

## What's Next

> **Master Plan:** [library-expansion-blueprint-v5.md](library-expansion-blueprint-v5.md)

1. **TASK-642 (5-point steel curve)** ← **START HERE**
2. **TASK-635 (biaxial bending)** — depends on TASK-642
3. **TASK-636 (effective length)** — parallelizable with TASK-635
4. **P12 Burn-in (15-20 sessions)** — OBSERVE + MEASURE only, no EVOLVE yet
5. **Quality scripts** — TASK-622/623/624 (check_function_quality, check_clause_coverage, check_new_element_completeness)

### Technical Debt

- 2 architecture violations: rebar_optimizer/multi_objective_optimizer bypass api facade
- ~13 backward-compat stub imports in streamlit_app/
- 28 unit conversion warnings in IS 456 code (documented)

---

## Required Reading

1. [TASKS.md](../TASKS.md) — current task board & priorities
2. [agent-bootstrap.md](../getting-started/agent-bootstrap.md) — full project reference
3. [api.md](../reference/api.md) — API reference (29 public functions)

---

## Quick Commands

```bash
./run.sh session start              # Begin work
./run.sh commit "type: message"     # Safe commit (THE ONE RULE)
./run.sh check --quick              # Fast validation (<30s)
./run.sh pr create TASK-XXX "desc"  # Start a PR
./run.sh test                       # Run pytest
docker compose up --build           # FastAPI at :8000/docs
cd react_app && npm run dev         # React at :5173
```

## Key Files

- Task tracking: [docs/TASKS.md](../TASKS.md)
- Session history: [docs/SESSION_LOG.md](../SESSION_LOG.md)
- Agent bootstrap: [docs/getting-started/agent-bootstrap.md](../getting-started/agent-bootstrap.md)

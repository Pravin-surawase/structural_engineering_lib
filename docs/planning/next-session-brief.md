---
owner: Main Agent
status: active
last_updated: 2026-04-02
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
**Last Updated:** 2026-04-02

---

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-04-02
- Session: Claw-code implementation Sessions 2+3 — agent infrastructure
- Done: 19/23 claw-code tasks complete (TASK-850 through TASK-872, except 861/867/869/871)
- Remaining: Session 4 — TASK-861 (trust gate), TASK-867 (snapshot tests), TASK-869 (update agent files), TASK-871 (update entry docs)
- State: main branch, all scripts created and reviewed
- New commands: ./run.sh route, ./run.sh tools, ./run.sh pipeline
<!-- HANDOFF:END -->

| Release | Version | Status |
|---------|---------|--------|
| **Current** | v0.20.0 | 🔄 React UX Overhaul + Library Expansion |
| **Next** | v0.22.0 | 📋 Planned |

---

## What's Next

1. **Session 4 — Final claw-code tasks** ← START HERE
   - TASK-861: Trust gate (defer destructive ops until session start confirms clean state)
   - TASK-867: Snapshot regression tests (assert minimum script/tool/test counts)
   - TASK-869: Update all 15 .agent.md files with permission_level, registry_ref
   - TASK-871: Update AGENTS.md + CLAUDE.md with new commands (route, tools, pipeline)
2. **TASK-638 (long column design)** — `design_long_column` orchestrator
3. **TASK-640 (design_column_is456 orchestrator)** — combines all column functions

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

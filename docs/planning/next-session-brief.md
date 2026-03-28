# Next Session Briefing

**Type:** Handoff
**Audience:** All Agents
**Status:** Active
**Importance:** Critical
**Created:** 2025-01-01
**Last Updated:** 2026-03-28<br>
Date:** 2026-03-28

---

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-03-28
<!-- HANDOFF:END -->

| Release | Version | Status |
|---------|---------|--------|
| **Previous** | v0.20.0 | ✅ Done (React migration complete) |
| **Current** | v0.19.1 | 🔄 React UX Overhaul + Library Expansion |
| **Next** | v0.22.0 | 📋 Planned |

**Last Session:** Session 104 (Git Automation Knowledge Transfer) | **Focus:** Git automation audit + agent feedback loop

---

## Session 104 Summary

**Completed:** Git automation audit → knowledge transfer to agents → feedback loop mechanism → pipeline alignment fix → comprehensive prompt quality pass

**Files Updated:**
- `.github/agents/ops.agent.md` — Git architecture, error recovery, feedback loop
- `.github/agents/orchestrator.agent.md` — Governance cadence, git awareness
- `.github/agents/reviewer.agent.md` — Git hygiene checklist, feedback escalation
- `.github/prompts/master-workflow.prompt.md` — 6-step pipeline + feedback rules

**Key Outcomes:**
- ✅ Git automation knowledge documented and accessible
- ✅ Feedback loop: 2x warning → 3x enforcement → 5x redesign
- ✅ Pipeline audit caught and fixed skipped steps
- ✅ Comprehensive prompt quality pass: fixed 19 issues across 11 files (endpoint counts 35→38, hook counts 18→20, removed Streamlit refs, standardized commands)

**Known Issues:**
- `should_use_pr.sh` doesn't check fastapi_app/ or react_app/ paths — verify intentional
- `commit_template.txt` is empty — consider adding conventional commit examples
- Consider JSON logging for ai_commit.sh telemetry

---

## Required Reading

- [TASKS.md](../TASKS.md) — Current task tracking
- [SESSION_LOG.md](../SESSION_LOG.md) — Session history
- [agent-bootstrap.md](../getting-started/agent-bootstrap.md) — Agent setup
- [AGENTS.md](../../AGENTS.md) — Cross-agent instructions
- [CLAUDE.md](../../CLAUDE.md) — Claude-specific instructions

---

## Next Priorities

### Do First — UX Polish + Library Expansion

1. **TASK-525: Smart HubPage** ← START HERE
   - Replace ModeSelectPage with smart hub: quick actions + resume last project

2. **TASK-517: Project BOQ** — Aggregate BBS → project quantities
3. **TASK-519: Alternatives Panel (Pareto)** — Expose multi_objective_optimizer.py
4. **TASK-527: TopBar settings + TASK-528: Breadcrumb** — Settings panel + workflow navigation

### Design Principles
- **Editor is the workstation** → manual form only in `/design`
- **Data-first** → import → navigate 3D → click beam → see reinforcement
- **IS 456 accuracy** → top bars match between 3D/2D, utilization = Mu/Mu_cap

### Recently Completed
- TASK-505: API integration tests (86 tests, 12 routers)
- TASK-510: Batch design page
- TASK-514: PDF export
- TASK-515: Load calculator
- TASK-518: Torsion API

### Technical Debt
- 2 architecture violations: rebar_optimizer/multi_objective_optimizer bypass api facade
- ~13 backward-compat stub imports in streamlit_app/
- 28 unit conversion warnings in IS 456 code (documented)

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

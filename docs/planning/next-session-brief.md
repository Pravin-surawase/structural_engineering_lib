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

**Last Session:** Session 105 (Agent Testing + Architecture Fixes) | **Focus:** Agent testing, architecture fixes, shear tests, commit PR #441

---

## Session 105 Summary

**Completed:** Agent testing (8.7/10) → architecture fixes → shear tests → agent infrastructure → committed PR #441

**Files Updated:**
- `react_app/src/components/design/BeamDetailPanel.tsx` — 3 arch violations fixed
- `fastapi_app/routers/analysis.py`, `design.py` — import fixes
- `Python/structural_lib/codes/is456/shear.py` — num_legs bug fixed
- `Python/tests/unit/test_shear.py` — +234 lines new tests
- `.github/agents/`, `.github/skills/`, `.github/prompts/`, `scripts/` — self-evolving system

**Key Outcomes:**
- ✅ All agents scored, audit documented
- ✅ 3 arch violations + 2 import bugs + 1 num_legs bug fixed
- ✅ Shear test coverage significantly expanded
- ✅ Self-evolving infrastructure complete (governance, tester, health, feedback, evolve)
- ✅ PR #441 open

**Known Issues:**
- Agent terminal PATH issue NOT fixed yet: agents try `cd Python && .venv/bin/pytest` (wrong venv location)
- Phase 6 (archive planning docs) not started
- PR #441 CI pending

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

### Do First — Agent Terminal Fixes + UX Polish

1. **FIX AGENT TERMINAL PATHS** ← URGENT (prevents wasted tokens each session)
   - All agents need correct venv path: `.venv/` is at PROJECT ROOT, not in Python/
   - Correct pytest: from project root = `.venv/bin/pytest Python/tests/ -v`
   - Correct pytest from Python/ subdir = `../.venv/bin/pytest tests/ -v`
   - Update all .github/agents/*.agent.md files with a "Terminal Commands" section

2. **TASK-525: Smart HubPage**
   - Replace ModeSelectPage with smart hub: quick actions + resume last project

3. **Phase 6: Archive stale planning docs** (43 active → target <10)
4. **TASK-517: Project BOQ** — Aggregate BBS → project quantities

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

# Next Session Briefing

**Type:** Handoff
**Audience:** All Agents
**Status:** Active
**Importance:** Critical
**Created:** 2025-01-01
**Last Updated:** 2026-03-25

---

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-03-25
<!-- HANDOFF:END -->

| Release | Version | Status |
|---------|---------|--------|
| **Current** | v0.19.1 | Shipped |
| **Next** | v0.20.0 | React migration — nearly complete |

**Last Session:** Session 96 | **Focus:** TASK-510 merged, TopBar nav, feature audit

---

## Session 96 Summary

### TASK-510 Merged + Navigation Upgraded
- Merged TASK-510 (batch design page) to main
- TopBar: added compact inline nav links (Design, Import, Batch, Editor, Dashboard) — desktop shows nav, mobile shows breadcrumbs
- ModeSelectPage: added contextual quick-links when beams are loaded (Editor, Batch Design, Dashboard)
- Build passes (0 TypeScript errors)

### Feature Audit: No New Pages Needed
- **TASK-511 (compliance)** — Already exists: `useCodeChecks()` hook + `CodeChecksPanel` in DesignView + hardcoded checks in BuildingEditor sidebar
- **TASK-512 (cost optimizer)** — Already exists: `useRebarSuggestions()` hook + panel in DesignView
- Both marked as "Not needed" in TASKS.md — features already built, no standalone pages required
- React app is now **feature-complete** relative to Streamlit (except AI assistant)

---

## Next Priorities

1. **TASK-505: E2E Docker + React test** — 13 routers need integration tests
2. **Wire BuildingEditor Cost tab** — currently placeholder, wire to real data
3. **TASK-513: AI assistant port** — needs OpenAI/LLM integration design for React
4. **Manual testing** — CSV import → batch design → dashboard flow end-to-end

### Recently Completed
- **TASK-508** - Split `ai_workspace.py` (5103→5314 lines, 7 files) — commit `b9b2733`
- **TASK-503** - REST fallback in DesignView — commit `cad5e24`
- **TASK-506** - Vitest + 5 test suites (23 tests) — commit `ff3a937`
- **TASK-507** - Fix arch violations + dead test — commit `0e6657e`

### Technical Debt
- **2 architecture violations** - rebar_optimizer/multi_objective_optimizer bypass api facade
- **~13 backward-compat stub imports** in streamlit_app/ - functional but messy
- **28 unit conversion warnings** in IS 456 code - documented via var names

---

## Quick Commands

```bash
./run.sh session start              # Begin work
./run.sh commit "type: message"     # Safe commit (THE ONE RULE)
./run.sh check --quick              # Fast validation (<30s)
./run.sh check                      # Full validation (28 checks)
./run.sh pr create TASK-XXX "desc"  # Start a PR
./run.sh pr finish                  # Ship the PR
./run.sh find "topic"               # Find scripts
./run.sh test                       # Run pytest
docker compose up --build           # FastAPI at :8000/docs
cd react_app && npm run dev         # React at :5173
```

---

## Key Files

| Purpose | Location |
|---------|----------|
| Task tracking | [docs/TASKS.md](../TASKS.md) |
| Session history | [docs/SESSION_LOG.md](../SESSION_LOG.md) |
| Git workflow audit | [docs/audit/git-workflow-audit-pr436.md](../audit/git-workflow-audit-pr436.md) |
| Agent essentials | [docs/getting-started/agent-essentials.md](../getting-started/agent-essentials.md) |
| API hooks | [react_app/src/hooks/](../../react_app/src/hooks/) |

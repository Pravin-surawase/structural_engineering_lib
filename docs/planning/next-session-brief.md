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
| **Next** | v0.20.0 | React migration (batch design, compliance, cost optimizer) |

**Last Session:** Session 95 | **Focus:** React migration — TASK-510 batch design page

---

## Session 95 Summary

### TASK-510: React Batch Design Page (In PR)
- Created `useBatchDesign.ts` SSE hook (EventSource → progress tracking, cancel support)
- Created `BatchDesignPage.tsx` (beam selection table → live progress bar → results table with utilization badges)
- Added `/batch` route to App.tsx with lazy loading
- Build passes (0 TypeScript errors)
- Branch: `task/TASK-510`, commit: `2861429`
- **Needs:** Review and merge PR, then manual testing with CSV import → batch design flow

### Strategic Shift
- Assessed TASK-509 (Streamlit type annotations) as low-value given React migration
- Rewrote TASKS.md: all new features go to React, Streamlit bug fixes only
- Added TASK-510/511/512/513 for React migration work

---

## Next Priorities

1. **Finish TASK-510 PR** — merge batch design page, test with `npm run dev`
2. **TASK-511: Compliance checker React page** (insights/code-checks → React) — 🔴 High
3. **TASK-512: Cost optimizer React page** (optimization.py → React) — 🟡 Medium
4. **TASK-505: E2E Docker + React test** — 13 routers need integration tests
5. **Add navigation link** — add "Batch Design" to TopBar/ModeSelectPage so users can reach `/batch`

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

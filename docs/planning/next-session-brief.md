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
- Session: 93 (continued)
- Branch: main (PR #436 merged)
<!-- HANDOFF:END -->

| Release | Version | Status |
|---------|---------|--------|
| **Current** | v0.19.1 | Shipped |
| **Next** | v0.20.0 | V3 Foundation (code-splitting, SSE progress, REST fallback) |

**Last Session:** Session 93 | **Focus:** Unified CLI merged + git workflow audit

---

## Session 93 Summary

### PR #436 Merged to Main (TASK-500)
- Created `run.sh` (~600 lines, 9 subcommands) + `check_all.py` (28 checks, 9 categories)
- Archived 7 Streamlit-era scripts (85 to 78 active)
- Fixed 46 to 15 stale refs, 4 runtime breaks, updated all agent docs
- Git workflow audit: `docs/audit/git-workflow-audit-pr436.md` (11 issues, 7 fixed)

### TASK-501: Pre-existing check failures
- 9 of 28 `check_all.py` checks were pre-existing failures - fixed in PR

---

## Next Priorities

1. **Code-split Three.js bundles** - index.js chunk is 1.16 MB
2. **REST fallback in DesignView** - when WebSocket is unavailable
3. **SSE batch progress UI** - streaming.py router exists, needs React consumer
4. **React test infrastructure** - Zero test files, needs Vitest + core tests
5. **Split ai_workspace.py** - 5103 lines to 6 modules (needs dedicated PR)
6. **Governance single source of truth** - make governance-limits.json the only config

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

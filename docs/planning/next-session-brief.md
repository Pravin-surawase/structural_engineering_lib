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
- Date: 2026-03-24
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

### TASK-501: Pre-existing check failures (PR pending)
- check_all.py improved from 19/28 → 25/28 (6 checks fixed)
- Fixed: API validation, API stability sync, API manifest, doc front-matter, OpenAPI snapshot, TASKS.md format, broken links, brief trimming
- Remaining 3 failures are tech debt (documented in TASKS.md Backlog): architecture boundaries (2 Streamlit violations), import validation (293 legacy), type annotations (68 gaps)
- Branch: `task/TASK-501`, commit: `f40f807`

---

## Next Priorities

1. **Code-split Three.js bundles** (TASK-502) - index.js chunk is 1.16 MB
2. **SSE batch progress UI** (TASK-504) - streaming.py router exists, needs React consumer
3. **E2E Docker + React test** (TASK-505) - 13 routers need integration tests
4. **Type annotations** (TASK-509) - 49 missing return types + 4 missing `__all__` in Streamlit
5. **Governance single source of truth** - make governance-limits.json the only config

### Recently Completed
- **TASK-508** - Split `ai_workspace.py` (5103→5314 lines, 7 files) — commit `b9b2733`
- **TASK-503** - REST fallback in DesignView — commit `cad5e24`
- **TASK-506** - Vitest + 5 test suites (23 tests) — commit `ff3a937`
- **TASK-507** - Fix arch violations + dead test — commit `0e6657e`

### Technical Debt
- **2 architecture violations** - rebar_optimizer/multi_objective_optimizer bypass api facade
- **~13 backward-compat stub imports** in streamlit_app/ - functional but messy
- **28 unit conversion warnings** in IS 456 code - documented via var names
- **Original ai_workspace.py** renamed to `ai_workspace_ORIGINAL_BACKUP.py` — can be deleted once package is stable

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

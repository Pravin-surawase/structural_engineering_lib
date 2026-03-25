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
| **Previous** | v0.20.0 | ✅ Done (React migration complete) |
| **Current** | v0.21.0 | 🔄 React UX Overhaul + Library Expansion |

**Last Session:** Session 99 | **Focus:** TASK-518 Torsion API + React, WORKLOG.md creation

---

## Session 99 Summary

### Completed

| Task | What was done | Commit |
|------|--------------|--------|
| **WORKLOG.md** | Created compact append-only work log (one line per change) | — |
| **agent-bootstrap** | Added WORKLOG.md to session workflow + quick-scan table | — |
| **TASK-518** | Torsion design — FastAPI endpoint + Pydantic models + React hook + DesignView toggle + results panel + 3 API tests (103 total) | — |

### Files Changed
- `docs/WORKLOG.md` (NEW) — compact change log
- `fastapi_app/models/beam.py` — `TorsionDesignRequest` + `TorsionDesignResponse` models
- `fastapi_app/routers/design.py` — `POST /api/v1/design/beam/torsion` endpoint
- `react_app/src/api/client.ts` — `TorsionDesignRequest/Response` types + `designBeamTorsion()` function
- `react_app/src/hooks/useTorsionDesign.ts` (NEW) — `useTorsionDesign` mutation hook
- `react_app/src/components/design/DesignView.tsx` — torsion toggle in Design Forces + TorsionResultsPanel
- `fastapi_app/tests/test_endpoints.py` — 3 new torsion tests
- `docs/getting-started/agent-bootstrap.md` — WORKLOG reference + torsion endpoint
- `CLAUDE.md` — Added WORKLOG to session end workflow

---

## Next Priorities

### Do first — Library exposes more functions through the app

1. **TASK-515: Load Calculator** ← START HERE
   - Python `compute_bmd_sfd()` already exists, needs FastAPI endpoint + React panel
   - New: `POST /api/v1/analysis/loads/simple`
   - New: `useLoadAnalysis` hook + `LoadCalculatorPanel.tsx`
   - Feeds Mu/Vu directly into DesignView

2. **TASK-525: Smart HubPage**
   - Replace ModeSelectPage with smart hub: quick actions + resume last project

3. **TASK-514: PDF Export**
   - HTML report → PDF via WeasyPrint
   - Extend existing export router + `useExportReport` hook

4. **TASK-517: Project BOQ**
   - Aggregate BBS across beams → project-level quantities

### Design Principles (carry forward)
- **Editor is the workstation** — manual form only in `/design`
- **Data-first** — import project → navigate 3D → click beam → see reinforcement
- **IS 456 accuracy** — top bars match between 3D and 2D views, utilization is Mu/Mu_cap
- Full UX spec: [react-ux-improvement-plan.md](react-ux-improvement-plan.md)

### Recently Completed
- **TASK-505** - API integration tests (86 tests, 12 routers) — commit `a732e62`
- **TASK-510** - Batch design page (merged to main)
- **TopBar nav** + ModeSelect quick-links — commit `7710eb9`

### Technical Debt
- **2 architecture violations** - rebar_optimizer/multi_objective_optimizer bypass api facade
- **~13 backward-compat stub imports** in streamlit_app/ - functional but messy
- **28 unit conversion warnings** in IS 456 code - documented via var names
- **0 tests** for services/report.py (1700+ lines) — addressed by TASK-520

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

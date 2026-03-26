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
| **Next** | v0.22.0 | 📋 Planned |

**Last Session:** Session 99 | **Focus:** TASK-515 Load Calculator, TASK-514 PDF Export, TASK-518 Torsion API

---

## Session 99 Summary

### Completed

| Task | What was done | Commit |
|------|--------------|--------|
| **WORKLOG.md** | Created compact append-only work log (one line per change) | — |
| **agent-bootstrap** | Added WORKLOG.md to session workflow + quick-scan table | — |
| **TASK-518** | Torsion design — FastAPI endpoint + Pydantic models + React hook + DesignView toggle + results panel + 3 API tests | — |
| **TASK-515** | Load Calculator — FastAPI endpoint `POST /api/v1/analysis/loads/simple` + Pydantic models + `useLoadAnalysis` hook + MiniDiagram SVG + DesignView Load Calculator panel + 4 API tests | — |
| **TASK-514** | PDF Export — `export_pdf()` via WeasyPrint + FastAPI format=pdf + React PDF button + 4 export tests + fix ReportData construction bug | — |

### Files Changed
- `docs/WORKLOG.md` (NEW) — compact change log
- `fastapi_app/models/beam.py` — `TorsionDesignRequest` + `TorsionDesignResponse` models
- `fastapi_app/models/analysis.py` — `LoadItem`, `LoadAnalysisRequest`, `LoadAnalysisResponse` models
- `fastapi_app/routers/design.py` — `POST /api/v1/design/beam/torsion` endpoint
- `fastapi_app/routers/analysis.py` — `POST /api/v1/analysis/loads/simple` endpoint
- `fastapi_app/routers/export.py` — PDF format support + fix ReportData construction
- `react_app/src/api/client.ts` — Torsion + LoadAnalysis types and API functions
- `react_app/src/hooks/useTorsionDesign.ts` (NEW) — `useTorsionDesign` mutation hook
- `react_app/src/hooks/useLoadAnalysis.ts` (NEW) — `useLoadAnalysis` mutation hook
- `react_app/src/hooks/useExport.ts` — PDF format support in export hook
- `react_app/src/components/design/DesignView.tsx` — torsion toggle, Load Calculator panel with MiniDiagram, PDF export button, DropdownField made generic
- `Python/structural_lib/services/report.py` — `export_pdf()` function via WeasyPrint
- `requirements.txt` — Added `weasyprint>=60.0`
- `fastapi_app/tests/test_endpoints.py` — 4 load analysis + 4 export tests (36 total)
- `docs/getting-started/agent-bootstrap.md` — WORKLOG reference + torsion endpoint
- `CLAUDE.md` — Added WORKLOG to session end workflow

---

## Next Priorities

### Do first — UX polish + remaining library expansion

1. **TASK-525: Smart HubPage** ← START HERE
   - Replace ModeSelectPage with smart hub: quick actions + resume last project

2. **TASK-517: Project BOQ**
   - New `boq.py` module — aggregate BBS across beams → project-level quantities
   - New FastAPI endpoint `POST /api/v1/insights/project-boq`
   - New `useProjectBOQ` hook + panel

3. **TASK-519: Alternatives Panel (Pareto)**
   - Expose existing `multi_objective_optimizer.py` (637 lines) via FastAPI
   - New `POST /api/v1/optimization/beam/pareto` endpoint
   - New `useParetoDesign` hook + panel in DesignView

4. **TASK-527: TopBar settings + TASK-528: Breadcrumb**
   - TopBar settings icon → SettingsPanel slide-over
   - Workflow breadcrumb for batch flow

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

## Required Reading

- [docs/getting-started/agent-bootstrap.md](../getting-started/agent-bootstrap.md)
- [docs/TASKS.md](../TASKS.md)

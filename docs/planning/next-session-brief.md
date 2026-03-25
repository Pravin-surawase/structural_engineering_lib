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

**Last Session:** Session 98 | **Focus:** React UX overhaul — 6 tasks completed + 3 bugs fixed

---

## Session 98 Summary

### Completed (6 UX tasks + 3 bug fixes)

| Task | What was done | Commit |
|------|--------------|--------|
| **TASK-522** | BeamDetailPanel in BuildingEditorPage — beam click → 3D rebar + cross-section + results + redesign button + edit rebar mode + export | `a242878`, `a5612b0` |
| **TASK-523** | FloatingDock activated in App.tsx (AppDock component, macOS spring dock on all pages except `/`) | `a242878` |
| **TASK-524** | DesignView dynamic layout — 3D expands when no result, collapse/expand toggle, export dropdown, CompactResultsBar, preset button | `a242878` |
| **TASK-526** | CrossSectionView annotations — `ascRequired`, `barDia`, `barCount`, `utilization` props, emerald/amber/rose color coding | `a242878`, `a5612b0` |
| **DashboardPage** | Complete rewrite with BentoGrid layout + export buttons (BBS, Report) in page header | `a242878` |
| **Backend** | Added `utilization_ratio = Mu/Mu_cap` to `BatchDesignResult` in `imports.py` | `a5612b0` |

### Bugs Fixed

| Bug | Root Cause | Fix |
|-----|-----------|-----|
| 3D shows 3 top bars, 2D shows 2 | CrossSectionView used `Math.min(2, ceil(numBars*0.3))` while 3D API uses `select_bar_arrangement(0.25*Ast)` | Added `ascRequired` prop; computes `ceil(ascRequired/barArea)` |
| Utilization % was wrong | Was `ast_required/(0.04*b*D)` (steel ratio), should be `Mu/Mu_cap` | Added `utilization_ratio` to backend BatchDesignResult |
| Stirrup 275 not 300 | **Not a bug** — IS 456 Cl 26.5.1.5: `max_sv = min(0.75d, 300)`. For d≈367: 0.75×367=275 governs | Added annotation showing governing limit |

---

## Next Priorities

### Do first — React UX Phase A (remaining items)

1. **TASK-525: Smart HubPage** ← START HERE
   - Replace ModeSelectPage with smart hub: quick actions + resume last project
   - New file: `components/pages/HubPage.tsx` (~150 lines)
   - Read `useImportedBeamsStore` for last project context

2. **TASK-527: TopBar context badges + Settings**
   - Add material/beam count badges to right side of TopBar
   - Fix settings button (dead link) → slide-over SettingsPanel

3. **TASK-528: Workflow breadcrumb**
   - Step indicator on batch flow pages: Import → Editor → Batch → Dashboard
   - New `WorkflowBreadcrumb.tsx` (~60 lines)

4. **CommandPalette (Ctrl+K)** — already coded, just needs global keybind wiring

### Then — Library Expansion (TASK-514–521)
See [next-phase-improvements-plan.md](next-phase-improvements-plan.md) Part 2 for full specs.
- TASK-518 (Torsion) is easiest — Python is FULLY IMPLEMENTED, only needs FastAPI + React

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

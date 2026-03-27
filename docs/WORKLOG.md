# Work Log

> **One line per item. Compact. Append-only.**
> Format: `DATE | TASK-ID | what changed | commit`

**Type:** Reference
**Audience:** All Agents
**Status:** Approved
**Importance:** Critical
**Created:** 2026-03-25
**Last Updated:** 2026-03-25

---

## Rules

1. **Every code change gets a line** — no exceptions
2. **One line** — date, task, change, commit hash
3. **Agents must append here** at session end (see agent-bootstrap §2)
4. Don't delete old entries — this is append-only

---

## Log

| Date | Task | Change | Commit |
|------|------|--------|--------|
| 2026-03-25 | TASK-522 | BeamDetailPanel — beam click → 3D rebar + results + redesign + edit rebar | `a242878`, `a5612b0` |
| 2026-03-25 | TASK-523 | FloatingDock + BentoGrid Dashboard activated | `a242878` |
| 2026-03-25 | TASK-524 | DesignView dynamic layout — 3D expands when no result, export dropdown | `a242878` |
| 2026-03-25 | TASK-526 | CrossSectionView annotations — utilization color, ascRequired, barDia/barCount | `a242878`, `a5612b0` |
| 2026-03-25 | BUG | Fix 3D/2D top bar mismatch — CrossSectionView now uses ascRequired prop | `a5612b0` |
| 2026-03-25 | BUG | Fix utilization formula — BatchDesignResult.utilization_ratio = Mu/Mu_cap | `a5612b0` |
| 2026-03-25 | FEAT | Single-beam redesign button + editable rebar mode in BeamDetailPanel | `a5612b0` |
| 2026-03-25 | DOCS | Session 98 — update bootstrap, README, UX plan, TASKS, next-session-brief | `ffd5173` |
| 2026-03-25 | DOCS | Created WORKLOG.md compact change log + updated agent-bootstrap + CLAUDE.md | — |
| 2026-03-25 | TASK-518 | Torsion FastAPI endpoint — `POST /api/v1/design/beam/torsion` + Pydantic models | — |
| 2026-03-25 | TASK-518 | Torsion React — `useTorsionDesign` hook + DesignView toggle + TorsionResultsPanel | — |
| 2026-03-25 | TASK-518 | 3 new API tests — basic, unsafe section, validation (103 total) | — |
| 2026-03-25 | TASK-515 | Load Calculator FastAPI endpoint `POST /api/v1/analysis/loads/simple` + Pydantic models | — |
| 2026-03-25 | TASK-515 | Load Calculator React — `useLoadAnalysis` hook + MiniDiagram SVG + DesignView Load Calculator panel | — |
| 2026-03-25 | TASK-515 | 4 load analysis tests — UDL, point load, cantilever, validation (36 total) | — |
| 2026-03-25 | TASK-514 | PDF Export — `export_pdf()` in report.py + WeasyPrint + FastAPI format=pdf | — |
| 2026-03-25 | TASK-514 | PDF Export React — useExport pdf format + PDF button in DesignView export dropdown | — |
| 2026-03-25 | TASK-514 | 4 export tests — HTML, JSON, PDF, invalid format + fix ReportData construction bug | — |
| 2026-03-27 | TASK-101 | Mac Mini migration fixes — CSV import crash, sample building 404, xlwings crash, Dockerfile, Vite IPv6, doc links | PR #440 |
| 2026-03-27 | TASK-102 | Remove all Streamlit remnants — 21 scripts cleaned, 4 orphaned tests deleted (1627 lines), dxf docstring fixed | PR #440 |
| 2026-03-27 | BUG | Fix uvicorn IPv6 bind — `--host "::"` so browser's localhost→::1 reaches FastAPI | `docs only` |
| 2026-03-27 | DOCS | Add issue #9 (IPv6 uvicorn) to mac-mini-migration-issues.md + lessons learned | — |
| 2026-03-27 | DOCS | Add IPv6 rows to agent-bootstrap.md troubleshooting + common mistakes tables | — |
| 2026-03-27 | DOCS | Update mac-mini-setup.md + github-fix-plan.md with IPv6 root cause & fix | — |
| 2026-03-25 | BUG | Fix export router ReportData construction — was passing wrong field names | — |

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
| 2026-03-28 | PROMPTS | Comprehensive quality pass: fixed 7 issues across 11 files (agents, prompts, instructions) | 8fb7aeb2 |
| 2026-03-28 | PROMPTS | Fixed endpoint count 35→38 in AGENTS.md, CLAUDE.md, fastapi.instructions.md | 8fb7aeb2 |
| 2026-03-28 | PROMPTS | Removed streamlit_app/ references from active instructions (5 files) | 8fb7aeb2 |
| 2026-03-28 | PROMPTS | Standardized session commands to ./run.sh format in session-end.prompt.md, doc-master.agent.md | 8fb7aeb2 |
| 2026-03-28 | PROMPTS | Updated hook count 18→20 in frontend.agent.md, added PR check to new-feature.prompt.md | 8fb7aeb2 |
| 2026-03-28 | AGENTS | Added git system architecture, error recovery, historical mistakes, feedback loop to ops.agent.md | b28d8b04 |
| 2026-03-28 | AGENTS | Added governance cadence and git awareness to orchestrator.agent.md | b28d8b04 |
| 2026-03-28 | AGENTS | Added git hygiene checklist and feedback-to-orchestrator to reviewer.agent.md | b28d8b04 |
| 2026-03-28 | AGENTS | Updated master-workflow.prompt.md: 5→6 step pipeline, added feedback loop with escalation rules | b28d8b04 |
| 2026-03-28 | AGENTS | Fixed duplicates in ops.agent.md, consolidated error recovery tables, aligned pipeline counts | — |
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

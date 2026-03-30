---
owner: Main Agent
status: active
last_updated: 2026-03-30
doc_type: guide
complexity: intermediate
tags: []
---

# Work Log

> **One line per item. Compact. Append-only.**
> Format: `DATE | TASK-ID | what changed | commit`

**Type:** Reference
**Audience:** All Agents
**Status:** Approved
**Importance:** Critical
**Created:** 2026-03-25
**Last Updated:** 2026-03-29

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
| 2026-03-28 | Agent maintenance | Added A11y checklist to ui-designer.agent.md | pending |
| 2026-03-28 | Agent maintenance | Fixed frontend.agent.md hooks table: 9 → 21 hooks | pending |
| 2026-03-28 | Script audit | Rewrote scripts/_archive/README.md: 6 → 99 scripts documented | pending |
| 2026-03-28 | Script audit | Added ⚠️ Archived warnings to automation-catalog.md entries 56, 98 | pending |
| 2026-03-28 | TASK-AGENTS | Agent testing audit: all 11 agents tested, scored 8.7/10, identified 7 fix phases | ecfede46 |
| 2026-03-28 | PHASE-1-2 | Fix BeamDetailPanel arch violations (3), FastAPI router imports (2 files analysis+design) | ecfede46 |
| 2026-03-28 | PHASE-3 | Fix num_legs stirrup scaling bug in shear.py (effective_tv = tv * 2.0/num_legs) | ecfede46 |
| 2026-03-28 | PHASE-4 | Fix stale doc numbers in agent-bootstrap.md (agents 9→11, skills 4→6, prompts 8→13) | ecfede46 |
| 2026-03-28 | PHASE-7 | Add 234 lines shear tests: TestSelectStirrupDiameterNumLegs + 2 more classes | ecfede46 |
| 2026-03-28 | INFRA | Add governance/tester agents, architecture-check/react-validation skills, 3 prompts, 5 scripts | ecfede46 |
| 2026-03-28 | GIT | Commit 61 files to task/TASK-AGENTS, create PR #441 | ecfede46 |
| 2026-03-28 | Session 107 | Safety gates hardening: FORBIDDEN commands (5 files), CodeQL fix, ops no-script rule | — |
| 2026-03-28 | AGENTS | Add structural-math agent + new-structural-element skill + add-structural-element prompt + update orchestrator pipeline (8 steps) | — |
| 2026-03-28 | Session 105 | Agent testing audit (8.7/10), BeamDetailPanel fixes, shear tests (+234 lines), FastAPI import fixes, PR #441 | ecfede46 |
| 2026-03-28 | Session 106 | CI fix (3 root causes): Black formatting 3 files, Ruff F401 fix, circular import false positives fix | efc0384c |
| 2026-03-28 | Session 107 | Post-mortem Session 106 safety gates: FORBIDDEN commands in 5 files, CodeQL fix, ops no-script rule | — |
| 2026-03-28 | Session 108 | Agent infrastructure expansion: @structural-math agent, /new-structural-element skill, #add-structural-element prompt, orchestrator 6→8 steps | — |
| 2026-03-29 | Session 109 | Doc maintenance: batch metadata updates (53 docs), WORKLOG backfill S105-108, indexes regenerated, 2 docs archived | — |
| 2026-03-30 | SESSION-110 | Doc system overhaul: audit, tool research (MkDocs Material), Phase 1 implementation (budget check, CODEOWNERS, append-first policy, archive extension, SESSION_LOG rotation) | pending |
| 2026-03-30 | SESSION-110-P2 | MkDocs Material setup + frontmatter backfill (182 docs) + lychee CI workflow | pending |
| 2026-03-30 | TASK-525 | Created HubPage.tsx replacing ModeSelectPage — smart landing with quick actions + last session | Session 111 |
| 2026-03-30 | TASK-517 | Created services/boq.py — project BOQ aggregation from BBS data | Session 111 |
| 2026-03-30 | TASK-517 | Created FastAPI POST /api/v1/insights/project-boq endpoint | Session 111 |
| 2026-03-30 | TASK-517 | Created useProjectBOQ hook + ProjectBOQPanel + DashboardPage integration | Session 111 |
| 2026-03-30 | CI | Created deploy-docs.yml for MkDocs GitHub Pages auto-deploy | Session 111 |
| 2026-03-30 | CI | Expanded API docs to 15 modules, set link-check fail:true | Session 111 |

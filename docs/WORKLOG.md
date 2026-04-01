---
owner: Main Agent
status: active
last_updated: 2026-04-01
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
| 2026-04-01 | TASK-800.T | Added 84 evolver unit tests (scorer, drift, compliance, registry, data, scoring lib) | c1e0d222 |
| 2026-04-01 | TASK-800.P3 | Fixed agent_registry.py name extraction bug (.stem → .name.removesuffix) | c1e0d222 |
| 2026-04-01 | TASK-800.P3 | Created scripts/_lib/agent_registry.py, scoring.py, agent_data.py (shared evolver libs) | 8808c16b |
| 2026-04-01 | TASK-800.P4 | Created agent_session_collector.py (gather session artifacts for scoring) | 8808c16b |
| 2026-04-01 | TASK-800.P5 | Created agent_scorer.py (11-dimension scoring, auto+manual, composite grades) | d875dcfa |
| 2026-04-01 | TASK-800.P6 | Created agent_drift_detector.py (12 agents × drift rules, violation tracking) | d875dcfa |
| 2026-04-01 | TASK-800.P7 | Created agent_compliance_checker.py (8 compliance rules, per-agent checks) | d875dcfa |
| 2026-04-01 | TASK-800.P8 | Created agent_trends.py (Mann-Kendall trend test, degradation alerts) | d69c4a4f |
| 2026-04-01 | TASK-800.P10 | Created export_paper_data.py (CSV export, bootstrap CIs, Hedges' g) | d69c4a4f |
| 2026-04-01 | TASK-800.P9 | Created agent_evolve_instructions.py (SHA-256, security levels, rollback) | e0702346 |
| 2026-04-01 | TASK-800.P2 | Created agent-evolver.agent.md (15th meta-agent) + agent-evolution/SKILL.md | pending |
| 2026-03-31 | TASK-630 | Added ColumnClassification enum, ColumnAxialResult dataclass, E_COLUMN_001–005 error codes, 7 column constants | 69d4d2c3 |
| 2026-03-31 | TASK-631 | Implemented classify_column (Cl 25.1.2) and min_eccentricity (Cl 25.4) in codes/is456/column/axial.py | 69d4d2c3 |
| 2026-03-31 | TASK-632 | Implemented short_axial_capacity (Cl 39.3) with full validation in codes/is456/column/axial.py | 69d4d2c3 |
| 2026-04-01 | TASK-633 | feat(column): implement design_short_column_uniaxial() Cl 39.5 | 94f1005d |
| 2026-04-01 | TASK-633 | test(column): 45 tests for uniaxial bending (6 types) | 0ce8d69c |
| 2026-04-01 | TASK-633 | feat(column): wire uniaxial into services/api.py | 143b9d46 |
| 2026-04-01 | TASK-633 | feat(api): POST /api/v1/design/column/uniaxial endpoint + 12 API tests | 0fa31cd6 |
| 2026-03-31 | TASK-630+ | Wired 3 column API functions (classify/min_ecc/axial) to services/api.py with is456 suffix convention | 69d4d2c3 |
| 2026-03-31 | TASK-630+ | Created fastapi_app/routers/column.py with 3 POST endpoints (/classify, /eccentricity, /axial) | 69d4d2c3 |
| 2026-03-31 | TASK-630+ | 75 column tests: unit, boundary, edge, SP:16 benchmark, Hypothesis property-based | 69d4d2c3 |
| 2026-03-31 | TASK-630 | Fixed clause refs 39.6→39.3, boundary ≤→< in API wrappers + router | 69d4d2c3 |
| 2026-03-31 | TASK-712 | Enhanced shear near supports (Cl 40.3): new function + 14 tests + API endpoint | pending |
| 2026-03-31 | TASK-709,710 | Phase 0 complete: ductile.py→is13920, upward import fix, archive strategic-roadmap | 32f49571 |
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
| 2026-03-30 | TASK-611 | Created core/numerics.py — safe_divide(), approx_equal(), clamp() | — |
| 2026-03-30 | TASK-612 | Created codes/is456/common/ — stress_blocks.py, reinforcement.py, validation.py | — |
| 2026-03-30 | TASK-613 | Created codes/is456/common/constants.py — 22 IS 456 named constants | — |
| 2026-03-30 | TASK-614 | Extract @deprecated to core/deprecation.py + backward-compat re-exports | 8716c02c |
| 2026-03-30 | TASK-615 | Populate clauses.json: 22 new IS 456 subclauses (92→119), fix 33.2/33.3 numbering | 8716c02c |
| 2026-03-30 | TASK-616 | Add 5 IS 13920 entries (6.3, 7.4.1, 8.1, 9.2, 9.3), total 11→16 | 8716c02c |
| 2026-03-30 | — | Add 41 new tests: clauses.json schema (36) + deprecation import paths (5) | 8716c02c |
| 2026-03-31 | TASK-PREFLIGHT | fix: release preflight memory safety — timeouts, RAM check, NODE_OPTIONS, --docker flag, process group cleanup | — |
| 2026-03-31 | TASK-617,618,619 | Phase 1 Batch 4: test helpers, top-level exports, unit plausibility guards | pending |
| 2026-03-31 | — | Progress audit: Blueprint v5.0 §3.2 corrected, Phase 0 marked complete, Column design (TASK-630-632) planned | — |

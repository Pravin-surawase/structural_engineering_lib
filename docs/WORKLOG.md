---
owner: Main Agent
status: active
last_updated: 2026-04-04
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
**Last Updated:** 2026-04-04

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
| 2026-04-04 | TASK-681 | Migrated python-jose → PyJWT in auth.py, tests, CI | pending |
| 2026-04-04 | TASK-646 | IS 13920 Cl 7 column ductile detailing — completes Phase 2 Column (14/14) | pending |
| 2026-04-04 | maintenance | React test coverage: 5 component test files, 26 tests | pending |
| 2026-04-04 | TASK-647 | fix: should_use_pr.sh now detects fastapi_app + react_app + Docker as production code | `37d9ed77` |
| 2026-04-04 | TASK-647 | fix: ai_commit.sh removes --force suggestion from PR-blocked message, suggests --branch instead | `37d9ed77` |
| 2026-04-04 | TASK-647 | fix: pyproject.toml replaces 11 individual IS 456 per-file-ignores with 2 glob patterns + 9 new ignore-names | `37d9ed77` |
| 2026-04-03 | TASK-645 | Column detailing IS 456 Cl 26.5.3 — detailing.py + API + endpoint + 47 tests | feat(column) |
| 2026-04-01 | TASK-642 | feat: 5-point steel stress-strain curve (stress_blocks.py, uniaxial.py, 26 tests) | PR #481 |
| 2026-04-01 | TASK-636 | feat: effective length per IS 456 Table 28 (axial.py, EndCondition enum, 69 tests) | PR #481 |
| 2026-04-01 | TASK-636 | feat: POST /column/effective-length FastAPI endpoint + 12 API tests | PR #481 |
| 2026-04-01 | TASK-635 | feat: biaxial bending check IS 456 Cl 39.6 (biaxial.py, ColumnBiaxialResult, 84 tests) | PR #482 |
| 2026-04-01 | TASK-635 | feat: POST /column/biaxial-check FastAPI endpoint + 19 API tests | PR #482 |
| 2026-04-01 | TASK-800.T | Added 84 evolver unit tests (scorer, drift, compliance, registry, data, scoring lib) | c1e0d222 |
| 2026-04-01 | TASK-634 | Added P-M interaction curve (IS 456 Cl. 39.5) — core function, API wrapper, FastAPI endpoint, 45 tests | PR #478 |
| 2026-04-01 | TASK-800.P3 | Fixed agent_registry.py name extraction bug (.stem → .name.removesuffix) | c1e0d222 |
| 2026-04-01 | TASK-800.P3 | Created scripts/_lib/agent_registry.py, scoring.py, agent_data.py (shared evolver libs) | 8808c16b |
| 2026-04-01 | TASK-800.P4 | Created agent_session_collector.py (gather session artifacts for scoring) | 8808c16b |
| 2026-04-01 | TASK-800.P5 | Created agent_scorer.py (11-dimension scoring, auto+manual, composite grades) | d875dcfa |
| 2026-04-01 | TASK-800.P6 | Created agent_drift_detector.py (12 agents × drift rules, violation tracking) | d875dcfa |
| 2026-04-01 | TASK-800.P7 | Created agent_compliance_checker.py (8 compliance rules, per-agent checks) | d875dcfa |
| 2026-04-01 | TASK-800.P8 | Created agent_trends.py (Mann-Kendall trend test, degradation alerts) | d69c4a4f |
| 2026-04-02 | TASK-872 | Created skill_tiers.py — 3 tiers (core/specialist/experimental), validation | claw-code S3 |
| 2026-04-02 | TASK-870 | Added parallel pipeline to pipeline_state.py — PARALLEL_GROUPS, advance_parallel | claw-code S3 |
| 2026-04-02 | TASK-868 | Created config_precedence.py — 5 precedence levels, audit command | claw-code S3 |
| 2026-04-02 | TASK-866 | Created parity dashboard — 4 dimensions, 78% overall score | claw-code S3 |
| 2026-04-02 | TASK-865 | Created CLI smoke tests — 13 tests, all passing | claw-code S3 |
| 2026-04-02 | TASK-864 | Implemented 6 hooks — pre_commit(3), post_commit(2), pre_route(1) | claw-code S3 |
| 2026-04-02 | TASK-863 | Created hooks/ framework — HookRunner, auto-discovery, 5 event types | claw-code S3 |
| 2026-04-02 | TASK-853 | Added route, tools, pipeline commands to run.sh | claw-code S2 |
| 2026-04-02 | TASK-858 | Added --fast flag to session.py start — <1s startup | claw-code S2 |
| 2026-04-02 | TASK-857 | Created pipeline_state.py — 6 functions, JSON persistence, default+IS456 steps | claw-code S2 |
| 2026-04-02 | TASK-862 | Created audit_permissions.py — 5 anomaly checks, full audit reports | claw-code S2 |
| 2026-04-02 | TASK-860 | Created tool_permissions.py — 3 permission levels, file scope enforcement | claw-code S2 |
| 2026-04-02 | TASK-852 | Created prompt_router.py — 14 routing rules, weighted keyword scoring | claw-code S2 |
| 2026-04-02 | TASK-637 | feat(column): additional moment for slender columns IS 456 Cl 39.7.1 (slenderness.py, 24 tests) | PR #485 |
| 2026-04-02 | TASK-637 | feat(column): POST /column/additional-moment FastAPI endpoint + 8 API tests | PR #485 |
| 2026-04-01 | TASK-800.P10 | Created export_paper_data.py (CSV export, bootstrap CIs, Hedges' g) | d69c4a4f |
| 2026-04-01 | TASK-800.P9 | Created agent_evolve_instructions.py (SHA-256, security levels, rollback) | e0702346 |
| 2026-04-01 | TASK-800.P2 | Created agent-evolver.agent.md (15th meta-agent) + agent-evolution/SKILL.md | PR #476 |
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
| 2026-03-31 | TASK-712 | Enhanced shear near supports (Cl 40.3): new function + 14 tests + API endpoint | PR #468 |
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
| 2026-03-28 | Agent maintenance | Added A11y checklist to ui-designer.agent.md | committed |
| 2026-03-28 | Agent maintenance | Fixed frontend.agent.md hooks table: 9 → 21 hooks | committed |
| 2026-03-28 | Script audit | Rewrote scripts/_archive/README.md: 6 → 99 scripts documented | committed |
| 2026-03-28 | Script audit | Added ⚠️ Archived warnings to automation-catalog.md entries 56, 98 | committed |
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
| 2026-03-30 | SESSION-110 | Doc system overhaul: audit, tool research (MkDocs Material), Phase 1 implementation (budget check, CODEOWNERS, append-first policy, archive extension, SESSION_LOG rotation) | PR #451 |
| 2026-03-30 | SESSION-110-P2 | MkDocs Material setup + frontmatter backfill (182 docs) + lychee CI workflow | PR #452 |
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
| 2026-03-31 | TASK-617,618,619 | Phase 1 Batch 4: test helpers, top-level exports, unit plausibility guards | PR #469 |
| 2026-03-31 | — | Progress audit: Blueprint v5.0 §3.2 corrected, Phase 0 marked complete, Column design (TASK-630-632) planned | — |
| 2026-04-01 | CI/Docker | Merged docker-build + docker-security-scan into one job (~5 min savings) | PR #480 |
| 2026-04-01 | CI/Docker | Trivy now fails CI on CRITICAL vulns (exit-code: 1) | PR #480 |
| 2026-04-01 | Security | Added cap_drop: ALL + no-new-privileges to docker-compose.yml + dev | PR #480 |
| 2026-04-01 | Security | Trimmed security.yml to scan prod deps only | PR #480 |
| 2026-04-01 | TASK-620 | Stack trace sanitization in fastapi_app/main.py — generic exception handler | PR #480 |
| 2026-04-02 | TASK-861 | Trust gate initialization in session.py — trust state tracking for destructive op control | Session 4 |
| 2026-04-02 | TASK-867 | Snapshot regression tests — 10 tests guarding API surface counts | Session 4 |
| 2026-04-02 | TASK-869 | Updated all 15 agent .md files with permission_level + registry_ref | Session 4 |
| 2026-04-02 | TASK-871 | Updated AGENTS.md + CLAUDE.md + copilot-instructions.md with new commands | Session 4 |
| 2026-04-02 | TASK-621 | feat(core): add recovery field to DesignError + text for 39 errors | committed |
| 2026-04-02 | TASK-622 | feat(scripts): create check_function_quality.py 12-point checker | committed |
| 2026-04-02 | TASK-623 | feat(scripts): create check_clause_coverage.py clause gap scanner | committed |
| 2026-04-02 | TASK-624 | feat(scripts): create check_new_element_completeness.py matrix | committed |
| 2026-04-02 | TASK-625 | docs(governance): create maintenance-playbook.md 11 sections | committed |
| 2026-04-03 | TASK-651 | fix(footing): both-direction flexure design + Cl 34.3.1 steel distribution (F-004, F-005) | PR #496 |
| 2026-04-03 | TASK-653 | fix(footing): both-direction one-way shear check + governing direction (F-006) | PR #496 |
| 2026-04-03 | TASK-650 | fix(footing): 150mm minimum depth enforcement in _common.py (F-001) | PR #496 |
| 2026-04-03 | TASK-650 | fix(footing): FootingFlexureResult both-direction fields + central_band_fraction (F-008) | PR #496 |
| 2026-04-03 | TASK-650 | test(footing): 79 tests (16 new — both-direction, Cl 34.3.1, min depth) | PR #496 |
| 2026-04-04 | TASK-660 | Standardize IS 456 variable naming — 21 field renames, 4 dataclasses, ~60 files, backward-compat aliases | — |
| 2026-04-04 | TASK-670 | Fix calculation_report.py: 4 broken ShearResult fields + update templates + real-object tests | — |
| 2026-04-03 | TASK-671 | Fix 1: Unified effective depth — canonical `compute_effective_depth()` in core/geometry.py, updated inputs.py, models.py, design.py router | feat |
| 2026-04-03 | TASK-671 | Fix 2: Serviceability pipeline integration — `include_serviceability` opt-in flag in beam_pipeline.py, auto-constructs DeflectionParams | feat |
| 2026-04-03 | TASK-671 | Fix 3: Multi-layer rebar — RebarLayer + RebarArrangement dataclasses in data_types.py, calculate_effective_depth_multilayer() in flexure.py | feat |
| 2026-04-03 | TASK-671 | Fix 4: Failure story enhancement — ast_required_mm2 field in FailureScenario, redesign narrative in research_design_companion.py | feat |
| 2026-04-03 | TASK-671 | Updated FastAPI models: stirrup_dia_mm, main_bar_dia_mm, include_serviceability, RebarLayerConfig, DeflectionCheckResult, CrackWidthCheckResult | feat |
| 2026-04-03 | TASK-671 | Tests: 22 new tests, 4 fixed (effective depth assertions), 4193 Python + 180 FastAPI all passing | test |
| 2026-04-04 | TASK-690 | fix(column): SP:16 Table I continuity (C1/C2 at k=1.0), Cl 38.1 modified strain for xu>D, xu_bal with 0.002 inelastic strain, Pu_0 envelope cap | 832ec45f |
| 2026-04-04 | TASK-691 | fix(column): Cl 25.4 e_min enforcement in biaxial_bending_check for both axes | 832ec45f |
| 2026-04-04 | TASK-692 | fix(security): Sanitize 13 exception handlers in column.py router (CWE-209) | 832ec45f |
| 2026-04-04 | TASK-690 | fix(column): Add design_short_column_uniaxial, pm_interaction_curve, biaxial_bending_check to __all__ exports | 832ec45f |
| 2026-04-04 | TASK-690 | test(column): 7 updated + 6 new tests, 4258 total passing (0 failures) | 832ec45f |
| 2026-04-04 | RELEASE | v0.21.0 release — CHANGELOG finalized, version bump, 11+ docs updated | pending |
| 2026-04-04 | TASK-650-653 | Phase 3 Footing: bearing, flexure, one-way shear, punching shear (61 tests) | pending |
| 2026-04-04 | TASK-638 | Long column design (IS 456 Cl 39.7) — braced/unbraced, 23 tests | pending |
| 2026-04-04 | TASK-639 | Helical reinforcement (IS 456 Cl 39.4) — 1.05 enhancement, 14 tests | pending |
| 2026-04-04 | TASK-640-641 | Column orchestrator + 13 FastAPI endpoints | pending |
| 2026-04-04 | TASK-850-872 | Agent infrastructure: registry, router, permissions, hooks, pipeline | pending |
| 2026-04-04 | TASK-900 | Git workflow hardening (13/14 phases) | pending |
| 2026-04-04 | AUDIT-P0 | Fixed all 5 P0 audit findings: auth middleware, nightly CI, WCAG contrast, batch limits, bilinear tests | 2c8a2a9c |
| 2026-04-04 | AUDIT-P1 | Fixed 6 P1 findings: fck/fy validation, float tolerance, torsion guards, beam/column warnings, ErrorBoundary | pending |
| 2026-04-04 | AUDIT-P2-B1 | P2 Batch 1: 7 fixes (S-15 error sanitize, S-18 float-inf JSON, SM-6 ShearResult frozen, SM-8 bearing tolerance, SM-10 ColumnAxialResult frozen, API-8 BarAreasResponse model, API-10 DXF MIME) | — |
| 2026-04-05 | AUDIT-P2-B2 | P2 Batch 2: 7 fixes + 2 closures (OPS-4 IPv6, SM-7 puz validation, SM-9 steel_stress guards, FE-5 toast activation, BE-6 anchorage export, S-17 CLI path containment, DOC-7 CHANGELOG highlights; S-16/S-22 closed invalid) | — |
| 2026-04-05 | P2-Batch3 | S-19: sanitize_filename() for Content-Disposition headers | pending |
| 2026-04-05 | P2-Batch3 | API-9: Smoke calc in /health/ready with 30s cache | pending |
| 2026-04-05 | P2-Batch3 | A-2: importlib.resources in traceability.py (removed Path/open) | pending |
| 2026-04-05 | P2-Batch3 | IS-3: @clause decorators for 12 IS 13920 functions | pending |
| 2026-04-05 | P2-Batch3 | U-2: README package name callout prominence | pending |
| 2026-04-05 | P2-Batch3 | PH-3: 3 stale doc version refs fixed to v0.21.0 | pending |
| 2026-04-05 | P2-Batch3 | T-8: React validation job added to CI fast-checks.yml | pending |
| 2026-04-05 | P2-Batch4 | S-20: Pinned upper bounds on security deps | pending |
| 2026-04-05 | P2-Batch4 | S-21: Auth event audit logging | pending |
| 2026-04-05 | P2-Batch4 | S-23: Docker dev read-only mounts | pending |
| 2026-04-05 | P2-Batch4 | T-13: Serviceability Hypothesis tests (10 tests) | pending |
| 2026-04-05 | P2-Batch4 | BE-2: Function count fixes in 4 docs | pending |
| 2026-04-05 | P2-Batch4 | GOV-4: Release process in CONTRIBUTING.md | pending |
| 2026-04-05 | P2-Batch4 | FE-4: Parameter tooltips in BeamForm | pending |
| 2026-04-05 | P2-Batch4 | OPS-6: Closed (already done) | pending |
2026-04-05 | P2-B5 | DOC-1: Updated PyPI description (beams + columns + footings) | —
2026-04-05 | P2-B5 | DOC-2: Created MANIFEST.in for py.typed in sdist | —
2026-04-05 | P2-B5 | DOC-3: Fixed examples README (9 actual files, was 4 non-existent) | —
2026-04-05 | P2-B5 | OPS-2: Updated publish.yml + link-check.yml action versions | —
2026-04-05 | P2-B5 | OPS-7: Docker JWT secret fail-fast (no insecure default) | —
2026-04-05 | P2-B5 | UX-7: Added prefers-reduced-motion support (CSS + hook + HomePage guards) | —
2026-04-05 | P2-B5 | FE-8: WebGL context loss handling (hook + recovery UI in Viewport3D) | —

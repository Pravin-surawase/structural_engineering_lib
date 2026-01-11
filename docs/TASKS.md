# Task Board

> Single source of truth for work. Keep it short and current.

**Updated:** 2026-01-11 (Session 13 Part 7: Final Review Fixes)

> **Note:** For detailed specifications, see [docs/planning/](planning/) folder.

---

## Rules (read first)
- **WIP = 2** (max 2 active tasks). Use WIP=2 only for independent tasks. For complex features, keep WIP=1.
- Move tasks between sections; do not duplicate.
- **Umbrella tasks:** Keep a single umbrella task in Active/Up Next and list included TASK IDs in description.
- Definition of Done: tests pass, docs updated, CHANGELOG/RELEASES updated when needed.
- Keep "Recently Done" to last 10-20 items; older history in archive.

---

## Current Release

- **Version:** v0.16.5 ✅ Released (2026-01-08)
- **Focus:** UI Layout + Streamlit Improvements
- **Next:** v0.17.0 (Q1 2026) - Continue Streamlit + API integration

---

## v0.16.0 Target (Q1 2026 - Week 1)

**Goal:** Stabilize API refactoring foundation

**Focus:** Fix all test/benchmark failures from API changes

**Key Deliverables:**
1. ✅ All tests passing (fix 8 API refactoring failures)
2. ✅ All benchmarks passing (fix 13 signature errors)

**Success Metrics:**
- 2300+ tests passing, 0 failures
- 86%+ coverage maintained
- 0 ruff/mypy errors

---

## v0.17.0 Target (Q1 2026 - Weeks 2-4)

**Goal:** Implement first professional engineering requirements

**Focus:** Developer productivity + professional compliance foundation

**Key Deliverables:**
1. ✅ Interactive testing UI (Streamlit/Gradio for developer validation)
2. ✅ Code clause database (traceability system)
3. ✅ Security hardening baseline (input validation, dependency scanning)
4. ✅ Professional liability framework (disclaimers, templates)

**Success Metrics:**
- Working Streamlit app for manual testing
- Clause references traceable in code
- Basic security scanning in CI
- Legal protection docs in place
- API grade: A- → A (93/100)

---

## Active

### IS 456 Module Migration (Multi-Code Support) ✅ COMPLETE

> **Research:** [is456-migration-research.md](research/is456-migration-research.md) | [Workflow Guide](guidelines/migration-workflow-guide.md)
> **Status:** ✅ **COMPLETE** (2026-01-10, Session 5) - All 7 modules migrated, PR #323 merged
> **Results:** 3,048 lines migrated, 2392 tests passing, zero breaking changes

| ID | Task | Agent | Est | Priority | Status |
|----|------|-------|-----|----------|--------|
| **TASK-313** | Execute Phase 1-7: Migrate all IS 456 modules | DEV | 2.5h | 🔴 HIGH | ✅ Done |
| **TASK-317** | Update codes/is456/__init__.py exports & validate | DEV | 30m | 🟠 P1-High | ✅ Done |

> **TASK-317 Completed:** Session 6, 2026-01-11. PR #324 merged. Created `validate_stub_exports.py` + `update_is456_init.py` automation scripts.
> **Automation Created:** Pre-migration checks, stub validation, __init__.py generator. See [migration-issues-analysis.md](research/migration-issues-analysis.md)

---

## Up Next

### Future: Core Module Organization (Low Priority)

> **Purpose:** Move code-agnostic modules to `core/` for multi-code support
> **Status:** ⏳ Backlog - Only needed when adding ACI 318 or EC2 support
> **Research:** [migration-issues-analysis.md](research/migration-issues-analysis.md)

| ID | Task | Agent | Est | Priority | Status |
|----|------|-------|-----|----------|--------|
| **TASK-320** | Migrate materials.py → core/materials.py (if needed) | DEV | 30m | 🔵 P3-Low | ⏳ Backlog |
| **TASK-321** | Migrate utilities.py → core/utilities.py (if needed) | DEV | 30m | 🔵 P3-Low | ⏳ Backlog |

> **Note:** core/ already has base.py, geometry.py, materials.py. Root materials.py may be redundant - investigate before migrating.

---

### IS 456 Migration Details (Reference)

> **Detailed tasks for TASK-313 breakdown if needed:**

| Phase | Module | Est | Dependencies |
|-------|--------|-----|--------------|
| 1 | tables.py | 15m | None |
| 2 | shear.py | 20m | tables |
| 3 | flexure.py | 30m | materials |
| 4-7 | detailing, serviceability, compliance, ductile | 1h | Previous phases |

---

### Folder Structure Governance (Session 11-13) ✅ COMPLETE

> **Governance Spec:** [folder-structure-governance.md](guidelines/folder-structure-governance.md)
> **Progress Tracker:** [folder-migration-progress.md](planning/folder-migration-progress.md)
> **Status:** ✅ COMPLETE - All validators pass, CI enforced, spec/validator aligned

| ID | Task | Session | Status |
|----|------|---------|--------|
| **GOV-001** | Create governance spec (V2.0) | S11 | ✅ Done |
| **GOV-002** | Reorganize agents/ folder structure | S11 | ✅ Done |
| **GOV-003** | Fix compliance checker bugs (for-else, paths) | S13.1 | ✅ Done |
| **GOV-004** | Fix root file counting consistency | S13.1 | ✅ Done |
| **GOV-005** | Update agent-9-quick-start.md paths | S13.1 | ✅ Done |
| **GOV-006** | Reduce root files 14→9 | S13.1 | ✅ Done |
| **GOV-007** | Remove docs/reference/vba-guide.md stub | S13.1 | ✅ Done |
| **GOV-008** | Create progress tracker | S13.1 | ✅ Done |
| **GOV-013** | Fix validator limit 20→10, consolidate governance | S13.2 | ✅ Done |
| **GOV-014** | Fix third review issues, add CI governance checks | S13.3 | ✅ Done |
| **GOV-015** | Align validator with spec, fix stale refs | S13.4 | ✅ Done |

> **Session 13 Total:** 11 commits, 4 PRs (#323, #326, #327, #328), 23/26 review claims validated (88% accuracy)

---

### Agent 9 Governance (Phase C: Semantic Navigation) ✅ MOSTLY COMPLETE

> **Research:** [Navigation Study](research/navigation_study/navigation-study-results.md) showed structural cleanup doesn't improve navigation (1.0x speedup).
> **Status:** ✅ 6/7 tasks complete (2026-01-10). Only TASK-305 (re-run nav study) remains.
> **Results:** 277 files, 717 links, 0 broken. 13 stubs removed. Front-matter template + validation added.
> **Completed:** TASK-300 (semantic README), TASK-301 (test files), TASK-302 (stubs), TASK-303 (front-matter), TASK-304 (duplicate), TASK-306 (automation)

| ID | Task | Agent | Est | Priority | Status |
|----|------|-------|-----|----------|--------|
| **TASK-305** | Re-run navigation study with semantic indexes | AGENT_9 | 1h | 🟡 P2-Medium | ⏳ Queued |

---

## Up Next

### v0.17.0 Implementation

#### Agent 9 Governance (Phase A: Critical Infrastructure) ✅ COMPLETE

> **Research:** [Phase 1](../agents/agent-9/research/RESEARCH_FINDINGS_STRUCTURE.md) + [Phase 2](../agents/agent-9/research/RESEARCH_FINDINGS_EXTERNAL.md) (3.5h, 14 research tasks, 4,747 lines)
> **Status:** ✅ **PHASE A COMPLETE** - All 4 tasks done 2026-01-10
> **Results:** Root docs 47→9 (81% reduction), CI enforcement active, archival automation running

*All Phase A tasks moved to Recently Done section.*

---

#### Agent 9 Governance (Phase B: Folder Migration) ✅ COMPLETE

> **Governance Spec:** [folder-structure-governance.md](guidelines/folder-structure-governance.md)
> **Status:** ✅ **PHASE B COMPLETE** - All 6 tasks done 2026-01-10 (5 commits)
> **Results:** 292 files, 710 links, 0 broken. Agent entry points 3/3. Governance folder 36→7 (81% reduction).

| ID | Task | Agent | Commit | Status |
|----|------|-------|--------|--------|
| **B0** | Merge roadmap branch to main | AGENT_9 | 59f4dc0 | ✅ Done |
| **B1** | Agent 6 entry points (quick-start + hub) | AGENT_9 | ce57e44 | ✅ Done |
| **B2** | Agent registry in docs/agents/README.md | AGENT_9 | ce57e44 | ✅ Done |
| **B3** | Archive 29 Phase A planning docs | AGENT_9 | 1570d3c | ✅ Done |
| **B4** | Navigation study re-run | AGENT_9 | cacf83c | ✅ Done |
| **B5** | Weekly governance check script | AGENT_9 | cacf83c | ✅ Done |

*All Phase B tasks complete. Historical docs archived in [docs/_archive/2026-01/agent-9-governance-legacy/](_archive/2026-01/agent-9-governance-legacy/).*

---

#### Critical Path (Must complete for v0.17.0)

| ID | Task | Agent | Est | Priority | Status |
|----|------|-------|-----|----------|--------|
| **TASK-273** | Implement Interactive Testing UI (Streamlit basic app with design validation) | DEV | 1 day | 🔴 HIGH | ⏳ Queued |
| **TASK-272** | Implement Code Clause Database (JSON DB, @clause decorator, traceability) | DEV | 4-6 hrs | 🔴 HIGH | ⏳ Queued |
| **TASK-274** | Security Hardening Baseline (input validation audit, dependency scanning setup) | DEVOPS | 2-3 hrs | 🔴 HIGH | ⏳ Queued |
| **TASK-275** | Professional Liability Framework (MIT+engineering disclaimer, templates in docs/) | DOCS | 2-3 hrs | 🔴 HIGH | ⏳ Queued |

### v0.18+ (Professional Features Pipeline)

#### Agent 9 Governance (Phase D: Automation & Observability)

> **Goal:** Establish governance cadence (80/20 rule), automate maintenance, enable proactive monitoring
> **Dependencies:** ✅ Phase A+B complete. Phase C (semantic navigation) in progress.

| ID | Task | Agent | Est | Priority | Status | Due |
|----|------|-------|-----|----------|--------|-----|
| **TASK-284** | Weekly Governance Sessions (80/20 rule: 1 governance per 5 feature sessions) | AGENT_9 | 3h | 🟠 P1-High | ⏳ Queued | 2026-01-30 |
| **TASK-285** | Metrics Dashboard (trending: velocity, docs, quality, alerts) | AGENT_9 | 4h | 🟡 P2-Medium | ⏳ Blocked by 284 | 2026-02-04 |
| **TASK-286** | Leading Indicator Alerts (CI warnings for 6 metrics: crisis docs, handoffs, etc.) | AGENT_9 | 2h | 🟡 P2-Medium | ⏳ Blocked by 285 | 2026-02-06 |

**Success Criteria:**
- Governance ratio: 20% of sessions (1 per 5)
- Alert count: 3/6 → 0/6 (all green)
- Dashboard: Daily automated updates

#### Professional Features

| ID | Task | Agent | Est | Priority | Status |
|----|------|-------|-----|----------|--------|
| **TASK-276** | Implement Input Flexibility (BeamInput dataclasses, import helpers, builder pattern) | DEV | 4-5 hrs | 🔴 HIGH | ⏳ Queued |
| **TASK-277** | Implement Calculation Report Generation (Jinja2 templates, HTML/PDF reports) | DEV | 4-5 hrs | 🔴 HIGH | ⏳ Queued |
| **TASK-278** | Implement Verification & Audit Trail (SHA-256 signatures, immutable audit logs) | DEV | 3-4 hrs | 🔴 HIGH | ⏳ Queued |
| **TASK-279** | Implement Engineering Testing Strategies (visual regression, property-based tests) | TESTER | 4-5 hrs | 🔴 HIGH | ⏳ Queued |

### Post-v0.16.0 (Deferred)

| ID | Task | Agent | Est | Priority | Status |
|----|------|-------|-----|----------|--------|
| **TASK-145** | Visualization Stack (matplotlib/plotly, BMD/SFD, beam elevation, cross-sections) | DEV | 3-4 days | 🟡 MEDIUM | ⏳ Queued |
| **TASK-146** | DXF Quality Polish (CAD visual QA, DWG conversion workflow) | QA | 2-3 days | 🟡 MEDIUM | ⏳ Queued |
| **TASK-147** | Developer Documentation (10+ examples, extension points, tutorials) | DOCS | 2-3 days | 🟡 MEDIUM | ⏳ Queued |

---

## v1.0+ Long-Term Governance (Phase C: Advanced Optimization)

> **Goal:** Predictive analytics, dynamic optimization, long-term sustainability
> **Timeline:** v1.0.0+ (March 2026+)

### Agent 9 Governance (Phase C: Advanced Features)

| ID | Task | Agent | Est | Priority | Status | Due |
|----|------|-------|-----|----------|--------|-----|
| **TASK-287** | Predictive Velocity Modeling (7-day forecasting, trend analysis, anomaly detection) | AGENT_9 | 8h | 🔵 P3-Low | ⏳ Blocked by 286 | 2026-03-15 |
| **TASK-288** | Release Cadence Optimization (dynamic scheduling based on velocity patterns) | AGENT_9 | 6h | 🔵 P3-Low | ⏳ Blocked by 287 | 2026-03-20 |
| **TASK-289** | Governance Health Score (0-100 composite metric: velocity, docs, quality, alerts) | AGENT_9 | 4h | 🔵 P3-Low | ⏳ Blocked by 288 | 2026-03-22 |
| **TASK-290** | Context Optimization for AI Agents (progressive disclosure, table-first docs) | AGENT_9 | 6h | 🔵 P3-Low | ⏳ Blocked by 289 | 2026-03-25 |
| **TASK-291** | Technical Debt Dashboard (debt inventory, trending, ROI calculator) | AGENT_9 | 5h | 🔵 P3-Low | ⏳ Blocked by 290 | 2026-03-27 |

**Success Criteria:**
- Health score: >85/100 (sustainable governance)
- Predictive alerts: 7-day velocity forecast accuracy >90%
- Tech debt trend: Declining month-over-month
- Context optimization: AI agent onboarding <30min (vs. current 2-3h)

---

## Backlog

### Phase 4: API Improvement & Professional Requirements (v1.0 Critical)

> **Context:** [Research backlog review](research/research-backlog-review.md) | [API specs](planning/api-improvement-research-specs.md)
> **Status:** Research complete (10,547 lines of guidelines), ready for implementation

#### Foundation Implementation (HIGH Priority)

*All foundation implementation tasks complete (TASK-210-214). See Recently Done.*

#### Professional Engineering Requirements (HIGH Priority)

*All professional requirements research complete (TASK-230, 238, 240, 242, 245, 252, 260, 261). See Recently Done.*

**Implementation Order:**
1. Translate completed research into v1.0 implementation epics and milestones.
2. Prioritize deliverables that unblock compliance/reporting and user-facing UX wins.

---

### Phase 4B: Post-v1.0 Enhancements (MEDIUM Priority)

> **Timeline:** v1.1-v1.2 (Q2-Q3 2026) - Based on user feedback

| ID | Task | Agent | Est | Target |
|----|------|-------|-----|--------|
| **TASK-241** | Research: Load Combination Generation (IS 1893/875, automatic combinations, envelope analysis) | RESEARCHER | 3-4 hrs | v1.1 |
| **TASK-244** | Research: Material Database Management (built-in properties, regional variations, user-defined materials) | RESEARCHER | 2-3 hrs | v1.1 |
| **TASK-223** | Research: Configuration Management System (user preferences, project defaults, config files) | RESEARCHER | 2-3 hrs | v1.2 |
| **TASK-224** | Research: Advanced Validation Frameworks (Pydantic integration, cross-parameter validation) | RESEARCHER | 3-4 hrs | v1.2 |
| **TASK-231** | Research: Multi-Platform Distribution (Conda packaging, PyInstaller, multi-OS testing) | DEVOPS | 3-4 hrs | v1.2 |
| **TASK-221** | Research: Performance Optimization Patterns (caching, vectorization, lazy evaluation) | RESEARCHER | 3-4 hrs | When needed |
| **TASK-243** | Research: CAD/BIM Integration (Revit, IFC, parametric modeling) | INTEGRATION | 3-4 hrs | v2.0 |

---

### Future Research Ideas (Archived)

> **Status:** Deferred until v1.0 ships and real user feedback validates necessity
> **Rationale:** These solve hypothetical problems without user validation

**Removed Tasks:** TASK-220 (Multi-code architecture), TASK-222 (Plugin architecture), TASK-225 (DSL patterns), TASK-226 (Internationalization), TASK-227 (Code generation), TASK-232 (CI/CD best practices), TASK-233 (Data serialization), TASK-234 (Observability), TASK-250 (Dev environment setup), TASK-251 (Interactive docs), TASK-253 (Collaboration tools), TASK-262 (Licensing/monetization)

**Decision:** Removed completely from backlog. Will revisit if users request these features post-v1.0.

---

### Visualization & Quality (Deferred)

| ID | Task | Agent | Est | Priority |
|----|------|-------|-----|----------|
| **TASK-145** | Visualization Stack (matplotlib/plotly, BMD/SFD, beam elevation, cross-sections) | DEV | 3-4 days | 🟡 MEDIUM |
| **TASK-146** | DXF Quality Polish (CAD visual QA, DWG conversion workflow) | QA | 2-3 days | 🟡 MEDIUM |
| **TASK-147** | Developer Documentation (10+ examples, extension points, tutorials) | DOCS | 2-3 days | 🟡 MEDIUM |

---

### Post-v1.0 (Beam Scope)

| ID | Task | Agent | Est | Priority |
|----|------|-------|-----|----------|
| **TASK-081** | Level C Serviceability (creep + shrinkage) | DEV | 1-2 days | 🟡 MEDIUM |
| **TASK-082** | VBA parity automation harness | DEVOPS | 1-2 days | 🟡 MEDIUM |
| **TASK-138** | ETABS tables → beam input mapping (export checklist + converter) | INTEGRATION | 1-2 days | 🟡 MEDIUM |
| **TASK-085** | Torsion design + detailing (Cl. 41) | DEV | 2-3 days | 🟡 MEDIUM |
| **TASK-087** | Anchorage space check (Cl. 26.2) | DEV | 1 day | 🟡 MEDIUM |
| **TASK-088** | Slenderness/stability check (Cl. 23.1.2) | DEV | 4 hrs | 🟡 MEDIUM |

---

## Recently Done

| ID | Task | Agent | Status |
|----|------|-------|--------|
| **ONBOARD-03** | Final onboarding cleanup: agent_start.sh v2.1 (full mode fix, worktree passthrough), archive 3 automation docs, mark agent-9 summary archived, README WIP banner | DEVOPS | ✅ 2026-01-11 |
| **ONBOARD-02** | Finalize onboarding: agent_start.sh v2.0 (calls agent_setup.sh, proper preflight, --worktree support, removes || true), update agent-onboarding.md, fix script count 102→103 | DEVOPS | ✅ 2026-01-11 |
| **ONBOARD-01** | Agent onboarding efficiency: Created unified `agent_start.sh` script, consolidated 4 redundant docs (agent-automation-implementation, agent-8-quick-start, agent-8-implementation-guide, git-workflow-quick-reference) into archives, merged metrics into agent-automation-system.md v1.1.0 (PR #329 + 1 commit) | DEVOPS | ✅ 2026-01-11 |
| **TASK-325** | Folder cleanup phase 1: Archive 14 streamlit orphan files, rename typo folder, add batch_archive.py + rename_folder_safe.py (PR #325) | DEVOPS | ✅ 2026-01-11 |
| **TASK-312** | IS 456 migration research & automation: migration-research.md, preflight-checklist.md, workflow-guide.md, migrate_module.py, validate_migration.py, pre_migration_check.py | ARCHITECT | ✅ 2026-01-10 |
| **TASK-311** | Folder cleanup automation: safe_file_move.py, safe_file_delete.py, check_folder_readmes.py, find_orphan_files.py + guides | DEVOPS | ✅ 2026-01-10 |
| **TASK-310** | Multi-code foundation: core/, codes/ structure with CodeRegistry, MaterialFactory, geometry classes, docs-index.json generator (PR #322) | ARCHITECT | ✅ 2026-01-10 |
| **AGENT9-PHASE-B** | Folder Migration Complete: Agent 6 entry points, agent registry, 29 docs archived, navigation study, governance automation (5 commits: 59f4dc0, ce57e44, 1570d3c, cacf83c, 8a66d8a) | AGENT_9 | ✅ 2026-01-10 |
| **TASK-270** | Fix 8 test failures from API refactoring (exception types, validation, CLI) | TESTER | ✅ 2026-01-10 |
| **TASK-271** | Fix 13 benchmark errors from API signature changes | TESTER | ✅ 2026-01-10 |
| **TASK-280** | Repository hygiene implementation (naming, link fixes, archives, health scripts) | DEVOPS | ✅ 2026-01-07 |
| **TASK-261** | Research: Professional Liability & Disclaimers (MIT + engineering addendum, disclaimer templates, certification guidance) | RESEARCHER | ✅ 2026-01-07 |
| **TASK-260** | Research: Security Best Practices (input validation, dependency scanning, CI hardening) | DEVOPS | ✅ 2026-01-07 |
| **TASK-252** | Research: Interactive Testing UI (Jupyter widgets + Streamlit UI plan) | INTEGRATION | ✅ 2026-01-07 |
| **TASK-245** | Research: Verification & Audit Trail (SHA-256 signatures, immutable audit records, CLI verification) | RESEARCHER | ✅ 2026-01-07 |
| **TASK-242** | Research: Calculation Report Generation (Jinja2 HTML, PDF via WeasyPrint, Excel export) | RESEARCHER | ✅ 2026-01-07 |
| **TASK-240** | Research: Code Clause Database Architecture (JSON clause DB, @clause decorator, traceability) | ARCHITECT | ✅ 2026-01-07 |
| **TASK-238** | Research: Input Flexibility & Data Interchange (BeamInput dataclasses, import helpers, builder pattern) | ARCHITECT | ✅ 2026-01-07 |
| **AGENT8-WEEK1** | Git workflow optimizations (4/4): Parallel Fetch (#309), Incremental Whitespace (#310), CI Monitor Daemon (#311), Merge Conflict Test Suite (#312). **Performance: 45-60s → 5s commits (90% faster!)** | AGENT8 | ✅ 2026-01-09 |
| **TASK-230** | Research: Testing Strategies for Engineering Software (visual regression, property-based, mutation testing) | TESTER | ✅ 2026-01-07 |
| **TASK-211** | Apply API Guidelines to core modules (flexure/shear/detailing refactor + tests) | DEV | ✅ 2026-01-07 |
| **TASK-210** | Apply API Guidelines to `api.py` (keyword-only signatures, result objects) | DEV | ✅ 2026-01-07 |
| **TASK-213** | Implement error message templates (Three Questions Framework: dimension, material, design, compliance, calculation templates) → error_messages.py + 29 tests | DEV | ✅ 2026-01-07 |
| **TASK-212** | Create exception hierarchy (3-level: StructuralLibError→5 categories→3 specific with details/suggestion/clause_ref) → errors.py + 19 tests | DEV | ✅ 2026-01-07 |
| **TASK-214** | Create result object base classes (BaseResult, CalculationResult, ComplianceResult with to_dict/summary/validate) → result_base.py + 14 tests | DEV | ✅ 2026-01-07 |
| **TASK-207** | Research: API Evolution & Migration Strategies (SemVer, deprecation, breaking changes, migration tools) → 1700 lines | RESEARCHER | ✅ 2026-01-07 |
| **TASK-206** | Research: API Documentation & Discoverability (docstring standards, IDE integration, API reference) → 1500 lines | RESEARCHER | ✅ 2026-01-07 |
| **TASK-205** | Research: Engineering Domain API Patterns (PyNite, ezdxf, pint, handcalcs, unit handling) → 1000 lines | RESEARCHER | ✅ 2026-01-07 |
| **TASK-204** | Research: Error Handling & Exception Design (exception hierarchy, error messages, validation) → 2100 lines | RESEARCHER | ✅ 2026-01-07 |
| **TASK-203** | Research: Result Object Design Patterns (dataclass vs alternatives, methods, serialization) → 950 lines | RESEARCHER | ✅ 2026-01-07 |
| **TASK-202** | Research: Function Signature Design Standards (parameter ordering, keyword-only, type hints) → 1000 lines | 2026-01-07 | RESEARCHER |
| **TASK-201** | Research: UX Patterns for Technical APIs (cognitive load, discoverability, pit of success) | 2026-01-07 | RESEARCHER |
| **TASK-215** | Update workflow: allow docs/research direct commits (no PR) with checks intact | 2026-01-07 | DEVOPS |
| **TASK-209** | Implementation Roadmap: API Improvements (48 functions, 3 tiers, 3-phase plan) | 2026-01-07 | PM |
| **TASK-208** | Synthesis: Create API Guidelines Document (2609 lines, 11 sections, 30-point checklist) | 2026-01-07 | ARCHITECT |
| **TASK-200** | Research: Professional Python Library API Patterns (NumPy, SciPy, Pandas, Requests) | 2026-01-07 | RESEARCHER |
| **TASK-199** | Sync Colab notebooks (root + docs) and document output review findings | 2026-01-06 | DOCS |
| **TASK-198** | Update Colab workflow notebook for v0.15 smart design + comparison testing | 2026-01-06 | DOCS |
| **TASK-192** | Add per-module coverage + baseline performance benchmarks (13 benchmarks, coverage by module) | 2026-01-06 | TESTER |
| **TASK-191** | Restructure tests into category subfolders with pytest markers (5 categories, 7 markers) | 2026-01-06 | TESTER |
| **TASK-190** | Resolve dead-code findings + TODOs + comprehensive CI linting cleanup (91→0 ruff errors) | 2026-01-06 | DEV |
| **TASK-193** | Type Annotation Modernization (PEP 585/604: 398 issues resolved, 25 files) | 2026-01-06 | DEV |
| **TASK-187** | Standardize license headers in Python + VBA modules (SPDX-License-Identifier: MIT) | 2026-01-06 | DEV |
| **TASK-162** | Replace Dict[str, Any] with TypedDicts (BeamGeometry, LoadCase, JobSpec) | 2026-01-06 | DEV |
| **TASK-144** | Smart Library Integration (SmartDesigner unified dashboard, smart_analyze_design API) | 2026-01-06 | DEV |

---

## Archive

Full task history: `docs/_archive/tasks-history.md`

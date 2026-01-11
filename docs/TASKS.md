# Task Board

> Single source of truth for work. Keep it short and current.

**Updated:** 2026-01-11 (Session 14: TASKS Cleanup & v0.17.0 Planning)

> **Note:** For detailed specifications, see [docs/planning/](planning/) folder.

---

## Rules (read first)
- **WIP = 2** (max 2 active tasks). Use WIP=2 only for independent tasks. For complex features, keep WIP=1.
- Move tasks between sections; do not duplicate.
- **Umbrella tasks:** Keep a single umbrella task in Active/Up Next and list included TASK IDs in description.
- Definition of Done: tests pass, docs updated, CHANGELOG/RELEASES updated when needed.
- **Archive rule:** Move "Recently Done" items to [docs/_archive/tasks-history.md](_archive/tasks-history.md) after 20+ items or 14+ days old. Keep last 10-15 items visible.

---

## Current Release

- **Version:** v0.16.5 ✅ Released (2026-01-08)
- **Focus:** Folder Structure Governance + Multi-Code Foundation
- **Next:** v0.17.0 (Q1 2026, Weeks 2-4) - Professional Requirements Foundation

---

## v0.17.0 Release Target (Q1 2026 - Weeks 2-4)

**Goal:** Implement first professional engineering requirements

**Focus:** Security, legal compliance, traceability, developer productivity

**Key Deliverables:**
1. 🔴 Security hardening baseline (input validation audit, dependency scanning)
2. 🔴 Professional liability framework (disclaimers, templates, certification guidance)
3. 🔴 Code clause database (JSON DB, @clause decorator, traceability system)
4. 🔴 Interactive testing UI (Streamlit/Gradio for design validation)

**Success Metrics:**
- Security: Input validation audit complete, dependency scanning in CI
- Legal: MIT+engineering disclaimer, templates in docs/legal/
- Traceability: Clause references in 80%+ design functions
- Developer UX: Working Streamlit app for manual validation
- API grade: A- → A (93/100)

---

## Active

*No active tasks. Pick from Up Next and move here when starting.*

---

## Up Next

### v0.17.0 - Critical Path (Must Complete)

> **Phase Approach:** Start with low-risk foundation (security, legal) before high-risk features (Streamlit)

**Phase 1 (Week 2): Foundation (Low Risk, 4-6 hours)**
| ID | Task | Agent | Est | Priority | Blockers |
|----|------|-------|-----|----------|----------|
| **TASK-274** | Security Hardening Baseline (input validation audit, dependency scanning, CI setup) | DEVOPS | 2-3 hrs | 🔴 HIGH | None |
| **TASK-275** | Professional Liability Framework (MIT+engineering disclaimer, templates, certification guidance) | DOCS | 2-3 hrs | 🔴 HIGH | None |

**Phase 2 (Week 3): Traceability (Medium Risk, 4-6 hours)**
| ID | Task | Agent | Est | Priority | Blockers |
|----|------|-------|-----|----------|----------|
| **TASK-272** | Code Clause Database (JSON DB, @clause decorator, traceability) | DEV | 4-6 hrs | 🔴 HIGH | None |

**Phase 3 (Week 4): Developer UX (High Value, 1-2 days)**
| ID | Task | Agent | Est | Priority | Blockers |
|----|------|-------|-----|----------|----------|
| **TASK-273** | Interactive Testing UI (Streamlit basic app with design validation) | DEV | 1-2 days | 🔴 HIGH | Test infrastructure |

> **Note:** TASK-273 depends on stable test infrastructure. If blocked, deliver v0.17.0 with TASK-272/274/275 only.

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

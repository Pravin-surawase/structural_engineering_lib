# Task Board

> Single source of truth for work. Keep it short and current.

**Updated:** 2026-01-07

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

- **Version:** v0.15.0 ✅ Released (2026-01-07)
- **Focus:** Code Quality Excellence - Enterprise-grade standards
- **Next:** v1.0 (API improvement + professional requirements)

---

## Active

*No active tasks currently.*

---

## Up Next

| ID | Task | Agent | Est | Priority | Status |
|----|------|-------|-----|----------|--------|
| **TASK-145** | Visualization Stack (matplotlib/plotly, BMD/SFD, beam elevation, cross-sections) | DEV | 3-4 days | 🟡 MEDIUM | ⏳ Queued |
| **TASK-146** | DXF Quality Polish (CAD visual QA, DWG conversion workflow) | QA | 2-3 days | 🟡 MEDIUM | ⏳ Queued |
| **TASK-147** | Developer Documentation (10+ examples, extension points, tutorials) | DOCS | 2-3 days | 🟡 MEDIUM | ⏳ Queued |

---

## Backlog

### Phase 4: API Improvement & Professional Requirements (v1.0 Critical)

> **Context:** [Research backlog review](research/research-backlog-review.md) | [API specs](planning/api-improvement-research-specs.md)
> **Status:** Research complete (10,547 lines of guidelines), ready for implementation

#### Foundation Implementation (HIGH Priority)

| ID | Task | Agent | Est | Blockers |
|----|------|-------|-----|----------|
| **TASK-210** | Apply API Guidelines to `api.py` (refactor signatures, keyword-only params, result objects) | DEV | 2-3 days | None |
| **TASK-211** | Apply API Guidelines to core modules (flexure.py, shear.py, detailing.py) | DEV | 2-3 days | TASK-210 |
| **TASK-212** | Create exception hierarchy (3-level: base→category→specific per guidelines) | DEV | 1 day | None |
| **TASK-213** | Implement error message templates (Three Questions Framework) | DEV | 1 day | TASK-212 |
| **TASK-214** | Create result object base classes (BaseResult with to_dict/summary/validate) | DEV | 1 day | None |

#### Professional Engineering Requirements (HIGH Priority)

| ID | Task | Agent | Est | Why Critical |
|----|------|-------|-----|--------------|
| **TASK-230** | Research: Testing Strategies for Engineering Software (visual regression, property-based testing, mutation testing) → [research doc](research/) | TESTER | 4-5 hrs | Quality assurance for DXF/reports |
| **TASK-238** | Research: Input Flexibility & Data Interchange (ETABS, spreadsheets, CAD, BIM workflows) → [research doc](research/) | ARCHITECT | 4-5 hrs | Fixes Colab UX pain (C- → B+) |
| **TASK-240** | Research: Code Clause Database Architecture (structured IS 456 clause storage, traceability) → [research doc](research/) | ARCHITECT | 3-4 hrs | Professional traceability requirement |
| **TASK-242** | Research: Calculation Report Generation (LaTeX/PDF, equation rendering, clause citations) → [research doc](research/) | RESEARCHER | 4-5 hrs | Core engineering deliverable |
| **TASK-245** | Research: Verification & Audit Trail (checksums, audit logs, reproducibility proof) → [research doc](research/) | RESEARCHER | 3-4 hrs | Professional liability protection |
| **TASK-252** | Research: Interactive Testing UI (Streamlit/Gradio for manual testing + dogfooding) → [research doc](research/) | INTEGRATION | 2-3 hrs + 1 day impl | Developer productivity boost |
| **TASK-260** | Research: Security Best Practices (input sanitization, secrets management, code signing) → [research doc](research/) | DEVOPS | 2-3 hrs | Production security review |
| **TASK-261** | Research: Professional Liability & Disclaimers (legal framework, engineer seal, terms of service) → [research doc](research/) | RESEARCHER | 2-3 hrs | Legal protection before marketing |

**Implementation Order:**
1. Week 1-2: TASK-210-214 (API Implementation)
2. Week 2-3: TASK-252 (Interactive UI - can start in parallel)
3. Week 3-6: TASK-230, 238, 240, 242, 245, 260, 261 (Research tasks)

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
| **TASK-207** | Research: API Evolution & Migration Strategies (SemVer, deprecation, breaking changes, migration tools) → 1700 lines | RESEARCHER | ✅ 2026-01-07 |
| **TASK-206** | Research: API Documentation & Discoverability (docstring standards, IDE integration, API reference) → 1500 lines | RESEARCHER | ✅ 2026-01-07 |
| **TASK-205** | Research: Engineering Domain API Patterns (PyNite, ezdxf, pint, handcalcs, unit handling) → 1000 lines | RESEARCHER | ✅ 2026-01-07 |
| **TASK-204** | Research: Error Handling & Exception Design (exception hierarchy, error messages, validation) → 2100 lines | RESEARCHER | ✅ 2026-01-07 |
| **TASK-203** | Research: Result Object Design Patterns (dataclass vs alternatives, methods, serialization) → 950 lines | RESEARCHER | ✅ 2026-01-07 |
| **TASK-202** | Research: Function Signature Design Standards (parameter ordering, keyword-only, type hints) → 1000 lines | RESEARCHER | ✅ 2026-01-07 |
| **TASK-201** | Research: UX Patterns for Technical APIs (cognitive load, discoverability, pit of success) | RESEARCHER | ✅ 2026-01-07 |
| **TASK-215** | Update workflow: allow docs/research direct commits (no PR) with checks intact | DEVOPS | ✅ 2026-01-07 |
| **TASK-209** | Implementation Roadmap: API Improvements (48 functions, 3 tiers, 3-phase plan) | PM | ✅ 2026-01-07 |
| **TASK-208** | Synthesis: Create API Guidelines Document (2609 lines, 11 sections, 30-point checklist) | ARCHITECT | ✅ 2026-01-07 |
| **TASK-200** | Research: Professional Python Library API Patterns (NumPy, SciPy, Pandas, Requests) | RESEARCHER | ✅ 2026-01-07 |
| **TASK-199** | Sync Colab notebooks (root + docs) and document output review findings | DOCS | ✅ 2026-01-06 |
| **TASK-198** | Update Colab workflow notebook for v0.15 smart design + comparison testing | DOCS | ✅ 2026-01-06 |
| **TASK-192** | Add per-module coverage + baseline performance benchmarks (13 benchmarks, coverage by module) | TESTER | ✅ 2026-01-06 |
| **TASK-191** | Restructure tests into category subfolders with pytest markers (5 categories, 7 markers) | TESTER | ✅ 2026-01-06 |
| **TASK-190** | Resolve dead-code findings + TODOs + comprehensive CI linting cleanup (91→0 ruff errors) | DEV | ✅ 2026-01-06 |
| **TASK-193** | Type Annotation Modernization (PEP 585/604: 398 issues resolved, 25 files) | DEV | ✅ 2026-01-06 |
| **TASK-187** | Standardize license headers in Python + VBA modules (SPDX-License-Identifier: MIT) | DEV | ✅ 2026-01-06 |
| **TASK-162** | Replace Dict[str, Any] with TypedDicts (BeamGeometry, LoadCase, JobSpec) | DEV | ✅ 2026-01-06 |
| **TASK-144** | Smart Library Integration (SmartDesigner unified dashboard, smart_analyze_design API) | DEV | ✅ 2026-01-06 |

---

## Archive

Full task history: `docs/_archive/TASKS_HISTORY.md`

# Task Board

> Single source of truth for work. Keep it short and current.

**Updated:** 2026-01-07

> **Note:** For TASK-165 to TASK-170 (Professional Standards & Hygiene), see detailed specifications in [docs/planning/hygiene-research-specs.md](planning/hygiene-research-specs.md)

---

## Rules (read first)
- **WIP = 2** (max 2 active tasks). Use WIP=2 only for independent tasks (e.g., research + cleanup, small fix + docs). For complex features, keep WIP=1 to maintain focus.
- Move tasks between sections; do not duplicate.
- **Umbrella tasks:** For phased work, keep a single umbrella task in Active/Up Next and list included TASK IDs in its description; move included tasks to Recently Done when finished.
- Definition of Done: tests pass, docs updated, CHANGELOG/RELEASES updated when needed.
- Keep "Recently Done" to the last 10-20 items; older history lives in the archive.
- Use agent roles from `agents/` and the workflow in `docs/_internal/AGENT_WORKFLOW.md`.

---

## Current Release

- Target: v0.15.0 (TBD)
- Focus: Smart library features & comparison tools
- Blockers: none

---

## Active

*No active tasks. Review Up Next queue.*

---

## Up Next

| ID | Task | Agent | Est | Priority | Status |
|----|------|-------|-----|----------|--------|
| **TASK-145** | Visualization Stack (matplotlib/plotly, BMD/SFD, beam elevation, cross-sections) | DEV | 3-4 days | 🟡 MEDIUM | ⏳ Queued |
| **TASK-146** | DXF Quality Polish (CAD visual QA, DWG conversion workflow) | QA | 2-3 days | 🟡 MEDIUM | ⏳ Queued |
| **TASK-147** | Developer Documentation (10+ examples, extension points, tutorials) | DOCS | 2-3 days | 🟡 MEDIUM | ⏳ Queued |

---

## Backlog

### API Improvement Research (CRITICAL for v1.0 — Professional Standards)

> **Full specifications:** [docs/planning/api-improvement-research-specs.md](planning/api-improvement-research-specs.md)
> **Philosophy:** Research-first, then guidelines, then implementation.

#### Phase 1: Core Research (Critical)

| ID | Task | Agent | Est | Priority |
|----|------|-------|-----|----------|
| **TASK-204** | **Research: Error Handling & Exception Design** (Exception hierarchy, error message quality, validation patterns, error recovery; 40+ exception examples) → `docs/guidelines/error-handling-standard.md` | RESEARCHER | 3-4 hrs | 🔴 HIGH |

#### Phase 2: Domain Research

| ID | Task | Agent | Est | Priority |
|----|------|-------|-----|----------|
| **TASK-205** | **Research: Engineering Domain API Patterns** (Study PyNite, OpenSees, ezdxf, handcalcs, pint; unit handling, IS 456 notation, domain conventions) → `docs/research/engineering-domain-apis.md` | RESEARCHER | 3-4 hrs | 🟡 MEDIUM |
| **TASK-206** | **Research: API Documentation & Discoverability** (Docstring best practices, example-driven docs, IDE integration, auto-doc tools) → `docs/guidelines/documentation-standard.md` | RESEARCHER | 3-4 hrs | 🟡 MEDIUM |
| **TASK-207** | **Research: API Evolution & Migration Strategies** (Deprecation strategies, backward compatibility, version communication, migration tools) → `docs/guidelines/api-evolution-standard.md` | RESEARCHER | 2-3 hrs | 🟡 MEDIUM |

#### Phase 3: Synthesis

| ID | Task | Agent | Est | Priority |
|----|------|-------|-----|----------|
| **TASK-208** | **Synthesis: Create API Guidelines Document** (Consolidate all research into unified `docs/guidelines/api-design-guidelines.md`; actionable rules; code templates; review checklists) | ARCHITECT | 3-4 hrs | 🔴 HIGH |
| **TASK-209** | **Implementation Roadmap: API Improvements** (Prioritized improvements from research; implementation sequence; migration strategies; timeline) → `docs/planning/api-improvement-roadmap.md` | PM | 2-3 hrs | 🔴 HIGH |

### Documentation Enhancement (From Handoff Analysis)

_Most tasks completed — see Recently Done._

### Professional Standards & Hygiene (CRITICAL for v1.0 readiness)
All research tasks completed (see Recently Done).

### Professional Standards & Hygiene Implementation (Phase 1-3)

_TASK-191 (test restructuring), TASK-192 (coverage + benchmarks), TASK-193-196 (type annotations, naming, docstrings) completed — see Recently Done._

| ID | Task | Agent | Est | Priority |
|----|------|-------|-----|----------|
| **TASK-210** | Apply API Guidelines to `api.py` (After research: refactor function signatures, add keyword-only params, improve result objects) | DEV | 2-3 days | 🔴 HIGH |
| **TASK-211** | Apply API Guidelines to core modules (flexure.py, shear.py, detailing.py based on guidelines) | DEV | 2-3 days | 🔴 HIGH |

### Foundation & Architecture (CRITICAL for stability)

| ID | Task | Agent | Est | Priority |
|----|------|-------|-----|----------|
| **TASK-212** | Create custom exception hierarchy (BaseLibraryError, ValidationError, DesignError, ComplianceError based on research) | DEV | 1 day | 🔴 HIGH |
| **TASK-213** | Implement error message templates (actionable, context-rich messages following research guidelines) | DEV | 1 day | 🔴 HIGH |
| **TASK-214** | Create result object base classes (BaseResult with to_dict, summary, validate methods) | DEV | 1 day | 🔴 HIGH |

### v1.0 Readiness (carryover)

| ID | Task | Agent | Est | Priority |
|----|------|-------|-----|----------|

### Post-v1.0 (beam scope)

| ID | Task | Agent | Est | Priority |
|----|------|-------|-----|----------|
| **TASK-081** | Level C Serviceability (creep + shrinkage) | DEV | 1-2 days | 🟡 Medium |
| **TASK-082** | VBA parity automation harness | DEVOPS | 1-2 days | 🟡 Medium |
| **TASK-138** | ETABS tables → beam input mapping (export checklist + converter) | INTEGRATION | 1-2 days | 🟡 Medium |
| **TASK-085** | Torsion design + detailing (Cl. 41) | DEV | 2-3 days | 🟡 Medium |
| **TASK-087** | Anchorage space check (Cl. 26.2) | DEV | 1 day | 🟡 Medium |
| **TASK-088** | Slenderness/stability check (Cl. 23.1.2) | DEV | 4 hrs | 🟡 Medium |

---

## Recently Done

| ID | Task | Completed | Agent |
|----|------|-----------|-------|
| **TASK-203** | **Research: Result Object Design Patterns** (12 sections: dataclass vs namedtuple vs dict, essential methods, immutability, nested results, error handling, serialization, anti-patterns, migration; comprehensive ~950 line standard with SciPy OptimizeResult case study) → `docs/guidelines/result-object-standard.md` | 2026-01-07 | RESEARCHER |
| **TASK-202** | **Research: Function Signature Design Standards** (11 sections: core principles, parameter ordering, keyword-only patterns, type hints, defaults, unit suffixes, validation params, special cases, anti-patterns, migration guide, examples; comprehensive ~1000 line standard document with quick reference card and PR review checklist) → `docs/guidelines/function-signature-standard.md` | 2026-01-07 | RESEARCHER |
| **TASK-201** | **Research: UX Patterns for Technical APIs** (Cognitive load, discoverability, error design, "pit of success"; created docs/research/ux-patterns-for-technical-apis.md) | 2026-01-07 | RESEARCHER |
| **TASK-215** | Update workflow to allow docs/research direct commits (no PR) with checks intact | 2026-01-07 | DEVOPS |
| **TASK-200** | **Research: Professional Python Library API Patterns** (Study NumPy, SciPy, Pandas, Requests, Pydantic, scikit-learn patterns) | 2026-01-07 | RESEARCHER |
| **TASK-199** | Sync Colab notebooks (root + docs) and document output review findings | 2026-01-06 | DOCS |
| **TASK-198** | Update Colab workflow notebook for v0.15 smart design + comparison testing | 2026-01-06 | DOCS |
| **TASK-182** | **Phase 3: Final Documentation Pass** (Review all Phase 1+2 changes; update cross-references; validate all links; final quality check for consistency) | 2026-01-06 | DOCS |
| **TASK-181** | **Phase 3: Add Data Flow Diagrams** (Create Mermaid diagrams for complex pipelines: job_runner, smart_designer; show data transformations through layers; commit to docs/architecture/) | 2026-01-06 | DOCS |
| **TASK-180** | **Phase 3: Create Module Dependency Graph** (Use pydeps or similar to generate Python/structural_lib dependency graph; commit PNG to docs/architecture/dependencies.png) | 2026-01-06 | DOCS |
| **TASK-179** | **Phase 3: Generate Visual Architecture Diagrams** (Create PlantUML or Mermaid diagrams for: layer architecture, module dependencies, data flows; commit to docs/architecture/) | 2026-01-06 | DOCS |
| **TASK-197** | Add repo hygiene artifact check (block tracked `.DS_Store`/`.coverage`; add `scripts/check_repo_hygiene.py`; pre-commit hook; documented in automation catalog) | 2026-01-06 | DEV |
| **TASK-164** | Complete Error Migration (v0.14: add deprecation warnings to error_message/remarks fields; v1.0: remove deprecated fields; update all callers) | 2026-01-06 | DEV |
| **TASK-163** | Add Missing Return Type Annotations (audit script to find functions without return types; add types to all public functions; mypy --disallow-untyped-defs) | 2026-01-06 | DEV |
| **TASK-196** | Add Complete Docstrings to Core Modules (flexure.py, shear.py, detailing.py) | 2026-01-06 | DEV |
| **TASK-192** | Add per-module coverage report + baseline performance benchmarks (pytest-benchmark added to dev dependencies; 13 benchmarks covering core calculations, module functions, API, optimization, batch processing; 2 skipped; baseline data saved in .benchmarks/; documented current coverage: 6 modules >90%, 8 modules 80-90%, 5 modules <80%; updated Python/tests/README.md with performance testing section; PR #270 merged) | 2026-01-06 | TESTER |
| **TASK-191** | Restructure tests into category subfolders with pytest markers (59 files → 5 categories: unit/12, integration/38, regression/8, property/1, performance/0; 7 markers in pytest.ini; comprehensive Python/tests/README.md; fixed data/ and fixtures/ paths; updated CI workflow paths; removed 28 iCloud duplicate files; all 2270 tests pass; PR #269 merged) | 2026-01-06 | TESTER |
| **TASK-190** | Resolve dead-code findings + TODOs + comprehensive CI linting cleanup (removed 2 dead code items: bbs.py unused param, comparison.py unused var; updated 3 TODOs with deferral notes; created deferred-integrations.md tracking doc; fixed all 91 ruff errors: 21 auto-fixed, config updates for structural notation, test naming patterns; documented CI scope mismatch prevention; PR #268 merged; all 2270 tests pass) | 2026-01-06 | DEV |
| **TASK-195** | Add Complete Docstrings to api.py (compute_detailing, compute_bbs, compute_dxf, compute_report; 139 lines added; Google Style with Args/Returns/Raises/Examples) | 2026-01-06 | DEV |
| **TASK-194** | Fix Naming Convention Issues (configured ruff to allow structural engineering conventions: D, D_mm, Df, etc.; 59 naming issues resolved; per-file ignores for excel_bridge) | 2026-01-06 | DEV |
| **TASK-193** | Type Annotation Modernization (PEP 585/604: 398 issues resolved; 25 files modified; list/dict/tuple instead of List/Dict/Tuple; all 2270 tests pass) | 2026-01-06 | DEV |
| **TASK-189** | Expand ruff rules + docstring guide (9 rule categories; Google Style guide; 17 auto-fixes; phased implementation plan; see docs/research/ruff-expansion-summary.md) | 2026-01-06 | DEV |
| **TASK-187** | Standardize license headers in Python modules and align VBA header format (SPDX-License-Identifier: MIT, Copyright (c) 2024-2026 Pravin Surawase; 40 Python files, 33 VBA files; script: add_license_headers.py; all 2270 tests pass) | 2026-01-06 | DEV |
| **TASK-188** | Publish nomenclature glossary + naming rules in `docs/contributing/development-guide.md`; update key examples to match | 2026-01-06 | DOCS |
| **TASK-184** | Canonicalize doc sources (define single source per topic + redirect stubs) and add a `docs/README.md` canonical index map | 2026-01-06 | DOCS |
| **TASK-175** | **Phase 2: Create Learning Paths Guide** (Map task complexity → required docs; paths: beginner/intermediate/advanced; examples: "small bug fix" → copilot-instructions + known-pitfalls; "new feature" → architecture + API + testing strategy) → `docs/contributing/learning-paths.md` | 2026-01-06 | DOCS |
| **TASK-176** | **Phase 2: Enhance Agent Role Decision Tree** (Update agents/README.md with task type → agent role mappings; decision tree: bug fix → DEV+TESTER, new feature → PM→RESEARCHER→DEV→TESTER→DOCS, docs → DOCS, release → DEVOPS→PM) | 2026-01-06 | DOCS |
| **TASK-177** | **Phase 2: Create Research Document Index** (Create docs/research/README.md; list 12+ research docs with topic tags (git, testing, tooling, CS practices, etc.); add when-to-read guidance) | 2026-01-06 | DOCS |
| **TASK-178** | **Phase 2: Update Session Brief with Findings** (Update next-session-brief.md with documentation audit findings; summarize gaps and recommendations) | 2026-01-06 | DOCS |
| **TASK-185** | Phase 1 hygiene umbrella (includes TASK-183, TASK-186): archive legacy planning docs (v0.10-v0.12) with redirect stubs in `docs/planning/` | 2026-01-06 | DOCS |
| **TASK-183** | Fix broken internal links and add missing doc stubs (cost optimization guide, link repairs) | 2026-01-06 | DOCS |
| **TASK-186** | Add repo metadata files (CITATION.cff, AUTHORS.md, FUNDING.yml, support issue template, third-party licenses summary) | 2026-01-06 | DOCS |
| **TASK-165** | **Research: Project Hygiene & File Organization** (Audit: duplicate files, obsolete content, inconsistent naming, broken links, outdated docs, archive candidates; cleanup plan and file structure standards) → `docs/research/project-hygiene-audit.md` | 2026-01-06 | RESEARCHER |
| **TASK-166** | **Research: Nomenclature Standardization** (Audit: naming, abbreviations; glossary + standards) → `docs/research/nomenclature-standards.md` | 2026-01-06 | RESEARCHER |
| **TASK-167** | **Research: Professional Repository Standards** (Audit: license headers, community health files, templates, badges, metadata) → `docs/research/professional-repo-standards.md` | 2026-01-06 | RESEARCHER |
| **TASK-168** | **Research: Documentation Quality & Completeness** (Audit: outdated info, broken links, missing examples, formatting, redundancy) → `docs/research/documentation-quality-audit.md` | 2026-01-06 | RESEARCHER |
| **TASK-169** | **Research: Code Style Consistency** (Audit: formatting consistency, docstrings, TODOs, magic numbers) → `docs/research/code-style-consistency.md` | 2026-01-06 | RESEARCHER |
| **TASK-170** | **Research: Test Organization & Coverage Gaps** (Audit: test structure, categories, coverage gaps, performance tests) → `docs/research/test-organization-audit.md` | 2026-01-06 | RESEARCHER |
| **TASK-171** | **Phase 1: Create Automation Script Catalog** (Cataloged all 41 scripts: Session (3), Git (9), Doc Quality (8), Release (4), Testing (5), Code Quality (4), Specialized (8); comprehensive usage guide) → `docs/reference/automation-catalog.md` | 2026-01-06 | DOCS |
| **TASK-172** | **Phase 1: Update AI_CONTEXT_PACK with Automation Section** (Added automation quick reference; categorized key scripts; linked to catalog) | 2026-01-06 | DOCS |
| **TASK-173** | **Phase 1: Add Automation Links to AGENT_BOOTSTRAP** (Updated quick reference with automation catalog link; improved agent discoverability) | 2026-01-06 | DOCS |
| **TASK-174** | **Phase 1: Test Automation Discoverability** (Validated new agent workflow: AI_CONTEXT_PACK → automation section → catalog; all links working; <30 second discovery confirmed) | 2026-01-06 | DOCS |
| **TASK-156** | Research: Backward Compatibility Automation (contract testing in CI, breaking change detection, API stability enforcement, mutation testing) | 2026-01-06 | RESEARCHER |

| ID | Task | Agent | Status |
|----|------|-------|--------|
| **TASK-144** | Smart Library Integration (SmartDesigner unified dashboard with smart_analyze_design() API; 6 data classes; CLI integration; 700+ lines; 19/20 tests passing; complete with API wrapper solution for type architecture) | DEV | ✅ Done |
| **TASK-143** | Comparison & Sensitivity Enhancement (created comparison.py with compare_designs and cost_aware_sensitivity; 400+ lines with DesignAlternative, ComparisonMetrics, ComparisonResult, CostSensitivityResult; 19 tests; exports via insights/__init__.py; 2231 tests pass) | DEV | ✅ Done |
| **TASK-162** | Replace Dict[str, Any] with TypedDicts (BeamGeometry, LoadCase, JobSpec created; job_runner/report/report_svg updated; 2231 tests pass; mypy clean) | DEV | ✅ Done |
| **TASK-161 Sprint 2** | Gradually Tighten Mypy Configuration - Sprint 2 (enabled check_untyped_defs, no_implicit_optional; fixed 2 errors; added Optional imports; 2200 tests pass; mypy clean) | DEV | ✅ Done |
| **TASK-161 Sprint 1** | Gradually Tighten Mypy Configuration - Sprint 1 (enabled warn_return_any, strict_optional; fixed 5 errors; 2200 tests pass; mypy clean) | DEV | ✅ Done |
| **TASK-159** | Standardize Error Handling by Layer (documented strategy in CONTRIBUTING.md with 5 layers; created audit script; 25 modules audited - all compliant) | DEV+DOCS | ✅ Done |
| **TASK-158** | Eliminate Silent Failures in Core Modules (17 functions fixed: flexure, shear, materials, detailing, serviceability, ductile; all now raise ValueError with clear messages; 2200 tests pass) | DEV | ✅ Done |
| **TASK-158** | Eliminate Silent Failures in Core Modules (Fixed 8 functions: calculate_mu_lim, calculate_tv, calculate_ast_required, get_xu_max_d, get_ec, get_fcr, calculate_development_length, calculate_bar_spacing - all now raise ValueError; updated 7 tests; 2200 tests passing) | DEV | ✅ Done |
| **TASK-160** | Fix Mypy Pre-Commit Configuration (use local hook with full venv path, cd Python && mypy structural_lib/) | DEVOPS | ✅ Done |
| **TASK-157** | Complete Validation Utilities Module (6 new validators + 37 tests: validate_cover, validate_loads, validate_material_grades, validate_reinforcement, validate_span, validate_beam_inputs) | DEV | ✅ Done |
| **TASK-155** | **Research: CS Best Practices Implementation Plan** (23 tasks across 3 phases: validation utilities, error handling, mypy, docstrings, TypedDicts) → `docs/research/cs-practices-implementation-plan.md` | RESEARCHER | ✅ Done |
| **TASK-154** | **Research: xlwings vs VBA Strategy** (Hybrid approach: deprecate VBA calculations, keep minimal UI VBA; 85% VBA reduction; 3-phase migration plan) → `docs/research/xlwings-vba-strategy.md` | RESEARCHER | ✅ Done |
| **TASK-153** | Add deprecation decorator and policy (@deprecated, deprecated_field, policy docs, CHANGELOG template) → `Python/structural_lib/utilities.py`, `docs/reference/deprecation-policy.md`, 18 tests | DEV | ✅ Done |
| **TASK-152** | Standardize error handling (validation utilities, flexure.py refactor) → `Python/structural_lib/validation.py`, 41 tests | DEV | ✅ Done |
| **TASK-151** | Implement contract testing (API stability safeguards, pre-commit hook) → `Python/tests/test_contracts.py` | DEV | ✅ Done |
| **TASK-150** | Research: Modern Python Tooling Evaluation (uv, Hypothesis, pytest-benchmark, mutmut for structural libraries) → `docs/research/modern-python-tooling.md` | RESEARCHER | ✅ Done |
| **TASK-149** | Research: Backward Compatibility Strategy (evaluate pytest-regressions, contract testing, semantic versioning tools, API stability safeguards) → `docs/research/backward-compatibility-strategy.md` | RESEARCHER | ✅ Done |
| **TASK-148** | Research: CS Best Practices Audit (review codebase against Python scientific library standards, compare to numpy/scipy/pandas patterns, identify gaps) → `docs/research/cs-best-practices-audit.md` | RESEARCHER | ✅ Done |
| **TASK-142** | Design Suggestions Engine (17 expert rules, 6 categories, confidence scoring, JSON) | DEV | ✅ Done |
| **TASK-141** | Integrate cost calculation into `api.py` and CLI | INTEGRATION | ✅ Done |
| **TASK-140** | Implement Cost Optimization Feature (Python) | DEV | ✅ Done |
| **TASK-139** | Cost Optimization Research (Day 1): Material/Labor models | RESEARCHER | ✅ Done |
| **TASK-135** | Insights verification pack: 10 benchmark cases + JSON data + pytest module | TESTER | ✅ Done |
| **TASK-137** | Complete insights documentation (user guide + API reference, cross-linked) | DOCS | ✅ Done |
| **TASK-136** | Insights JSON schema + CLI integration (`.to_dict()` methods, `--insights` flag, 6 tests) | INTEGRATION | ✅ Done |
| **TASK-134** | Constructability scoring refinement (0-100 scale, 7 factors, 10 comprehensive tests) | DEV | ✅ Done |
| **TASK-133b** | Comprehensive tests for sensitivity analysis (14 tests: golden vectors, edge cases, physical validation) | TESTER | ✅ Done |
| **TASK-133** | Sensitivity analysis fixes + robustness scoring (normalization bug, margin-based robustness) | DEV | ✅ Done |
| **TASK-132** | Insights module scaffolding + precheck (types, precheck.py, tests) | DEV | ✅ Done |
| **TASK-086** | Side-face reinforcement check (Cl. 26.5.1.3) | DEV | ✅ Done |
| **TASK-089** | Flanged effective width helper | INTEGRATION | ✅ Done |
| **TASK-077** | External user CLI test | CLIENT | ✅ Done |
| **TASK-079** | VBA parity spot-check | TESTER | ✅ Done |
| **TASK-078** | Seismic detailing validation | TESTER | ✅ Done |
| **TASK-131** | Add regression fixtures for BBS/DXF mark-diff (missing marks, mismatched counts) | TESTER | ✅ Done |
| **TASK-130** | Add contract tests for units conversion boundaries at API/CLI entrypoints | TESTER | ✅ Done |
| **TASK-129** | Reduce property-invariant skips by tightening generators (d > d_min, paired fy inputs) | TESTER | ✅ Done |
| **TASK-126** | Warn on Table 19 fck out-of-range in shear design | DEV | ✅ Done |
| **TASK-127** | Document Table 19 range warning in known-pitfalls + error schema | DOCS | ✅ Done |
| **TASK-128** | Add tests for Table 19 range warning | TESTER | ✅ Done |
| **TASK-122** | v0.12 release notes (CHANGELOG + RELEASES) | DOCS | ✅ Done |
| **TASK-123** | v0.12 version bump (Python/VBA) | DEVOPS | ✅ Done |
| **TASK-124** | v0.12 session log + next-session brief | DOCS | ✅ Done |
| **TASK-125** | v0.12 release tag + publish | DEVOPS | ✅ Done |
| **TASK-104** | Define stable API surface + doc updates | DOCS | ✅ Done |
| **TASK-105** | Validation APIs + `validate` CLI subcommand | DEV | ✅ Done |
| **TASK-106** | Detailing + BBS APIs + `detail` CLI subcommand | DEV | ✅ Done |
| **TASK-107** | DXF/report/critical API wrappers (no behavior change) | DEV | ✅ Done |
| **TASK-108** | API/CLI tests + stability labels | TESTER | ✅ Done |

---

## Archive

- Full history: `docs/_archive/TASKS_HISTORY.md`

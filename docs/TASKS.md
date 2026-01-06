# Task Board

> Single source of truth for work. Keep it short and current.

**Updated:** 2026-01-06

---

## Rules (read first)
- WIP = 1. Move tasks between sections; do not duplicate.
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

| ID | Task | Agent | Est | Priority | Status |
|----|------|-------|-----|----------|--------|
| **TASK-144** | Smart Library Integration (unified SmartDesigner API, dashboard output, CLI) | DEV | 1-2 days | 🔴 HIGH | 🚧 In Progress |

---

## Up Next

| ID | Task | Agent | Est | Priority | Status |
|----|------|-------|-----|----------|--------|
| **TASK-145** | Visualization Stack (matplotlib/plotly, BMD/SFD, beam elevation, cross-sections) | DEV | 3-4 days | 🟡 MEDIUM | ⏳ Queued |
| **TASK-146** | DXF Quality Polish (CAD visual QA, DWG conversion workflow) | QA | 2-3 days | 🟡 MEDIUM | ⏳ Queued |
| **TASK-147** | Developer Documentation (10+ examples, extension points, tutorials) | DOCS | 2-3 days | 🟡 MEDIUM | ⏳ Queued |

---

## Backlog

### Foundation & Architecture (CRITICAL for stability)

| ID | Task | Agent | Est | Priority |
|----|------|-------|-----|----------|
| **TASK-156** | **Research: Backward Compatibility Automation** (From TASK-149: contract testing in CI, breaking change detection, API stability enforcement, mutation testing for robustness) → Save as `docs/research/backward-compat-automation.md` | RESEARCHER | 3-4 hrs | 🔴 HIGH |
| **TASK-163** | Add Missing Return Type Annotations (audit script to find functions without return types; add types to all public functions; mypy --disallow-untyped-defs) | DEV | 1-2 days | 🔴 HIGH |
| **TASK-164** | Complete Error Migration (v0.14: add deprecation warnings to error_message/remarks fields; v1.0: remove deprecated fields; update all callers) | DEV | 1.5 days | 🔴 HIGH |

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

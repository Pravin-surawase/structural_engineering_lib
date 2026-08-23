# Task Board (Archive Snapshot)

> Snapshot of `docs/TASKS.md` before cleanup/restructure. Keep for history only.

> How to use: start each session here. Pick a task from "Up Next", move it to "Active", then move to "Done" when finished.

---

## Multi-Agent Workflow

When working on tasks, specify which agent role to use:

| Role | Doc | Use For |
|------|-----|---------|
| **DEV** | `agents/dev.md` | Implementation, refactoring, architecture |
| **TESTER** | `agents/tester.md` | Test design, edge cases, validation |
| **DEVOPS** | `agents/devops.md` | Repo structure, automation, releases |
| **PM** | `agents/pm.md` | Scope, prioritization, changelog |
| **UI** | `agents/ui.md` | Excel layout, UX flow, VBA forms |
| **CLIENT** | `agents/client.md` | Requirements, user stories, validation |
| **RESEARCHER** | `agents/researcher.md` | IS Codes, algorithms, technical constraints |
| **INTEGRATION** | `agents/integration.md` | Data schemas, ETABS/CSV mapping |
| **DOCS** | `agents/docs.md` | API docs, guides, changelog |
| **SUPPORT** | `agents/SUPPORT.md` | Troubleshooting, known issues |

See also: `docs/_internal/agent-workflow.md`

---

## Active

No active tasks. Pick from "Up Next" and move here when starting.

## Archived from TASKS.md (2026-01-13)

| ID | Task | Agent | Status |
|----|------|-------|--------|
| **RESEARCH-1.1/1.4/1.5** | Phase 1 MOO research completion: foundational audit, HAI/decision support, synthesis roadmap | MAIN | ✅ 2026-01-13 |
| **RESEARCH-1.3** | Phase 1.3 Bridge to Structural Engineering Complete: Analyzed 4 key papers (Parhi et al. 2026, Hong & Nguyen 2023, etc.) on MOO for RC beams/IS 456. | MAIN | ✅ 2026-01-13 |
| **RESEARCH-1.2** | Phase 1.2 Web Research Complete: 2025-2026 MOO trends consolidated in `KEY-FINDINGS.md` and `PAPER-TRACKER.csv` (20+ papers) | MAIN | ✅ 2026-01-13 |
| **TASK-457** | Add future annotations to 12 core modules (PR #344) | DEV | ✅ 2026-01-12 |
| **TASK-401** | Scanner Phase 4: Path division, max() patterns (PR #339) | AGENT_6 | ✅ 2026-01-12 |
| **SESSION-16** | PR workflow optimization for solo dev (150-line threshold, Streamlit category) | MAIN | ✅ 2026-01-12 |
| **TASK-435** | Fix session_manager.py division issue (PR #337) | AGENT_6 | ✅ 2026-01-11 |
| **TASK-437** | Move timedelta import to module level (PR #337) | AGENT_6 | ✅ 2026-01-11 |
| **TASK-432** | Archive outdated Agent 6 files | AGENT_6 | ✅ 2026-01-11 |
| **TASK-433** | Create Agent 6 comprehensive onboarding guide (PR #336) | DOCS | ✅ 2026-01-11 |
| **TASK-272** | Code Clause Database (67 clauses, 13 functions decorated, PR #333) | DEV | ✅ 2026-01-11 |
| **TASK-275** | Professional Liability Framework (docs/legal/) | DOCS | ✅ 2026-01-11 |
| **TASK-274** | Security Hardening Baseline (input validation audit, dependency scanning, CI setup) | DEVOPS | ✅ PR #331 |
| **TASK-273** | Interactive Testing UI (Streamlit clause traceability page) | DEV | ✅ PR #334 merged |
| **TASK-276** | Input Flexibility (BeamInput dataclasses, import helpers) | DEV | ✅ Session 19 |
| **TASK-277** | Calculation Report Generation (HTML/JSON/Markdown) | DEV | ✅ Session 19 |
| **TASK-278** | Verification & Audit Trail (SHA-256, immutable logs) | DEV | ✅ Session 19 |
| **TASK-279** | Engineering Testing Strategies (tolerance, property-based, regression) | TESTER | ✅ Session 19 |
| **TASK-422** | Document PR auto-merge behavior in copilot-instructions | DOCS | ✅ Session 15 |
| **TASK-431** | Fix finish_task_pr.sh auto-merge behavior | DEVOPS | ✅ Session 15 |
| **TASK-402** | Add type annotation checker to scanner | AGENT_6 | ✅ Session 18 |
| **TASK-403** | Add widget return type validation | AGENT_6 | ✅ Session 17 |
| **TASK-404** | Add circular import detection | AGENT_6 | ✅ Session 18 |
| **TASK-405** | Add performance issue detection | AGENT_6 | ✅ Session 18 |
| **TASK-411** | Create streamlit_preflight.sh (combines scanner + pylint + tests) | AGENT_6 | ✅ Session 17 |
| **TASK-412** | Create generate_streamlit_page.py scaffold | AGENT_6 | ✅ Session 19 |
| **TASK-413** | Create validate_session_state.py (audit all session_state usage) | AGENT_6 | ✅ Session 17 |
| **TASK-414** | Create performance profiler | AGENT_6 | ✅ Session 19 |
| **TASK-421** | Create agent-coding-standards.md | DOCS | ✅ Session 15 |
| **TASK-423** | Update copilot-instructions with coding rules | DOCS | ✅ Session 15 |
| **TASK-434** | Create Streamlit code files analysis (file-by-file research) | DOCS | ✅ Session 15 |
| **SESSION-14P3** | Git automation: docs/git-automation/ hub (6 files), ai_commit.sh --dry-run/--help, git_automation_health.sh, improvement plan, copilot-instructions update | MAIN | ✅ 2026-01-11 |
| **SESSION-14** | Phase 1: TASKS cleanup (50→15) + v0.17.0 roadmap (6 commits); Phase 2: Agent 8 research (8116 lines analyzed) + consolidation plan + archival + --quick default (5 commits) | MAIN | ✅ 2026-01-11 |
| **ONBOARD-03** | Agent start v2.1: full mode fix, worktree passthrough | DEVOPS | ✅ 2026-01-11 |
| **ONBOARD-02** | Agent start v2.0: unified script, proper preflight | DEVOPS | ✅ 2026-01-11 |
| **ONBOARD-01** | Unified agent_start.sh, consolidated 4 docs (PR #329) | DEVOPS | ✅ 2026-01-11 |
| **TASK-325** | Folder cleanup: archive 14 streamlit files (PR #325) | DEVOPS | ✅ 2026-01-11 |
| **TASK-313** | IS 456 Module Migration (7 modules, 3,048 lines, PR #323) | DEV | ✅ 2026-01-10 |
| **TASK-317** | Update codes/is456/__init__.py exports (PR #324) | DEV | ✅ 2026-01-11 |
| **TASK-312** | IS 456 migration research + automation scripts | ARCHITECT | ✅ 2026-01-10 |
| **TASK-311** | Folder cleanup automation scripts | DEVOPS | ✅ 2026-01-10 |
| **TASK-310** | Multi-code foundation: core/, codes/ (PR #322) | ARCHITECT | ✅ 2026-01-10 |
| **AGENT9-PHASE-B** | Folder Migration (5 commits) | AGENT_9 | ✅ 2026-01-10 |
| **GOV-001-015** | Folder Governance (11 tasks, 4 PRs, S11-S13) | AGENT_9 | ✅ 2026-01-11 |
| **TASK-270** | Fix 8 test failures from API refactoring | TESTER | ✅ 2026-01-10 |
| **TASK-271** | Fix 13 benchmark signature errors | TESTER | ✅ 2026-01-10 |
| **AGENT8-WEEK1** | Git workflow optimizations (4 PRs, 90% faster commits) | AGENT8 | ✅ 2026-01-09 |

## Recently Completed (Quality Hardening)

| ID | Task | Agent | Status |
|----|------|-------|--------|
| **TASK-126** | Warn on Table 19 fck out-of-range in shear design | DEV | ✅ Done |
| **TASK-127** | Document Table 19 range warning in known-pitfalls + error schema | DOCS | ✅ Done |
| **TASK-128** | Add tests for Table 19 range warning | TESTER | ✅ Done |

## Recently Completed (BBS + DXF Improvement Program)

| ID | Task | Agent | Status |
|----|------|-------|--------|
| **TASK-098** | Define BBS/DXF contracts + bar mark spec | DOCS | ✅ Done |
| **TASK-099** | Deterministic bar mark generator + wire into BBS | DEV | ✅ Done |
| **TASK-100** | BBS cut-length + hook/bend updates + weight rules | DEV | ✅ Done |
| **TASK-101** | DXF callouts include bar marks + zone labels | DEV | ✅ Done |
| **TASK-102** | DXF/BBS consistency checker (mark diff) | DEV | ✅ Done |
| **TASK-103** | DXF content tests (layers + text) | TESTER | ✅ Done |
| **TASK-083** | DXF deliverable layout polish | DEV | ✅ Done |
| **TASK-084** | DXF to PDF/PNG export workflow | DEVOPS | ✅ Done |

## Recently Completed (Public API Maintenance)

| ID | Task | Agent | Status |
|----|------|-------|--------|
| **TASK-109** | Centralize units validation in public API | DEV | ✅ Done |
| **TASK-110** | Fix `get_library_version()` fallback | DEV | ✅ Done |
| **TASK-111** | Align `__all__` exports with stability policy | DEV | ✅ Done |
| **TASK-112** | Document `api.py` stable entrypoints in api-stability.md | DOCS | ✅ Done |
| **TASK-113** | Add return type annotation for `detail_beam_is456()` | DEV | ✅ Done |
| **TASK-114** | Clarify units for `check_compliance_report()` in docs | DOCS | ✅ Done |
| **TASK-115** | Document or demote `beam_pipeline` in API docs | DOCS | ✅ Done |
| **TASK-116** | Fix serviceability function names in api-stability.md | DOCS | ✅ Done |
| **TASK-117** | Classify `report`/`report_svg` stability or stop re-exporting | DEV | ✅ Done |
| **TASK-118** | Document `get_library_version()` in api.md | DOCS | ✅ Done |
| **TASK-119** | Add public API helpers overview in api.md | DOCS | ✅ Done |
| **TASK-120** | Fix shear function names in api-stability.md | DOCS | ✅ Done |
| **TASK-121** | Classify `excel_integration` stability or stop re-exporting | DEV | ✅ Done |

## Recently Completed (v0.12)

| ID | Task | Agent | Status |
|----|------|-------|--------|
| **TASK-104** | Define stable API surface + doc updates | DOCS | ✅ Done |
| **TASK-105** | Validation APIs + `validate` CLI subcommand | DEV | ✅ Done |
| **TASK-106** | Detailing + BBS APIs + `detail` CLI subcommand | DEV | ✅ Done |
| **TASK-107** | DXF/report/critical API wrappers (no behavior change) | DEV | ✅ Done |
| **TASK-108** | API/CLI tests + stability labels | TESTER | ✅ Done |
| **TASK-122** | v0.12 release notes (CHANGELOG + RELEASES) | DOCS | ✅ Done |
| **TASK-123** | v0.12 version bump (Python/VBA) | DEVOPS | ✅ Done |
| **TASK-124** | v0.12 session log + next-session brief | DOCS | ✅ Done |
| **TASK-125** | v0.12 release tag + publish | DEVOPS | ✅ Done |

## Recently Completed (Visual v0.11)

| ID | Task | Agent | Status |
|----|------|-------|--------|
| **#134 (V01)** | report.py skeleton + load_job_spec helper | DEV | ✅ Done |
| **#135 (V02)** | report subcommand in __main__.py | DEV | ✅ Done |
| **#136 (V03)** | Critical Set Export (sorted utilization table) | DEV | ✅ Done |
| **#137 (V04)** | report_svg.py + cross-section SVG | DEV | ✅ Done |
| **#138 (V05)** | Input Sanity Heatmap | DEV | ✅ Done |
| **#139 (V06)** | Stability Scorecard | DEV | ✅ Done |
| **#140 (V07)** | Units Sentinel | DEV | ✅ Done |
| **#141 (V08)** | HTML export + batch packaging | DEV | ✅ Done |
| **#142 (V09)** | Golden file tests for report module | DEV | ✅ Done |

---

## Recently Completed (v0.10.6)

### W03-W05: Structured Error Schema Sprint — ✅ COMPLETE

| ID | Task | Agent | Status |
|----|------|-------|--------|
| **W03** | Design error schema (docs/reference/error-schema.md) | DOCS | ✅ Done |
| **W04** | Implement DesignError dataclass + integrate in core | DEV | ✅ Done |
| **W05** | Structured validation for doubly/flanged beams | DEV | ✅ Done |

**Deliverables:**
- `errors.py` module with frozen `DesignError` dataclass
- 16+ error codes: `E_INPUT_*`, `E_FLEXURE_*`, `E_SHEAR_*`, `E_DUCTILE_*`
- Structured errors in all core design functions
- 38 new tests for error schema
- Full error catalog in docs/reference/error-schema.md

---

## Recently Completed (v0.9.7-dev)

### Level B Serviceability + CLI/AI Discoverability (PR #62) — ✅ COMPLETE

| ID | Task | Agent | Status |
|----|------|-------|--------|
| **TASK-055** | Level B Serviceability (curvature-based deflection) | DEV | ✅ Done |
| **TASK-069** | Add `llms.txt` (AI summary) | DOCS | ✅ Done |
| **TASK-070** | CLI help pass | DEV | ✅ Done |
| **TASK-071** | Sync CLI reference | DOCS | ✅ Done |
| **TASK-072** | Cross-links from docs | DOCS | ✅ Done |

**Deliverables:**
- 7 new Level B functions in `serviceability.py`
- `DeflectionLevelBResult` dataclass
- 16 new tests (1730 total passing)
- `llms.txt` for AI discovery
- Enhanced CLI help text

### Release Automation Sprint (TASK-065 through TASK-068) — ✅ COMPLETE

**Deliverables (PR #59):**
- `scripts/release.py` — One-command release helper
- `scripts/check_doc_versions.py` — Validate no stale versions
- `.pre-commit-config.yaml` — Enhanced with ruff, doc check hooks
- CI doc drift check step

### Guardrails Hardening (Local CI Parity) — ✅ COMPLETE

| ID | Task | Agent | Status |
|----|------|-------|--------|
| **TASK-097** | Add local CI parity script (`scripts/ci_local.sh`) | DEVOPS | ✅ Done |

### Error Message Review (TASK-080) — ✅ COMPLETE

| ID | Task | Agent | Status |
|----|------|-------|--------|
| **TASK-080** | Error message review | SUPPORT | ✅ Done |

### Multi-Agent Review Remediation (Phase 1/2) — ✅ COMPLETE

| ID | Task | Agent | Status |
|----|------|-------|--------|
| **TASK-090** | Add branch coverage gate + pytest timeout in CI | DEVOPS | ✅ Done |
| **TASK-091** | Add `CODEOWNERS` | DEVOPS | ✅ Done |
| **TASK-092** | Complete Shear section in `docs/reference/api.md` | DOCS | ✅ Done |
| **TASK-093** | Document golden/parity vector sources | DOCS | ✅ Done |
| **TASK-094** | Add explicit `__all__` in `api.py` | DEV | ✅ Done |
| **TASK-095** | Remove duplicate doc drift check in CI | DEVOPS | ✅ Done |
| **TASK-096** | Add Mu_lim clause comment + expand `design_shear` docstring | DEV | ✅ Done |

---

## Up Next (v0.9.7 Release Sprint)

**Goal:** Prepare for v0.9.7 release with Level B serviceability + polish.

| ID | Task | Agent | Est. | Priority |
|----|------|-------|------|----------|
| **TASK-073** | Update CHANGELOG for v0.9.7 | PM | 15 min | 🔴 High |
| **TASK-074** | Bump version to 0.9.7 | DEVOPS | 10 min | 🔴 High |
| **TASK-075** | Update next-session-brief | DOCS | 15 min | 🟡 Medium |
| **TASK-076** | Tag and release v0.9.7 | DEVOPS | 15 min | 🔴 High |

---

## Up Next (v1.0 Readiness)

**Goal:** Complete beta gates and prepare for v1.0 stable release.

| ID | Task | Agent | Est. | Priority |
|----|------|-------|------|----------|
| **TASK-077** | External user CLI test | CLIENT | 1 hr | 🔴 Critical |
| **TASK-078** | Seismic detailing validation | TESTER | 45 min | 🟡 Medium |
| **TASK-079** | VBA parity spot-check | TESTER | 1 hr | 🟡 Medium |
| **TASK-083** | DXF deliverable layout polish | DEV | 2 hrs | 🟡 Medium |
| **TASK-084** | DXF to PDF/PNG export workflow | DEVOPS | 2 hrs | 🟡 Medium |

**v1.0 Beta Gates (from pre-release-checklist):**
- [x] 5 real beam validations documented
- [ ] One external engineer tries CLI cold
- [ ] All tests pass (currently: 1956 passed, 91 skipped)
- [ ] VBA parity verified

---

## Planned (BBS + DXF Improvement Program)

**Plan doc:** `docs/_archive/planning-completed-2026-03/bbs-dxf-improvement-plan.md`

| ID | Task | Agent | Est. | Priority | Bundle |
|----|------|-------|------|----------|--------|

---

## Planned (v0.12 Scope)

All v0.12 release tasks completed.

---

## Planned (Test Hardening)

| ID | Task | Agent | Est. | Priority |
|----|------|-------|------|----------|
| **TASK-126** | Reduce property-invariant skips by tightening generators (d > d_min, paired fy inputs) | TESTER | 2 hrs | 🟡 Medium |
| **TASK-127** | Add contract tests for units conversion boundaries at API/CLI entrypoints | TESTER | 2 hrs | 🟡 Medium |
| **TASK-128** | Add regression fixtures for BBS/DXF mark-diff (missing marks, mismatched counts) | TESTER | 2 hrs | 🟡 Medium |

---

## Planned (Public API Maintenance)

**Review doc:** `docs/planning/public-api-maintenance-review.md`

All Public API Maintenance tasks are complete.

---

## Backlog (Post-v1.0)

| ID | Task | Agent | Description |
|----|------|-------|-------------|
| **TASK-081** | Level C Serviceability | DEV | Shrinkage + creep deflection (Annex C full) |
| **TASK-082** | VBA Parity Automation | DEVOPS | Automated Python vs VBA comparison harness |
| **TASK-085** | Torsion Design + Detailing | DEV | Equivalent shear/moment + closed stirrups (Cl. 41) |
| **TASK-086** | Side-Face Reinforcement Check | DEV | D > 750 mm -> 0.1% web area bars (Cl. 26.5.1.3) |
| **TASK-087** | Anchorage Space Check | DEV | Verify Ld at supports; suggest hooks/bends if short (Cl. 26.2) |
| **TASK-088** | Slenderness/Stability Check | DEV | L > 60b or 250b^2/d warning (Cl. 23.1.2) |
| **TASK-089** | Flanged Effective Width Helper | INTEGRATION | Compute bf from slab geometry for T/L beams |

---

## Completed (v0.9.6)

- [x] **TASK-059: Shared Beam Pipeline Module** — `beam_pipeline.py` — PR #55
- [x] **TASK-060: Canonical Result Schema v1** — `BeamDesignOutput`, `MultiBeamOutput` — PR #55
- [x] **TASK-061: Units Validation at App Layer** — `validate_units()` — PR #55
- [x] **TASK-062: BBS/DXF Null Detailing Guard** — `or {}` guard in `__main__.py` — PR #56
- [x] **TASK-063: Canonical Units in job_runner Output** — Use return value of `validate_units()` — PR #56
- [x] **TASK-064: Case-Insensitive Units Validation** — Normalize to uppercase — PR #56

---

## Archive

- Full history: `docs/_archive/tasks-2025-12-27.md`

---

## Notes

- **Current Version**: v0.11.0
- **Last Updated**: 2025-12-30
- **Active Branch**: main
- **Tests**: Run `python scripts/update_test_stats.py` for current count
- **Target**: v0.20.0 stable release (see `docs/planning/v0.20-stabilization-checklist.md`)

## Archived from TASKS.md (2026-04-02)

### Phase 0: Quality Infrastructure (TASK-600–610)

| ID | Task | Status |
|----|------|--------|
| TASK-600 | Create function-quality-pipeline skill | ✅ Done |
| TASK-601 | Create function-quality-gate prompt | ✅ Done |
| TASK-602 | Update structural-math agent (12-point checklist, numerical rules) | ✅ Done |
| TASK-603 | Update tester agent (benchmark, degenerate, monotonicity tests) | ✅ Done |
| TASK-604 | Update reviewer agent (two-pass review, IS 456 quality checks) | ✅ Done |
| TASK-605 | Update api-developer agent (endpoint quality, plausibility guards) | ✅ Done |
| TASK-606 | Update structural-engineer agent (math verification protocol) | ✅ Done |
| TASK-607 | Update governance agent (quality metrics tracking) | ✅ Done |
| TASK-608 | Update doc-master agent (element doc checklist) | ✅ Done |
| TASK-609 | Update library-expert agent (quality enforcement rules) | ✅ Done |
| TASK-610 | Create blueprint v4.0 with quality pipeline | ✅ Done |

### Phase 1: Foundation Cleanup (TASK-611–625)

| ID | Task | Status |
|----|------|--------|
| TASK-611 | Create core/numerics.py — safe_divide(), approx_equal(), clamp() | ✅ Done |
| TASK-612 | Extract shared math to codes/is456/common/ | ✅ Done |
| TASK-613 | Hardcode safety factors in codes/is456/common/constants.py | ✅ Done |
| TASK-614 | Create @deprecated decorator in core/deprecation.py | ✅ Done |
| TASK-615 | Populate clauses.json with ~66 subclauses | ✅ Done |
| TASK-616 | Add IS 13920 references to clauses.json | ✅ Done |
| TASK-617 | Create test assertion helpers | ✅ Done |
| TASK-618 | Top-level __init__.py exports | ✅ Done |
| TASK-619 | Unit plausibility guards in services/api.py | ✅ Done |
| TASK-620 | Stack trace sanitization in fastapi_app/main.py | ✅ Done |
| TASK-621 | Add recovery field to DesignError | ✅ Done |
| TASK-622 | Create check_function_quality.py script | ✅ Done |
| TASK-623 | Create check_clause_coverage.py script | ✅ Done |
| TASK-624 | Create check_new_element_completeness.py script | ✅ Done |
| TASK-625 | Create maintenance playbook | ✅ Done |

### Phase 1.5: IS 456 Beam Restructure (TASK-700–712)

| ID | Task | Status |
|----|------|--------|
| TASK-700 | Create codes/is456/beam/ directory + __init__.py | ✅ PR #466 |
| TASK-701 | Move flexure.py → beam/flexure.py | ✅ PR #466 |
| TASK-702 | Move shear.py → beam/shear.py | ✅ PR #466 |
| TASK-703 | Move detailing.py → beam/detailing.py | ✅ PR #466 |
| TASK-704 | Move serviceability.py → beam/serviceability.py | ✅ PR #466 |
| TASK-705 | Move torsion.py → beam/torsion.py | ✅ PR #466 |
| TASK-706 | Update compliance.py imports | ✅ PR #466 |
| TASK-707 | Update __init__.py re-exports | ✅ PR #466 |
| TASK-708 | Generate backward-compat shims | ✅ PR #466 |
| TASK-709 | Move ductile.py → codes/is13920/beam.py + shim | ✅ PR #467 |
| TASK-710 | Fix upward import in detailing.py | ✅ PR #467 |
| TASK-711 | Run full test suite — zero failures gate | ✅ PR #466 |
| TASK-712 | Enhanced shear near supports (Cl 40.3) | ✅ PR #468 |

### Agent Evolver Infrastructure (TASK-800.P3–P11, P.T)

| ID | Task | Status |
|----|------|--------|
| TASK-800.P3 | Shared libraries | ✅ Done |
| TASK-800.P4 | Session collector | ✅ Done |
| TASK-800.P5 | Agent scorer (11 dimensions) | ✅ Done |
| TASK-800.P6 | Drift detector | ✅ Done |
| TASK-800.P7 | Compliance checker (8 rules) | ✅ Done |
| TASK-800.P8 | Trend analysis (Mann-Kendall) | ✅ Done |
| TASK-800.P9 | Instruction evolver | ✅ Done |
| TASK-800.P10 | Paper data export | ✅ Done |
| TASK-800.P2 | Agent-evolver definition + skill | ✅ Done |
| TASK-800.P11 | run.sh evolve integration | ✅ Done |
| TASK-800.T | Evolver unit tests | ✅ Done |

### Agent Infrastructure — claw-code adaptation (TASK-850–872)

| ID | Task | Status |
|----|------|--------|
| TASK-850 | Agent Registry JSON | ✅ Done |
| TASK-851 | Unified Tool Registry | ✅ Done |
| TASK-852 | Prompt Router | ✅ Done |
| TASK-853 | run.sh integration | ✅ Done |
| TASK-854 | Automation-map groups | ✅ Done |
| TASK-855 | SESSION_LOG compaction | ✅ Done |
| TASK-856 | Session state persistence | ✅ Done |
| TASK-857 | Pipeline state tracking | ✅ Done |
| TASK-858 | Fast session start | ✅ Done |
| TASK-859 | Cost/token logging | ✅ Done |
| TASK-860 | Tool permission enforcement | ✅ Done |
| TASK-862 | Permission audit report | ✅ Done |
| TASK-863 | Hook framework | ✅ Done |
| TASK-864 | Hook implementations (6 hooks) | ✅ Done |
| TASK-865 | CLI smoke tests (13 tests) | ✅ Done |
| TASK-866 | Parity dashboard | ✅ Done |
| TASK-868 | Config precedence validator | ✅ Done |
| TASK-870 | Parallel pipeline stages | ✅ Done |
| TASK-872 | Skill tier classification | ✅ Done |
| TASK-861 | Trust gate initialization | ✅ Done |
| TASK-867 | Snapshot regression tests | ✅ Done |
| TASK-869 | Update all 15 agent files | ✅ Done |
| TASK-871 | Update AGENTS.md/CLAUDE.md | ✅ Done |

### v0.20–v0.21 Recently Done (archived 2026-04-02)

| ID | Task | Status |
|----|------|--------|
| — | Release infrastructure overhaul | ✅ Done |
| — | Session 107: Safety gates hardening | ✅ Done |
| — | TopBar nav + ModeSelect quick links | ✅ Done |
| TASK-518 | Torsion API + React | ✅ Done |
| TASK-515 | Load Calculator | ✅ Done |
| TASK-514 | PDF Export | ✅ Done |
| — | Created WORKLOG.md | ✅ Done |
| TASK-522 | BeamDetailPanel | ✅ Done |
| TASK-523 | FloatingDock + BentoGrid Dashboard | ✅ Done |
| TASK-524 | DesignView dynamic layout | ✅ Done |
| TASK-526 | Cross-section annotations | ✅ Done |
| TASK-525 | Smart HubPage | ✅ Done |
| TASK-517 | Project BOQ | ✅ Done |
| — | Bug fix: 3D/2D top bar mismatch | ✅ Done |
| TASK-505 | React API integration tests (86 tests) | ✅ Done |
| TASK-510 | React Batch design page | ✅ Done |
| TASK-509 | Type annotations: Streamlit coverage | ✅ Done |
| — | Phase 1+2 cleanup | ✅ Done |
| TASK-502 | Code-split React bundle | ✅ Done |
| TASK-501 | Fix check_all.py failures | ✅ Done |
| TASK-508 | Split ai_workspace.py | ✅ Done |
| TASK-503 | Wire REST fallback in DesignView | ✅ Done |
| TASK-506 | React test infra: Vitest | ✅ Done |
| TASK-507 | Fix arch violations | ✅ Done |
| TASK-500 | Unified CLI + onboarding audit | ✅ Done |
| TASK-499 | AI agent efficiency | ✅ Done |

### Column Design — Phase 2 Recently Done (archived 2026-04-02)

| ID | Task | IS 456 Clause | Status |
|----|------|---------------|--------|
| TASK-630 | Column types | — | ✅ Done |
| TASK-631 | classify_column + min_eccentricity | Cl 25.1.2, 25.4 | ✅ Done |
| TASK-632 | short_axial_capacity | Cl 39.3 | ✅ Done |
| TASK-633 | Short column uniaxial | Cl 39.5 | ✅ Done |
| TASK-634 | P-M interaction curve | Cl 39.5, Annex G | ✅ Done |
| TASK-635 | Biaxial bending check | Cl 39.6 | ✅ Done |
| TASK-636 | Effective length | Cl 25.2, PR #481 | ✅ Done |
| TASK-637 | Additional moment | Cl 39.7.1 | ✅ Done |
| TASK-621 | DesignError recovery field | — | ✅ Done |
| TASK-622 | check_function_quality.py | — | ✅ Done |
| TASK-623 | check_clause_coverage.py | — | ✅ Done |
| TASK-624 | check_new_element_completeness.py | — | ✅ Done |
| TASK-625 | maintenance-playbook.md | — | ✅ Done |

### v0.21 React UX Overhaul (archived 2026-04-06)

| # | Task ID | Feature | Files | Status |
|---|---------|---------|-------|--------|
| A1 | TASK-522 | BeamDetailPanel in BuildingEditorPage | `BeamDetailPanel.tsx`, `BuildingEditorPage.tsx`, `Viewport3D.tsx` | ✅ Done |
| A2 | TASK-523 | Activate FloatingDock + BentoGrid Dashboard | `App.tsx`, `DashboardPage.tsx` | ✅ Done |
| A3 | TASK-524 | DesignView dynamic layout | `DesignView.tsx` | ✅ Done |
| A4 | TASK-525 | Smart HubPage replacing ModeSelectPage | `HubPage.tsx`, `App.tsx` | ✅ Done |
| A5 | TASK-526 | Cross-section annotations | `CrossSectionView.tsx` | ✅ Done |
| A6 | TASK-527 | TopBar context badges + SettingsPanel | `TopBar.tsx`, `SettingsPanel.tsx` | ✅ Done |
| A7 | TASK-528 | Workflow breadcrumb for batch flow | `WorkflowBreadcrumb.tsx` | ✅ Done |

### v0.21 Library Expansion (items 1–6, archived 2026-04-06)

| # | Task ID | Feature | Status |
|---|---------|---------|--------|
| 1 | TASK-514 | PDF Export | ✅ Done |
| 2 | TASK-515 | Load Calculator | ✅ Done |
| 3 | TASK-516 | Triangular + Moment loads | ✅ Done |
| 4 | TASK-517 | Project BOQ | ✅ Done |
| 5 | TASK-518 | Torsion API + React | ✅ Done |
| 6 | TASK-519 | Alternatives Panel (Pareto) | ✅ Done |

## Archived from TASKS.md (2026-08-16 post-INDIA-2 compaction)

Older completed rows moved intact from the live `Recently Done` table;
current release and INDIA-2 accepted/HOLD truth remain in `docs/TASKS.md`.

| ID | Task | Agent | Status |
|----|------|-------|--------|
| LIB-PRO-007-G0 | Froze canonical product contracts and the bounded P1-P7 foundation sequence before further INDIA-3 engineering | Main Agent | ✅ DONE — PR #852 merged at `a6d47a85` |
| LIB-PRO-006 | Established maintained no-hidden-default gravity onboarding, discoverability, and governing-result foundations from the practical audit | Main Agent | ✅ DONE — PR #851 merged at `2d6df18e` |
| MAINT-0134 | Consolidated Claude, Copilot, VS Code, and Codex agent instructions into one validated ownership contract | Main Agent | ✅ DONE — PR #850 merged at `69c09cc7` |
| INDIA-2-FLAT | Implemented and accepted one bounded regular-interior direct-design flat-slab and concrete-only punching workflow with public provenance | Main Agent + structural engineer | ✅ DONE — G0 and A-E integrated; 214-test focused family selection and independent hand benchmark pass; qualified review and excluded flat-slab systems remain held |
| INDIA-2-FLAT-E | Published the typed Python composition, thin REST route, capability/semantic truth, deterministic manifest promotion, and publication evidence | Main Agent + API developer | ✅ INTEGRATED — PR #785 merged as `b04d8065`; supported case is 11/21 manifest truth and all 79 routes have direct tests |
| INDIA-2-FLAT-D | Added centred square interior-column punching demand, concrete-only capacity, and both redesign boundaries | Main Agent + structural math | ✅ INTEGRATED — PR #784 merged as `d1884946`; frozen reaction/perimeter/stress/utilization and fail-closed cases pass |
| INDIA-2-FLAT-C | Added bounded flexure, provided straight-bar checks, no-drop support-top extension, and reviewed span/depth comparison in both directions | Main Agent + structural math | ✅ COMPLETE — all frozen steel/detailing/serviceability values pass; direct deflection, crack width, punching, and public workflow remain held |
| INDIA-2-FLAT-B | Added total static moment and bounded interior negative/positive and column/middle-strip distribution in both directions | Main Agent + structural math | ✅ COMPLETE — frozen moment values and conservation identities pass; capability remains held until FLAT-E |
| INDIA-2-FLAT-A | Added typed grid/panel/material/load contracts, direct-design eligibility, both clear-span directions, strip definitions, exact Clause 31 registration, and fail-closed tests | Main Agent + structural math | ✅ COMPLETE — 131 focused geometry/clause/traceability/manifest tests pass; capability remains held until FLAT-E |
| INDIA-2-FLAT-G0 | Froze one equal-span square interior flat-slab direct-design and centred square-column punching case with a pre-implementation hand benchmark | Main Agent + structural engineer | ✅ GO — FLAT-A-E owner-activated; unequal/exterior/drop/head/opening/patterned-load/moment-transfer and punching-reinforcement cases remain held |
| INDIA-2-DEEP | Implemented and accepted one bounded simply supported Clause 29 positive-reinforcement workflow with public provenance | Main Agent + structural engineer | ✅ DONE — G0 and A-D integrated; 157-test focused family selection and independent hand benchmark pass; qualified review and excluded deep-beam systems remain held |
| INDIA-2-DEEP-D | Added thin typed FastAPI transport, canonical deep-beam capability/semantic truth, deterministic manifest promotion, and publication evidence | Main Agent + API developer | ✅ COMPLETE — public bounded workflow is supported; React, release, and all held systems remain excluded |
| INDIA-2-DEEP-C | Published one typed Python workflow composing geometry, action, positive tie, anchorage, side-face, provenance, and retained holds | Main Agent + backend | ✅ COMPLETE — canonical root/services API, executable hand benchmark, JSON-safe result, and public docs pass; capability remains held until DEEP-D |
| INDIA-2-DEEP-B | Added required/provided positive tie, placement, continuity, exact 0.8Ld anchorage, side-face area/spacing/grid, transverse-enclosure boundary, and composed dispositions | Main Agent + structural math | ✅ COMPLETE — 42 direct deep-beam tests pass; capability remains held until DEEP-D |
| INDIA-2-DEEP-A | Added typed geometry/material/action contracts, effective-span classification, both Clause 29.2 lever-arm branches, tension-zone depth, exact clause registration, and fail-closed tests | Main Agent + structural math | ✅ COMPLETE — 109 focused geometry/clause-database/traceability/manifest tests pass; no capability claim before DEEP-D |
| INDIA-2-DEEP-G0 | Froze one simply supported solid rectangular deep-beam positive-reinforcement check with public clause provenance and a pre-implementation hand benchmark | Main Agent + structural engineer | ✅ GO — caller-supplied positive factored moment; bearing/nodal verification is an external prerequisite; openings, hanging action, continuous beams, generalized strut-and-tie, and alternate systems remain held |
| INDIA-2-WALL | Implemented and accepted one bounded braced empirical vertical-compression wall workflow with public Clause 32 provenance | Main Agent + structural engineer | ✅ DONE — A-D integrated; 135-test focused family selection and independent hand benchmark pass; qualified review and excluded wall systems remain held |
| INDIA-2-WALL-D | Added thin typed FastAPI transport, canonical wall capability/semantic truth, manifest promotion, and publication evidence | Main Agent + API developer | ✅ INTEGRATED — PR #772 merged as `46094a8c`; family acceptance passed from that exact integrated head |
| INDIA-2-WALL-C | Published one typed Python workflow composing the axial and provided-reinforcement checks with retained provenance and holds | Main Agent + backend | ✅ INTEGRATED — PR #771 merged as `ea282b6d` |
| INDIA-2-WALL-B | Implemented provided vertical/horizontal reinforcement area, material-ratio, spacing, and transverse-enclosure boundary checks | Main Agent + structural math | ✅ INTEGRATED — PR #770 merged as `e9e589d2`; capability remains held until WALL-D |
| INDIA-2-WALL-A | Implemented typed bracing/geometry/action contracts, effective height, slenderness, eccentricity, empirical axial capacity, exact Clause 32 registration, and fail-closed tests | Main Agent + structural math | ✅ INTEGRATED — PR #769 merged as `7eb55746`; capability remains held until WALL-D |
| INDIA-2-WALL-G0 | Froze one Clause 32.2 braced wall vertical-compression check with public clause provenance, pre-implementation benchmark, units, fail-closed boundaries, and focused-gate cadence | Main Agent + structural engineer | ✅ GO — owner activated WALL-A-D; applied moment, horizontal action, two-grid and alternate wall systems remain held |
| INDIA-2-PLAN | Consolidated INDIA-2 scope, family order, packet gates, exclusions, validation cadence, and completion criteria into one execution document | Main Agent + repository owner | ✅ DONE — INDIA-2-WALL-G0 remains the next decision; no engineering implementation activated |
| INDIA-COMPLETION-PLAN | Reconciled the canonical INDIA-0 through INDIA-4 finish waves and mapped historical staircase receipts to INDIA-2-STAIR without renaming them | Main Agent + repository owner | ✅ DONE — next discussion is INDIA-2-WALL-G0; no calculation implementation activated |
| INDIA-2-STAIR | Completed one bounded longitudinal straight-flight staircase family | Main Agent + structural engineer | ✅ DONE — historical INDIA-2A-D and INDIA-2-CUMULATIVE remain the immutable evidence names |
| INDIA-2-CUMULATIVE | Ran the broad Python suite, full repository gate, manifest reconciliation, and cumulative essential review after A-D integration | Main Agent + reviewer | ✅ DONE — 5,950 Python tests and full 30/30 gate green; staircase remains one bounded L2 API workflow and qualified review remains separate |
| INDIA-2D | Published one typed Python/FastAPI straight-flight workflow and reconciled capability truth | Main Agent + API developer | ✅ DONE — public benchmark returns REVIEW_REQUIRED truthfully; unsafe and passing cases preserve FAIL/PASS boundaries; React remains excluded |
| INDIA-2C | Composed accepted actions into singly reinforced flexure, supplied-bar detailing, ordinary shear, action-integrity, and basic span/depth dispositions | Main Agent + structural math | ✅ DONE — NPTEL Example 9.1 strength/detailing targets pass and truthfully return REVIEW_REQUIRED for unmodified L/d; unsafe cases return FAIL |
| INDIA-2B | Implemented typed Clause 33 geometry, explicit concrete self-weight, and equilibrated three-segment actions for the accepted straight-flight case | Main Agent + structural math | ✅ DONE — NPTEL Example 9.1 geometry/load/action targets and fail-closed boundaries pass; capability remains HELD until INDIA-2D |
| INDIA-2A | Selected and froze one longitudinal straight waist-slab flight with collinear landings against controlled Clause 33 sources and the IIT Kharagpur NPTEL Example 9.1 benchmark | Main Agent + structural engineer | ✅ GO — B-D owner-activated; alternate stairs, other families, IS 875/IS 1893, qualified review, and release remain held |
| INDIA-1-CUMULATIVE | Ran broad Python, full repository, manifest reconciliation, and cumulative essential review after A-D integration | Main Agent + reviewer | ✅ DONE — PR #758 exact-head gate passed; 5,926 Python tests and full 30/30 gate green; reviewed tree squash-merged as `4e92f3d7` |
| INDIA-1D | Closed solid-slab direct-deflection, crack-width, automatic-shear-reinforcement, and single-action load-envelope decisions with machine-visible holds | Main Agent | ✅ DONE — PR #757 exact-head gate passed; reviewed tree squash-merged as `ca55f22d` |
| INDIA-1C | Published the bounded concentric isolated-footing composition with typed provenance, accepted benchmark, and explicit eccentric/other-foundation holds | Main Agent | ✅ DONE — PR #756 exact-head gate passed; reviewed tree squash-merged as `236ce646` |
| INDIA-1B | Reconfirmed stable solid rectangular tied-column routes as a symmetric two-face reinforcement idealization and retained circular, arbitrary-layout, and experimental PMM cases | Main Agent | ✅ DONE — PR #755 exact-head gate passed; reviewed tree squash-merged as `f44452dd` |
| INDIA-1A | Added a benchmarked monolithic sagging T-beam flexure/web-shear/explicit-serviceability composition with fail-closed retained boundaries | Main Agent | ✅ DONE — PR #754 exact-head gate passed; reviewed tree squash-merged as `3a7e162e` |
| INDIA-0 | Reconciled supported and held Indian RC scope into one generated, standard-namespaced capability/registration manifest; repaired both coverage consumers | Main Agent | ✅ DONE — PR #753 exact-head gate passed; reviewed tree squash-merged as `0373de68` |
| COLUMN-PMM-001 | Recovered and independently benchmarked the experimental rectangular-column P-Mx-My fiber surface | Main Agent | ✅ SOFTWARE COMPLETE — PR #738 merged; module remains experimental and outside the stable API |
| ALPHA-0231-CANDIDATE | Published the exact 0.23.1a1 Alpha through exact-head CI, TestPyPI, production PyPI, and GitHub prerelease gates | Main Agent + ops | ✅ DONE — production run `31468341946`; exact public package UAT green |
| IS456-SLAB-PRELAUNCH | Record and enforce source/licensing permission for public distribution of approved-scope normalized IS 456 data | Owner + Main Agent | ✅ DONE — owner confirmed 2026-08-11; canonical record, preflight, candidate, and publish-CI gates added |
| IS456-SLAB-001 | Implemented simply supported/continuous one-way and common two-way solid slabs with built-in/external coefficients, topology, strips, corner torsion, detailing, serviceability, shear, FastAPI and a revision-safe React workbench | Main Agent | ✅ SOFTWARE COMPLETE — 5,532 Python, 388 FastAPI, 241 React, 30/30 integrated checks and live browser pass; flat slabs held |
| UIX-001 | Built one compact 3D-first structural workbench and schema-driven bounded workflow foundation | Main Agent | ✅ DONE — PR #721 merged; Pages/release/public runner remain held |
| DEPS-MAINT-001 | Replaced incompatible Python and React dependency PRs with coherent Python 3.11/Node 24 packets and added recurrence guards | Main Agent | ✅ DONE — PRs #708, #709, and #712 merged |
| ADOPT-001 | Completed executable public truth, capability discovery, typed API contracts, production auth fail-close, evidence identity, React/BOQ trust presentation, and truthful Alpha/docs policy | Main Agent | ✅ DONE — PR #707 merged; release holds retained |
| LIB-IS456-V1 | Completed C0-C4, bounded evidence, exact artifacts, public Alpha UAT, and v0.23.1a1 publication | Main Agent + owner | ✅ DONE |
| MAINT-009 | Integrated automation and Actions updates, repaired Weekly Verification compatibility, and cleared obsolete GitHub/session state | Main Agent | ✅ DONE |
| MAINT-001 | Preserve the inherited worktree, recover the Mac baseline, and close PR #676 required checks | Main Agent | ✅ DONE |
| MAINT-006 | Add enforceable low-token defaults, context rules, analytics-calibrated model routing, and automation | Main Agent | ✅ DONE |
| MAINT-007 | Re-audit and modernize onboarding, agent/tool discovery, usage telemetry, and PR browser behavior | Main Agent | ✅ DONE |
| MAINT-005 | Verify the full live browser/export workflow and establish the evidence-based v0.21.7 finish line | Main Agent | ✅ DONE |
| MAINT-004 | Reconcile canonical checks, manifests, indexes, health, parity, active docs, and feedback | Main Agent | ✅ DONE |
| MAINT-002 | Repair nightly QA, maintained import E2E contracts, and documentation links | Main Agent | ✅ DONE |
| MAINT-003 | Rebuild clean Python/npm dependency locks and enforce security audits | Main Agent | ✅ DONE |

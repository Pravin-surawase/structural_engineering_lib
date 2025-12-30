# Task Board (Archive Snapshot)

> Snapshot of `docs/TASKS.md` before cleanup/restructure. Keep for history only.

> How to use: start each session here. Pick a task from "Up Next", move it to "Active", then move to "Done" when finished.

---

## Multi-Agent Workflow

When working on tasks, specify which agent role to use:

| Role | Doc | Use For |
|------|-----|---------|
| **DEV** | `agents/DEV.md` | Implementation, refactoring, architecture |
| **TESTER** | `agents/TESTER.md` | Test design, edge cases, validation |
| **DEVOPS** | `agents/DEVOPS.md` | Repo structure, automation, releases |
| **PM** | `agents/PM.md` | Scope, prioritization, changelog |
| **UI** | `agents/UI.md` | Excel layout, UX flow, VBA forms |
| **CLIENT** | `agents/CLIENT.md` | Requirements, user stories, validation |
| **RESEARCHER** | `agents/RESEARCHER.md` | IS Codes, algorithms, technical constraints |
| **INTEGRATION** | `agents/INTEGRATION.md` | Data schemas, ETABS/CSV mapping |
| **DOCS** | `agents/DOCS.md` | API docs, guides, changelog |
| **SUPPORT** | `agents/SUPPORT.md` | Troubleshooting, known issues |

See also: `docs/_internal/AGENT_WORKFLOW.md`

---

## Active

No active tasks. Pick from "Up Next" and move here when starting.

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

**Plan doc:** `docs/planning/bbs-dxf-improvement-plan.md`

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

- Full history: `docs/_archive/TASKS_2025-12-27.md`

---

## Notes

- **Current Version**: v0.11.0
- **Last Updated**: 2025-12-30
- **Active Branch**: main
- **Tests**: Run `python scripts/update_test_stats.py` for current count
- **Target**: v0.20.0 stable release (see `docs/planning/v0.20-stabilization-checklist.md`)

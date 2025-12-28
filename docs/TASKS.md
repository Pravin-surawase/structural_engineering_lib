# Task Board

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

*(Nothing currently in progress)*

---

## Recently Completed (v0.20.0 Stabilization)

### Documentation & Quality Sprint (PRs #89-93) — ✅ COMPLETE

| ID | Task | Agent | Status |
|----|------|-------|--------|
| **S-015** | Fix broken internal links | DOCS | ✅ Done |
| **S-014** | Fix runnable examples | DOCS | ✅ Done |
| **S-009** | Fix verification examples | TESTER | ✅ Done |
| **S-006** | Improve error messages | SUPPORT | ✅ Done |
| **S-020–S-032** | Verify all High Priority items | DEV | ✅ Done |

**Deliverables:**
- `scripts/check_links.py` — reusable link checker
- Improved `job_runner.py` error messages
- Fixed 4 broken doc links
- Fixed 2 incorrect expected values in examples
- All robustness + performance items verified

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

### External CLI Smoke Test (TASK-077) — ✅ COMPLETE

| ID | Task | Agent | Status |
|----|------|-------|--------|
| **TASK-077** | External user CLI test | CLIENT | ✅ Done |

### Seismic Detailing Validation (TASK-078) — ✅ COMPLETE

| ID | Task | Agent | Status |
|----|------|-------|--------|
| **TASK-078** | Seismic detailing validation | TESTER | ✅ Done |

### VBA Parity Spot-Check (TASK-079) — ✅ COMPLETE

| ID | Task | Agent | Status |
|----|------|-------|--------|
| **TASK-079** | VBA parity spot-check | TESTER | ✅ Done |

### DXF Deliverable Layout Polish (TASK-083) — ✅ COMPLETE

| ID | Task | Agent | Status |
|----|------|-------|--------|
| **TASK-083** | DXF deliverable layout polish | DEV | ✅ Done |

### DXF to PDF/PNG Export Workflow (TASK-084) — ✅ COMPLETE

| ID | Task | Agent | Status |
|----|------|-------|--------|
| **TASK-084** | DXF to PDF/PNG export workflow | DEVOPS | ✅ Done |

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

**v1.0 Beta Gates (from pre-release-checklist):**
- [x] 5 real beam validations documented
- [ ] One external engineer tries CLI cold
- [ ] All tests pass (currently: 1730 passed, 95 skipped)
- [x] VBA parity verified

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

- **Current Version**: v0.10.3
- **Last Updated**: 2025-12-28
- **Active Branch**: main
- **Tests**: Run `python scripts/update_test_stats.py` for current count
- **Target**: v0.20.0 stable release (see `docs/planning/v0.20-stabilization-checklist.md`)

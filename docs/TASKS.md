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
| **TASK-080** | Error message review | SUPPORT | 30 min | 🟢 Low |

**v1.0 Beta Gates (from pre-release-checklist):**
- [x] 5 real beam validations documented
- [ ] One external engineer tries CLI cold
- [ ] All tests pass (currently: 1730 passed, 95 skipped)
- [ ] VBA parity verified

---

## Backlog (Post-v1.0)

| ID | Task | Agent | Description |
|----|------|-------|-------------|
| **TASK-056** | Column Design Module | DEV | Axial + biaxial bending, IS 456 interaction curves |
| **TASK-057** | Slab Design Module | DEV | One-way/two-way slabs, Table 26 coefficients |
| **TASK-058** | ETABS API Integration | INTEGRATION | CSI OAPI access (Windows only) |
| **TASK-081** | Level C Serviceability | DEV | Shrinkage + creep deflection (Annex C full) |
| **TASK-082** | VBA Parity Automation | DEVOPS | Automated Python vs VBA comparison harness |

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

- **Current Version**: v0.10.2
- **Last Updated**: 2025-12-28
- **Active Branch**: main
- **Tests**: 1730 passed, 95 skipped
- **Target**: v1.0 stable release after external user validation

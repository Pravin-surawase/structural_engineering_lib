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

### Release Automation Sprint (TASK-065 through TASK-068) — ✅ COMPLETE

**Goal:** Automate release workflow to prevent version drift and missed updates.

| ID | Task | Agent | Est. | Status |
|----|------|-------|------|--------|
| **TASK-065** | Release helper script | DEVOPS | 30 min | ✅ Done |
| **TASK-066** | Doc drift check script | DEVOPS | 30 min | ✅ Done |
| **TASK-067** | Pre-commit hook config | DEVOPS | 15 min | ✅ Done |
| **TASK-068** | CI release-check job | DEVOPS | 30 min | ✅ Done |

**Deliverables (all merged in PR #59):**
- `scripts/release.py` — One-command release helper
- `scripts/check_doc_versions.py` — Validate no stale versions
- `.pre-commit-config.yaml` — Enhanced with ruff, doc check hooks
- `.github/workflows/python-tests.yml` — Added doc drift check step
- `scripts/bump_version.py` — Fixed api.md version pattern

### CLI + AI Discoverability Sprint (TASK-069 through TASK-072) — ✅ COMPLETE

**Goal:** Make CLI commands easy to discover for humans and AI without bloating README.
**Plan:** `docs/planning/cli-ai-discovery-plan.md`

| ID | Task | Agent | Est. | Status |
|----|------|-------|------|--------|
| **TASK-069** | Add `llms.txt` (AI summary + links) | DOCS | 30 min | ✅ Done |
| **TASK-070** | CLI help pass (examples + required args) | DEV | 45 min | ✅ Done |
| **TASK-071** | Sync CLI reference (`docs/cookbook/cli-reference.md`) | DOCS | 45 min | ✅ Done |
| **TASK-072** | Cross-links from docs index/README (light touch) | DOCS | 15 min | ✅ Done |

---

## Up Next (v1.0 Docs/PM)

- [x] **TASK-052: User Guide (Getting Started)** — Agent: DOCS — `docs/getting-started/user-guide.md` — Complete workflow guide.
- [x] **TASK-053: Validation Pack** — Agent: DOCS — `docs/verification/validation-pack.md` — 5 benchmark beams with IS 456 references.
- [x] **TASK-054: API Stability Commitment** — `docs/reference/api-stability.md` — Defines stable vs internal APIs.

---

## In Progress (v0.9.7)

- [ ] **TASK-055: Level B Serviceability** — Agent: DEV — Full deflection calc, long-term factors, cracking moment. *(implementation complete, awaiting PR)*

---

## Backlog (Advanced)

- [ ] **TASK-056: Column Design Module** — Agent: DEV — Axial + biaxial bending, IS 456 interaction curves.
- [ ] **TASK-057: Slab Design Module** — Agent: DEV — One-way/two-way slabs, Table 26 coefficients.
- [ ] **TASK-058: ETABS API Integration** — Agent: INTEGRATION — CSI OAPI access (Windows only).

---

## Recently Completed (v0.9.6)

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

- **Current Version**: v0.9.6
- **Last Updated**: 2025-12-27
- **Active Branch**: main
- **Tests**: See CI for current totals and coverage

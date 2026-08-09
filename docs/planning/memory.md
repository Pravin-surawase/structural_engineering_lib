---
owner: Main Agent
status: active
last_updated: 2026-08-09
doc_type: guide
complexity: intermediate
tags: []
---

# Project Memory - Persistent Context

**Type:** Reference
**Audience:** All Agents
**Status:** Active
**Importance:** High
**Created:** 2025-01-01
**Last Updated:** 2026-08-09

---

**Purpose:** Maintain continuity across sessions and agents
**Update Frequency:** After major milestones or architectural decisions

---

## Current Maintenance State (2026-08-07)

### Recovery Context

- Development resumed after a four-month pause and a Mac laptop → Mac Mini transfer.
- Git history, reachable objects, sample data, package source, and ARM64 Python environment transferred intact.
- The inherited April worktree began with 73 tracked modifications and 47 untracked files and is preserved in pushed checkpoint `b28ee4e3`.
- Seventy modified Python files are AST-equivalent formatter output; untracked learning/migration/master-plan docs contain roughly 25,000 lines and require human/editorial triage.
- Do not reset or bulk-clean the preserved history; continue through the enforced Git workflow on `task/MAINT-001`.

### Product and Engineering Baseline

- **Published:** v0.21.6 on PyPI; post-tag repository commits are documentation-only.
- **Python:** final preflight passes 5,159 tests (3 skipped, 6 deselected); core IS 456 calculation modules are generally 89–100% covered.
- **FastAPI:** 336 tests pass; 60 endpoints across 13 routers; response contract is `{success, data}`.
- **React:** 146 tests and production build pass; statement coverage is only 17.74%, but the critical live workstation flow is browser-verified through exports.
- **Package:** a fresh built-wheel environment passes 5,120 tests (41 skipped, 6 deselected) and the packaged job → critical-case → HTML-report CLI workflow.
- **Elements:** beam workflow is mature; column and footing mathematics/API exist; UI completeness and future slab/wall/stair scope must be decided separately.

### Current Risks and Decisions

1. **Preservation first:** recovery branch/checkpoint before modifying inherited work.
2. **Stabilization before features:** v0.21.7 should restore CI, security, environment, tests, and documentation truth.
3. **Nightly root cause:** workflow calls `scripts/check_links.py --fail-fast`, but the script has no such argument.
4. **Live import data is intact:** `/api/v1/import/sample` returns 153 beams; standalone scripts fail because they expect the old flat response instead of the response envelope.
5. **Environment drift repaired:** source, editable metadata, and module report v0.21.6; Python 3.11 and Node 24 are recorded; the dependency locks come from clean installs.
6. **Security baseline:** the clean Python graph audits at zero known vulnerabilities. npm has one exact React Router RSC-only exception; the browser-only app does not use the affected mode, and CI rejects any additional advisory.
7. **One source of truth restored:** `run.sh check` passes 28/28, audit passes 22/22, health is 100/100, and parity clearly separates informational Python-only exports from actionable test gaps.
8. **Documentation remains evidence:** completed plans were removed from `_active`, counts and commands were reconciled, and future maintenance must keep these records synchronized.
9. **Utilization contract:** UI/API beam utilization must use `ComplianceCaseResult.governing_utilization`; `Mu_lim` is the singly reinforced limit and is not the final capacity of a valid doubly reinforced design.
10. **Mac port safety:** local cleanup may target only `LISTEN` processes. Plain `lsof -ti :PORT` also returns connected clients and is forbidden in the launcher.
11. **Live design contract:** WebSocket results must preserve the full REST `BeamDesignResponse`; frontend compatibility normalization may fill legacy shapes but must never overwrite live capacity or utilization data.
12. **Release runtime truth:** macOS preflight uses reclaimable memory and the Node major in `.nvmrc`; isolated wheel verification installs the package `[dev]` extra before running the source test suite.

### Recovery Progress (2026-08-07)

- `task/MAINT-001` and pushed checkpoint `b28ee4e3` preserve all inherited April work.
- Python editable metadata and module version now match v0.21.6.
- Node 24.19.0 LTS is installed keg-only; `.nvmrc`, React engines, lock metadata, CI, and setup docs target Node 24.
- React passes 146 tests, lint (one known hook warning), and production build on Node 24.
- Nightly no longer uses the unsupported link-checker flag; all 1,056 internal links pass.
- Maintained import E2E scripts understand the standard response envelope and pass 18/18 against a live API with all 153 sample beams.
- Import validation excludes archives, recognizes optional `xlwings`, and resolves all scanned imports; quick gate is 8/8.
- Colima's transferred VZ disk remains marked in use despite process cleanup. Preserve the disk; restart macOS before retrying, and require backup/approval before VM recreation.
- Root requirements now declare the previously implicit `pytest-asyncio` plugin and patched security floors. The final preflight passes 5,159 tests (3 skipped, 6 deselected) and all 336 FastAPI tests.
- The Python lock excludes editable/local Git references and retired `python-jose` residue; pip-audit reports zero known vulnerabilities across 147 installed dependencies.
- npm audit is reduced from 13 findings to one underlying React Router RSC-only advisory. Its exact scope, rationale, CI allowlist, and removal condition are recorded in `dependency-security-baseline.md`.
- MAINT-004 is complete: API manifest, schema snapshot, script indexes, bootstrap counts, hooks, import scanner, health scanner, audit scanner, and parity scanner now agree.
- Project health is 100/100 with 22 of 23 feedback records resolved. Only the tester-output watch at occurrence two of three remains pending.
- MAINT-005 checkpoint `6f119132` raises actionable parity to 96%: 15/17 curated clause areas, 60/60 direct route tests, and 13/13 connected hooks.
- The live 153-beam sample import, auto-design, R3F editor, dashboard, and export path passes. WebSocket designs preserve the full REST result; valid doubly reinforced beams report governing utilization and real capacities.
- BBS, DXF, single HTML/PDF report, building HTML/PDF/CSV summary, and BOQ CSV actions reach the live API; byte-level artifact checks confirm valid CSV structure, DXF sections/EOF, and PDF signatures. Final quantities are 2,663.4 kg steel and 114.8 m³ concrete.
- MAINT-005 is complete. `./run.sh release preflight 0.21.7` is green with zero warnings; v0.21.7 is ready but has not been released.
- MAINT-001 remains blocked only on GitHub CLI browser authorization and a macOS restart before non-destructive Colima recovery. SSH push works; do not delete the transferred VM disk.

### Canonical Maintenance Records

- `docs/TASKS.md` — active priorities and exit conditions.
- `docs/WORKLOG.md` — completed changes only, one line per meaningful change.
- `docs/SESSION_LOG.md` — decisions, evidence, and session outcomes.
- `docs/planning/next-session-brief.md` — exact restart point and blockers.
- This file — durable project state and architectural decisions, not command-by-command history.

---

## Historical State (2026-01-07)

### Recent Release
- **v0.15.0** released (2026-01-07)
- Focus: Code Quality Excellence
- Metrics: 2270 tests, 86% coverage, 0 ruff errors
- Status: Published on PyPI

### Active Development
- **Current:** v0.16.0 (Week 1) - Stabilize API refactoring (fix tests/benchmarks)
- **Next:** v0.17.0 (Weeks 2-4) - First professional requirements (Testing UI, Clause DB, Security, Liability)
- **Status:** Foundation complete, test fixes in progress, agent collaboration framework ready

---

## Active Goals

### Primary Objective: v1.0 Professional-Grade API
**Target Date:** Q1 2026 (8-10 weeks)

**Completed (Phase 1-3):**
- ✅ 10,547 lines of API design guidelines
- ✅ 7,772 lines of professional requirements research
- ✅ Exception hierarchy (errors.py)
- ✅ Error message templates (error_messages.py)
- ✅ Result object base classes (result_base.py)
- ✅ API refactoring (api.py, core modules)

**In Progress (Phase 4):**
- ⏳ Fix 8 test failures from API refactoring
- ⏳ Fix 13 benchmark errors from API changes
- ⏳ Implement research findings (clause DB, reports, UI)

**Remaining (Phase 4):**
- Code clause database architecture
- Calculation report generation (LaTeX/PDF)
- Verification & audit trail
- Interactive testing UI (Jupyter/Streamlit)
- Security hardening
- Professional liability framework

---

## Architecture Decisions

### API Design Philosophy
**Decision:** Follow NumPy/SciPy patterns with engineering domain adaptations
**Rationale:** Professional libraries use consistent patterns; engineers familiar with NumPy
**Impact:** All APIs use keyword-only params (>3 args), dataclass results, structured errors
**Date:** 2026-01-07 (TASK-200-209 research)

### Error Handling Strategy
**Decision:** 3-level exception hierarchy + structured error dataclasses
**Rationale:** Dual approach: exceptions for raising, dataclasses for collecting
**Impact:** All modules raise StructuralLibError subclasses; results have .errors field
**Date:** 2026-01-07 (TASK-212, 213)

### Type Modernization
**Decision:** PEP 585/604 modern syntax (`list[X]`, `X | None`)
**Rationale:** Python 3.9+ supports modern syntax; better readability
**Impact:** 398 type hints updated across 25 files
**Date:** 2026-01-06 (TASK-193)

### Test Organization
**Decision:** Category-based structure (unit, integration, regression, property, performance)
**Rationale:** Clear separation of test types; pytest markers for selective running
**Impact:** 59 test files reorganized into 5 categories
**Date:** 2026-01-06 (TASK-191)

---

## Technology Stack

### Core (Stable)
- **Python:** 3.9+ (f-strings, type hints, dataclasses)
- **Testing:** pytest + pytest-cov + pytest-benchmark
- **Linting:** ruff (9 rule categories, 0 errors)
- **Formatting:** black (88 char line length)
- **Type Checking:** mypy (strict mode enabled)
- **DXF Export:** ezdxf 1.0+

### CI/CD
- **Platform:** GitHub Actions
- **Checks:** black, ruff, mypy, pytest (2270 tests)
- **Pre-commit:** 11 hooks (formatting, type checking, linting)
- **Release:** PyPI automation via tags

### Documentation
- **Format:** Markdown (GitHub-flavored)
- **API Docs:** Inline docstrings (Google style)
- **Research:** Standalone docs in `docs/research/`

---

## Current Challenges

### 1. Test Failures from API Refactoring
**Issue:** 8 tests failing due to exception type changes
**Impact:** Low - Expected during refactoring
**Solution:** Update tests to use new exception hierarchy
**Owner:** TESTER agent
**ETA:** 1-2 hours

### 2. Benchmark Errors from API Changes
**Issue:** 13 benchmarks fail due to signature changes
**Impact:** Medium - Can't track performance regression
**Solution:** Update benchmark signatures for new API
**Owner:** TESTER agent
**ETA:** 2-3 hours

### 3. Research Implementation Gap
**Issue:** 7,772 lines of research not yet implemented
**Impact:** High - Professional features not available
**Solution:** Create implementation tasks for v0.16
**Owner:** PM agent (roadmap) → DEV agents (implementation)
**ETA:** 2-3 weeks

---

## Dependencies & Constraints

### Critical Dependencies
- **Python 3.9+:** Required for type hints syntax
- **ezdxf:** DXF export (optional dependency)
- **GitHub Actions:** Free tier sufficient for CI

### Known Constraints
- **Scope:** Beam design only (columns/slabs out of scope)
- **Code:** IS 456:2000 (ACI/Eurocode deferred to v2.0)
- **Platform:** Cross-platform (Win/Mac/Linux)

---

## Recent Lessons Learned

### Background Agents Work Well
**Observation:** Agents completed 13 critical tasks in parallel (TASK-210-214, 230, 238, 240, 242, 245, 252, 260, 261)
**Quality:** A+ grade (7,772 lines research + 74 new tests)
**Success Factors:**
- Clear task boundaries
- Isolated file ownership
- Automated workflows (scripts/ai_commit.sh)
- Handoff protocol

**Application:** Formalize agent collaboration framework for v0.16+

### Research-First Approach Pays Off
**Observation:** 10,547 lines of guidelines prevented API mistakes
**Impact:** Jumped from B+ to A- grade API in one session
**Application:** Continue research-first for major features

### Test Failures Expected During Refactoring
**Observation:** 8 test failures normal when changing exception types
**Learning:** Don't panic - update tests systematically
**Application:** Plan test updates as part of refactoring tasks

---

## Roadmap Snapshot

### v0.16.0 (Week 1 - Q1 2026)
**Focus:** Stabilize API refactoring foundation
**Timeline:** 3-5 hours
**Key Deliverables:**
- Fix 8 test failures from API changes
- Fix 13 benchmark errors from signature changes

### v0.17.0 (Weeks 2-4 - Q1 2026)
**Focus:** First professional engineering requirements
**Timeline:** 2-3 weeks
**Key Deliverables:**
- Interactive testing UI (Streamlit/Gradio)
- Code clause database
- Security hardening baseline
- Professional liability framework

### v1.0.0 (Q1 2026)
**Focus:** Complete professional requirements
**Timeline:** 6-8 weeks from now
**Key Deliverables:**
- Calculation report generation
- Verification & audit trail
- Professional liability framework
- A+ grade API (95/100)

### v1.1+ (Q2 2026)
**Focus:** Post-v1.0 enhancements based on user feedback
**Candidates:**
- Load combination generation
- Material database management
- Configuration management
- Multi-platform distribution (Conda)

---

## Contact & Escalation

### Project Owner
- **Name:** Pravin Surawase
- **GitHub:** https://github.com/Pravin-surawase

### Agent Coordination
- **MAIN Agent:** Handles user communication, task assignment, PR merges
- **Framework:** docs/contributing/agent-collaboration-framework.md
- **Workflow:** docs/contributing/background-agent-guide.md

---

## Quick Reference

### Key Files
- **Tasks:** `docs/TASKS.md`
- **Guidelines:** `docs/guidelines/api-design-guidelines.md` (2609 lines)
- **Research Index:** `docs/research/README.md`
- **Agent Framework:** `docs/contributing/agent-collaboration-framework.md`

### Key Commands
```bash
# Run all tests
cd Python && python -m pytest

# Check code quality
python -m black --check .
python -m ruff check .
python -m mypy

# Create task PR
./scripts/create_task_pr.sh TASK-XXX "description"

# Commit with hooks
./scripts/ai_commit.sh "type: message"
```

### Success Metrics
- Tests: 2270+ passing
- Coverage: 86%+ overall
- Ruff errors: 0
- API Grade: A- (92/100), targeting A+ (95/100)

---

## Notes for Next Session

1. **Immediate:** Assign TASK-270 & TASK-271 to TESTER agent (fix tests/benchmarks - 3-5 hours)
2. **v0.17 Prep:** Create detailed task specs for TASK-272-275 (Testing UI, Clause DB, Security, Liability)
3. **Agent Ready:** Full collaboration framework in place, can now run multiple agents in parallel
4. **Workflow:** Use background-agent-guide.md v2.0 for all agent assignments
5. **Context:** All agents should read memory.md before starting work

**Agent Collaboration Framework Status:**
- ✅ 5-role system defined (RESEARCHER, DEV, TESTER, DEVOPS, PM)
- ✅ Detailed workflows documented (6,147 lines)
- ✅ Background agent guide updated (v2.0)
- ✅ Memory persistence system in place
- ✅ Ready for parallel agent deployment

---

**Last Major Update:** 2026-01-07 (Agent collaboration framework v2.0, v0.16-v0.17 roadmap)

---

## 2026-08-07 — Maintenance and Agent Operations Update

- The active stack is React 19 → FastAPI → `Python/structural_lib`; Streamlit is
  legacy only. PR #676 is merged; current work is the isolated MAINT-008 skills
  lane on `task/MAINT-008-SKILLS` / draft PR #689.
- Mac Mini recovery is complete: GitHub CLI plus SSH pass, and Colima/Docker are
  healthy on the preserved transferred disk.
- Preserve the user's active parent model and reasoning selection. The advisory
  picker recommends Luna for clear repeatable work, Terra for normal
  implementation, and Sol only after explicit approval. Keep zero subagents by
  default and never exceed two.
- Use `./run.sh model` for task-aware recommendations and
  `./run.sh session usage` at start, 2–3 hour milestones, and closeout. The
  usage ledger records observable model/agent/time/check data but does not
  estimate billing tokens or cost.
- `./run.sh pr status` is terminal-only. Browser opening requires
  `./run.sh pr status --web`; GitHub device login may still open a browser as
  part of explicit authentication.
- Current automation inventory: 16 Copilot roles, 14 Copilot skills, 113 mapped
  scripts, 29 full validation checks, and 9 quick checks. Copilot's Claude
  model fields are separate from Codex Luna/Terra/Sol routing.
- On 2026-08-09 the owner authorized maintenance closeout. Commit `242ba8ce`
  removed three empty evidence-template links, replaced one crawler-blocked
  OpenAI URL, and pinned Ruff 0.15.8 across active install surfaces. PR #676
  passed every required check and was safely squash-merged as `755ac9fb`.
- MAINT-008 skills commits `5ac70ac1` and `fc4d0249` repair all 14 entrypoints,
  make `skill_tiers.json` the canonical catalog, validate registry routing, and
  make API/architecture/release/evolution evidence fail closed. Session
  summary, sync, and end are read-only unless an explicit mutation flag is
  supplied. Draft PR #689 is clean and green, but its merge remains an explicit
  owner decision; packet A, the required-check change, later MAINT-008 merge,
  and v0.21.7 release remain separate operations.
- Repeat-prevention rule: shared control-plane facts need one catalog plus
  validation, observational commands must not hide writes, and evidence tools
  must reject missing or ambiguous proof. Locate current documentation through
  folder indexes or `rg --files`; the canonical compact log is
  `docs/WORKLOG.md`.

## 2026-08-09 — Professional Library Audit and Release Hold

- v0.23.0 is a prepared source candidate, not a published release. No
  v0.23.0 tag, GitHub Release, or branch PR was found. Keep publication and
  released wording on hold until LIB-PRO-001 and exact-wheel review complete.
- Confirmed outcome defects include non-finite beam/footing inputs, unsafe
  shear reported/applied as batch PASS, report sections defaulting missing
  status to PASS, footing minimum-steel area/count contracts, and ambiguous
  bounded two-way slab review semantics.
- Do not repeat TASK-660 naming migration, TASK-670 calculation-report field
  repair, TASK-729/730 web validation, MAINT-004 manifest work, or MAINT-005's
  positive browser sweep. The active plan maps each remaining gap to that
  history in `professional-library-remediation-plan.md`.
- The terminal root fix makes `./run.sh test` explicitly Python-only and adds
  `--fastapi`, `--react`, `--all`, plus `./run.sh frontend ...` on the shared
  `.nvmrc` runtime selector. Missing executable script targets now fail the
  control-path validator; dead VBA/Streamlit commands are removed.
- Next implementation is LIB-PRO-R1 only: a shared finite numeric boundary for
  supported public beam and footing entry points. Preserve the separate model
  policy, terminal control, audit/governance, and structural remediation lanes.

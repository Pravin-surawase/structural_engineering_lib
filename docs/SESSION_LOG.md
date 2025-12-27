# Session Log

Append-only record of decisions, PRs, and next actions. For detailed task tracking, see [TASKS.md](TASKS.md).

---

## 2025-12-27 — v0.9.5 Release + Docs Restructure

### Decisions

1. **PyPI Publishing:** Implemented Trusted Publishing (OIDC) workflow. No API tokens needed.
2. **Docs restructure:** Approved 7-folder structure with redirect stubs. Files staying at root: `README.md`, `TASKS.md`, `AI_CONTEXT_PACK.md`, `RELEASES.md`, `v0.7_REQUIREMENTS.md`, `v0.8_EXECUTION_CHECKLIST.md`.
3. **VBA parity scope:** Limited to critical workflows (design, compliance, detailing), not every function.

### PRs Merged

| PR | Title | Summary |
|----|-------|---------|
| #36 | feat: add PyPI publish workflow | Trusted Publishing + GitHub Release automation |
| #37 | chore: bump version to 0.9.5 | Version bump for first PyPI release |
| #38 | docs: update README and CHANGELOG for v0.9.5 | PyPI badge, simplified install |
| #39 | fix: README accuracy corrections | VBA parity wording, optimizer import, test command |
| #40 | docs: add migration scaffold folders (Phase 1) | 7 new folders with README indexes |
| #41 | docs: migrate verification docs (Phase 2) | Moved VERIFICATION_*.md with redirect stubs |
| #42 | docs: migrate reference docs (Phase 3) | Moved API_REFERENCE, KNOWN_PITFALLS, IS456_QUICK_REFERENCE, TROUBLESHOOTING |
| #43 | docs: migrate getting-started docs (Phase 4) | Moved BEGINNERS_GUIDE, GETTING_STARTED_PYTHON, EXCEL_QUICKSTART, EXCEL_TUTORIAL |
| #44 | docs: migrate contributing docs (Phase 5) | Moved DEVELOPMENT_GUIDE, TESTING_STRATEGY, VBA_GUIDE, VBA_TESTING_GUIDE, EXCEL_ADDIN_GUIDE |
| #45 | docs: migrate architecture + planning docs (Phase 6) | Moved PROJECT_OVERVIEW, DEEP_PROJECT_MAP, MISSION_AND_PRINCIPLES, CURRENT_STATE_AND_GOALS, NEXT_SESSION_BRIEF, PRODUCTION_ROADMAP, RESEARCH_AI_ENHANCEMENTS, RESEARCH_DETAILING |
| #46 | docs: update SESSION_LOG with completed migration phases | Session log bookkeeping |
| #47 | docs: fix broken links after migration | Fixed planning/README.md, architecture/README.md, and others |
| #48 | docs: fix remaining broken links to old root paths | Fixed TASKS.md, v0.8_EXECUTION_CHECKLIST.md, deep-project-map.md, etc. |
| #49 | docs: update version marker to v0.9.5 | Fixed docs/README.md version display |
| #50 | docs: update SESSION_LOG and CHANGELOG | Added docs restructure to CHANGELOG (permanent record) |
| #51 | docs: update remaining old path references + CLI reference | Fixed agents/*.md paths, added cookbook/cli-reference.md |

### Releases

- **v0.9.5** published to PyPI: `pip install structural-lib-is456`
- **v0.9.4** tag created (was missing)

### Docs Migration Progress

| Phase | Folder | Status |
|-------|--------|--------|
| 1 | Scaffold folders | ✅ PR #40 |
| 2 | verification/ | ✅ PR #41 |
| 3 | reference/ | ✅ PR #42 |
| 4 | getting-started/ | ✅ PR #43 |
| 5 | contributing/ | ✅ PR #44 |
| 6 | architecture/ + planning/ | ✅ PR #45 |

### Next Actions

- [x] Phase 3: Migrate reference docs
- [x] Phase 4: Migrate getting-started docs
- [x] Phase 5: Migrate contributing docs
- [x] Phase 6: Migrate architecture + planning docs
- [x] Fix broken links (PRs #47-51)
- [x] Create `cookbook/cli-reference.md` (PR #51)
- [ ] Add SP:16 table references to existing verification examples (optional enhancement)
- [ ] Remove redirect stubs (scheduled for v1.0)

---

## 2025-12-27 — API/CLI Docs UX Pass (Phases 0–4)

### Decisions

1. **CLI is canonical:** Unified CLI (`python -m structural_lib design|bbs|dxf|job`) is the default reference; legacy CLI entrypoints are treated as legacy.
2. **Docs must match code:** Examples are kept copy-paste runnable with real signatures and outputs.
3. **No breaking API changes:** This pass updates docs and docstrings only.

### Changes

- Updated public API docstrings with args/returns/examples (`Python/structural_lib/api.py`).
- Aligned CLI reference to actual CLI behavior (`docs/cookbook/cli-reference.md`).
- Fixed Python recipes to use real function signatures (`docs/cookbook/python-recipes.md`).
- Corrected DXF and spacing examples in beginners guide (`docs/getting-started/beginners-guide.md`).
- Updated legacy CLI reference in v0.7 mapping spec (`docs/specs/v0.7_DATA_MAPPING.md`).

### Status

- Phase 0–5 complete.

---

## 2025-12-27 — v0.9.6 Release (Validation + Examples)

### PRs Merged

| PR | Title | Summary |
|----|-------|---------|
| #53 | Release v0.9.6: API docs UX pass + validation examples | All validation work + docs improvements |

### Key Deliverables

1. **Verification Examples Pack:**
   - Appendix A: Detailed IS 456 derivations (singly/doubly reinforced)
   - Appendix B: Runnable manual vs library comparison commands
   - Appendix C: Textbook examples (Pillai & Menon, Krishna Raju, Varghese, SP:16)

2. **Validations Completed:**
   - Singly reinforced beam: 0.14% Ast difference ✅
   - Doubly reinforced beam: 0.06% Asc difference ✅
   - Flanged beam (T-beam): exact match ✅
   - High shear design: exact match ✅
   - 5 textbook examples: all within 0.5% tolerance ✅

3. **Documentation:**
   - Pre-release checklist (`docs/planning/pre-release-checklist.md`)
   - API docs UX plan (`docs/planning/api-docs-ux-plan.md`)
   - Git governance updated with current protection rules

### Release

- **v0.9.6** published to PyPI
- Tag: `v0.9.6`
- Tests: 1686 passed, 91 skipped

---

### Status

- Phase 0–4 complete.
- Phase 5 pending (final summary check).

---

## 2025-12-28 — Architecture Review: beam_pipeline Implementation

### Background

Implemented recommendations from `docs/architecture/architecture-review-2025-12-27.md`:
- TASK-059: Canonical beam design pipeline
- TASK-060: Schema v1 with explicit version field
- TASK-061: Units validation at application layer

### PR

| PR | Title | Branch | Status |
|----|-------|--------|--------|
| #55 | feat: implement architecture recommendations - beam_pipeline | `feat/architecture-beam-pipeline` | Open (CI pending) |

### Files Changed

| File | Change |
|------|--------|
| `Python/structural_lib/beam_pipeline.py` | **NEW** - 528 lines, canonical pipeline |
| `Python/structural_lib/__main__.py` | Refactored to use `beam_pipeline.design_single_beam()` |
| `Python/structural_lib/job_runner.py` | Added units validation via `beam_pipeline.validate_units()` |
| `Python/tests/test_beam_pipeline.py` | **NEW** - 28 tests for pipeline |
| `Python/tests/test_cli.py` | Updated for new schema keys |
| `docs/TASKS.md` | Added TASK-059/060/061 |
| `docs/planning/next-session-brief.md` | Updated with architecture work |

### Architect Agent Review

**Reviewer:** Architect Agent (subagent invocation)  
**Verdict:** ✅ **APPROVED**  
**Score:** 4.5 / 5

#### Strengths Identified

1. **Layer boundaries respected** — `beam_pipeline.py` correctly lives in application layer, imports only from core layer, no I/O code
2. **Single source of truth achieved** — All beam design flows through `design_single_beam()` and `design_multiple_beams()`
3. **Canonical schema well-designed** — `SCHEMA_VERSION = 1`, structured dataclasses (`BeamDesignOutput`, `MultiBeamOutput`), explicit units dict
4. **Units validation robust** — `validate_units()` validates at application boundary before core calculations, raises `UnitsValidationError` with clear messages
5. **Comprehensive test coverage** — 28 tests covering units validation, schema structure, single/multi-beam design, edge cases

#### Minor Concerns (Non-blocking)

1. **Duplicate units constants** — `VALID_UNITS` dict appears in both `beam_pipeline.py` and `api.py` (DRY violation)
2. **Partial migration** — `job_runner.py` still uses `api.check_beam_is456()` directly for case design instead of `beam_pipeline`
3. **Silent error swallowing** — Detailing exceptions are caught and logged but not surfaced in output

#### Recommendations for Follow-up

| Priority | Recommendation |
|----------|----------------|
| P1 | Migrate `job_runner.py` to use `beam_pipeline.design_single_beam()` for case design |
| P2 | Extract `VALID_UNITS` to `constants.py` as shared source |
| P2 | Add `warnings` field to `BeamDesignOutput` for surfacing non-fatal issues |

#### VBA Parity Assessment

No immediate VBA changes required. `beam_pipeline.py` is Python-only orchestration layer. VBA equivalent (`M08_API.CheckBeam`) maintains its own flow.

### CI Fixes Applied

1. **Black formatting** — Auto-fixed by `.github/workflows/auto-format.yml` (4 files reformatted)
2. **Ruff lint** — Fixed unused variable `validated_units` in `job_runner.py` (commit `7874ae2`)

### Decision

Architect agent approved the implementation. PR is ready for merge once CI passes. Minor concerns documented as future tasks.

### Next Actions

- [x] Wait for CI to pass on PR #55
- [x] Merge PR #55 (squashed to main, commit `c77c6c7`)
- [x] Create follow-up task: Migrate job_runner to use beam_pipeline for case design
- [x] Create follow-up task: Extract shared units constants

---

## 2025-12-27 — Architecture Bugfixes (Post-Review)

### Background

After merging PR #55, additional review identified three bugs in the beam_pipeline implementation:

| Severity | Issue | Impact |
|----------|-------|--------|
| HIGH | `detailing: null` in JSON crashes BBS/DXF | `AttributeError` on valid outputs |
| MEDIUM | `validated_units` return value unused | Non-canonical units in output |
| LOW | Mixed-case units fail validation | Poor UX for case variations |

### Fixes Applied (TASK-062, 063, 064)

**TASK-062 (HIGH): Fix detailing `null` crash**
- File: `__main__.py`
- Change: `beam.get("detailing", {})` → `beam.get("detailing") or {}`
- Reason: `dict.get(key, default)` returns `None` if value is explicitly `null`, not the default

**TASK-063 (MEDIUM): Use canonical units in output**
- File: `job_runner.py`
- Change: Store `validate_units()` return value, use throughout downstream code
- Before: `units = job.get("units")` → `validate_units(units)` (discarded return)
- After: `units_input = job.get("units")` → `units = validate_units(units_input)` (canonical form used)

**TASK-064 (LOW): Case-insensitive units validation**
- File: `beam_pipeline.py`
- Change: Normalize to uppercase, remove spaces before comparison
- Now accepts: `"Is456"`, `"IS 456"`, `"is 456"`, `"IS456"`, etc.

### Tests Added

| File | Tests Added | Purpose |
|------|-------------|---------|
| `test_beam_pipeline.py` | `test_validate_units_mixed_case` | Verify mixed-case variants work |
| `test_cli.py` | `TestExtractBeamParamsFromSchema` (3 tests) | Verify null/missing handling |

### Test Results

```
1714 passed, 95 skipped in 1.02s
```

### Files Changed

- `Python/structural_lib/__main__.py`
- `Python/structural_lib/job_runner.py`
- `Python/structural_lib/beam_pipeline.py`
- `Python/tests/test_beam_pipeline.py`
- `Python/tests/test_cli.py`
- `docs/TASKS.md`
- `docs/SESSION_LOG.md`


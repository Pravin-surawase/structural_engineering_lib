# Next Session Brief

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-04-07
<!-- HANDOFF:END -->

**Last Updated:** 2026-04-07
**Last Session:** Batch 3 API naming convention — complete

## What Was Completed
- **Type-Safety Audit — COMPLETE**
  - Fixed 28+ Pylance type errors in `column_api.py` — changed `_resolve_deprecated_param` return from `Any` to `TypeVar[_T]`
  - Applied same TypeVar fix in `beam_api.py`
  - Created `pyrightconfig.json` at workspace root — resolves Pylance import errors for `structural_lib`
  - Added `# type: ignore` comments to 12 deliberate wrong-type tests in `test_coverage_boost_is456.py`
  - Deprecation audit: confirmed no items overdue (current v0.21.6, removals at v0.24 and v1.0.0)
  - Inventory: 23 field deprecations (v1.0.0), 29 param deprecations (v0.24), 9 stubs
- **Previous: Batch 3 Phase 1+2: API Naming Convention — COMPLETE**
  - TASK-740 through TASK-744 all marked ✅ Done

## Current Version State
- **v0.21.5** = last PyPI release (tag: v0.21.5)
- **v0.21.6** = feature-complete, unreleased

## Priorities (Updated)

### Immediate — Batch 3: API Naming Convention (v0.22.0)

**Issue 15 fix — 12 functions need parameter rename:**

Phase 1 (P0+P1 — column_api.py, single PR):
- `design_column_axial_is456`: `fck`→`fck_nmm2`, `fy`→`fy_nmm2`
- `design_short_column_uniaxial_is456`: same
- `pm_interaction_curve_is456`: same
- `biaxial_bending_check_is456`: same
- `calculate_additional_moment_is456`: same
- `design_long_column_is456`: same
- `check_helical_reinforcement_is456`: same
- `design_column_is456`: same
- `detail_column_is456`: same
- `check_column_ductility_is13920`: same

Phase 2 (P2 — beam_api.py, separate PR):
- `check_beam_ductility`: `b`→`b_mm`, `D`→`D_mm`, `d`→`d_mm`, `fck`→`fck_nmm2`, `fy`→`fy_nmm2`
- `check_anchorage_at_simple_support`: `fck`→`fck_nmm2`, `fy`→`fy_nmm2`

Migration strategy: Add new param names, keep old as deprecated aliases with warnings, update all callers.

**Issue 16 — Public surface audit (defer to v0.23+):**
- 107 exports is reasonable for the library's scope
- No action needed now — just document stable vs experimental tiers

### Immediate — Next Priorities
- [ ] Consolidate `_resolve_deprecated_param` from `beam_api.py` + `column_api.py` into `common_api.py` (reduces duplication)
- [ ] Add direct unit tests for `_resolve_deprecated_param` TypeVar helper
- TASK-745: Decide stable vs experimental API tiers (Issue 16 — defer to v0.23+)
- v0.21.7 Security Hardening:
  - JSON body size limit middleware (TASK-728)
  - Cross-field plausibility guards (TASK-729)
  - Input validation audit (TASK-730)
  - WebSocket message rate limit (TASK-731)

### Later (v0.21.8 — Performance & Property Testing)
- pytest-benchmark integration (TASK-732)
- Hypothesis test expansion (TASK-733)
- Performance regression baselines (TASK-734)

## Batch 3 Summary (COMPLETED)

All 5 tasks (TASK-740 through TASK-744) done. Files changed:
- `Python/structural_lib/services/column_api.py` — 10 functions renamed
- `Python/structural_lib/services/beam_api.py` — 2 functions renamed
- `fastapi_app/routers/column.py` + `fastapi_app/models/` — Pydantic alias backward compat
- `Python/tests/test_param_deprecation.py` — 40 new deprecation tests
- `docs/architecture/unified-architecture-v1.md` — §10.5 updated with two-tier convention

### Key decisions made:
- Two-tier convention: full suffixes at L3, IS 456 shorthand at L2
- `fck_nmm2` (not `fck_MPa`) — matches IS 456 notation (N/mm²)
- `Mu_kNm` (not `mu_knm`) — matches IS 456 uppercase notation
- Backward compat via deprecated aliases + DeprecationWarning (removal in v0.24)
- Layer 2 functions (codes/) keep bare `fck`, `fy` — no change needed

## Blockers
- None

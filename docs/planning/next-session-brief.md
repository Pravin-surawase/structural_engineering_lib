# Next Session Brief

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-04-07
<!-- HANDOFF:END -->

**Last Updated:** 2026-04-07
**Last Session:** Audit remediation review + Batch 3 planning

## What Was Completed
- **Post-commit review:** All 15 files from Batch 1+2 verified by @reviewer — APPROVED
- **2 minor fixes:** Stale deprecated import paths in geometry_3d.py docstring + test_visualization_integration.py
- **Security review:** PASS — fallback HTML uses html.escape(), no XSS
- **Batch 3 planning complete:** Full analysis by @library-expert, @structural-engineer, @security
  - API naming: 12 functions, ~26 params to rename (all in column_api.py + 2 beam outliers)
  - Public surface: 107 exports mapped and categorized (56 functions, 29 classes, 21 submodules)
  - Two-tier naming convention approved by @structural-engineer

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

### Next (v0.21.7 — Security Hardening)
- JSON body size limit middleware (TASK-728)
- Cross-field plausibility guards (TASK-729)
- Input validation audit (TASK-730)
- WebSocket message rate limit (TASK-731)

### Later (v0.21.8 — Performance & Property Testing)
- pytest-benchmark integration (TASK-732)
- Hypothesis test expansion (TASK-733)
- Performance regression baselines (TASK-734)

## Batch 3 Implementation Plan (for next session)

### Agent Pipeline:
1. @backend — Add deprecated param aliases to column_api.py (Phase 1)
2. @backend — Add deprecated param aliases to beam_api.py (Phase 2)
3. @api-developer — Update FastAPI column router to use new param names
4. @tester — Update column tests + add deprecation warning tests
5. @reviewer — Review all changes
6. @doc-master — Update API docs, architecture doc §10.5
7. @ops — Commit as `refactor(api): standardize parameter naming convention`

### Files to modify:
- `Python/structural_lib/services/column_api.py` — 10 functions
- `Python/structural_lib/services/beam_api.py` — 2 functions
- `fastapi_app/routers/column.py` — update request model field names
- `fastapi_app/models/` — update Pydantic models
- `Python/tests/` — update test call sites
- `docs/architecture/unified-architecture-v1.md` — document convention

### Key decisions made:
- Two-tier convention: full suffixes at L3, IS 456 shorthand at L2
- `fck_nmm2` (not `fck_MPa`) — matches IS 456 notation (N/mm²)
- `Mu_kNm` (not `mu_knm`) — matches IS 456 uppercase notation
- Backward compat via deprecated aliases + DeprecationWarning
- Layer 2 functions (codes/) keep bare `fck`, `fy` — no change needed

## Blockers
- None

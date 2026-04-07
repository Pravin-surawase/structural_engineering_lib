# Next Session Briefing

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-04-07
<!-- HANDOFF:END -->

**Last Updated:** 2026-04-07
**Last Session:** v0.21.7 Session 1 — Security Hardening (P1–P3 complete)

## What Was Completed (v0.21.7 Session 1)
- **v0.21.6 version refs fixed** — CHANGELOG.md, Python/README.md, docs/git-automation/README.md
- **TASK-729: Cross-field plausibility guards** ✅ — 14 @model_validator checks across beam, column, geometry, analysis models
- **TASK-730: Input validation audit** ✅ — Security audit found 16 gaps, all fixed, 49 tests written
- **TASK-802: Column API export** ✅ — Column functions already exported; fixed 6 missing contract test assertions
- **TASK-796: ImportError path leak fix** ✅ — Added sanitize_error_string(), sanitized 4 router response patterns, 15 tests
- **TASK-CI-FIX: 5 daily CI failures fixed** ✅ (PR #550):
  - `time.time()` → `time.perf_counter()` in 6 library files (Windows CI timing)
  - CycloneDX SBOM CLI syntax fixed + version pinned (cyclonedx-bom v7+)
  - OpenSSF Scorecard permissions narrowed to job-level (least-privilege)
  - OpenAPI baseline updated for BiaxialCheckRequest description drift
  - Nightly QA smoke test failure guard added

## Current Version State
- **v0.21.5** = last PyPI release (tag: v0.21.5)
- **v0.21.6** = Released to PyPI
- v0.21.6 released on 2026-04-07 with all preflight checks passed (5143 tests, 69 golden vectors, 18 contracts)
- **v0.21.7** = in progress — 4/14 tasks done (P1–P3)

## Priorities — v0.21.7 Remaining

### P4 — Packaging Gates (next)
- TASK-790: `check-wheel-contents` + `twine check` in CI
- TASK-791: TestPyPI dry-run before prod
- TASK-793: Optional dependency group tests (`.[dxf]`, `.[report]`)

### P5 — CI Hardening
- TASK-795: OpenAPI drift check in publish workflow
- TASK-794: Docker base image digest pin
- TASK-792: Pin Trivy action to SHA

### P6 — API Security
- TASK-728: JSON body size limit middleware (1MB)
- TASK-804: Auth auto-enable when JWT secret set

### P7 — Docs & CVE
- TASK-803: Document negative Mu behavior
- TASK-731: Dependency CVE scanning (pip-audit)
### Later — v0.21.8 Performance & Property Testing
- TASK-732: pytest-benchmark for hot paths
- TASK-733: Hypothesis test expansion
- TASK-734: Performance regression baselines

### v0.22.0 — Stabilization
- ARCH-NEW-12: Split services/api.py god module
- FE-NEW-01: Three.js dispose() on unmount
- UX-02: Typed return consistency (column dict → dataclass)
- IS-NEW-01/02: @clause decorators for ~26 functions (detailing: 11, common: 8, footing: 4, slenderness: 3)
- T-NEW-01: Remove MagicMock from test files
- Beam rationalization (TASK-521)
- CalculationProvenance foundation (TASK-735, includes merged OL-15 audit trail)
- TASK-797: SLSA provenance + PEP 740 attestations
- TASK-798: Security event logging (OWASP A09)
- TASK-799: Multi-stage Dockerfile
- TASK-800: Verification methodology doc consolidation
- TASK-801: License compliance scan

## Infrastructure Notes
- `session_summary.py` doesn't exist — use `scripts/session.py summary`
- Registry metadata skill_count=10 should be 14 (cosmetic)
- 3 FastAPI import violations (non-blocking, planned for v0.22.0)

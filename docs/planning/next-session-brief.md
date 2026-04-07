# Next Session Brief

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-04-07
<!-- HANDOFF:END -->

**Last Updated:** 2026-04-07
**Last Session:** v0.21.6 Pre-Release Audit — COMPLETE

## What Was Completed
- **v0.21.6 Pre-Release Audit (14-agent deep audit)**
  - Score: A+ (9.0/10) — no release blockers found
  - Test suite: 5003/5003 passing, 99% branch coverage on IS 456 code
  - Security: 0 CVEs, Docker hardened, JWT safeguarded, rate limiting active
  - Agent infrastructure: 16 agents, 14 skills, 16 prompts — all verified
  - Architecture: 4-layer boundary intact, 108 API exports verified
  - IS 456: All formulas verified correct across 42 clauses + 8 IS 13920
  - Updated audit-readiness.md with full v0.21.6 status
  - Updated TASKS.md with pre-release audit section
  - 11 known findings documented as accepted deferrals with rationales

## Current Version State
- **v0.21.5** = last PyPI release (tag: v0.21.5)
- **v0.21.6** = feature-complete, audited, ready for PyPI release

## Online Research Findings (2026-04-07)

16 new issues discovered through online best practices research (OWASP 2025, PyPI publishing, IStructE guidance):

### Critical additions for v0.21.7:
- **OL-01/02:** `check-wheel-contents` + `twine check` missing in publish workflow — bad metadata can ship
- **OL-08:** OWASP 2025 A10 "Mishandling of Exceptional Conditions" — 2-4 HTTP-exposed ImportError leaks (38 total catch sites, all properly sanitized via sanitize_error())
- **OL-05:** Docker base image unpinned (reproducibility risk)
- **OL-07:** Container CVE scan exists (Trivy in docker-build.yml) but action unpinned @master — pin to SHA
- **OL-10:** TestPyPI dry-run exists but only on workflow_dispatch, not mandatory gate
- **OL-12:** Optional deps (`.[dxf]`, `.[report]`) never tested post-install
- **OL-16:** No OpenAPI drift check in publish workflow

### For v0.22.0:
- **OL-03/04:** OWASP 2025 A03 Supply Chain — need SLSA provenance + PEP 740 attestations
- **OL-09:** OWASP 2025 A09 — no security event logging
- **OL-14:** V&V infrastructure exists (42+ golden vectors, verification-checklist.md, validation-pack.md) but fragmented across 6+ files — needs consolidation
- **OL-15:** MERGED into TASK-735 — services/audit.py already provides basic audit trail; CalculationProvenance extends it

### 4-Agent Review Results (2026-04-07)

4-agent review (security, reviewer, structural-engineer, library-expert) completed 2026-04-07. Key corrections: OL-07 already exists (Trivy in docker-build.yml), OL-08 count corrected (2-4 not 22), UX-01 already fixed in code (_validate_plausibility), 8 TASK ID conflicts resolved (→ TASK-790+), 3 new root cause patterns identified (documentation drift, API stability, import performance), 9 new findings (AR-01 through AR-09).

### External Audit Root Cause Patterns (6 themes):
All 23 EA findings fixed, but prevention measures show gaps:
1. ❌ TestPyPI before prod (exists but not mandatory gate)
2. ✅ ImportError leaks mostly sanitized — 2-4 still HTTP-exposed
3. ✅ Container CVE scanning EXISTS (Trivy in docker-build.yml)
4. ✅ Cross-field validation done — _validate_plausibility raises ValueError; need input validation audit (TASK-730)
5. ❌ Security event logging
6. ❌ Column API not in __init__.py (NEW — AR-08)
7. ❌ Auth default-off with secret set (NEW — AR-02)

## Priorities (Updated)

### Immediate — Release v0.21.6
1. Fix version references (CHANGELOG [Unreleased]→[0.21.6], Python/README.md git pin, docs/git-automation version)
2. Run `./run.sh release preflight 0.21.6` to validate
3. Tag and publish to PyPI

### Next — v0.21.7 Security Hardening (4-agent consensus priority order)
1. TASK-729 + TASK-730: Cross-field plausibility guards + input validation audit
2. TASK-802: Export column API functions to structural_lib.__init__.py (HIGH user impact)
3. TASK-796: Fix 2-4 HTTP-exposed ImportError path leaks (OWASP A10)
4. TASK-790 + TASK-791 + TASK-793: Packaging gates (check-wheel-contents, TestPyPI, optional deps)
5. TASK-795: OpenAPI drift check in publish workflow
6. TASK-794: Docker base image digest pin
7. TASK-728: JSON body size limit middleware (1MB)
- TASK-731: Dependency CVE scanning in CI (pip-audit)
- TASK-804: Auto-enable auth or log CRITICAL when JWT_SECRET_KEY set but AUTH_ENABLED=false
- TASK-803: Document negative Mu abs-value behavior + hogging guidance
- WebSocket rate limiting
- Fix error message path leaks (S-NEW-01)
- Move create_dev_token() to test module (M-04)

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

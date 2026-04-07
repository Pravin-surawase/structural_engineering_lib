# Task Board

> **Single source of truth for active work.** Keep it short and current.

**Updated:** 2026-04-07 — v0.21.6 audit + online research root cause analysis; 16 new issues from OWASP 2025/PyPI best practices

---

## Rules (read first)
- **WIP = 2** (max 2 active tasks at once)
- **Done = tests pass + docs updated + scanner passes**
- **Archive rule:** Move completed items to [tasks-history.md](_archive/tasks-history.md) after 20+ items
- **No new Streamlit work** — all new features go to React. Bug fixes only for Streamlit-only features.

---

## Current Release

- **Version:** v0.21.6 ✅ COMPLETE → micro-releases v0.21.7–v0.21.8 → v0.22.0 Stabilization
- **Strategy:** Incremental micro-releases — each focuses on one quality dimension (tests, API, security, performance)
- **Focus:** API introspection → security hardening → performance baselines → stabilization
- **Target:** v0.21.7 next, then v0.21.8, then v0.22.0, then v0.23 (Slabs + Footing completion)
- **Vision:** [democratization-vision.md](planning/democratization-vision.md) — AI chat, automation, library evolution
- **Architecture:** [unified-architecture-v1.md](architecture/unified-architecture-v1.md) §20 — complete v0.21.5→v1.0 roadmap

### Release Roadmap

| Version | Focus | Status | Key Deliverables |
|---------|-------|--------|------------------|
| **v0.19.1** | AI Tools + UX | ✅ DONE | Dashboard insights, code checks, ExportPanel, rebar suggestions |
| **v0.20** | V3 Foundation | ✅ Released (v0.20.0) | Batch design React UI, compliance checker, cost optimizer, 86 API tests |
| **v0.21** | React UX + Library Expansion | ✅ Released (v0.21.0) | Editor-centric UX, BeamDetailPanel, FloatingDock, PDF export, load calc, BOQ, torsion |
| **v0.21.4** | Stabilization | ✅ Released (v0.21.4) | CostProfile fix, float sanitization, footing API, bearing check, torsion shim |
| **v0.21.5** | Test Coverage & Regression Prevention | ✅ DONE | Golden vectors (42+), contract tests (18), 99% branch coverage |
| **v0.21.6** | API Quality & Introspection | ✅ DONE | check_code(), show_versions(), OpenAPI freeze, limitation docs |
| **v0.21.7** | Security Hardening | � IN PROGRESS | Input validation, error sanitization, packaging gates, CI hardening |
| **v0.21.8** | Performance & Property Testing | 📋 PLANNED | Benchmarks, Hypothesis, performance baselines |
| **v0.22.0** | Stabilization Release | 📋 PLANNED | API naming convention (Batch 3), provenance, SP:16 verification |
| **v0.23** | IS 456 Slabs + Footing Completion | 📋 PLANNED | One-way slab, two-way slab, footing dowels + API, punching shear |
| **v0.24** | Multi-Code Infrastructure | 📋 PLANNED | CodeRegistry activation, DesignEnvelope, units.py, API v2 routes |
| **v0.25** | ACI 318-19 Beam | 📋 PLANNED | ACI beam flexure + shear, PCA Notes ±0.1% benchmarks |
| **v1.0** | Production Multi-Code | 📋 PLANNED | IS 456 complete, ACI 318 beam+column, EC2 beam, API stability guarantee |

### Migration Status (React vs Streamlit)

| Feature | Streamlit | React | API Ready | Priority |
|---------|-----------|-------|-----------|----------|
| Single beam design | ✅ | ✅ | ✅ | Done |
| CSV import (40+ cols) | ✅ | ✅ | ✅ | Done |
| 3D visualization | ✅ | ✅ R3F | ✅ | Done |
| Export (BBS/DXF/Report) | ✅ | ✅ | ✅ | Done |
| Dashboard insights | ✅ | ✅ | ✅ | Done |
| Rebar suggestions | ✅ | ✅ | ✅ | Done |
| **Batch design UI** | ✅ | ✅ | ✅ streaming.py | Done |
| **Compliance checker** | ✅ | ✅ DesignView panel | ✅ insights.py | Done |
| **Cost optimizer** | ✅ | ✅ DesignView rebar | ✅ optimization.py | Done |
| **AI Assistant** | ✅ | -- | Partial | ⏸ Deferred |
| Learning center | ✅ | -- | -- | 🟢 Low |

### v0.21 Remaining Items (Library Expansion)

| # | Task ID | Feature | Status |
|---|---------|---------|--------|
| 7 | TASK-520 | Report/3D Test Coverage | ✅ DONE (71 new tests) |
| 8 | TASK-521 | Beam Rationalization | 📋 [→ v0.22.0] |

> v0.21 React UX Overhaul (TASK-522–528, all ✅) and Library Expansion items 1–6 (TASK-514–519, all ✅) archived to [tasks-history.md](_archive/tasks-history.md).
> Detailed specs: [next-phase-improvements-plan.md](planning/next-phase-improvements-plan.md) Part 2.

---

## Completed (Archived)

> All completed items below have been archived. See [tasks-history.md](_archive/tasks-history.md) for full details.

| Section | Items | Summary |
|---------|-------|---------|
| Architecture Doc Enhancement | 1 ✅ | unified-architecture-v1.md enhanced 413→1108 lines, 8 new sections, 9-agent review (library-expert, security, structural-engineer, reviewer, frontend, api-developer, innovator, tester, governance) |
| v0.21.2 Packaging Fixes | TASK-PKG-1–6 ✅ | Wheel content, package discovery, CI tests |
| v0.21.2 External Audit | EA-1–23 ✅ | 23 audit findings fixed (test infra, imports, API, security, frontend, docs) |
| v0.21.5 Stabilization | 8 items ✅ | CostProfile, sanitize_float, footing wiring, bearing pressure |
| Recent Fixes | 21 items ✅ | Response envelope, CI, audit P0–P2, column math, git hardening, variable naming |
| Audit P1 Batch 1 | 4 items ✅ | clause_cli, FlexureResult limits, streaming 404, Three.js cleanup |
| External Audit Remediation | 8 items ✅ | ETABS units/batch/geometry, SmartDesigner CLI, .j2 packaging, README fixes, bbs import path |

---

## External Audit Remediation — v0.21.6 ✅ DONE

**Theme:** Fix 8 external audit findings across ETABS import, SmartDesigner CLI, packaging, and documentation.
**Completed:** 2026-04-07

| ID | Finding | Priority | Status |
|----|---------|----------|--------|
| EXT-P1-1 | ETABS job generator uses `"SI-mm"` units → fixed to `"IS456"` | P1 | ✅ DONE |
| EXT-P1-2 | ETABS batch groups by `beam_id` only → fixed to `(story, beam_id)` to prevent cross-story collision | P1 | ✅ DONE |
| EXT-P1-3 | Geometry merge keys by `label` only → fixed to `(story, label)` with fallback to prevent overwrite | P1 | ✅ DONE |
| EXT-P1-4 | SmartDesigner CLI uses wrong function → fixed to `design_single_beam()` returning `BeamDesignOutput` | P1 | ✅ DONE |
| EXT-P1-5 | Report `.j2` templates missing from wheel → added to `pyproject.toml` package-data | P1 | ✅ DONE |
| EXT-P2-1 | README batch example uses non-existent `parse_file()` → fixed to `load_combined()` | P2 | ✅ DONE |
| EXT-P2-2 | `bbs.py` imports from deprecated shim → fixed to canonical `codes/is456/beam/detailing` | P2 | ✅ DONE |
| EXT-P3-1 | README version `0.21.3` → updated to `0.21.5` | P3 | ✅ DONE |
| EA-6 | Internal `ductile` import triggering deprecation warnings — fixed in `is456/__init__.py` | P2 | ✅ DONE |
| AUDIT-RPT | Wire reports `_generate_fallback_html` instead of raising `ImportError` | P2 | ✅ DONE |
| AUDIT-PIN | Update README git pin from `v0.21.3` to `v0.21.5` | P3 | ✅ DONE |
| AUDIT-SMOKE | Add 9 wheel smoke tests (`TestWheelSmokeTests`, `TestREADMESnippets`) | P2 | ✅ DONE |

---

## v0.21.5 — Test Coverage & Regression Prevention ✅ DONE

**Theme:** Golden vector baselines and contract tests. No future change can silently break existing calculations.
**Completed:** 2026-04-06
**Quality Gate:** `pytest -m golden` passes with 0 failures, branch coverage 99% on `codes/is456/` ✅

| ID | Task | Owner | Status |
|----|------|-------|--------|
| TASK-720 | Golden vector baselines for all IS 456 functions (`@pytest.mark.golden`) — 42+ tests (9 beam + 20 column + 13 footing) | @tester | ✅ DONE |
| TASK-721 | Contract tests for API surface stability (`@pytest.mark.contract`) — 18 contract tests | @tester | ✅ DONE |
| TASK-520 | Report & 3D visualization test coverage — 71 new tests | @tester | ✅ DONE |
| TASK-722 | conftest.py golden_vectors fixture with SP:16 values | @tester | ✅ DONE |
| TASK-723 | CI gate: `pytest -m golden` in GitHub Actions python-tests.yml | @ops | ✅ DONE |
| — | 90%+ branch coverage on `codes/is456/` — 99% achieved | @tester | ✅ DONE |
| — | Add `@clause("34.1")` to `size_footing()` | @structural-math | ✅ DONE |

## v0.21.6 — API Quality & Introspection ✅ DONE

**Theme:** Self-describing, self-validating library
**Completed:** 2026-04-06
**Quality Gate:** check_code("IS456") returns report, OpenAPI drift check in CI ✅

| ID | Task | Owner | Status |
|----|------|-------|--------|
| TASK-724 | Implement `check_code("IS456")` — validates code implementation contract | @backend | ✅ DONE |
| TASK-725 | Implement `show_versions()` — library + dependency info | @backend | ✅ DONE |
| TASK-726 | API surface freeze: OpenAPI baseline diff in CI | @ops | ✅ DONE |
| TASK-727 | Function limitation docs — what each function does NOT do | @doc-master | ✅ DONE |

## v0.21.6 Pre-Release Audit (2026-04-07)

**Theme:** Comprehensive 14-agent audit before PyPI release
**Overall Score:** A+ (9.0/10)
**Audit Report:** [comprehensive-library-audit-2026-04-04.md](audit/comprehensive-library-audit-2026-04-04.md)

### Release Blockers — NONE ✅

No critical or high-severity findings blocking this release.

### Version Fixes Required Before Tag

| Item | File | Fix | Status |
|------|------|-----|--------|
| CHANGELOG heading | CHANGELOG.md | `[Unreleased]` → `[0.21.6] — 2026-04-07` | 📋 |
| CHANGELOG link | CHANGELOG.md bottom | Add `[0.21.6]` compare link | 📋 |
| API docs version | docs/reference/api.md | `0.21.5` → `0.21.6` | 📋 |
| Python README git pin | Python/README.md | `@v0.21.5` → `@v0.21.6` | 📋 |
| Git-automation version | docs/git-automation/README.md | `0.21.5` → `0.21.6` | 📋 |

### Known Issues — Accepted Deferrals

These findings are documented in the comprehensive audit and planned for future releases. They are NOT release-blocking because they represent planned improvements, not regressions.

| ID | Finding | Severity | Deferred To | Reason for Deferral |
|----|---------|----------|-------------|---------------------|
| FE-NEW-01 | Three.js memory leak — no dispose() on unmount | CRITICAL | v0.22.0 | Requires R3F architecture change; no crash in normal usage, affects only rapid route switching |
| UX-01 | d_mm > D_mm accepted silently (impossible geometry) | ~~CRITICAL~~ | ✅ FIXED | _validate_plausibility in common_api.py now raises ValueError |
| UX-02 | Column returns dict, beam returns dataclass | CRITICAL | v0.22.0 | Breaking API change — requires major version or deprecation cycle |
| ARCH-NEW-12 | services/api.py god module (3610 lines) | HIGH | v0.22.0 | Structural refactor, no functional impact |
| S-NEW-01 | ImportError messages leak internal paths (22 instances) | HIGH | v0.21.7 | Security hardening release |
| H-01 | WebSocket connections lack rate limiting | HIGH | v0.21.7 | Security hardening release |
| M-04 | create_dev_token() importable in production | MEDIUM | v0.21.7 | No auth enabled by default, defense-in-depth improvement |
| M-05 | No per-endpoint scope checking | MEDIUM | v0.21.7 | Auth disabled by default, planned for security release |
| T-NEW-01 | MagicMock in 2 test files (TE-3 violation) | HIGH | v0.22.0 | Test quality, not production code |
| IS-NEW-01 | 4 footing functions lack @clause decorators | HIGH | v0.22.0 | Traceability enhancement, not math error |
| IS-NEW-02 | 17 serviceability functions lack @clause | HIGH | v0.22.0 | Traceability enhancement, not math error |

### Audit Highlights

- **Test Infrastructure:** 5003/5003 tests passing, 99% branch coverage on IS 456 code, 42+ golden vectors, 18 contract tests
- **Security:** 0 CVEs, Docker hardened (non-root, cap_drop ALL), JWT production safeguard, rate limiting on REST endpoints
- **Agent Infrastructure:** 16/16 agents, 14/14 skills, 16/16 prompts, all cross-references valid
- **Architecture:** 4-layer boundary intact, 108 API exports, consistent parameter naming with unit suffixes
- **IS 456 Compliance:** All formulas verified correct, 42 clauses + 8 IS 13920 covered, A+ compliance score
- **Packaging:** pyproject.toml v0.21.6, .j2 templates in wheel, all 19 modules have __init__.py
- **CI/CD:** 18 workflows, CodeQL + pip-audit + OpenSSF Scorecard, golden gate in CI

### Infrastructure Issues (non-blocking)

| Issue | Location | Impact | Fix Plan |
|-------|----------|--------|----------|
| skill_count=10 in registry metadata | agents/agent_registry.json | Cosmetic — actual count is 14 | Update _meta.skill_count |
| session_summary.py referenced but doesn't exist | CLAUDE.md, terminal-rules | Use `session.py summary` instead | Update 4 doc references |
| 3 architecture import violations in FastAPI | main.py, design.py, geometry.py | Non-functional, code works | Refactor in v0.22.0 |

## v0.21.6 Post-Audit: Online Research & Root Cause Analysis

**Source:** Online best practices (OWASP 2025, PyPI Trusted Publishers, PEP 740 attestations, IStructE software validation guidance) + External Audit EA-1 through EA-23 root cause patterns.

### NEW Issues Found (from online research)

These were NOT caught by the 14-agent audit. They come from comparing our setup against 2025 industry best practices.

| ID | Category | Issue | Severity | Target | How Found |
|----|----------|-------|----------|--------|-----------|
| OL-01 | Supply Chain | No `check-wheel-contents` validation in CI — malformed metadata can ship to PyPI | HIGH | v0.21.7 | PyPI packaging best practices |
| OL-02 | Supply Chain | No `twine check` in CI — README rendering errors discovered only post-publish | MEDIUM | v0.21.7 | PyPI publishing guide |
| OL-03 | Supply Chain | No SLSA provenance attestation — OWASP 2025 A03 (Supply Chain Failures) | HIGH | v0.22.0 | OWASP Top 10:2025 A03 |
| OL-04 | Supply Chain | No artifact signing (sigstore) — PEP 740 digital attestations now standard | MEDIUM | v0.22.0 | PyPI attestations blog (Nov 2024) |
| OL-05 | Docker | Base image `python:3.11-slim` not pinned to digest — reproducibility risk | MEDIUM | v0.21.7 | Container security best practices |
| OL-06 | Docker | No multi-stage build — dev tools included in production image (~1GB) | LOW | v0.22.0 | Docker security hardening guide |
| OL-07 | Docker | Container CVE scan exists but Trivy action unpinned (@master) | LOW | v0.21.7 | OWASP A03 + A06. Trivy scan already in docker-build.yml; pin action to SHA |
| OL-08 | Security | OWASP 2025 A10 "Mishandling of Exceptional Conditions" — 2-4 HTTP-exposed ImportError leaks (38 total catch sites, all properly sanitized via sanitize_error()) | LOW | v0.21.7 | OWASP Top 10:2025 (NEW category) |
| OL-09 | Security | No security logging / alerting — OWASP 2025 A09 has no implementation | MEDIUM | v0.22.0 | OWASP Top 10:2025 A09 |
| OL-10 | Packaging | No TestPyPI dry-run before production release | LOW | v0.21.7 | PyPI publishing workflow guide. TestPyPI job exists but only on workflow_dispatch, not mandatory gate |
| OL-11 | Packaging | No sdist contents verification (only wheel checked) | LOW | v0.22.0 | Python packaging best practices |
| OL-12 | Packaging | Optional dependency groups untested (`.[dxf]`, `.[report]`) | LOW | v0.21.7 | pip install variations |
| OL-13 | Licensing | No license compliance scan — BSD dependency chain could break GPL | LOW | v0.22.0 | FOSSA / pip-licenses |
| OL-14 | Struct Eng | No consolidated verification methodology doc — V&V infrastructure exists (42+ golden vectors, verification-checklist.md, validation-pack.md) but fragmented across 6+ files | MEDIUM | v0.22.0 | IStructE software validation guidance |
| OL-15 | Struct Eng | MERGED into TASK-735 — services/audit.py already provides basic audit trail; CalculationProvenance extends it | LOW | v0.22.0 | Building standards guidance on computer programs |
| OL-16 | API | No OpenAPI drift check in publish workflow — API clients break silently | MEDIUM | v0.21.7 | API versioning best practices |

### Additional Findings from 4-Agent Review (2026-04-07)

| ID | Finding | Severity | Source | Target |
|----|---------|----------|--------|--------|
| AR-01 | Trivy action@master unpinned (supply chain risk) | LOW | @security | v0.21.7 |
| AR-02 | Auth default-off even when JWT_SECRET_KEY is set in production | MEDIUM | @security | v0.21.7 |
| AR-03 | requirements.txt uses floor versions; Dockerfile installs unpinned deps | LOW | @security | v0.21.7 |
| AR-04 | Documentation drift — code fixes ahead of task board (e.g., UX-01 already fixed) | MEDIUM | @library-expert | Ongoing |
| AR-05 | No deprecation policy for 46 backward-compat stubs | LOW | @library-expert | v1.0 |
| AR-06 | Import time ~3-5s — ezdxf/pydantic eager loading in __init__.py | MEDIUM | @library-expert | v0.22.0 |
| AR-07 | Negative Mu silently abs-valued — no hogging/sagging guidance | MEDIUM | @library-expert | v0.21.7 |
| AR-08 | Column API not exported from structural_lib.__init__.py | HIGH | @library-expert | v0.21.7 |
| AR-09 | show_versions() reports stale version (0.21.1) from source install | LOW | @library-expert | v0.21.7 |

### Missing Root Cause Patterns (from @library-expert)

| # | Pattern | Severity | Description |
|---|---------|----------|-------------|
| 7 | Documentation Drift | MEDIUM | Code moves faster than docs; version strings, task statuses, verification checklist version all lag behind code |
| 8 | API Stability / No Deprecation Policy | LOW (HIGH at v1.0) | 46 backward-compat stubs with no formal removal timeline |
| 9 | Import Performance | MEDIUM | Cold start ~3-5s due to eager imports of ezdxf, pydantic, all stubs |

### External Audit Root Cause Analysis (EA-1 through EA-23)

We analyzed WHY each external audit finding was missed. Six patterns emerge:

| Pattern | Findings | Root Cause | Prevention Measure | Status |
|---------|----------|-----------|-------------------|--------|
| **Repo ≠ Installed** | EA-1, EA-6, EA-8, EA-9 | Tests only run in dev environment, never tested installed wheel | `@repo_only` marker, wheel smoke tests in CI | ✅ Fixed |
| **Dev-centric defaults** | EA-2, EA-10, EA-11, EA-16 | Config optimized for developer experience, not production safety | `.env.example`, auth-on-by-default in prod, lazy imports | ✅ Fixed |
| **Undocumented API ergonomics** | EA-3, EA-5, EA-12, EA-13 | API grew incrementally without UX design review | API levels doc, build_detailing_input() factory, e2e examples | ✅ Fixed |
| **Mixed API patterns** | EA-4, EA-14 | Features added fast without consistency enforcement | to_dict() added, task-oriented README | ✅ Fixed |
| **Security in exception messages** | EA-17, EA-18, EA-20 | Error messages treated as debug output, CORS hardcoded | sanitize_error() utility, Settings-based CORS, RateLimitMiddleware | ✅ Fixed |
| **Incomplete IS 456 coverage** | EA-21, EA-22, EA-23 | Code added without IS 456 clause coverage checklist | Clause audit list created, bearing_stress_enhancement(), SCWB check, D_mm param | ✅ Fixed |

### Are We Protected Against Recurrence?

| Prevention | Implemented? | Gap? |
|------------|-------------|------|
| Wheel smoke test in CI | ✅ Yes — python-tests.yml lines 147-158 | No gap |
| Clean import test | ✅ Yes — TestImportSilence, TestImportStrictWarnings | No gap |
| API stability test (105 functions) | ✅ Yes — TestAPIStability | No gap |
| E2E pipeline test | ✅ Yes — test_full_pipeline_e2e.py (8 tests) | No gap |
| RateLimitMiddleware on all endpoints | ✅ Yes — global middleware | No gap |
| sanitize_error() for all routers | ⚠️ Partial — 2-4 HTTP-exposed ImportError leaks (38 total catch sites properly sanitized) | OL-08 above |
| IS 456 clause checklist | ⚠️ Partial — @clause decorators exist but ~26 public IS 456 functions lack them (detailing: 11, common/: 8, footing/_common: 4, slenderness: 3; serviceability has full coverage) | IS-NEW-01, IS-NEW-02 |
| Cross-field input validation | ✅ Yes — _validate_plausibility in common_api.py raises ValueError for d>D | ✅ Fixed (was UX-01) |
| TestPyPI before prod publish | ❌ No — publish goes direct to PyPI | OL-10 above |
| OWASP 2025 A03 (Supply Chain) | ⚠️ Partial — Trusted Publishers ✅, but no attestations/provenance | OL-03, OL-04 |
| OWASP 2025 A09 (Logging) | ❌ No — no security event logging | OL-09 |
| OWASP 2025 A10 (Exceptions) | ⚠️ Partial — sanitize_error exists but not applied everywhere | OL-08 |
| Structural eng verification methodology | ⚠️ Partial — V&V infrastructure exists (42+ golden vectors, verification-checklist.md, validation-pack.md) but fragmented across 6+ files | OL-14 |
| Container security scanning | ✅ Yes — Trivy scan in docker-build.yml (action unpinned, needs SHA pin) | OL-07 above |

## v0.21.7 — Security Hardening (In Progress)

**Theme:** Input validation, error sanitization, packaging gates, CI hardening
**Execution Plan:** [v0217-execution-plan.md](_active/v0217-execution-plan.md)
**Target:** 2-3 sessions after v0.21.6
**Quality Gate:** `audit_input_validation.py` reports 0 unresolved findings. `pip-audit` clean.

| ID | Task | Owner | Status |
|----|------|-------|--------|
| TASK-728 | JSON body size limit middleware (1MB default) | @api-developer | 📋 |
| TASK-729 | Cross-field plausibility guards (14 model validators) | @api-developer | ✅ DONE |
| TASK-730 | Input validation audit (16 gaps found + fixed, 49 tests) | @security | ✅ DONE |
| TASK-731 | Dependency CVE scanning in CI (`pip-audit`) | @ops | 📋 |
| — | WebSocket message rate limit (5 msg/s per session) | @api-developer | 📋 |
| — | Computation timeout (prevent pathological inputs) | @api-developer | 📋 |
| TASK-790 | `check-wheel-contents` + `twine check` in publish workflow (OL-01, OL-02) | @ops | 📋 |
| TASK-791 | TestPyPI dry-run step before production PyPI publish (OL-10) | @ops | 📋 |
| TASK-792 | Container image security scan with Trivy in CI (OL-07) — Already exists in docker-build.yml; verify coverage only | @ops | 📋 |
| TASK-793 | Optional dependency group tests: `.[dxf]`, `.[report]` (OL-12) | @tester | 📋 |
| TASK-794 | Docker base image digest pinning (OL-05) | @ops | 📋 |
| TASK-795 | OpenAPI drift check in publish workflow (OL-16) | @ops | 📋 |
| TASK-796 | Fix ImportError path leaks (sanitize_error_string + 4 router fixes, 15 tests) | @api-developer | ✅ DONE |
| TASK-802 | Export column API to __init__.py (already exported — 6 contract test assertions fixed) | @backend | ✅ DONE |
| TASK-803 | Document negative Mu abs-value behavior + add hogging guidance (AR-07) | @doc-master + @structural-math | 📋 |
| TASK-804 | Auto-enable auth or log CRITICAL when JWT_SECRET_KEY set but AUTH_ENABLED=false (AR-02) | @api-developer | 📋 |

**Recommended action order (4-agent consensus):**
1. TASK-729 + TASK-730 (Input Safety — cross-field + validation audit)
2. TASK-802 (Column API export — HIGH user impact)
3. TASK-796 (ImportError leaks — 2-4 actual HTTP-exposed)
4. TASK-790 + TASK-791 + TASK-793 (Packaging gates)
5. TASK-795 (OpenAPI drift in publish)
6. TASK-794 (Docker digest pin)
7. TASK-728 (JSON body size limit)

## v0.21.8 — Performance & Property Testing

**Theme:** Performance baselines and property-based invariants
**Target:** 2-3 sessions after v0.21.7
**Quality Gate:** All benchmarks baselined. Hypothesis tests pass 10,000 examples.

| ID | Task | Owner | Status |
|----|------|-------|--------|
| TASK-732 | pytest-benchmark integration for hot-path functions | @tester | 📋 |
| TASK-733 | Property-based testing with Hypothesis (flexure/shear/column) | @tester | 📋 |
| TASK-734 | Performance regression baselines in CI (>20% slowdown blocks merge) | @ops | 📋 |
| — | Benchmark results stored in `Python/test_stats.json` | @tester | 📋 |

## Batch 3: API Naming Convention (v0.22.0)

**Theme:** Standardize parameter naming across L3 (services) API — `fck`→`fck_nmm2`, `fy`→`fy_nmm2`
**Ref:** Issue 15, architecture doc §10.5

| ID | Task | Owner | Status |
|----|------|-------|--------|
| TASK-740 | Standardize column_api.py param names (fck→fck_nmm2, fy→fy_nmm2) — 10 functions | @backend | ✅ |
| TASK-741 | Standardize beam_api.py outliers (check_beam_ductility, check_anchorage) — 2 functions | @backend | ✅ |
| TASK-742 | Update FastAPI column router + Pydantic models for new param names | @api-developer | ✅ |
| TASK-743 | Add deprecation warning tests for old param names | @tester | ✅ |
| TASK-744 | Document two-tier naming convention in architecture doc | @doc-master | ✅ |
| TASK-745 | Decide stable vs experimental API tiers (Issue 16 — defer to v0.23+) | @library-expert | 📋 |
| TASK-746 | Consolidate `_resolve_deprecated_param` from beam_api.py + column_api.py into common_api.py | @backend | 📋 [P4] |
| TASK-747 | Add direct unit tests for `_resolve_deprecated_param` TypeVar helper | @tester | 📋 [P4] |

---

## v0.22.0 — Stabilization Release

**Theme:** Production-quality release with full provenance and CI gates
**Target:** After all v0.21.x complete
**Quality Gate:** All v0.21.x quality gates pass simultaneously. SP:16 verification ±0.1%. Release preflight clean.

| ID | Task | Owner | Status |
|----|------|-------|--------|
| TASK-735 | CalculationProvenance foundation (`core/provenance.py`) — see arch doc §11 | @backend | 📋 |
| TASK-736 | SP:16 full verification | @structural-engineer | 📋 |
| TASK-797 | SLSA provenance + PEP 740 digital attestations (OL-03, OL-04) | @ops | 📋 |
| TASK-798 | Security event logging framework — OWASP 2025 A09 (OL-09) | @security (define) + @api-developer (implement) | 📋 |
| TASK-799 | Multi-stage Dockerfile (builder→runtime, reduce image to ~400MB) (OL-06) | @ops | 📋 |
| TASK-800 | Independent verification methodology doc — IStructE guidance (OL-14) | @structural-engineer | 📋 |
| — | ~~TASK-761~~ Calculation audit trail — MERGED into TASK-735 (CalculationProvenance); services/audit.py already provides basic audit trail | — | ✅ Merged |
| TASK-801 | License compliance scan with pip-licenses (OL-13) | @security | 📋 |
| TASK-521 | Beam rationalization | @backend | 📋 [CARRIED OVER] |
| TASK-643 | SP:16 chart verification completion | @structural-engineer | 📋 [CARRIED OVER] |
| — | Deprecate old architecture docs | @doc-master | 📋 |
| — | Full CI/CD pipeline with all quality gates active | @ops | 📋 |
| — | Release checklist automation | @ops | 📋 |

## Library Expansion — Multi-Code, Multi-Element

> **v5.0:** Multi-code (IS 456 + ACI 318 + EC2), multi-element expansion. Every function goes through a 9-step quality pipeline.
> See [library-expansion-blueprint-v5.md](planning/library-expansion-blueprint-v5.md) for full plan.
> Use `/function-quality-pipeline` skill for every new function.

### Completed Phases (Summary)

| Phase | Scope | Tasks | Status |
|-------|-------|-------|--------|
| Phase 0 | Quality Infrastructure | TASK-600–610 (11/11) | ✅ Done |
| Phase 1 | Foundation Cleanup | TASK-611–625 (15/15) | ✅ Done |
| Phase 1.5 | IS 456 Beam Restructure | TASK-700–712 (13/13) | ✅ Done |
| Phase 2 | Column Design | TASK-630–646 (14/14) | ✅ Done |
| Phase 3 (partial) | Footing Design | TASK-650–654 (5/7) | 🔄 5/7 |
| Variable Naming | IS 456 convention migration | TASK-660 (1/1) | ✅ Done |
| Agent Evolver | Self-evolving agent system | TASK-800.P3–P11 | ✅ Done (P12 burn-in) |
| Agent Infrastructure | claw-code adaptation | TASK-850–872 (23/23) | ✅ Done |
| Git Hardening | Git workflow automation | TASK-900–913 (13/14) | ✅ 13/14 |

> Full details for all completed phases: [tasks-history.md](_archive/tasks-history.md)

### Phase 3: Footing Design (Remaining)

| ID | Task | Function | IS 456 Clause | Status |
|----|------|----------|---------------|--------|
| TASK-655 | Dowel bars | `check_dowel_bars` | Cl 34.2.5 | 📋 |
| TASK-656 | Footing FastAPI endpoint | `POST /api/v1/design/footing` | — | 📋 |

> Phase 3: 5/7 tasks done (TASK-650–654 ✅). Covers: types+errors, bearing sizing (Cl 34.1), flexure (Cl 34.2.3.1), one-way shear (Cl 34.2.4.1(a)), punching shear (Cl 31.6.1), bearing pressure (Cl 34.4). 89+ tests. Remaining: TASK-655 (dowel bars), TASK-656 (FastAPI endpoint).

---

## v0.23 — IS 456 Slabs & Footing Completion

**Ref:** Architecture doc §20.6

### Footing Remaining

| ID | Task | Function | IS 456 Clause | Status |
|----|------|----------|---------------|--------|
| TASK-655 | Dowel bars | `check_dowel_bars` | Cl 34.2.5 | 📋 |
| TASK-656 | Footing FastAPI endpoint | `POST /api/v1/design/footing` | — | 📋 |
| — | Combined footing design | — | — | 📋 |
| — | Footing `@clause` coverage to 100% | — | — | 📋 |

### One-Way Slab Design (IS 456 Cl 24.1–24.2)

| ID | Task | Function | IS 456 Clause | Status |
|----|------|----------|---------------|--------|
| TASK-737 | One-way slab design (umbrella) | — | Cl 24.1–24.2 | 📋 |
| TASK-750 | Slab types + errors | Types (SlabClassification, SlabDesignResult) | — | 📋 |
| TASK-751 | classify_slab | `classify_slab()` | ly/lx ratio | 📋 |
| TASK-752 | One-way coefficients | `oneway_coefficients()` | Table 12/13 | 📋 |
| TASK-753 | Design one-way slab | `design_oneway_slab()` | Cl 24.1–24.2 | 📋 |
| TASK-754 | Slab detailing | `slab_detailing()` | Cl 26.5 | 📋 |

### Two-Way Slab Design (IS 456 Cl 24.3, Annex D)

| ID | Task | Function | IS 456 Clause | Status |
|----|------|----------|---------------|--------|
| TASK-738 | Two-way slab design (umbrella) | — | Cl 24.3, Annex D | 📋 |
| TASK-760 | Two-way moment coefficients | `twoway_moment_coefficients()` | Table 26 | 📋 |
| TASK-761 | Two-way shear coefficients | `twoway_shear_coefficients()` | Table 27 | 📋 |
| TASK-762 | Design two-way slab | `design_twoway_slab()` | Annex D-1 | 📋 |
| TASK-763 | Torsion reinforcement | `torsion_reinforcement()` | Annex D-1.7/D-1.8 | 📋 |
| TASK-764 | Strip distribution | `strip_distribution()` | Annex D-1.2 | 📋 |
| — | Flat slab with drop panels | — | IS 456 Cl 31 | 📋 |

### Punching Shear (Shared — Slab + Footing)

| ID | Task | Function | IS 456 Clause | Status |
|----|------|----------|---------------|--------|
| TASK-770 | General punching shear module | `punching_shear_check()` | Cl 31.6 | 📋 |

### Slab FastAPI + React

| ID | Task | Status |
|----|------|--------|
| TASK-780 | Slab API wiring (services/api.py) | 📋 |
| TASK-781 | Slab FastAPI endpoints | 📋 |
| TASK-782 | Slab React form + results panel | 📋 |

### Additional v0.23 Deliverables (from architecture doc §20.6)

| ID | Task | Owner | Status |
|----|------|-------|--------|
| — | Progress callbacks for batch operations (§13.2) | @backend | 📋 |
| — | Complete error hierarchy (§13.3) | @backend | 📋 |
| — | Property-based testing expansion to all modules (§14.1) | @tester | 📋 |
| — | Performance benchmarks baselined (§14.2) | @tester | 📋 |

---

## v0.24 — Multi-Code Infrastructure

**Ref:** Architecture doc §20.7 + [library-expansion-blueprint-v5.md](planning/library-expansion-blueprint-v5.md) Phase 2

| ID | Task | Description | Owner | Status |
|----|------|-------------|-------|--------|
| TASK-739 | CodeRegistry thread-safe locking | Make CodeRegistry safe for concurrent use | @backend | 📋 |
| TASK-740 | DesignEnvelope wrapper | Multi-code result wrapper (§5.3) | @backend | 📋 |
| TASK-741 | core/units.py | Unit conversion at boundary (in→mm, psi→MPa) | @backend | 📋 |
| TASK-800-INFRA-1 | Activate CodeRegistry | `services/api.py` uses `CodeRegistry.get()` for dispatch | @backend | 📋 |
| TASK-800-INFRA-2 | IS456Code implements ABCs | FlexureDesigner, ShearDesigner, ColumnDesigner | @backend | 📋 |
| TASK-800-INFRA-3 | Code-specific input dataclasses | IS456BeamInput, ACI318BeamInput, EC2BeamInput | @backend | 📋 |
| — | Code Amendment Tracking metadata (§11.2) | @structural-math | 📋 |
| — | National annex support infrastructure | @backend | 📋 |
| — | Entry-point plugin discovery for third-party codes (§16.7) | @backend | 📋 |
| — | Auto-generated client SDKs (Python + TypeScript, §13.1) | @api-developer | 📋 |
| — | API v2 routes: `/api/v2/{code}/design/beam` | @api-developer | 📋 |
| TASK-800-INFRA-6 | Namespace clauses.json v2 | Add code field to clause entries | @backend | 📋 |
| TASK-800-INFRA-7 | Code discovery API | `list_codes()`, `get_capabilities()` | @backend | 📋 |
| TASK-800-INFRA-8 | FastAPI v2 routes | `/api/v2/{code}/design/beam` | @api-developer | 📋 |
| TASK-800-INFRA-9 | Feature flags for experimental codes | EXPERIMENTAL_CODES config | @ops | 📋 |

---

## v0.25 — ACI 318-19 Beam

**Ref:** Architecture doc §20.8 + [library-expansion-blueprint-v5.md](planning/library-expansion-blueprint-v5.md) Phase 3

| ID | Task | Description | Owner | Status |
|----|------|-------------|-------|--------|
| TASK-742 | ACI 318-19 beam flexure | `codes/aci318/beam_flexure.py` | @structural-math | 📋 |
| TASK-743 | ACI 318-19 beam shear | `codes/aci318/beam_shear.py` | @structural-math | 📋 |
| — | PCA Notes (12th Ed.) benchmarks ±0.1% | @tester | 📋 |
| — | `@register_code("ACI318")` activation | @backend | 📋 |
| — | ACI318 FastAPI endpoints | @api-developer | 📋 |

### v0.26–v0.28 (Future)

| Version | Code | Elements | Benchmark Source |
|---------|------|----------|-----------------|
| v0.26 | ACI 318-19 | Column + Slab | PCA Notes |
| v0.27 | EC2 | Beam (flexure + shear) | Concrete Centre ±0.1% |
| v0.28 | EC2 | Column + Slab | Concrete Centre |

---

## v1.0 — Production Multi-Code Release

**Ref:** Architecture doc §20.9

| ID | Task | Owner | Status |
|----|------|-------|--------|
| — | IS 456 complete (beam + column + slab + footing) | @structural-math | 📋 |
| — | ACI 318 beam + column | @structural-math | 📋 |
| — | EC2 beam (basic) | @structural-math | 📋 |
| — | CalculationProvenance on all results (§11) | @backend | 📋 |
| — | Export integrity/watermarking (§11.3) | @backend | 📋 |
| — | Full OWASP compliance (§12) | @security | 📋 |
| — | API stability guarantee (no breaking changes without major version) | @backend | 📋 |
| — | Complete documentation coverage | @doc-master | 📋 |
| — | Performance benchmarks all met (§14.2) | @tester | 📋 |
| — | RBAC / scope enforcement (§3.5) | @api-developer | 📋 |
| — | Design audit trail middleware (§11.1) | @api-developer | 📋 |

### Post-v1.0 Research (from architecture doc §20.10)

| Item | Description | Status |
|------|-------------|--------|
| WASM compilation path | Layer 2 pure math → Pyodide/Rust for client-side calc | 🔲 Research |
| msgspec serialization | Benchmark vs frozen dataclass for batch perf | 🔲 Research |
| structuralcodes integration | Material models as optional backend | 🔲 Research |
| IS 16700 (tall buildings) | Wind/seismic response spectra | 🔲 Research |
| IS 1893 integration | Seismic load generation | 🔲 Research |

---

## Backlog

| ID | Task | Priority | Notes |
|----|------|----------|-------|
| TASK-513 | React: AI assistant port | ⏸ Deferred | Deferred — needs LLM API design, not in v0.22 scope |
| TASK-908 | bats-core tests for git scripts | 🟢 Low | Deferred — requires bats-core install |
| API-5 | OpenAPI examples on Pydantic models | 🟢 Low | Moved from v0.22 — non-blocking |
| OPS-3 | Python dependency lock file | 🟢 Low | Moved from v0.22 — non-blocking |
| DOC-4 | Footing section in api.md | 🟢 Low | Moved from v0.22 — non-blocking |
| DOC-5 | Clause-to-function mapping | 🟢 Low | Moved from v0.22 — non-blocking |
| — | E2E integration test (React against live FastAPI) | 🟡 Medium | Target v0.21.6+ |
| — | Wire BuildingEditor Cost tab (placeholder → real data) | 🟢 Low | Use `/optimization/cost-rates` |
| — | 28 unit conversion warnings | 🟢 Low | Informational, not bugs. Self-documenting via `_nmm`/`_knm` var names. |
| — | 287 legacy import warnings (Streamlit) | 🟢 Low | Won't fix — will go away when Streamlit is deprecated |
| — | IS 456 extended elements (Wall Cl 32, Staircase Cl 33, Deep beam Cl 29) | 🟢 Low | Post v1.0 |
| — | Companion codes (IS 875, IS 1893, ASCE 7, EN 1990/1991) | 🟢 Low | Post v1.0 |

---

## Archive

Sessions 32–73 and legacy TASK items have been completed. See [docs/_archive/tasks-history.md](_archive/tasks-history.md) for details.

Key milestones from archived sessions:
- **Session 73** (Jan 24): FastAPI skeleton (20 routes, 31 tests), WebSocket endpoint, `discover_api_signatures.py`
- **Session 66** (Jan 24): V3 automation foundation, 143 scripts audited, API latency validated
- **Session 65** (Jan 23): Agent effectiveness research, `docs-canonical.json`, `automation-map.json`
- **Session 63** (Jan 23): Rebar consolidation, scanner fixes, TASK-350/351/352 resolved
- **Sessions 32–62c** (Jan 22): Rebar editor, DXF export, cost optimizer, section geometry

---

**Session logs:** See [SESSION_LOG.md](SESSION_LOG.md) for detailed history.
**Task history:** See [_archive/tasks-history.md](_archive/tasks-history.md)

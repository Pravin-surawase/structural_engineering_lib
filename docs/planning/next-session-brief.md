# Next Session Briefing

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-08-07
- Focus: MAINT-005 interactive exports, v0.21.7 finish line, and Mac control-plane recovery
<!-- HANDOFF:END -->

**Last Updated:** 2026-08-07
**Current Session:** Maintenance Recovery — full-stack confidence green through dashboard; exports next

## Start Here

1. Finish MAINT-005 by exercising BBS, DXF, report, building-summary, and BOQ CSV downloads in the UI. Route/API coverage and the browser flow through the dashboard are already green.
2. MAINT-001 is preserved in pushed checkpoint `b28ee4e3`, but GitHub CLI authorization must be rerun and completed in the browser.
3. Restart macOS before retrying Colima. Do not delete/recreate the transferred VM until Docker data is backed up or deletion is explicitly approved.
4. Preserve the restored baseline: 28/28 canonical checks, 22/22 audit checks, 100/100 health, and 96% actionable parity.
5. Keep `docs/TASKS.md`, `docs/WORKLOG.md`, `docs/SESSION_LOG.md`, and this handoff synchronized at each checkpoint.

Full evidence and accepted risks are in
[maintenance-recovery-audit-2026-08-07.md](../audit/maintenance-recovery-audit-2026-08-07.md).

## Current Evidence

- Repository transfer is intact: no corrupt reachable Git objects, broken symlinks, submodule issues, or missing ETABS sample files.
- Local/remote `main`: `fa854e0f`; published package: v0.21.6.
- Pre-session dirty tree: 73 modified tracked files and 47 untracked files, preserved by checkpoint `b28ee4e3`.
- Passing baselines: Python 5,138; FastAPI 336; React 142; React production build; wheel install/design/detail/BBS/report smoke test.
- Current red gates: interactive UI downloads, 17.74% React statement coverage, GitHub CLI authorization, and the transferred Colima VM state.
- Local environment: Python 3.11 ARM64 editable install is repaired at v0.21.6; Node 24.19.0 is installed keg-only and React passes on it; Colima VZ requires a Mac restart; GitHub CLI authentication must be renewed.
- Recovery checkpoint: `b28ee4e3` pushed on `task/MAINT-001`.
- MAINT-002: complete and validated with 18/18 live E2E checks and zero broken internal links.
- Quick canonical gate: 8/8 green; all 3,248 scanned imports resolve.
- MAINT-003: clean Python lock audits at zero known vulnerabilities and passes 5,138 core plus 326 FastAPI tests; npm has one narrowly allowlisted RSC-only advisory and all 139 React tests/lint/build pass.
- MAINT-004: complete. Canonical check 28/28, audit 22/22, health 100/100, and completed active plans archived with zero broken links. Current feedback is 19/23 resolved; four maintenance watches remain.
- MAINT-005 checkpoint `6f119132`: 60/60 direct FastAPI route tests, 13/13 API-connected React hooks, and 96% actionable parity.
- Browser evidence: the 153-beam ETABS sample imports, auto-designs, renders in R3F, and reaches a 153/153-pass dashboard with max utilization 100% and no new warnings. Dashboard and BOQ steel totals agree at 1,928.5 kg.
- Mac launcher evidence: `.nvmrc` Node 24 is selected even when a stale unversioned Node is first on `PATH`; port cleanup targets listeners only and no longer kills connected browser/client helpers.

## Maintenance Sequence

| Order | Task | Outcome |
|-------|------|---------|
| 1 | MAINT-001 recovery checkpoint | No inherited work can be lost |
| 2 | MAINT-002 CI + E2E contract | Nightly stops failing/spamming; live import flow is enforced |
| 3 | MAINT-003 environment/security | Reproducible Mac Mini baseline and deliberate dependency upgrades |
| 4 | MAINT-004 canonical automation/docs | One trustworthy project status signal |
| 5 | MAINT-005 frontend/release scope | Credible v0.21.7 stabilization exit criteria |

## Previous Handoff (2026-04-07)

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

| **Current** | v0.21.6 | Released to PyPI |
| **Next** | v0.21.7 | Security Hardening — in progress (4/14 tasks done) |

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

## Required Reading
- [TASKS.md](../TASKS.md) — active task board
- [agent-bootstrap.md](../getting-started/agent-bootstrap.md) — project rules & architecture
- [api.md](../reference/api.md) — API reference (19 new symbols added)

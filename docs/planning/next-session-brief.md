# Next Session Briefing

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-08-07
- Focus: Obtain approval for the two focused PR #676 CI fixes, validate required checks, and request the v0.21.7 release decision
<!-- HANDOFF:END -->

**Last Updated:** 2026-08-07
**Current Session:** Maintenance Recovery — Mac/GitHub/Docker recovery complete; PR CI closeout remains

## Start Here

1. Obtain explicit approval before applying the two focused PR #676 CI fixes: replace three empty template links and pin Ruff 0.15.8 consistently instead of accepting unbounded 0.16.1 drift.
2. Re-run only the affected link/lint checks, push through `ai_commit.sh`, and monitor PR #676 required checks. Do not merge or release without explicit user approval.
3. Preserve the recovered Mac baseline: GitHub API/SSH pass, Colima/Docker are healthy with the transferred disk intact, and Docker release preflight is green.
4. Run the main orchestrator on Sol High for intake, planning, delegation, integration, and final review. Give Luna/Terra workers compact packets with exact scope, non-goals, pitfalls, acceptance criteria, tests, and return format; verify their work before acceptance.
5. Treat 17.74% React statement coverage, one hook lint warning, and one RSC-only advisory as recorded risks—not reasons to reopen completed maintenance without a focused task.

Full evidence and accepted risks are in
[maintenance-recovery-audit-2026-08-07.md](../audit/maintenance-recovery-audit-2026-08-07.md).

## Current Evidence

- Repository transfer is intact: no corrupt reachable Git objects, broken symlinks, submodule issues, or missing ETABS sample files.
- Local/remote `main`: `fa854e0f`; published package: v0.21.6.
- Pre-session dirty tree: 73 modified tracked files and 47 untracked files, preserved by checkpoint `b28ee4e3`.
- Passing baselines: release preflight 5,159 Python passed, 3 skipped, 6 deselected; FastAPI 336; React 146; Node 24 production build.
- Clean-wheel UAT: 5,120 passed, 41 skipped, 6 deselected plus packaged job, critical-case CSV, and HTML-report CLI workflows.
- GitHub CLI keyring/API, repository queries, PR access, SSH, and remote Git transport pass. PR #676 is open from `task/MAINT-001`.
- Colima is healthy on the preserved VZ disk after a targeted stale-lock recovery; Docker reports 4 CPUs/~4 GB and Compose config passes.
- Docker preflight passes 5,158 Python tests, 8 skips, 6 deselections, plus the Node 24 React production build.
- Low-token policy checkpoint `6e8e4a31` adds project Codex defaults, a two-subagent cap, focused handoffs, `./run.sh efficiency`, and a 9/9 quick gate.
- The analytics-calibrated model picker is in `agents/model_policy.json` and `./run.sh model`; it recommends Luna-first for repeatable work and never auto-selects approval-gated Sol.
- Model-routing checkpoint `fe55d130` is pushed on PR #676. Focused Ruff/tests pass; the full gate's 22 non-doc checks passed and the corrected Docs category passes 7/7.
- Sol High orchestrator checkpoint `ff6d525d` is pushed. Project defaults, picker, role instructions, worker-packet contract, and verification tests agree.
- MAINT-007 makes PR status terminal-only by default, corrects stale bootstrap/tool counts and active-task briefs, discovers all 14 Copilot skills, and adds honest local model/agent checkpoints through `./run.sh session usage`.
- MAINT-007 verification is green: 32 focused tests, quick 9/9, full 29/29, audit 22/22, and health 100/100. The first local usage ledger records Sol High, one parent, zero subagents, and no fabricated billing values.
- Current gate: PR #676 has two diagnosed CI failures awaiting approval—three empty template links and Ruff 0.16.1 dependency drift. React coverage remains an accepted follow-up risk.
- Recovery checkpoint: `b28ee4e3` pushed on `task/MAINT-001`.
- MAINT-002: complete and validated with 18/18 live E2E checks and zero broken internal links.
- Quick canonical gate: 9/9 green; all 3,248 scanned imports resolve.
- MAINT-003: clean Python lock audits at zero known vulnerabilities; npm has one narrowly allowlisted RSC-only advisory.
- MAINT-004: complete. Canonical check 28/28, audit 22/22, health 100/100, completed active plans archived, and feedback is 22/23 resolved.
- MAINT-005 checkpoint `6f119132`: 60/60 direct FastAPI route tests, 13/13 API-connected React hooks, and 96% actionable parity.
- Browser/export evidence: the 153-beam ETABS sample imports, auto-designs, renders in R3F, reaches a 153/153-pass dashboard, and exercises BBS, DXF, single report, building summary, and BOQ exports with no new warnings. Byte-level checks validate CSV/DXF/PDF artifacts; final quantities are 2,663.4 kg steel and 114.8 m³ concrete.
- Mac launcher evidence: `.nvmrc` Node 24 is selected even when a stale unversioned Node is first on `PATH`; port cleanup targets listeners only and no longer kills connected browser/client helpers.
- Live-design evidence: WebSocket payloads now retain the complete REST response contract, including real capacities and governing utilization; current and legacy payload shapes are normalized in the frontend.
- Release evidence: macOS reclaimable-memory and Node-runtime detection are repaired; `./run.sh release preflight 0.21.7` reports READY TO RELEASE with zero warnings.

## Maintenance Sequence

| Order | Task | Outcome |
|-------|------|---------|
| 1 | MAINT-001 recovery checkpoint | No inherited work can be lost |
| 2 | MAINT-002 CI + E2E contract | Nightly stops failing/spamming; live import flow is enforced |
| 3 | MAINT-003 environment/security | Reproducible Mac Mini baseline and deliberate dependency upgrades |
| 4 | MAINT-004 canonical automation/docs | One trustworthy project status signal |
| 5 | MAINT-005 frontend/release scope | Credible v0.21.7 stabilization exit criteria |
| 6 | MAINT-006 token/model policy | Analytics-calibrated low-token routing with enforced safety limits |
| 7 | MAINT-007 docs/tool refresh | Current onboarding, complete discovery, local usage evidence, and no surprise PR tabs |

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

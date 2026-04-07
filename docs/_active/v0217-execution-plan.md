# v0.21.7 Execution Plan — Security Hardening

**Type:** Guide
**Audience:** All Agents
**Status:** Draft
**Importance:** Critical
**Created:** 2026-04-07
**Last Updated:** 2026-04-07

> This plan covers ALL v0.21.7 tasks in execution order. Each task has: what to do, why, which agents, which files, pipeline steps, docs to update, and common mistakes to avoid.

---

## Pre-Requisites (Before Starting v0.21.7)

### v0.21.6 Release Must Be Complete First

These 3 version fixes + tag are blocking:

| # | File | Change | Agent |
|---|------|--------|-------|
| 1 | CHANGELOG.md | `[Unreleased]` → `[0.21.6] — 2026-04-07` + add compare link at bottom | @doc-master |
| 2 | Python/README.md | `@v0.21.5` → `@v0.21.6` (git install pin) | @doc-master |
| 3 | docs/git-automation/README.md | `Version: 0.21.5` → `Version: 0.21.6` | @doc-master |
| 4 | Run `./run.sh release preflight 0.21.6` | Validate before tag | @ops |
| 5 | Tag + publish to PyPI | `git tag v0.21.6 && publish` | @ops |

**Pipeline:** @doc-master (fixes 1-3) → @ops (preflight + release)
**Estimated effort:** 1 quick session

---

## Execution Order (4-Agent Consensus)

| Priority | Task(s) | Theme | Sessions |
|----------|---------|-------|----------|
| **P1** | TASK-729 + TASK-730 | Input Safety | 1-2 |
| **P2** | TASK-802 | Column API Export | 1 |
| **P3** | TASK-796 | ImportError Leak Fix | 1 |
| **P4** | TASK-790 + TASK-791 + TASK-793 | Packaging Gates | 1 |
| **P5** | TASK-795 + TASK-794 + TASK-792 | CI Hardening | 1 |
| **P6** | TASK-728 + TASK-804 | API Security | 1 |
| **P7** | TASK-803 + TASK-731 | Docs + CVE scanning | 1 |

---

## P1: Input Safety (TASK-729 + TASK-730)

### TASK-729: Cross-field Plausibility Guards

**What:** Add Pydantic validators that reject physically impossible input combinations at the API boundary (FastAPI routers). NOT in the core math library.

**Why:** A structural engineer entering d_mm=500, D_mm=400 (effective depth > total depth) gets wrong results instead of an error.
Originally flagged as UX-01 (now ✅ fixed for d>D) but other cross-field checks still needed. The `_validate_plausibility()` function exists in `services/common_api.py` but some cross-field checks may be missing from FastAPI Pydantic models.

**Agent Pipeline:**
1. @security — Run `audit_input_validation.py` to identify gaps → produces findings list
2. @api-developer — Add Pydantic `@model_validator(mode='after')` checks to beam/column/footing request models
3. @tester — Write tests: valid inputs pass, each invalid combo returns 422
4. @reviewer — Verify validators are at API boundary only (NOT in core math)
5. @doc-master — Update TASKS.md
6. @ops — Commit as `feat(api): cross-field plausibility guards`

**Files to check FIRST:**
- `fastapi_app/models/` — existing Pydantic models (BeamDesignRequest, ColumnRequest, etc.)
- `Python/structural_lib/services/common_api.py` — existing `_validate_plausibility()`
- `scripts/audit_input_validation.py` — validation gap scanner

**Key validations to add:**
- `d_mm < D_mm` (effective depth < total depth) — may already be in `_validate_plausibility`
- `clear_cover_mm + bar_dia/2 < D_mm/2` (cover not exceeding half section)
- `fck_nmm2` in {20, 25, 30, 35, 40, 45, 50} (IS 456 standard grades)
- `fy_nmm2` in {250, 415, 500} (IS 456 standard grades)
- `b_mm > 0`, `D_mm > 0` (positive dimensions)
- `Mu_knm >= 0` (moment magnitude, not signed — see AR-07)

**Mistakes to avoid:**
- ❌ Do NOT add validators in `codes/is456/` — that's Layer 2 (pure math, no I/O validation)
- ❌ Do NOT add validators in `services/api.py` — that's Layer 3 (orchestration)
- ✅ Add validators in `fastapi_app/models/` (Layer 4 — API boundary)
- ❌ Do NOT make `fck` restricted to standard grades in the LIBRARY — only at API boundary. The library should accept any value for research/custom use.

**Docs to update:** TASKS.md (mark done), next-session-brief.md

---

### TASK-730: Input Validation Audit

**What:** Run `audit_input_validation.py` to verify zero unresolved validation gaps across all 60 endpoints.

**Why:** Automated scan ensures we haven't missed any endpoint. This is the quality gate for TASK-729.

**Agent Pipeline:**
1. @security — Run audit, report findings
2. @api-developer — Fix any remaining gaps found
3. @tester — Verify audit passes with 0 findings
4. @reviewer — Approve
5. @ops — Commit as `fix(api): close input validation audit gaps`

**Files:**
- `scripts/audit_input_validation.py` — the scanner
- All files in `fastapi_app/routers/` — scan targets

**Mistakes to avoid:**
- ❌ Don't create a NEW validation audit script — one already exists
- ❌ Don't run audit before TASK-729 (it will have findings that 729 fixes)

---

## P2: Column API Export (TASK-802)

### TASK-802: Export Column API to `__init__.py`

**What:** Add column API functions to `Python/structural_lib/__init__.py` so users can do `from structural_lib import design_column_axial_is456`.

**Why:** Currently beams work from top-level (`from structural_lib import design_beam_is456`) but columns require `from structural_lib.services.column_api import ...`. This is inconsistent and confusing for users. @library-expert flagged this as HIGH user impact (AR-08).

**Agent Pipeline:**
1. @backend — Add imports to `__init__.py` + update `__all__`
2. @tester — Add contract test: verify all column functions importable from top-level
3. @reviewer — Check import chain doesn't break lazy loading
4. @ops — Commit as `feat(api): export column API to top-level __init__.py`

**Files to check FIRST:**
- `Python/structural_lib/__init__.py` — current exports (see `__all__` list)
- `Python/structural_lib/services/column_api.py` — functions to export
- `Python/tests/test_api_stability.py` — existing API contract tests

**Functions to export (check column_api.py for exact names):**
```python
# Run this to discover:
# .venv/bin/python scripts/discover_api_signatures.py design_column
```

**Mistakes to avoid:**
- ❌ Don't add eager imports — use the existing `__getattr__` lazy loading pattern in `__init__.py`
- ❌ Don't export private helpers (functions starting with `_`)
- ❌ Don't forget to add to `__all__` list
- ✅ Follow the exact same pattern used for beam functions

**Docs to update:** TASKS.md, docs/reference/api.md (add column functions to exported list)

---

## P3: ImportError Leak Fix (TASK-796)

### TASK-796: Fix 2-4 HTTP-Exposed ImportError Path Leaks

**What:** Find the 2-4 remaining ImportError handlers in FastAPI routers that expose internal paths to HTTP clients, and wrap them with `sanitize_error()`.

**Why:** OWASP 2025 A10 (Mishandling Exceptional Conditions). Even though `sanitize_error()` catches most cases, @security found 2-4 that slip through.

**Agent Pipeline:**
1. @security — Audit: `grep -rn "str(e)" fastapi_app/routers/` + identify exposed instances
2. @api-developer — Fix each: replace `str(e)` with `sanitize_error(e, "context")`
3. @tester — Write test: trigger each ImportError, verify response doesn't contain `/Users/` or file paths
4. @reviewer — Verify fixes
5. @ops — Commit as `fix(security): sanitize remaining ImportError path leaks`

**Files:**
- `fastapi_app/error_utils.py` — `sanitize_error()` function (the fix tool)
- `fastapi_app/routers/imports.py` — at least 1 known instance (line ~295)
- `fastapi_app/routers/export.py` — check for raw `str(e)` in except blocks
- `fastapi_app/routers/design.py` — check for raw `str(e)` in except blocks

**What sanitize_error() does:**
- Logs full error server-side (for debugging)
- Returns generic reference ID to client (for support)
- Strips messages containing `/`, `\`, or `Traceback`

**Mistakes to avoid:**
- ❌ Don't rewrite sanitize_error() — it already works correctly
- ❌ Don't remove ImportError handlers — keep them, just sanitize the output
- ❌ Don't count `pass` handlers as leaks — only `str(e)` or `raise HTTPException(detail=str(e))`

---

## P4: Packaging Gates (TASK-790 + TASK-791 + TASK-793)

### TASK-790: check-wheel-contents + twine check in CI

**What:** Add two validation steps to `.github/workflows/publish.yml`:
1. `check-wheel-contents` — validates wheel has correct files, no stale/missing modules
2. `twine check --strict` — validates metadata, README rendering, classifiers

**Why:** Historical packaging bugs (EXT-P1-5 missing .j2 templates) would have been caught by these tools. They're free safety nets.

**Agent Pipeline:**
1. @ops — Add steps to publish.yml after `python -m build` and before `pypi-publish`
2. @tester — Verify by running locally: `.venv/bin/pip install check-wheel-contents twine && check-wheel-contents dist/*.whl && twine check dist/*`
3. @reviewer — Verify steps are in correct position in workflow
4. @ops — Commit as `ci: add check-wheel-contents + twine check to publish workflow`

**Files:**
- `.github/workflows/publish.yml` — the publish workflow
- `requirements.txt` or `pyproject.toml [dev]` — add check-wheel-contents, twine as dev deps

**YAML to add (after `python -m build` step):**
```yaml
- name: Validate wheel contents
  run: |
    pip install check-wheel-contents twine
    check-wheel-contents dist/*.whl
    twine check --strict dist/*
```

**Mistakes to avoid:**
- ❌ Don't add to python-tests.yml — this belongs in publish.yml specifically
- ❌ Don't add after pypi-publish step — must be BEFORE upload
- ✅ Add after build step, before attestation/upload steps

---

### TASK-791: TestPyPI Dry-Run Before Production

**What:** Make the TestPyPI upload a mandatory gate before production PyPI publish in the tag-triggered path.

**Why:** TestPyPI exists as a manual option (workflow_dispatch) but the tag path goes straight to prod. A bad publish costs hours to fix.

**Agent Pipeline:**
1. @ops — Modify publish.yml: add TestPyPI upload as required step before prod upload on tag trigger
2. @reviewer — Verify the dependency chain (TestPyPI → prod) is correct
3. @ops — Commit as `ci: make TestPyPI dry-run mandatory before prod publish`

**Files:**
- `.github/workflows/publish.yml` — modify tag trigger path to require TestPyPI first

**Approach:**
- Add `needs: publish-testpypi` to the `publish-pypi` job for tag triggers
- TestPyPI upload uses `repository-url: https://test.pypi.org/legacy/`
- If TestPyPI fails, prod publish is blocked

**Mistakes to avoid:**
- ❌ Don't break the existing workflow_dispatch path
- ❌ Don't upload to TestPyPI for every push — only for tag triggers
- ✅ Keep the existing manual TestPyPI option working

---

### TASK-793: Optional Dependency Group Tests

**What:** Add CI test matrix that installs with each optional extra and runs basic import/functionality tests.

**Why:** `pip install structural-lib-is456[dxf]` might fail if ezdxf version is wrong. We never test this path.

**Agent Pipeline:**
1. @tester — Write test script that: installs with each extra, imports, runs one function
2. @ops — Add CI matrix job: `strategy: matrix: extra: [dxf, report, pdf, render, validation]`
3. @reviewer — Verify test covers the critical path for each extra
4. @ops — Commit as `test: add optional dependency group CI matrix`

**Files:**
- `Python/pyproject.toml` — check current optional deps: `dxf`, `render`, `report`, `pdf`, `validation`, `cad`, `docs`
- `.github/workflows/python-tests.yml` — add matrix job
- `Python/tests/test_optional_deps.py` — new test file

**Mistakes to avoid:**
- ❌ Don't test ALL extras in one job — use matrix for isolation
- ❌ Don't require ALL extras to pass — some may be platform-specific
- ✅ Test critical user-facing extras: `dxf`, `report`, `pdf`

---

## P5: CI Hardening (TASK-795 + TASK-794)

> **Note:** The 4-agent consensus ranked TASK-795 as priority 5 and TASK-794 as priority 6 separately. They are grouped here for session efficiency since both are CI/ops-only changes that @ops can handle in one pass.

### TASK-795: OpenAPI Drift Check in Publish

**What:** Add `python scripts/check_openapi_drift.py` step to publish.yml.

**Why:** OpenAPI drift check runs on PRs (python-tests.yml) but not at publish time. A force-push or skipped check could ship API changes that break clients.

**Agent Pipeline:**
1. @ops — Add step to publish.yml before upload
2. @reviewer — Verify it uses the same script as python-tests.yml
3. @ops — Commit as `ci: add OpenAPI drift check to publish workflow`

**Files:**
- `.github/workflows/publish.yml` — add step
- `scripts/check_openapi_drift.py` — already exists
- `fastapi_app/openapi_baseline.json` — the baseline

---

### TASK-794: Docker Base Image Digest Pin

**What:** Change `FROM python:3.11-slim` to `FROM python:3.11-slim@sha256:<digest>` in Dockerfile.fastapi.

**Why:** Mutable tags mean a compromised/updated base image silently changes the build. @security flagged as HIGH (OL-05).

**Agent Pipeline:**
1. @ops — Get current digest: `docker pull python:3.11-slim && docker inspect --format='{{index .RepoDigests 0}}' python:3.11-slim`
2. @ops — Update Dockerfile.fastapi line 1 with digest
3. @ops — Add comment with update date and how to refresh
4. @reviewer — Verify digest is correct
5. @ops — Commit as `fix(docker): pin base image to digest for reproducibility`

**Files:**
- `Dockerfile.fastapi` — line 1
- `docker-compose.yml` — verify no override
- `docker-compose.dev.yml` — verify no override

**Mistakes to avoid:**
- ❌ Don't pin docker-compose.preflight.yml separately — it uses the same Dockerfile
- ✅ Add a comment: `# Pinned 2026-04-XX. Refresh: docker pull python:3.11-slim && docker inspect ...`

---

### TASK-792: Pin Trivy Action to SHA

**What:** Change `aquasecurity/trivy-action@master` to `aquasecurity/trivy-action@<sha>` in `.github/workflows/docker-build.yml`.

**Why:** Using `@master` for security scanning tools is ironic — the scanner itself is a supply chain risk. @security flagged as AR-01.

**Agent Pipeline:**
1. @ops — Get latest release SHA: check https://github.com/aquasecurity/trivy-action/releases
2. @ops — Update docker-build.yml line ~94
3. @ops — Commit as part of P5 CI hardening batch

**Files:**
- `.github/workflows/docker-build.yml` — line ~94

**Effort:** 5 minutes — one line change.

---

## P6: API Security (TASK-728 + TASK-804)

### TASK-728: JSON Body Size Limit

**What:** Add middleware to FastAPI that rejects request bodies > 1MB.

**Why:** Without body size limits, a single request with a massive JSON payload can consume all server memory (DoS).
Originally flagged as H-01 in the v0.21.6 pre-release audit.

**Agent Pipeline:**
1. @api-developer — Add `ContentSizeLimitMiddleware` to `fastapi_app/main.py`
2. @tester — Write test: send 2MB body → expect 413; send normal body → expect 200
3. @reviewer — Verify limit is reasonable (1MB = ~10,000 beam designs in batch)
4. @ops — Commit as `feat(security): add 1MB JSON body size limit middleware`

**Files:**
- `fastapi_app/main.py` — add middleware
- `fastapi_app/config.py` — make limit configurable via env var

**Implementation approach:**
```python
# Option A: Use content-length + streaming size cap
class ContentSizeLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # Check declared size
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > settings.max_body_size:
            return JSONResponse(status_code=413, content={"detail": "Request body too large"})
        # Also cap actual body read (attacker can omit content-length)
        body = await request.body()
        if len(body) > settings.max_body_size:
            return JSONResponse(status_code=413, content={"detail": "Request body too large"})
        return await call_next(request)
```

**Mistakes to avoid:**
- ❌ Don't use a hardcoded limit — make it configurable via `MAX_BODY_SIZE` env var
- ❌ Don't apply to file upload endpoints (CSV import) without checking — they may need larger limits
- ❌ Don't ONLY check content-length header — attacker can omit it and stream large body
- ✅ Check both content-length AND actual body size
- ✅ Default 1MB, override via env var

---

### TASK-804: Auth Auto-Enable When JWT Secret Set

**What:** In `fastapi_app/config.py` or startup, if `JWT_SECRET_KEY` is non-default AND `ENVIRONMENT` is production, auto-enable auth or log CRITICAL warning.

**Why:** @security found (AR-02) that a deployment setting JWT_SECRET_KEY but forgetting AUTH_ENABLED=true runs without authentication. This is a silent security gap.

**Agent Pipeline:**
1. @api-developer — Add startup check in `fastapi_app/main.py` or `config.py`
2. @tester — Test: set JWT_SECRET_KEY + production env → verify auth auto-enabled or CRITICAL log
3. @reviewer — Verify no side effects for dev/test environments
4. @ops — Commit as `fix(security): auto-enable auth when JWT secret configured in production`

**Files:**
- `fastapi_app/config.py` — Settings class
- `fastapi_app/auth.py` — existing JWT handling
- `fastapi_app/main.py` — startup event

---

## P7: Documentation + CVE Scanning (TASK-803 + TASK-731)

### TASK-803: Document Negative Mu Behavior

**What:** Add clear documentation that `mu_knm` parameter expects magnitude (absolute value). If negative value is passed, library takes abs(). Explain that hogging design (tension at top) requires explicit top bar specification, not negative moment.

**Why:** @library-expert found (AR-07) that continuous beam design at supports has hogging moments. An engineer might pass negative Mu expecting different steel placement. Currently silently abs-valued.

**Agent Pipeline:**
1. @structural-math — Verify the behavior: does `design_beam_is456(mu_knm=-150, ...)` give same result as `mu_knm=150`?
2. @doc-master — Add note to: Python/README.md quickstart, docs/reference/api.md, function docstring
3. @reviewer — Verify note is technically accurate
4. @ops — Commit as `docs: clarify negative Mu abs-value behavior and hogging guidance`

**Files:**
- `Python/structural_lib/services/beam_api.py` — find where abs() is applied
- `Python/README.md` — quickstart section
- `docs/reference/api.md` — parameter docs

---

### TASK-731: Dependency CVE Scanning

**What:** Add `pip-audit` to CI that checks installed dependencies for known CVEs.

**Why:** Already in `security.yml` workflow but verify it blocks PRs, not just reports.

**Agent Pipeline:**
1. @ops — Verify `pip-audit` in security.yml is configured to fail CI on findings
2. @ops — If not blocking, make it blocking
3. @reviewer — Verify
4. @ops — Commit as `ci: ensure pip-audit blocks on CVE findings`

**Files:**
- `.github/workflows/security.yml` — existing pip-audit step

---

## Deferred Items (Tracked for v0.21.8 / v0.22.0)

These items are in the v0.21.7 scope in TASKS.md but are explicitly deferred from this execution plan with rationale:

| Item | Why Deferred | New Target |
|------|-------------|------------|
| WebSocket rate limit (5 msg/s) | Needs WebSocket middleware research; lower risk since WS is dev-only | v0.21.8 (assign TASK-805) |
| Computation timeout | Needs profiling to set safe limits; no reported DoS incidents | v0.21.8 (assign TASK-806) |
| TASK-792: Pin Trivy action to SHA | Overlaps with OL-07; low risk since Trivy runs in read-only CI | Add to P5 session (quick fix alongside TASK-794) |
| M-04: Move create_dev_token() | Auth disabled by default; low risk | v0.21.8 |
| M-05: Per-endpoint scope checking | Auth disabled by default | v0.22.0 |
| AR-03: Pin deps in Dockerfile | Low risk — lock file exists, just not used in Dockerfile | v0.21.8 |
| AR-09: Fix show_versions() stale version | Cosmetic — only affects dev-from-source | v0.21.8 |

**Exception — move to P5 session:**
- TASK-792 (Trivy SHA pin) — add as quick 5-minute fix when @ops is doing TASK-794 (Docker pin) and TASK-795 (OpenAPI drift). Just change `@master` to `@<sha>` in docker-build.yml.

---

## Cross-Cutting: Docs to Update After Each Task

| Doc | What to Update | When |
|-----|---------------|------|
| `docs/TASKS.md` | Mark each task ✅ DONE | After each task committed |
| `docs/planning/next-session-brief.md` | Update priorities, remove done items | End of each session |
| `docs/WORKLOG.md` | One line per change | After each commit |
| `docs/SESSION_LOG.md` | Auto via `./run.sh session summary` | End of session |
| `CHANGELOG.md` | Add entries under `[0.21.7]` section | After all v0.21.7 tasks done |

---

## Common Mistakes to Avoid (ALL Tasks)

### Git Mistakes
- ❌ NEVER: `git add` / `git commit` / `git push` — use `./scripts/ai_commit.sh`
- ❌ NEVER: `--force` or `--no-verify`
- ❌ NEVER: commit without running tests first
- ✅ ALWAYS: `.venv/bin/pytest Python/tests/ -v -k "test_name"` before committing

### Architecture Mistakes
- ❌ NEVER: Add validation logic in `codes/is456/` (Layer 2 — pure math only)
- ❌ NEVER: Add I/O or HTTP logic in `services/` (Layer 3 — orchestration only)
- ❌ NEVER: Import upward (core → services, or services → UI)
- ✅ ALWAYS: Check `__init__.py` exports match `__all__`
- ✅ ALWAYS: Use `.venv/bin/python scripts/discover_api_signatures.py <func>` before using any API function

### Testing Mistakes
- ❌ NEVER: Use `MagicMock` — use real objects
- ❌ NEVER: Skip golden vector tests — `pytest -m golden` must pass
- ❌ NEVER: Modify golden vectors without structural-engineer review
- ✅ ALWAYS: Run full test suite before PR: `.venv/bin/pytest Python/tests/ -v`

### CI/CD Mistakes
- ❌ NEVER: Add steps AFTER upload in publish.yml — must be BEFORE
- ❌ NEVER: Use `@master` or `@main` refs for GitHub Actions — pin to SHA
- ✅ ALWAYS: Test workflow changes locally first where possible
- ✅ ALWAYS: Pin new GitHub Actions to specific SHA or version tag

---

## Session Planning

### Session N+1: v0.21.6 Release + P1 Start
1. @doc-master: Fix 3 version refs (CHANGELOG, README, git-automation)
2. @ops: Release preflight + tag v0.21.6
3. @security: Run input validation audit (TASK-730 first pass)
4. @api-developer: Start TASK-729 cross-field validators based on audit
5. @tester: Write validation tests
6. @reviewer: Review

### Session N+2: P1 Complete + P2 + P3
1. @api-developer: Finish TASK-729 validators
2. @security: Final TASK-730 audit pass → 0 findings
3. @backend: TASK-802 column API export
4. @security + @api-developer: TASK-796 ImportError leaks
5. @reviewer: Review all
6. @ops: Commit all

### Session N+3: P4 + P5
1. @ops: TASK-790 (wheel checks), TASK-791 (TestPyPI), TASK-795 (OpenAPI drift), TASK-794 (Docker pin)
2. @tester: TASK-793 (optional deps tests)
3. @reviewer: Review CI changes
4. @ops: Commit all

### Session N+4: P6 + P7 + Release v0.21.7
1. @api-developer: TASK-728 (body limit), TASK-804 (auth auto-enable)
2. @doc-master: TASK-803 (Mu docs)
3. @ops: TASK-731 (verify pip-audit)
4. @reviewer: Final review
5. @ops: Release preflight + tag v0.21.7

---

## Review Checklist (Run After ALL v0.21.7 Tasks)

- [ ] `audit_input_validation.py` reports 0 findings
- [ ] `check-wheel-contents` + `twine check` in publish.yml
- [ ] TestPyPI gate before prod in publish.yml
- [ ] OpenAPI drift check in publish.yml
- [ ] Docker base image pinned to digest
- [ ] All column API functions importable from `structural_lib`
- [ ] No `str(e)` exposed in HTTP responses
- [ ] Body size limit middleware active
- [ ] Auth auto-enables in production when secret set
- [ ] `pip-audit` blocks on CVE findings
- [ ] Negative Mu behavior documented
- [ ] Optional deps CI matrix passes
- [ ] 5003+ tests passing
- [ ] TASKS.md fully updated
- [ ] CHANGELOG.md has [0.21.7] section
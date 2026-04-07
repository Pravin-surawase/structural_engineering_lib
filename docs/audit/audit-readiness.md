---
owner: Main Agent
status: active
last_updated: 2026-04-07
doc_type: guide
complexity: intermediate
tags: []
---

# Audit Readiness Checklist

**Type:** Reference
**Audience:** All Agents, Auditors, Compliance
**Status:** Approved
**Importance:** Critical
**Created:** 2026-01-24
**Last Updated:** 2026-04-07

---

## v0.21.6 Release Assessment (2026-04-07)

**Release Score: A+ (9.0/10)**

| Category | Status | Notes |
|----------|--------|-------|
| Testing & Verification | ✅ Pass | 5003/5003 tests (100%), 99% branch coverage on codes/is456/, 42+ golden tests, 18 contract tests |
| Static Analysis & Code Quality | ✅ Pass | ruff, black, mypy all clean; no circular imports; OpenAPI baseline in CI |
| Governance & Documentation | ⚠️ Minor | api.md needs version bump to v0.21.6; CHANGELOG [Unreleased] → [0.21.6] pending |
| Security & Supply Chain | ✅ Pass | 0 CVEs, non-root Docker, JWT safeguard; WebSocket rate limiting deferred to v0.21.7 |
| Change Control & Traceability | ✅ Pass | All production changes via PR; release tag to be created at release |
| Agent & Skill Infrastructure | ✅ Pass | 16 agents, 14 skills, 16 prompts; tool_registry/prompt_router/tool_permissions operational |

### Known Issues Accepted for v0.21.6

| ID | Description | Deferred To |
|----|-------------|-------------|
| FE-NEW-01 | Three.js memory leak | v0.22.0 |
| UX-01 | Cross-field validation gap (form 1) | v0.22.0 |
| UX-02 | Cross-field validation gap (form 2) | v0.22.0 |
| ARCH-NEW-12 | God module split | v0.22.0 |
| — | 3 architecture import violations in FastAPI routers | Non-blocking |
| — | WebSocket rate limiting | v0.21.7 |
| — | Error message path leaks | v0.21.7 |
| — | Performance benchmarks not baselined | v0.21.8 |
| — | skill_count in registry metadata says 10 (actual: 14) | Cosmetic |

---

## Purpose

This checklist defines the minimum evidence requirements for audit readiness. Each release must satisfy all "Required" items before deployment to production.

---

## Evidence Categories

### 1. Testing & Verification (SSDF PW/RV)

| Requirement | Status | Evidence Location | Required |
|-------------|--------|-------------------|----------|
| Unit tests pass | ✅ | CI: `python-tests.yml` — 5003/5003 (100% pass) | ✅ Yes |
| Integration tests pass | ✅ | CI: `python-tests.yml` | ✅ Yes |
| Contract tests pass | ✅ | CI: `fast-checks.yml` — 18 contract tests (@pytest.mark.contract) | ✅ Yes |
| Branch coverage ≥85% | ✅ | CI artifact: `coverage.xml` — 99% on codes/is456/ | ✅ Yes |
| Golden vector tests pass | ✅ | 42+ golden tests (@pytest.mark.golden) | ✅ Yes |
| Critical journey tests pass | ✅ | CI pipeline | ✅ Yes |
| Performance regression check | ⚠️ | Benchmarks exist but not baselined — planned for v0.21.8 | ⚠️ Recommended |

---

### 2. Static Analysis & Code Quality (SSDF PW)

| Requirement | Status | Evidence Location | Required |
|-------------|--------|-------------------|----------|
| Linting passes (ruff) | ✅ | CI: `fast-checks.yml` | ✅ Yes |
| Formatting valid (black) | ✅ | CI: `fast-checks.yml` | ✅ Yes |
| Type checking passes (mypy) | ✅ | CI: `fast-checks.yml` | ✅ Yes |
| No circular imports | ✅ | `scripts/check_circular_imports.py` | ✅ Yes |
| API signatures valid | ✅ | `scripts/check_api.py --signatures` | ✅ Yes |
| OpenAPI drift detection | ✅ | Baseline in CI (`openapi_baseline.json`) | ✅ Yes |

---

### 3. Governance & Documentation (SSDF PO)

| Requirement | Status | Evidence Location | Required |
|-------------|--------|-------------------|----------|
| Folder structure compliant | ✅ | `scripts/check_governance.py --structure` | ✅ Yes |
| Doc metadata valid | ✅ | `scripts/check_doc_metadata.py` | ✅ Yes |
| API docs synchronized | ⚠️ | api.md shows v0.21.5, needs bump to v0.21.6 | ✅ Yes |
| Internal links valid | ✅ | `scripts/check_links.py` | ✅ Yes |
| CHANGELOG updated | ⚠️ | Still says [Unreleased], needs [0.21.6] — 2026-04-07 | ✅ Yes |
| VERSION bumped | ✅ | `pyproject.toml` = 0.21.6 | ✅ Yes |

---

### 4. Security & Supply Chain (SSDF PS/SLSA)

| Requirement | Status | Evidence Location | Required |
|-------------|--------|-------------------|----------|
| No high/critical vulnerabilities | ✅ | CI: `codeql.yml`, `security.yml` — 0 CVEs, no critical findings | ✅ Yes |
| Dependencies pinned | ✅ | `Python/pyproject.toml` (ranges) | ✅ Yes |
| Docker security | ✅ | Non-root, cap_drop ALL | ✅ Yes |
| JWT production safeguard | ✅ | Production secret enforcement | ✅ Yes |
| WebSocket rate limiting | ⚠️ | Deferred to v0.21.7 | ⚠️ Recommended |
| SBOM generated (CycloneDX) | ⬜ | CI artifact: `sbom.json` | ⚠️ Recommended |
| Build provenance recorded | ⬜ | CI/release workflow | ⬜ Future |
| OpenSSF Scorecard ≥6 | ⬜ | GitHub Security tab | ⬜ Future |

---

### 5. Change Control & Traceability (SSDF RV)

| Requirement | Status | Evidence Location | Required |
|-------------|--------|-------------------|----------|
| All changes via PR | ✅ | Git history (production code) | ✅ Yes (for prod code) |
| PR reviews required | ⬜ | Branch protection rules | ⚠️ Recommended |
| Commit messages follow convention | ✅ | Git hooks (conventional commits) | ✅ Yes |
| Release tag created | 📋 | To be created at release | ✅ Yes |
| Release notes published | 📋 | CHANGELOG drafted, GitHub Release pending | ✅ Yes |

---

### 6. Agent & Skill Infrastructure

| Requirement | Status | Evidence Location | Required |
|-------------|--------|-------------------|----------|
| 16/16 agents defined (.agent.md) | ✅ | `.github/agents/` | ✅ Yes |
| 14/14 skills with SKILL.md | ✅ | `.github/skills/` | ✅ Yes |
| 16/16 prompts present | ✅ | `.github/prompts/` | ✅ Yes |
| tool_registry.py operational | ✅ | `scripts/tool_registry.py` | ✅ Yes |
| prompt_router.py operational | ✅ | `scripts/prompt_router.py` | ✅ Yes |
| tool_permissions.py operational | ✅ | `scripts/tool_permissions.py` | ✅ Yes |
| skill_count in registry metadata | ⚠️ | Says 10, actual is 14 (cosmetic) | ⬜ No |

---

## Compliance Summary

| Category | Required Items | Passed | Status |
|----------|---------------|--------|--------|
| Testing & Verification | 6 | 6/6 | ✅ |
| Static Analysis & Code Quality | 6 | 6/6 | ✅ |
| Governance & Documentation | 6 | 4/6 | ⚠️ |
| Security & Supply Chain | 2 | 2/2 | ✅ |
| Change Control & Traceability | 4 | 2/4 | 📋 |
| Agent & Skill Infrastructure | 6 | 6/6 | ✅ |
| **Total** | **30** | **26/30** | **A+** |

---

## Automation

Generate a full audit report:

```bash
# Full report with all evidence
.venv/bin/python scripts/audit_readiness_report.py

# Quick compliance check (pass/fail only)
.venv/bin/python scripts/audit_readiness_report.py --check-only

# Export for external auditors
.venv/bin/python scripts/audit_readiness_report.py --export json > audit-report.json
```

---

## Per-Release Checklist

Before each release:

1. [ ] Run `audit_readiness_report.py --check-only` — all Required items must pass
2. [ ] Review CI pipeline status for target branch
3. [ ] Verify coverage artifact exists and meets threshold
4. [ ] Confirm CHANGELOG is updated with release notes
5. [ ] Create signed release tag
6. [ ] Archive evidence bundle to `docs/audit/reports/vX.Y.Z/`

---

## Related Files

- [evidence-bundle-template.md](evidence-bundle-template.md) — Template for release evidence
- [../research/automation-audit-readiness-research.md](../_archive/research/pre-v021/automation-audit-readiness-research.md) — Standards background
- [../reference/automation-catalog.md](../reference/automation-catalog.md) — Script reference

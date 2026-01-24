# Audit Readiness Checklist

**Type:** Reference
**Audience:** All Agents, Auditors, Compliance
**Status:** Approved
**Importance:** Critical
**Created:** 2026-01-24
**Last Updated:** 2026-01-24

---

## Purpose

This checklist defines the minimum evidence requirements for audit readiness. Each release must satisfy all "Required" items before deployment to production.

---

## Evidence Categories

### 1. Testing & Verification (SSDF PW/RV)

| Requirement | Status | Evidence Location | Required |
|-------------|--------|-------------------|----------|
| Unit tests pass | ⬜ | CI: `python-tests.yml` | ✅ Yes |
| Integration tests pass | ⬜ | CI: `python-tests.yml` | ✅ Yes |
| Contract tests pass | ⬜ | CI: `fast-checks.yml` | ✅ Yes |
| Branch coverage ≥85% | ⬜ | CI artifact: `coverage.xml` | ✅ Yes |
| AppTest smoke tests pass | ⬜ | CI: `streamlit-validation.yml` | ✅ Yes |
| Critical journey tests pass | ⬜ | CI: `streamlit-validation.yml` | ✅ Yes |
| Performance regression check | ⬜ | `scripts/check_performance_issues.py` | ⚠️ Recommended |

---

### 2. Static Analysis & Code Quality (SSDF PW)

| Requirement | Status | Evidence Location | Required |
|-------------|--------|-------------------|----------|
| Linting passes (ruff) | ⬜ | CI: `fast-checks.yml` | ✅ Yes |
| Formatting valid (black) | ⬜ | CI: `fast-checks.yml` | ✅ Yes |
| Type checking passes (mypy) | ⬜ | CI: `fast-checks.yml` | ✅ Yes |
| No circular imports | ⬜ | `scripts/check_circular_imports.py` | ✅ Yes |
| Type annotation rate ≥50% | ⬜ | `scripts/check_type_annotations.py` | ✅ Yes |
| No Streamlit AST issues | ⬜ | `scripts/check_streamlit_issues.py` | ✅ Yes |
| No fragment API violations | ⬜ | `scripts/check_fragment_violations.py` | ✅ Yes |
| API signatures valid | ⬜ | `scripts/check_api_signatures.py` | ✅ Yes |

---

### 3. Governance & Documentation (SSDF PO)

| Requirement | Status | Evidence Location | Required |
|-------------|--------|-------------------|----------|
| Folder structure compliant | ⬜ | `scripts/validate_folder_structure.py` | ✅ Yes |
| Root file count ≤10 | ⬜ | `scripts/check_root_file_count.sh` | ✅ Yes |
| Doc metadata valid | ⬜ | `scripts/check_doc_metadata.py` | ✅ Yes |
| API docs synchronized | ⬜ | `scripts/check_api_docs_sync.py` | ✅ Yes |
| Internal links valid | ⬜ | `scripts/check_links.py` | ✅ Yes |
| CHANGELOG updated | ⬜ | Manual review | ✅ Yes |
| VERSION bumped | ⬜ | `Python/structural_lib/__init__.py` | ✅ Yes |

---

### 4. Security & Supply Chain (SSDF PS/SLSA)

| Requirement | Status | Evidence Location | Required |
|-------------|--------|-------------------|----------|
| No high/critical vulnerabilities | ⬜ | CI: `codeql.yml`, `security.yml` | ✅ Yes |
| Dependencies pinned | ⬜ | `Python/pyproject.toml` | ✅ Yes |
| SBOM generated (CycloneDX) | ⬜ | CI artifact: `sbom.json` | ⚠️ Recommended |
| Build provenance recorded | ⬜ | CI/release workflow | ⬜ Future |
| OpenSSF Scorecard ≥6 | ⬜ | GitHub Security tab | ⬜ Future |

---

### 5. Change Control & Traceability (SSDF RV)

| Requirement | Status | Evidence Location | Required |
|-------------|--------|-------------------|----------|
| All changes via PR | ⬜ | Git history | ✅ Yes (for prod code) |
| PR reviews required | ⬜ | Branch protection rules | ⚠️ Recommended |
| Commit messages follow convention | ⬜ | Git hooks | ✅ Yes |
| Release tag created | ⬜ | GitHub Releases | ✅ Yes |
| Release notes published | ⬜ | `CHANGELOG.md` + GitHub Release | ✅ Yes |

---

## Compliance Summary

| Category | Required Items | Recommended Items |
|----------|---------------|-------------------|
| Testing & Verification | 6 | 1 |
| Static Analysis | 8 | 0 |
| Governance | 7 | 0 |
| Security | 2 | 1 (+2 Future) |
| Change Control | 4 | 1 |
| **Total** | **27** | **3** |

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
- [../research/automation-audit-readiness-research.md](../research/automation-audit-readiness-research.md) — Standards background
- [../reference/automation-catalog.md](../reference/automation-catalog.md) — Script reference

# v0.17.0 Implementation Guide

**Type:** Guide
**Audience:** Developers
**Status:** Planning
**Importance:** High
**Created:** 2026-01-09
**Last Updated:** 2026-01-13

---

**Version:** 1.0.0
**Target Release:** 2026-01-15
**Theme:** Security + Traceability Foundation

---

## Executive Summary

v0.17.0 transforms structural_engineering_lib from a working prototype into a **professional-grade engineering tool** by establishing:
- **Security baseline** (input validation, dependency scanning)
- **Code traceability** (IS 456 clause database)
- **Professional clarity** (liability framework)
- **Interactive testing** (developer UI)

**Philosophy:** Build foundation first (low-risk), then add high-value features.

---

## Release Phases

### Phase 1: Low-Risk Foundation (Do First - Week 1)

**Why First?** Non-breaking changes that build trust and infrastructure.

#### TASK-272: Code Clause Database (4-6 hours)
**Owner:** ARCHITECT
**Priority:** 🔴 CRITICAL
**Blockers:** None

**Deliverables:**
- JSON clause database: `codes/is456_clauses.json`
- Clause reference decorator: `@clause("26.5.1.1")`
- Traceability API: `get_clause_refs(function_name)`

**Acceptance Criteria:**
- [ ] JSON database with 50+ IS 456 clauses (focus on beam design)
- [ ] Decorator integrates with existing functions
- [ ] Zero breaking changes to public API
- [ ] 100% backward compatible
- [ ] CLI tool: `python -m structural_lib.codes.is456 --clause 26.5.1.1`

**Files Changed:**
```
codes/is456_clauses.json         (new, ~200 lines)
codes/is456/__init__.py           (add decorator)
codes/is456/flexure.py            (add @clause decorators)
codes/is456/shear.py              (add @clause decorators)
tests/test_clause_database.py     (new, 20 tests)
```

**Research:** `docs/research/code-clause-database-architecture.md`

---

#### TASK-274: Security Hardening Baseline (2-3 hours)
**Owner:** DEVOPS
**Priority:** 🔴 HIGH
**Blockers:** None

**Deliverables:**
- Input validation (pydantic models)
- Dependency scanning (safety check in CI)
- Security policy: `SECURITY.md`

**Acceptance Criteria:**
- [ ] All public API functions validate inputs with Pydantic
- [ ] CI runs `safety check` on every PR
- [ ] SECURITY.md with vulnerability reporting process
- [ ] No new security warnings from bandit

**Files Changed:**
```
.github/workflows/security.yml    (new)
SECURITY.md                       (new, ~100 lines)
codes/is456/flexure.py            (add input validation)
pyproject.toml                    (add safety to dev-deps)
```

**Research:** `docs/research/security-best-practices.md`

---

#### TASK-275: Professional Liability Framework (2-3 hours)
**Owner:** LEGAL
**Priority:** 🟠 MEDIUM
**Blockers:** None

**Deliverables:**
- LICENSE_ENGINEERING.md (already exists, update)
- Disclaimer templates for calculation reports
- Certification guidance

**Acceptance Criteria:**
- [ ] Clear scope: "Design aid, not substitute for engineer judgment"
- [ ] Disclaimer templates in 3 formats (HTML, PDF, Excel)
- [ ] Certification guidance for structural engineers
- [ ] Legal review complete (if available)

**Files Changed:**
```
LICENSE_ENGINEERING.md            (update, ~50 lines)
templates/disclaimer.html         (new)
templates/disclaimer.txt          (new)
docs/legal/certification-guidance.md  (new, ~200 lines)
```

**Research:** `docs/research/professional-liability-disclaimers.md`

---

### Phase 2: Medium-Risk Traceability (Week 2)

**Why Second?** Depends on clause database (TASK-272), adds audit capability.

#### TASK-245: Verification & Audit Trail (3-4 hours)
**Owner:** DEV
**Priority:** 🔴 HIGH
**Depends On:** TASK-272 (clause database must exist)

**Deliverables:**
- SHA-256 calculation signatures
- Immutable audit records (JSON format)
- CLI verification tool

**Acceptance Criteria:**
- [ ] Every calculation returns immutable signature
- [ ] Signature includes: inputs, outputs, version, timestamp, clauses
- [ ] CLI tool verifies signatures: `python -m structural_lib verify <file>`
- [ ] 100% reproducible (same inputs → same signature)

**Files Changed:**
```
codes/is456/audit.py              (new, ~150 lines)
tests/test_audit_trail.py         (new, 15 tests)
cli/verify.py                     (new, ~80 lines)
```

**Research:** `docs/research/verification-audit-trail.md`

---

### Phase 3: High-Value Developer UX (Week 3)

**Why Last?** Complex, high-value feature that needs stable foundation.

#### TASK-273: Interactive Testing UI (1 day)
**Owner:** UI_DEV
**Priority:** 🟡 MEDIUM
**Blockers:** None (can run in parallel with Phase 1-2)

**Deliverables:**
- Streamlit app with interactive testing
- Beam design dashboard
- Visual comparison of design approaches

**Acceptance Criteria:**
- [ ] Streamlit app runs locally: `streamlit run app.py`
- [ ] Interactive parameter sliders (b, d, fck, fy)
- [ ] Real-time calculation display
- [ ] Visual comparison: hand calc vs library output
- [ ] Export results as PDF/JSON

**Files Changed:**
```
streamlit_app/pages/beam_design.py    (update, ~200 lines)
streamlit_app/components/results.py   (new, ~150 lines)
streamlit_app/utils/export.py         (new, ~100 lines)
tests/test_streamlit_app.py           (update, 10 tests)
```

**Research:** `docs/research/interactive-testing-ui.md`

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Security** | 0 critical vulnerabilities | `safety check` + bandit |
| **Traceability** | 50+ clause refs | Count @clause decorators |
| **Clarity** | Legal docs complete | LICENSE_ENGINEERING + templates |
| **UX** | Streamlit app working | Manual testing |
| **Breaking Changes** | 0 | Contract tests pass |
| **Test Coverage** | 86%+ | pytest-cov |

---

## Risk Management

### Low Risk
- ✅ TASK-272 (clause DB): Non-breaking, additive only
- ✅ TASK-274 (security): CI addition, no API changes
- ✅ TASK-275 (liability): Documentation only

### Medium Risk
- ⚠️ TASK-245 (audit trail): New return types, but backward compatible
- **Mitigation:** Make signature optional, default off

### High Risk
- 🔴 TASK-273 (Streamlit): Complex UI, many dependencies
- **Mitigation:** Isolate in streamlit_app/, doesn't affect core library

---

## Testing Strategy

### Unit Tests
- ✅ All new functions have tests
- ✅ Edge cases covered (invalid inputs, boundary conditions)
- ✅ Regression tests for existing behavior

### Integration Tests
- ✅ Clause database queries work end-to-end
- ✅ Audit signatures verify correctly
- ✅ Security validation catches bad inputs

### Manual Testing
- ✅ Streamlit app runs without errors
- ✅ All interactive features work
- ✅ Export functions generate valid files

---

## Documentation Updates

| Doc | Update |
|-----|--------|
| README.md | Add v0.17.0 highlights, security badges |
| CHANGELOG.md | Add v0.17.0 entry with all changes |
| releases.md | Add v0.17.0 locked entry |
| API docs | Add clause database API reference |
| Security docs | Add SECURITY.md to root |

---

## Dependencies

### New Dependencies
```toml
[tool.poetry.dependencies]
pydantic = "^2.5.0"  # Input validation

[tool.poetry.dev-dependencies]
safety = "^2.3.0"  # Dependency scanning
```

### No Breaking Changes
- All existing dependencies remain
- No version bumps for breaking changes
- Pydantic is additive (validates but doesn't break)

---

## Timeline

| Week | Phase | Tasks | Estimate |
|------|-------|-------|----------|
| Week 1 | Foundation | TASK-272, 274, 275 | 8-11 hours |
| Week 2 | Traceability | TASK-245 | 3-4 hours |
| Week 3 | Developer UX | TASK-273 | 1 day (8 hours) |
| **Total** | | **5 tasks** | **19-23 hours** |

**Parallelization:** TASK-273 can run in parallel with Phase 1-2 (different agents).

---

## Pre-Release Checklist

**Before tagging v0.17.0:**
- [ ] All 5 tasks complete
- [ ] All tests passing (2400+ tests expected)
- [ ] Security scan clean (0 critical vulns)
- [ ] Documentation updated
- [ ] CHANGELOG.md has v0.17.0 entry
- [ ] Version bumped in pyproject.toml
- [ ] All links valid (782+ internal links)
- [ ] Pre-commit hooks passing (23/23)

**Release Command:**
```bash
python scripts/release.py --version 0.17.0 --changelog-entry "Security + Traceability Foundation"
```

---

## Post-Release

### Verification
1. ✅ PyPI publish successful
2. ✅ GitHub release created
3. ✅ Documentation updated on GitHub Pages

### Announcement
- Update README with v0.17.0 highlights
- Post to relevant forums/communities (if applicable)
- Update project status: "Production-ready for professional use"

### Next Steps (v0.18.0)
- Input flexibility (BeamInput dataclasses)
- Calculation report generation (PDF/HTML)
- Engineering testing strategies

---

## Notes for Implementers

### Start Here
1. Read this guide completely
2. Review all research docs:
   - `docs/research/code-clause-database-architecture.md`
   - `docs/research/security-best-practices.md`
   - `docs/research/professional-liability-disclaimers.md`
   - `docs/research/verification-audit-trail.md`
3. Check `docs/TASKS.md` for current status
4. Use PR workflow for all production code changes

### Agent Assignment
| Task | Suggested Agent | Expertise Needed |
|------|----------------|------------------|
| TASK-272 | ARCHITECT | JSON, decorators, API design |
| TASK-274 | DEVOPS | CI, security tools, pydantic |
| TASK-275 | LEGAL/DOCS | Legal writing, disclaimers |
| TASK-245 | DEV | Cryptography, data structures |
| TASK-273 | UI_DEV | Streamlit, data visualization |

### Key Principles
- **Backward compatibility:** No breaking changes
- **Security first:** Validate all inputs
- **Traceability:** Every calculation cites code clause
- **Professional clarity:** Scope and limitations clear
- **Developer experience:** Interactive testing is fun

---

**Last Updated:** 2026-01-11
**Next Review:** After Phase 1 complete (TASK-272/274/275)

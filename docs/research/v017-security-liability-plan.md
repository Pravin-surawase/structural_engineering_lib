# v0.17.0 Security & Liability Implementation Plan

**Type:** Research
**Audience:** All Agents
**Status:** Draft
**Importance:** High
**Version:** 0.16.6
**Created:** 2026-01-11
**Last Updated:** 2026-01-11
**Related Tasks:** TASK-274, TASK-275, TASK-272

---

## Executive Summary

This document provides the research and execution plan for the three priority tasks in v0.17.0:

| Task | Description | Priority | Effort | Current State |
|------|-------------|----------|--------|---------------|
| **TASK-274** | Security Hardening Baseline | 🔴 HIGH | 2-3h | Partial (CodeQL, bandit exist) |
| **TASK-275** | Professional Liability Framework | 🔴 HIGH | 2-3h | Good (LICENSE_ENGINEERING.md exists) |
| **TASK-272** | Code Clause Database | 🔴 HIGH | 4-6h | Foundation (clause param in validation.py) |

**Recommended Order:** TASK-274 → TASK-275 → TASK-272 (security first, quick wins, then foundation)

---

## 1. TASK-274: Security Hardening Baseline

### Current State Assessment

**Existing Security Infrastructure:**
| Component | Status | Notes |
|-----------|--------|-------|
| CodeQL | ✅ Active | Weekly schedule, PR checks |
| Bandit | ✅ Active | In pre-commit, dev deps |
| Dependabot | ❌ Missing | No dependency updates |
| pip-audit | ❌ Missing | No vulnerability scanning |
| SBOM | ❌ Missing | No software bill of materials |
| Input validation | ⚠️ Partial | validation.py exists, needs audit |

### Implementation Plan

**Phase 1: Dependency Scanning (30 min)**
```yaml
# Add to nightly.yml or new security.yml
- name: Audit dependencies
  run: |
    pip install pip-audit
    pip-audit --format json --output pip-audit.json
```

**Phase 2: Dependabot Configuration (15 min)**
```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/Python"
    schedule:
      interval: "weekly"
    groups:
      dev-dependencies:
        patterns: ["*"]
```

**Phase 3: SBOM Generation (30 min)**
```yaml
# In release workflow
- name: Generate SBOM
  run: |
    pip install cyclonedx-bom
    cyclonedx-py environment > sbom.json
```

**Phase 4: Input Validation Audit Script (1h)**
```python
# scripts/audit_input_validation.py
# Scan all design functions for input validation coverage
```

### Deliverables
1. `.github/dependabot.yml` - Automated dependency updates
2. Updated `nightly.yml` - pip-audit integration
3. Updated `publish.yml` - SBOM generation
4. `scripts/audit_input_validation.py` - Validation coverage report
5. `docs/security/security-policy.md` - Security practices documentation

---

## 2. TASK-275: Professional Liability Framework

### Current State Assessment

**Existing Infrastructure:**
| Document | Status | Quality |
|----------|--------|---------|
| LICENSE | ✅ Exists | MIT license |
| LICENSE_ENGINEERING.md | ✅ Exists | Excellent (46 lines) |
| docs/legal/usage-guidelines.md | ✅ Exists | Good (44 lines) |
| README disclaimers | ⚠️ Partial | Needs enhancement |
| API docstring disclaimers | ❌ Missing | Add to public API |

### Implementation Plan

**Phase 1: Enhance README.md (30 min)**
- Add prominent engineering disclaimer section
- Link to LICENSE_ENGINEERING.md

**Phase 2: API Docstring Updates (1h)**
```python
# Add to api.py and key public functions
"""
.. warning:: Engineering Disclaimer
   This library is for use by licensed engineers only.
   See LICENSE_ENGINEERING.md for full disclaimer.
"""
```

**Phase 3: Certification Templates (1h)**
```
docs/legal/
├── certification-template.md      # PE certification guidance
├── verification-checklist.md      # Independent verification steps
└── jurisdiction-notes.md          # Multi-jurisdiction guidance
```

### Deliverables
1. Updated README.md with disclaimer section
2. API docstrings with engineering warnings
3. `docs/legal/certification-template.md`
4. `docs/legal/verification-checklist.md`
5. CHANGELOG entry

---

## 3. TASK-272: Code Clause Database

### Current State Assessment

**Existing Clause References:**
- `validation.py`: Uses `clause` parameter in ValidationResult (e.g., "26.4", "26.5.1.1")
- References are inline strings, not from centralized database
- ~15 unique clause references found in codebase

### Implementation Plan

**Phase 1: Clause Database Schema (1h)**
```python
# structural_lib/codes/is456/clauses.py
CLAUSE_DB = {
    "26.4": {
        "title": "Nominal Cover",
        "section": "26.4",
        "text": "The nominal cover to reinforcement shall be...",
        "category": "detailing"
    },
    # ... more clauses
}
```

**Phase 2: @clause Decorator (1h)**
```python
def clause(clause_ref: str):
    """Decorator to mark functions with IS 456 clause reference."""
    def decorator(func):
        func._clause_ref = clause_ref
        return func
    return decorator

@clause("G-1.1")
def calculate_mu_lim(...):
    ...
```

**Phase 3: Traceability Report (2h)**
```python
# scripts/generate_clause_report.py
# Scan all @clause decorators and generate traceability matrix
```

### Deliverables
1. `structural_lib/codes/is456/clauses.py` - Clause database
2. `structural_lib/core/traceability.py` - @clause decorator
3. Updated design functions with @clause decorators
4. `scripts/generate_clause_report.py` - Traceability automation
5. `docs/reference/clause-matrix.md` - Generated traceability matrix

---

## Execution Strategy

### Priority Order

1. **TASK-274 (Security)** - Highest impact, lowest friction
   - Adds immediate security value
   - Dependabot prevents future vulnerabilities
   - pip-audit catches known CVEs
   - ~2 hours to complete

2. **TASK-275 (Liability)** - Quick wins, builds trust
   - Most infrastructure already exists
   - Templates are documentation-only
   - ~2 hours to complete

3. **TASK-272 (Clauses)** - Foundation for traceability
   - Enables future audit trail features
   - Requires more careful design
   - ~4-6 hours to complete

### Automation Opportunities

| Automation | Purpose | Reuse Value |
|------------|---------|-------------|
| `audit_input_validation.py` | Check validation coverage | High (run in CI) |
| `generate_clause_report.py` | Generate traceability matrix | High (release docs) |
| Dependabot | Auto-update dependencies | Permanent (set and forget) |
| SBOM in releases | Supply chain transparency | High (enterprise requirement) |

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Dependency vulnerabilities | 0 critical/high | pip-audit output |
| Input validation coverage | 100% public API | audit script |
| Clause coverage | 80%+ design functions | clause report |
| Documentation completeness | All templates created | file count |

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| pip-audit false positives | Use --ignore-vuln for accepted risks |
| Dependabot noise | Group updates, weekly schedule |
| Clause decorator overhead | Keep decorator lightweight |
| Breaking changes | All changes are additive |

---

## References

- [OWASP Dependency Check](https://owasp.org/www-project-dependency-check/)
- [CycloneDX SBOM Standard](https://cyclonedx.org/)
- [IS 456:2000 Standard](https://law.resource.org/pub/in/bis/S03/is.456.2000.pdf)

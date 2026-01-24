# Automation Gap Analysis & Manual Work Opportunities

**Type:** Research
**Audience:** All Agents, Maintainers
**Status:** Draft
**Importance:** High
**Created:** 2026-01-24
**Last Updated:** 2026-01-24
**Related Tasks:** TASK-AUTO-001
**Archive Condition:** Archive when all HIGH priority items automated

---

## Executive Summary

This research identifies manual workflows that can be automated to improve development velocity, reduce errors, and maintain quality standards. Analysis covers both existing automation gaps and opportunities for new automation.

### Key Findings

| Category | Manual Tasks | Automation Potential | Effort |
|----------|-------------|---------------------|--------|
| FastAPI development | 8 tasks | High | 4-6 hrs |
| Testing | 5 tasks | High | 3-4 hrs |
| Documentation | 6 tasks | Medium | 2-3 hrs |
| Release management | 4 tasks | Medium | 2-3 hrs |
| Code review | 3 tasks | Low | 4-6 hrs |

**Total automation opportunity:** 26 manual tasks → ~15-22 hours of scripting = ROI in 2-3 weeks

---

## 1. Current Automation Inventory

### Scripts by Tier

| Tier | Count | Purpose | Usage |
|------|-------|---------|-------|
| Tier 0 (Critical) | 5 | Primary daily scripts | 90%+ of operations |
| Git Workflow | 17 | Git operations | High frequency |
| Code Validation | 22 | Quality enforcement | Every commit |
| Documentation | 18 | Doc maintenance | As needed |
| Session Management | 12 | Agent lifecycle | Every session |
| Project Structure | 14 | Governance | Pre-commit |
| Testing | 8 | Test automation | CI/local |
| Release | 6 | Versioning | Monthly |
| **Total** | **152** | | |

### Automation Coverage by Area

| Area | Coverage | Scripts | Gap |
|------|----------|---------|-----|
| Python core | 95% | 40+ | Minor |
| Streamlit | 85% | 15+ | Medium |
| FastAPI | 20% | 2 | **Critical** |
| VBA/Excel | 30% | 4 | High |
| Documentation | 80% | 18 | Low |
| Git workflow | 98% | 17 | Minimal |

---

## 2. Manual Tasks Identified

### 2.1 FastAPI Development (High Priority)

| # | Manual Task | Frequency | Time/Occurrence | Automation Script |
|---|-------------|-----------|-----------------|-------------------|
| 1 | Update OpenAPI docs after API change | Every API PR | 15 min | `sync_openapi_to_docs.py` |
| 2 | Test API endpoints manually | Every change | 10 min | `test_api_quick.py` |
| 3 | Validate API request/response schemas | Every endpoint | 20 min | `validate_api_schemas.py` |
| 4 | Check API backward compatibility | Every PR | 30 min | `check_api_compat.py` |
| 5 | Generate client SDK types | Every release | 1 hr | `generate_sdk_types.py` |
| 6 | Benchmark API performance | Weekly | 30 min | `benchmark_api.py` (exists) |
| 7 | Check WebSocket handlers | Every WS change | 15 min | `check_ws_handlers.py` |
| 8 | Verify JWT configuration | Every auth change | 10 min | `validate_jwt_config.py` |

**Total manual time:** ~3.5 hrs/week
**Automation effort:** 4-6 hours
**ROI:** 1-2 weeks

### 2.2 Testing (High Priority)

| # | Manual Task | Frequency | Time/Occurrence | Automation Script |
|---|-------------|-----------|-----------------|-------------------|
| 1 | Run all tests before commit | Every commit | 2 min | `quick_test.sh` (exists) |
| 2 | Check test coverage report | Every PR | 5 min | `coverage_report.py` |
| 3 | Add missing tests for new code | Per feature | 30 min | `suggest_tests.py` |
| 4 | Run integration tests | Per PR | 5 min | Part of CI |
| 5 | Validate test fixtures | Per test file | 10 min | `validate_fixtures.py` |

**Total manual time:** ~1 hr/week
**Automation effort:** 3-4 hours
**ROI:** 1 month

### 2.3 Documentation (Medium Priority)

| # | Manual Task | Frequency | Time/Occurrence | Automation Script |
|---|-------------|-----------|-----------------|-------------------|
| 1 | Update API reference docs | Every API change | 20 min | `sync_api_docs.py` |
| 2 | Check doc staleness | Weekly | 15 min | `check_doc_freshness.py` |
| 3 | Validate internal links | Every doc PR | 5 min | `check_links.py` (exists) |
| 4 | Generate changelog entries | Every PR | 10 min | `generate_changelog.py` |
| 5 | Update session log | Every session | 5 min | `update_session_log.py` (exists) |
| 6 | Check doc metadata | Every doc | 5 min | `check_doc_metadata.py` (exists) |

**Total manual time:** ~1 hr/week
**Existing automation:** 50%
**Gap:** 30 min/week

### 2.4 Release Management (Medium Priority)

| # | Manual Task | Frequency | Time/Occurrence | Automation Script |
|---|-------------|-----------|-----------------|-------------------|
| 1 | Bump version numbers | Each release | 15 min | `bump_version.py` (exists) |
| 2 | Generate release notes | Each release | 30 min | `generate_release_notes.py` |
| 3 | Check pre-release checklist | Each release | 20 min | `check_pre_release.py` (exists) |
| 4 | Publish to PyPI | Each release | 10 min | `publish.yml` (exists) |

**Total manual time:** ~1.25 hrs/release
**Existing automation:** 60%
**Gap:** 30 min/release

### 2.5 Code Review (Low Priority)

| # | Manual Task | Frequency | Time/Occurrence | Automation Script |
|---|-------------|-----------|-----------------|-------------------|
| 1 | Check code style | Every PR | 5 min | Pre-commit (exists) |
| 2 | Review architecture boundaries | Every PR | 15 min | `check_architecture_boundaries.py` (exists) |
| 3 | Suggest improvements | Every PR | 20 min | AI-assisted (future) |

---

## 3. Proposed New Automation Scripts

### 3.1 Critical Priority (Create This Week)

#### `check_fastapi_issues.py`
**Purpose:** AST scanner for FastAPI anti-patterns (like `check_streamlit_issues.py`)

```python
# Detects:
# - Missing response_model
# - Unhandled exceptions
# - Async/await issues
# - Missing dependency injection
# - Security anti-patterns
```

**Effort:** 2-3 hours
**Impact:** Prevents 80% of FastAPI bugs

#### `validate_api_contracts.py`
**Purpose:** Validate API responses against OpenAPI schema

```python
# Usage:
python scripts/validate_api_contracts.py --endpoint /beam/design

# Output:
✅ Response matches BeamDesignResponse schema
❌ Missing required field: 'calculation_id'
```

**Effort:** 2-3 hours
**Impact:** Catches schema drift before production

#### `generate_fastapi_tests.py`
**Purpose:** Auto-generate test stubs for new endpoints

```python
# Usage:
python scripts/generate_fastapi_tests.py fastapi_app/routers/new_router.py

# Output:
Created: fastapi_app/tests/test_new_router.py
  - test_endpoint_success
  - test_endpoint_validation_error
  - test_endpoint_auth_required
```

**Effort:** 3-4 hours
**Impact:** 50% faster test creation

### 3.2 High Priority (Create This Month)

#### `sync_openapi_to_docs.py`
**Purpose:** Generate markdown docs from OpenAPI spec

```python
# Usage:
python scripts/sync_openapi_to_docs.py

# Output:
Updated: docs/api/endpoints.md
Updated: docs/api/models.md
Updated: docs/api/authentication.md
```

**Effort:** 3-4 hours
**Impact:** Always-current documentation

#### `check_api_compat.py`
**Purpose:** Detect breaking API changes

```python
# Usage:
python scripts/check_api_compat.py --base main

# Output:
⚠️ Breaking changes detected:
  - Removed field: BeamDesign.old_field
  - Changed type: width (int → float)
  - Removed endpoint: GET /deprecated
```

**Effort:** 4-6 hours
**Impact:** Prevents client breakage

#### `generate_client_types.py`
**Purpose:** Generate TypeScript types from OpenAPI

```python
# Usage:
python scripts/generate_client_types.py --output frontend/types/api.ts

# Output:
Generated TypeScript types for 15 models
Generated TypeScript API client
```

**Effort:** 2-3 hours
**Impact:** Type-safe frontend development

### 3.3 Medium Priority (Create This Quarter)

| Script | Purpose | Effort |
|--------|---------|--------|
| `check_ws_handlers.py` | Validate WebSocket message handling | 2-3 hrs |
| `benchmark_websocket.py` | WebSocket performance benchmarks | 2-3 hrs |
| `generate_postman_collection.py` | Export API to Postman | 1-2 hrs |
| `check_rate_limit_config.py` | Validate rate limiting setup | 1-2 hrs |
| `security_audit_api.py` | Comprehensive API security audit | 4-6 hrs |

---

## 4. Scripts Needing Catalog Expansion

The following 53 scripts exist in `scripts/` but are only listed in the "Recently Added" appendix of the automation catalog:

### By Priority

**High Priority (Expand First):**
1. `discover_api_signatures.py` - V3 critical
2. `check_performance_issues.py` - Code quality
3. `check_python_version.py` - Compatibility
4. `audit_input_validation.py` - Security
5. `check_governance_compliance.py` - Governance
6. `validate_folder_structure.py` - Structure
7. `run_vba_smoke_tests.py` - Cross-platform

**Medium Priority:**
8-20. Documentation scripts (7)
21-32. File operations (6)
33-42. Git workflow additions (5)

**Lower Priority:**
43-53. Governance, testing, analysis scripts

### Expansion Template

Each script should be documented with:

```markdown
### `script_name.py`

**Purpose:** One-line description

**When to Use:**
- ✅ Situation 1
- ✅ Situation 2
- ❌ Do NOT use when...

**Usage:**
\`\`\`bash
.venv/bin/python scripts/script_name.py [options]
\`\`\`

**Options:**
| Flag | Description |
|------|-------------|
| `--option1` | Description |
| `--verbose` | Show details |

**Example Output:**
\`\`\`
✅ Check passed: ...
⚠️  Warning: ...
❌ Error: ...
\`\`\`

**Related Scripts:**
- `related_script.py` - Similar purpose
```

---

## 5. Automation Efficiency Metrics

### Current State

| Metric | Value | Target |
|--------|-------|--------|
| Commits automated | 98% | 100% |
| Tests in CI | 95% (Python) | 100% |
| FastAPI in CI | 0% | 100% |
| Pre-commit hooks | 25 | 30 |
| Scripts documented | 65% | 95% |
| Average commit time | 5s | 5s ✅ |

### After Implementing This Research

| Metric | Current | After | Improvement |
|--------|---------|-------|-------------|
| FastAPI CI coverage | 0% | 100% | +100% |
| API bugs in prod | ~3/month | ~0/month | -100% |
| Manual testing time | 3.5 hrs/wk | 0.5 hrs/wk | -85% |
| Documentation sync | Manual | Auto | -100% |
| Release prep time | 1.25 hrs | 0.5 hrs | -60% |

---

## 6. Implementation Roadmap

### Week 1: Critical Automation

- [ ] Add FastAPI tests to CI (2-3 hrs)
- [ ] Create `check_fastapi_issues.py` (2-3 hrs)
- [ ] Add FastAPI pre-commit hooks (1-2 hrs)
- [ ] Expand 10 high-priority scripts in catalog (2 hrs)

### Week 2: Testing Automation

- [ ] Create `validate_api_contracts.py` (2-3 hrs)
- [ ] Create `generate_fastapi_tests.py` (3-4 hrs)
- [ ] Add API performance benchmarks to CI (2-3 hrs)
- [ ] Expand 15 more scripts in catalog (2 hrs)

### Week 3: Documentation Automation

- [ ] Create `sync_openapi_to_docs.py` (3-4 hrs)
- [ ] Create `check_api_compat.py` (4-6 hrs)
- [ ] Expand remaining scripts in catalog (2 hrs)

### Week 4: Client Tooling

- [ ] Create `generate_client_types.py` (2-3 hrs)
- [ ] Create `generate_postman_collection.py` (1-2 hrs)
- [ ] Comprehensive security audit script (4-6 hrs)

---

## 7. Quick Wins (Implement Today)

1. **Add FastAPI to pytest.ini** (5 min)
   ```ini
   testpaths = Python/tests fastapi_app/tests
   ```

2. **Create FastAPI lint pre-commit** (15 min)
   Add ruff/black rules for `fastapi_app/`

3. **Document 5 undocumented scripts** (30 min)
   Focus on v3_migration and testing categories

4. **Add FastAPI to coverage report** (10 min)
   Update pytest command in CI

5. **Create issue templates for FastAPI bugs** (15 min)
   Add `.github/ISSUE_TEMPLATE/api-bug.yml`

---

## 8. Related Resources

### Existing Research
- [v3-infrastructure-gap-analysis.md](v3-infrastructure-gap-analysis.md) - Infrastructure gaps
- [critical-infrastructure-gaps-v018.md](critical-infrastructure-gaps-v018.md) - Previous audit
- [automation-audit-readiness-research.md](automation-audit-readiness-research.md) - Audit readiness

### Existing Automation
- [scripts/index.json](../../scripts/index.json) - Scripts catalog
- [automation-map.json](../../scripts/automation-map.json) - Context mapping
- [automation-catalog.md](../reference/automation-catalog.md) - Full catalog

### Guides
- [agent-workflow-master-guide.md](../agents/guides/agent-workflow-master-guide.md) - Workflow guide
- [week3-realtime-features-guide.md](../guides/week3-realtime-features-guide.md) - FastAPI guide

---

## Appendix: Research Methodology

### Data Sources
1. `scripts/` directory listing (152 scripts)
2. `.pre-commit-config.yaml` analysis (25 hooks)
3. `.github/workflows/` analysis (16 workflows)
4. Manual task observation (development sessions)
5. Previous research documents

### Analysis Commands

```bash
# Count scripts
ls scripts/*.{py,sh} | wc -l

# Check pre-commit hooks
grep -c "id:" .pre-commit-config.yaml

# Check CI coverage
grep -r "pytest" .github/workflows/*.yml

# Find undocumented scripts
diff <(ls scripts/*.py | xargs -I{} basename {}) \
     <(grep -o '"[^"]*\.py"' docs/reference/automation-catalog.md | tr -d '"')
```

# V3 Infrastructure Gap Analysis & Automation Audit

**Type:** Research
**Audience:** All Agents, Maintainers
**Status:** Draft
**Importance:** Critical
**Created:** 2026-01-24
**Last Updated:** 2026-01-24
**Related Tasks:** TASK-CI-001, TASK-TEST-001
**Archive Condition:** Archive after V3 FastAPI migration complete

---

## Executive Summary

**Problem Statement:** The V3 FastAPI migration introduces a new code surface (`fastapi_app/`) that previously lacked:
- CI/CD integration (no tests run in GitHub Actions)
- Pre-commit hook coverage
- Performance benchmarks
- Security scanning
- Code quality enforcement

**Status Update (2026-01-24):** Phase 1 and Phase 2 are now COMPLETE ✅

### Critical Gaps Overview (Updated Status)

| # | Gap | Severity | Status | Evidence |
|---|-----|----------|--------|----------|
| 1 | **No FastAPI CI tests** | 🔴 Critical | ✅ **FIXED** | PR #407 - `fastapi-validation` job in fast-checks.yml |
| 2 | **No pre-commit for FastAPI** | 🔴 Critical | ✅ **FIXED** | 4 hooks added: black, ruff, isort, bandit |
| 3 | **No API performance benchmarks** | 🟡 High | ✅ **FIXED** | `scripts/benchmark_api.py` (350 lines) |
| 4 | **No WebSocket/SSE testing in CI** | 🔴 Critical | ✅ **FIXED** | 74 tests in CI including WebSocket/SSE |
| 5 | **No auth security validation** | 🔴 Critical | ✅ **FIXED** | `fastapi_app/tests/test_security.py` (22 tests) |
| 6 | **Scripts not in catalog** | 🟡 High | ✅ **FIXED** | 3 new scripts added to index.json |
| 7 | **Missing FastAPI documentation** | 🟡 High | ✅ **FIXED** | Deployment guide + Week 3 guide |

**Completed:** 12-15 hours of work
**Remaining:** Phase 3 (load tests, client SDKs, integration tests) - 11-21 hours

---

## 1. FastAPI CI/CD Gaps (Critical)

### Current State

| Component | Status | Evidence |
|-----------|--------|----------|
| FastAPI tests exist | ✅ Yes | `fastapi_app/tests/` - 4 test files |
| FastAPI tests in CI | ❌ No | No workflow includes `fastapi_app/` |
| Coverage tracking | ❌ No | Not included in coverage report |
| Performance benchmarks | ❌ No | No API latency benchmarks |

### Evidence

```bash
# Searching for FastAPI in CI workflows
grep -r "fastapi" .github/workflows/*.yml
# Result: 0 matches

# Check what tests are run
cat .github/workflows/fast-checks.yml | grep pytest
# Only Python/tests/ is executed
```

### Impact

- **52 FastAPI tests exist but are NEVER run in CI**
- Potential regressions go undetected until production
- No confidence in API stability between releases

### Solution: Add FastAPI CI Job

Create new job in `.github/workflows/fast-checks.yml`:

```yaml
  fastapi-validation:
    name: FastAPI Validation
    needs: changes
    if: ${{ hashFiles('fastapi_app/**') != '' }}
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-python@v6
        with:
          python-version: "3.11"
          cache: 'pip'

      - name: Install FastAPI dependencies
        run: |
          pip install -e "Python/[dev]"
          pip install -r fastapi_app/requirements.txt

      - name: Run FastAPI tests
        run: pytest fastapi_app/tests/ -v --cov=fastapi_app --cov-report=term

      - name: API contract tests
        run: python scripts/check_api_signatures.py --fastapi
```

---

## 2. Pre-Commit Hook Gaps

### Current State

| Hook Type | Python/structural_lib | streamlit_app | fastapi_app |
|-----------|----------------------|---------------|-------------|
| Black formatting | ✅ Yes | ⚠️ Partial | ❌ No |
| Ruff linting | ✅ Yes | ⚠️ Partial | ❌ No |
| MyPy type check | ✅ Yes | ❌ No | ❌ No |
| Isort imports | ✅ Yes | ❌ No | ❌ No |
| Bandit security | ✅ Yes | ❌ No | ❌ No |

### Solution: Extend Pre-Commit Config

Add to `.pre-commit-config.yaml`:

```yaml
  # FastAPI formatting
  - repo: https://github.com/psf/black
    rev: 25.9.0
    hooks:
      - id: black-fastapi
        name: black (fastapi)
        entry: black
        files: ^fastapi_app/
        types: [python]

  # FastAPI linting
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.4
    hooks:
      - id: ruff-fastapi
        name: ruff (fastapi)
        args: [--fix, --exit-non-zero-on-fix]
        files: ^fastapi_app/

  # FastAPI type checking
  - repo: local
    hooks:
      - id: mypy-fastapi
        name: mypy (fastapi)
        entry: bash -c 'cd fastapi_app && ../.venv/bin/python -m mypy .'
        language: system
        files: ^fastapi_app/.*\.py$
        pass_filenames: false
```

---

## 3. Missing FastAPI Test Categories

### Current Test Coverage

| Test Category | Exists | Count | Notes |
|---------------|--------|-------|-------|
| Unit tests | ✅ | ~40 | Endpoint tests |
| Auth tests | ✅ | 14 | JWT + rate limiting |
| WebSocket tests | ✅ | ~8 | Basic connection tests |
| SSE tests | ✅ | 7 | Batch streaming |
| Integration tests | ❌ | 0 | End-to-end flows |
| Load tests | ❌ | 0 | Concurrent requests |
| Contract tests | ❌ | 0 | API schema stability |
| Security tests | ❌ | 0 | Auth bypass, injection |

### Missing Test Types to Add

#### 3.1 Integration Tests
```python
# fastapi_app/tests/test_integration.py
class TestE2EDesignFlow:
    """End-to-end beam design through API."""

    async def test_full_design_workflow(self, client):
        """Complete workflow: create → design → export."""
        # 1. Create beam via REST
        # 2. Update via WebSocket
        # 3. Get results via SSE
        # 4. Export to JSON/CSV
```

#### 3.2 Load Tests
```python
# fastapi_app/tests/test_load.py
@pytest.mark.load
class TestAPILoad:
    """Load testing for API endpoints."""

    async def test_concurrent_requests(self, client):
        """Test 100 concurrent design requests."""
        tasks = [client.post("/beam/design", json=beam_data) for _ in range(100)]
        results = await asyncio.gather(*tasks)
        assert all(r.status_code == 200 for r in results)
```

#### 3.3 Contract Tests
```python
# fastapi_app/tests/test_contracts.py
@pytest.mark.contract
class TestAPIContracts:
    """API schema stability tests."""

    def test_beam_response_schema(self, client):
        """Response schema should not change without version bump."""
        response = client.post("/beam/design", json=valid_beam)
        assert_schema_matches(response.json(), "beam_design_v1.json")
```

#### 3.4 Security Tests
```python
# fastapi_app/tests/test_security.py
class TestAPISecurity:
    """Security validation tests."""

    def test_jwt_required_endpoints(self, client):
        """Protected endpoints require valid JWT."""
        response = client.get("/protected/endpoint")
        assert response.status_code == 401

    def test_rate_limiting(self, client):
        """Rate limiting enforced."""
        for _ in range(101):
            response = client.get("/limited")
        assert response.status_code == 429
```

---

## 4. Performance Benchmark Gaps

### Current State

| Benchmark Type | Python Core | FastAPI | Notes |
|----------------|-------------|---------|-------|
| Calculation benchmarks | ✅ 13 | ❌ 0 | Core has pytest-benchmark |
| API latency | ❌ | ❌ | No endpoint timing |
| WebSocket latency | ❌ | ❌ | No real-time benchmarks |
| Batch throughput | ❌ | ❌ | No beam/second metrics |

### Solution: Add API Benchmarks

#### 4.1 Create Benchmark Script

```python
# scripts/benchmark_api_latency.py
"""Benchmark FastAPI endpoint latency."""

import asyncio
import statistics
import httpx

async def benchmark_design_endpoint(iterations=100):
    """Measure /beam/design response times."""
    times = []
    async with httpx.AsyncClient() as client:
        for _ in range(iterations):
            start = time.perf_counter()
            await client.post("http://localhost:8000/beam/design", json=BEAM_DATA)
            times.append(time.perf_counter() - start)

    return {
        "p50_ms": statistics.median(times) * 1000,
        "p95_ms": sorted(times)[int(len(times) * 0.95)] * 1000,
        "p99_ms": sorted(times)[int(len(times) * 0.99)] * 1000,
        "mean_ms": statistics.mean(times) * 1000,
    }
```

#### 4.2 Add to CI

```yaml
- name: API Performance Regression Check
  run: |
    python scripts/benchmark_api_latency.py --json > api-perf.json
    python scripts/check_performance_regression.py api-perf.json
```

---

## 5. Security Scanning Gaps

### Current Security Tools

| Tool | Python Core | FastAPI | Purpose |
|------|-------------|---------|---------|
| Bandit | ✅ Yes | ❌ No | Static security analysis |
| CodeQL | ✅ Yes | ❌ No | Security vulnerability detection |
| pip-audit | ✅ Yes | ❌ No | Dependency vulnerabilities |
| SBOM | ✅ Yes | ❌ No | Software bill of materials |

### Solution: Extend Security Scans

```yaml
# .github/workflows/security.yml - Add FastAPI
- name: Bandit (FastAPI)
  run: bandit -r fastapi_app/ -ll

- name: pip-audit (FastAPI deps)
  run: pip-audit -r fastapi_app/requirements.txt
```

---

## 6. Scripts Catalog Gap (53 Scripts)

### Problem

53 scripts in `scripts/` are listed in the "Recently Added" appendix but not expanded into main catalog sections with:
- Full documentation
- Usage examples
- Category placement
- Priority ratings

### Impact

- Agents may not discover useful scripts
- Duplicate efforts creating similar automation
- Inconsistent documentation quality

### Solution

Expand each script into its proper category section with:
1. **Purpose** (one line)
2. **When to Use** (bullet points)
3. **Usage Example** (code block)
4. **Output Example** (code block)
5. **Related Scripts** (links)

**Scripts by Category:**

| Category | Count | Priority |
|----------|-------|----------|
| code_validation | 7 | High |
| documentation | 7 | Medium |
| file_operations | 6 | Medium |
| git_workflow | 5 | High |
| governance | 6 | Medium |
| project_structure | 6 | High |
| testing | 6 | High |
| session_management | 3 | Medium |
| v3_migration | 1 | Critical |
| Other | 6 | Low |

---

## 7. FastAPI Documentation Gaps

### Missing Documentation

| Document | Status | Priority |
|----------|--------|----------|
| API reference (auto-generated) | ⚠️ OpenAPI only | High |
| Authentication guide | ❌ Missing | Critical |
| Rate limiting guide | ❌ Missing | High |
| WebSocket protocol spec | ⚠️ Basic | High |
| SSE event types reference | ⚠️ Basic | High |
| Deployment guide | ❌ Missing | Critical |
| Client SDK examples | ⚠️ Python only | Medium |

### Solution: Documentation Checklist

1. [ ] Create `docs/api/authentication.md`
2. [ ] Create `docs/api/rate-limiting.md`
3. [ ] Create `docs/api/websocket-protocol.md`
4. [ ] Create `docs/api/sse-events.md`
5. [ ] Create `docs/deployment/fastapi-docker.md`
6. [ ] Add TypeScript client examples

---

## 8. Predicted Future Issues

Based on patterns from previous releases (v0.8, v0.15, v0.17, v0.18):

| Issue Pattern | Prediction | Preventive Action |
|---------------|------------|-------------------|
| API breaking changes | Schema changes break clients | Add contract tests + deprecation warnings |
| Performance regression | SSE latency increases | Add benchmark tracking in CI |
| Auth bypass bugs | JWT edge cases | Add security fuzzing tests |
| Rate limit bypass | Distributed clients | Add IP aggregation + Redis |
| WebSocket memory leaks | Long-running connections | Add connection timeout + cleanup |
| Documentation drift | API changes don't update docs | Add OpenAPI → markdown sync |

---

## 9. Automation Opportunities

### Manual Work That Should Be Automated

| Manual Task | Frequency | Automation Script to Create |
|-------------|-----------|---------------------------|
| Update OpenAPI docs | Every API change | `sync_openapi_docs.py` |
| Generate client SDKs | Every release | `generate_client_sdks.py` |
| Check API backward compat | Every PR | `check_api_compat.py` |
| Performance regression check | Every merge | `check_perf_regression.py` |
| Security audit | Monthly | `security_audit.py` |

### Proposed New Scripts

1. **`check_fastapi_issues.py`** - AST scanner for FastAPI anti-patterns
2. **`validate_api_contracts.py`** - Check API responses against schemas
3. **`benchmark_api.py`** - Comprehensive API benchmarking
4. **`sync_openapi_docs.py`** - Sync OpenAPI spec to markdown docs
5. **`check_websocket_handlers.py`** - Validate WebSocket message handling

---

## 10. Implementation Priority

### Phase 1: Critical (Week 1) ✅ COMPLETE
- [x] Add FastAPI tests to CI (2-3 hrs) → **Done: PR #407**
- [x] Add FastAPI pre-commit hooks (1-2 hrs) → **Done: black, ruff, isort, bandit**
- [x] Add security tests (2-3 hrs) → **Done: 22 tests in test_security.py**
- [x] Document authentication (2 hrs) → **Done: week3-realtime-features-guide.md**

### Phase 2: High (Week 2) ✅ COMPLETE
- [x] Add API performance benchmarks (2-3 hrs) → **Done: benchmark_api.py**
- [x] Add contract tests (2-3 hrs) → **Done: validate_api_contracts.py**
- [x] Expand scripts catalog (2 hrs) → **Done: 3 scripts added to index.json**
- [x] Add deployment documentation (2 hrs) → **Done: fastapi-deployment-guide.md**

### Phase 3: Medium (Week 3+) ⏳ IN PROGRESS
- [ ] Add load tests (2-3 hrs)
- [ ] Generate client SDKs (4-6 hrs)
- [ ] Add integration tests (3-4 hrs)
- [ ] Complete documentation (4-6 hrs)

---

## 11. Quick Wins (Do These Today)

1. **Add FastAPI to pyproject.toml test paths** (10 min)
2. **Create `fastapi_app/pytest.ini`** (5 min)
3. **Add FastAPI lint to pre-commit** (15 min)
4. **Document current API endpoints** (30 min)
5. **Create basic security test file** (30 min)

---

## Related Documents

- [critical-infrastructure-gaps-v018.md](critical-infrastructure-gaps-v018.md) - Previous infrastructure audit
- [week3-realtime-features-guide.md](../guides/week3-realtime-features-guide.md) - WebSocket/SSE implementation
- [automation-catalog.md](../reference/automation-catalog.md) - Scripts catalog
- [8-week-development-plan.md](../planning/8-week-development-plan.md) - Development roadmap

---

## Appendix: Evidence Collection Commands

```bash
# Check FastAPI test count
pytest fastapi_app/tests/ --collect-only | grep "test session starts" -A 100

# Check CI workflows for FastAPI
grep -r "fastapi" .github/workflows/*.yml

# Check pre-commit for FastAPI
grep -r "fastapi_app" .pre-commit-config.yaml

# List uncategorized scripts
cat docs/reference/automation-catalog.md | grep -A 100 "Recently Added"

# Check FastAPI coverage
pytest fastapi_app/tests/ --cov=fastapi_app --cov-report=term-missing
```

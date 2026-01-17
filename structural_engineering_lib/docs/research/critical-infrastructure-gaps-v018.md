# Critical Infrastructure Gap Analysis (Pre-v0.18.0)

**Type:** Research
**Audience:** All Agents, Maintainers
**Status:** Draft
**Importance:** Critical
**Version:** 1.0.0
**Created:** 2026-01-13
**Last Updated:** 2026-01-13
**Related Tasks:** TASK-500+ (To be created)
**Archive Condition:** Archive after v0.18.0 release OR when all CRITICAL gaps addressed

---

## Executive Summary

**Problem Statement:** After each release (v0.8, v0.15, v0.17), critical infrastructure gaps emerge requiring weeks of refactoring. This pattern must stop.

**Key Finding:** Despite strong automation (128 scripts, 2,598 tests, 13 workflows), **5 CRITICAL gaps** will cause post-v0.18.0 pain if not addressed NOW.

### Top 5 Critical Gaps (Must Fix Before v0.18.0)

| # | Gap | Impact | Time to Fix | Time if Delayed |
|---|-----|--------|-------------|-----------------|
| 1 | **No Cross-Platform CI** | Windows/macOS bugs undetected, VBA untested | 4-6 hrs | 2-3 weeks (post-release firefighting) |
| 2 | **VBA Testing Manual** | Python/VBA parity unverifiable, regression risk | 6-8 hrs | 3-4 weeks (user bug reports) |
| 3 | **No Performance Regression Tracking** | Silent slowdowns accumulate | 3-4 hrs | 1-2 weeks (user complaints) |
| 4 | **No Integration Tests (Streamlit)** | Page-level bugs slip through | 4-6 hrs | 2-3 weeks (production issues) |
| 5 | **No User Feedback Loop** | Flying blind on adoption/issues | 2-3 hrs | Ongoing pain (unknown usage) |

**Total effort NOW:** 19-27 hours (2.4-3.4 work days)
**Total effort LATER:** 8-12 weeks of reactive work + user trust damage

### Quick Win Recommendations (Do These First)

1. **Add macOS + Windows to CI matrix** (2 hrs) - Immediate cross-platform validation
2. **Setup Dependabot monitoring** (30 min) - Already configured, just verify
3. **Create performance baseline script** (2 hrs) - Track benchmark trends
4. **Add PyPI download tracking** (1 hr) - Understand actual usage
5. **Document VBA test automation plan** (1 hr) - Clear path forward

---

## 1. Current Infrastructure State

### ✅ What We Have (Strong Foundation)

| Category | Assets | Status |
|----------|--------|--------|
| **Automation** | 128 scripts (git, validation, testing, docs) | ✅ Excellent |
| **Testing** | 2,598 Python tests, 86% coverage | ✅ Strong |
| **Security** | CodeQL, Bandit, pip-audit, SBOM generation | ✅ Good |
| **CI/CD** | 13 workflows, fast-checks, security scans | ✅ Good |
| **Documentation** | 872 tracked internal links, agent guides | ✅ Strong |
| **Dependency Mgmt** | Dependabot configured (GitHub Actions + Python) | ✅ Configured |
| **Git Workflow** | Pre-commit hooks, safe_push automation | ✅ Excellent |
| **AST Scanner** | Streamlit runtime error prevention | ✅ Excellent |
| **Performance** | 13 benchmarks exist | ⚠️ No regression tracking |

### ❌ What We're Missing (Pain Points)

| Category | Gap | Evidence |
|----------|-----|----------|
| **Cross-Platform** | CI runs **ubuntu-latest ONLY** | All 13 workflows use ubuntu-latest |
| **VBA Testing** | Manual Excel execution required | PR template: "ran relevant tests in VBA/Tests/ (manual)" |
| **Integration Tests** | No Streamlit page-level tests | No test files matching `*integration*test*.py` |
| **User Feedback** | No telemetry, download tracking, or surveys | No .github/ISSUE_TEMPLATE automation beyond 3 basic forms |
| **Performance Tracking** | Benchmarks exist but no trend analysis | test_benchmarks.py exists but no --benchmark-compare in CI |
| **API Migration** | Deprecation decorator exists, no automation | Found references to deprecation policy but no migration scripts |
| **SBOM Publishing** | Generated but not published | No evidence of SBOM in PyPI metadata or docs |

---

## 2. Gap Analysis by Category

### 🔴 CRITICAL (Blocks Release Quality)

#### GAP-001: No Cross-Platform CI Testing

**Problem:**
- ALL CI workflows run on `ubuntu-latest` only
- VBA Excel files require Windows/macOS validation
- Mac VBA safety rules (CDbl wrapping) not CI-verified
- Potential Windows-specific Python bugs undetected

**Evidence:**
```bash
grep -r "runs-on:" .github/workflows/*.yml
# Result: 100% ubuntu-latest (20/20 jobs)
```

**Impact:**
- **User Trust:** Windows users report bugs we can't reproduce
- **VBA Parity:** Manual testing burden, regression risk
- **Release Quality:** Platform-specific issues discovered post-release

**Solution:** Add matrix strategy to python-tests.yml
```yaml
strategy:
  matrix:
    os: [ubuntu-latest, windows-latest, macos-latest]
    python-version: ['3.11', '3.12']
```

**Estimated Effort:** 4-6 hours
- 2 hrs: Update workflows with matrix
- 2 hrs: Fix path issues (Windows uses backslashes)
- 1-2 hrs: Debug macOS-specific issues

**If Delayed:**
- 2-3 weeks: Post-release issues from Windows/macOS users
- Loss of confidence in "production-ready" claims
- Emergency hotfix releases

---

#### GAP-002: VBA Testing Manual & Not CI-Automated

**Problem:**
- VBA tests exist (`VBA/Tests/Test_*.bas`) but require manual Excel execution
- Python/VBA parity claims unverifiable in CI
- PR template explicitly states "manual" testing required
- Regression risk: VBA changes can break silently

**Evidence:**
```markdown
# From .github/pull_request_template.md:
- [ ] VBA: ran relevant tests in `VBA/Tests/` (manual)

# From CONTRIBUTING.md:
- Tests live in `VBA/Tests/` and are currently **manual-run**.
```

**Impact:**
- **Parity Claims:** Cannot confidently claim Python/VBA feature parity
- **Regression Risk:** VBA bugs discovered by users, not CI
- **Maintenance Burden:** Agents must remember to manually test VBA

**Possible Solutions:**
1. **Option A:** Excel COM automation (Windows-only, brittle)
2. **Option B:** VBA → Python parser + test runner (complex, 2-3 weeks)
3. **Option C:** Minimal smoke tests via Excel CLI (2-3 days)
4. **Option D:** Document-only approach (update docs to clarify manual testing required)

**Recommended:** Option C (Minimal smoke tests)
- Use Excel CLI to open workbook, run `Test_RunAll.RunAllVBATests`, capture output
- Run on Windows CI runner only
- Accept some manual testing burden for now

**Estimated Effort:** 6-8 hours
- 3 hrs: Research Excel CLI automation
- 2 hrs: Write test runner script (PowerShell/Python)
- 2 hrs: Integrate into CI (windows runner)
- 1 hr: Documentation

**If Delayed:**
- 3-4 weeks: User-reported VBA bugs
- Loss of trust in parity claims
- Manual testing burden continues indefinitely

---

#### GAP-003: No Performance Regression Tracking

**Problem:**
- 13 benchmarks exist (`tests/performance/test_benchmarks.py`)
- pytest-benchmark installed and used
- **BUT:** No CI job runs `--benchmark-compare` to detect regressions
- **BUT:** No historical baseline storage or trend visualization

**Evidence:**
```python
# test_benchmarks.py exists with 13 benchmarks
# README.md claims: "13 performance benchmarks"
# But no CI workflow includes --benchmark-only or --benchmark-compare
```

**Impact:**
- **Silent Performance Degradation:** Refactoring can slow down API without detection
- **User Experience:** Users notice slowness, we discover it post-release
- **Technical Debt:** Accumulating performance regressions

**Solution:** Add benchmark tracking to CI
```yaml
# In .github/workflows/nightly.yml (or new workflow)
- name: Run Performance Benchmarks
  run: |
    cd Python
    python -m pytest tests/performance/ --benchmark-only --benchmark-json=benchmark.json

- name: Compare Against Baseline
  uses: benchmark-action/github-action-benchmark@v1
  with:
    tool: 'pytest'
    output-file-path: Python/benchmark.json
    github-token: ${{ secrets.GITHUB_TOKEN }}
    auto-push: true
    alert-threshold: '150%'  # Alert if 50% slower
    comment-on-alert: true
```

**Estimated Effort:** 3-4 hours
- 1 hr: Research GitHub Actions benchmark tools
- 1 hr: Add workflow job
- 1 hr: Test and tune alert thresholds
- 30 min: Documentation

**If Delayed:**
- 1-2 weeks: User complaints about slow API calls
- Detective work to find which commit caused regression
- Emergency performance optimization work

---

#### GAP-004: No Integration Tests for Streamlit

**Problem:**
- Streamlit app has 6+ pages (beam design, results, viewer, help, etc.)
- Unit tests exist for utilities
- **BUT:** No page-level integration tests
- **BUT:** No end-to-end workflow tests (input → design → results)

**Evidence:**
```bash
find . -name "*integration*test*.py"
# Result: No files found

# Streamlit app has extensive unit tests but no:
# - Page load tests
# - State transition tests
# - Multi-page workflow tests
```

**Impact:**
- **Page-Level Bugs:** Scanner catches some issues, but not user workflows
- **State Management:** Session state bugs between pages not caught
- **User Experience:** Broken flows discovered by users

**Solution:** Add Streamlit integration test suite
```python
# tests/streamlit_integration/test_design_workflow.py
def test_beam_design_full_workflow(streamlit_test_client):
    """Test complete design workflow: input → calculate → results."""
    # 1. Navigate to design page
    # 2. Fill inputs
    # 3. Click calculate
    # 4. Verify results page shows
    # 5. Verify download buttons work
```

**Estimated Effort:** 4-6 hours
- 2 hrs: Setup streamlit testing framework
- 2 hrs: Write 5-8 critical path tests
- 1 hr: Integrate into CI
- 1 hr: Documentation

**If Delayed:**
- 2-3 weeks: Production issues with multi-page workflows
- User frustration with broken state management
- Emergency bug fixes

---

#### GAP-005: No User Feedback Loop

**Problem:**
- Library published to PyPI (v0.17.0)
- **BUT:** No download tracking/analytics
- **BUT:** No user survey mechanism
- **BUT:** No automated feedback collection

**Evidence:**
```bash
# No PyPI download tracking documented
# No user telemetry (opt-in) in Streamlit app
# Issue templates exist (3) but no automation beyond manual triage
```

**Impact:**
- **Unknown Adoption:** Don't know who's using the library
- **Unknown Pain Points:** Users struggle silently
- **Roadmap Blindness:** Can't prioritize based on usage data

**Solution:** Add lightweight feedback mechanisms
1. **PyPI Download Tracking:** Document how to query download stats
2. **Optional Telemetry:** Streamlit opt-in usage tracking
3. **User Survey Link:** Add to README and app help page
4. **Issue Template Automation:** Use GitHub Issue Forms with auto-labeling

**Estimated Effort:** 2-3 hours
- 1 hr: Setup PyPI stats dashboard
- 30 min: Add survey link to docs
- 30 min: Document telemetry approach
- 30 min: Enhance issue templates with auto-labels

**If Delayed:**
- Ongoing pain: Never know if users are happy or struggling
- Missed opportunities for improvements
- Wasted effort on unused features

---

### 🟠 HIGH (Technical Debt Bomb)

#### GAP-006: No API Migration Automation

**Problem:**
- API deprecation policy exists
- `@deprecated` decorator exists in codebase
- **BUT:** No automated migration tool for users
- **BUT:** No version-to-version migration scripts

**Impact:**
- **User Friction:** Breaking changes require manual code updates
- **Adoption Barrier:** Users fear upgrade pain

**Solution:** Create migration automation
```python
# scripts/migrate_api.py
"""Automatic API migration tool for version upgrades."""
def migrate_v017_to_v018(code_path):
    """Auto-update user code from v0.17 to v0.18 API."""
    # AST-based code transformation
    # Report changes made
```

**Estimated Effort:** 8-10 hours
**If Delayed:** Ongoing user upgrade friction

---

#### GAP-007: No Changelog Automation

**Problem:**
- CHANGELOG.md maintained manually
- Risk of missing entries
- Time-consuming to curate

**Solution:** Use conventional commits + auto-changelog generation
```yaml
# .github/workflows/release.yml
- name: Generate Changelog
  uses: orhun/git-cliff-action@v1
```

**Estimated Effort:** 2-3 hours
**If Delayed:** Manual effort continues, risk of incomplete changelogs

---

#### GAP-008: No Memory Profiling

**Problem:**
- No memory usage tracking for API calls
- Risk of memory leaks in long-running Streamlit app
- No profiling in CI

**Solution:** Add memory_profiler to dev dependencies, periodic profiling runs

**Estimated Effort:** 3-4 hours
**If Delayed:** Memory issues discovered in production

---

### 🟡 MEDIUM (Quality of Life)

#### GAP-009: No Load Testing

**Problem:**
- Streamlit app performance under concurrent users unknown
- API batch operations not stress-tested

**Solution:** Add locust or pytest-xdist load tests

**Estimated Effort:** 4-5 hours
**If Delayed:** Scalability issues discovered when users scale

---

#### GAP-010: No Accessibility Audit

**Problem:**
- Streamlit app accessibility (WCAG) unknown
- Color contrast, screen reader support untested

**Solution:** Add lighthouse CI, axe-core tests

**Estimated Effort:** 3-4 hours
**If Delayed:** Exclusion of users with disabilities

---

## 3. Infrastructure Comparison (Similar Projects)

### What NumPy/SciPy Have That We Don't

| Feature | NumPy/SciPy | Us | Gap |
|---------|-------------|-----|-----|
| **Cross-platform CI** | ✅ Linux, Windows, macOS, ARM | ❌ Linux only | CRITICAL |
| **Benchmark tracking** | ✅ asv (airspeed velocity) dashboard | ⚠️ Benchmarks exist, no tracking | HIGH |
| **API deprecation** | ✅ Deprecation timeline, migration guide | ⚠️ Decorator exists, no automation | HIGH |
| **Community metrics** | ✅ Download stats, user surveys | ❌ No tracking | HIGH |
| **Integration tests** | ✅ Full workflow tests | ❌ Unit tests only | CRITICAL |
| **Memory profiling** | ✅ valgrind, memory_profiler | ❌ None | MEDIUM |

**Learning:** Mature scientific Python libraries invest heavily in cross-platform testing and performance tracking.

---

## 4. Prioritized Action Plan

### Phase 1: Pre-v0.18.0 CRITICAL Fixes (Must Do)

**Timeline:** 2-3 weeks (20-30 hours total)

| Task | Gap | Effort | Owner | Priority |
|------|-----|--------|-------|----------|
| **TASK-501** | Cross-platform CI (macOS + Windows) | 4-6 hrs | DEV | P0 |
| **TASK-502** | VBA test automation (smoke tests) | 6-8 hrs | DEV | P0 |
| **TASK-503** | Performance regression tracking | 3-4 hrs | TESTER | P0 |
| **TASK-504** | Streamlit integration tests | 4-6 hrs | DEV | P0 |
| **TASK-505** | User feedback setup | 2-3 hrs | DOC | P0 |

**Success Criteria:**
- [ ] CI runs on 3 platforms (Linux, Windows, macOS)
- [ ] VBA tests run automatically (even if minimal)
- [ ] Benchmarks tracked in CI with alerts
- [ ] 5-8 integration tests for Streamlit workflows
- [ ] PyPI download tracking documented

---

### Phase 2: v0.18-v1.0 HIGH Priority (Technical Debt)

**Timeline:** Q1 2026 (30-40 hours total)

| Task | Gap | Effort | Priority |
|------|-----|--------|----------|
| **TASK-506** | API migration automation | 8-10 hrs | P1 |
| **TASK-507** | Changelog automation | 2-3 hrs | P1 |
| **TASK-508** | Memory profiling setup | 3-4 hrs | P1 |
| **TASK-509** | SBOM publishing | 2-3 hrs | P1 |
| **TASK-510** | Enhanced issue templates | 2-3 hrs | P1 |

---

### Phase 3: v1.0+ MEDIUM Priority (Polish)

**Timeline:** Q2 2026 (20-30 hours total)

| Task | Gap | Effort | Priority |
|------|-----|--------|----------|
| **TASK-511** | Load testing | 4-5 hrs | P2 |
| **TASK-512** | Accessibility audit | 3-4 hrs | P2 |
| **TASK-513** | E2E testing framework | 6-8 hrs | P2 |
| **TASK-514** | User telemetry (opt-in) | 4-5 hrs | P2 |

---

## 5. Cost-Benefit Analysis

### Scenario A: Fix CRITICAL Gaps Now (Recommended)

| Category | Time NOW | Time LATER (if deferred) | Savings |
|----------|----------|-------------------------|---------|
| Cross-platform CI | 4-6 hrs | 2-3 weeks (80-120 hrs firefighting) | 74-114 hrs |
| VBA automation | 6-8 hrs | 3-4 weeks (120-160 hrs debugging) | 112-152 hrs |
| Performance tracking | 3-4 hrs | 1-2 weeks (40-80 hrs detective work) | 36-76 hrs |
| Integration tests | 4-6 hrs | 2-3 weeks (80-120 hrs bug fixes) | 74-114 hrs |
| User feedback | 2-3 hrs | Ongoing pain (unknown cost) | ∞ |
| **TOTAL** | **19-27 hrs** | **8-12 weeks (320-480 hrs)** | **296-456 hrs** |

**ROI:** 11-17x return on investment (fix now vs fix later)

### Scenario B: Defer to Post-v0.18.0 (Not Recommended)

**Consequences:**
- Repeat of v0.17 pattern: Release → bugs → weeks of refactoring
- User trust erosion: "Another buggy release"
- Agent productivity loss: Firefighting instead of feature work
- Opportunity cost: Features delayed while fixing infrastructure

---

## 6. Maintenance Burden Assessment

### Current Manual Processes (Need Automation)

| Process | Frequency | Manual Time | Automation Potential |
|---------|-----------|-------------|----------------------|
| VBA testing | Per PR | 10-15 min | HIGH (TASK-502) |
| Changelog curation | Per release | 30-45 min | HIGH (TASK-507) |
| Performance checks | Ad-hoc | 20-30 min | HIGH (TASK-503) |
| Dependency updates | Weekly (Dependabot) | 5-10 min review | ✅ Already automated |
| Link validation | Pre-release | 2-3 min | ✅ Already automated |
| Doc version drift | Pre-release | 2-3 min | ✅ Already automated |

**Total Manual Burden:** ~1.5-2 hours per release cycle
**After Phase 1 Automation:** ~30-45 minutes per release cycle
**Savings:** 66% reduction in manual overhead

---

## 7. Recommendations

### Immediate Actions (This Week)

1. **Create TASK-501 through TASK-514** in TASKS.md
2. **Assign to Agent 9 (Infrastructure)** or schedule for next sprint
3. **Block v0.18.0 release** until TASK-501 to TASK-505 complete
4. **Communicate to user** (if applicable): "Focusing on infrastructure stability before v0.18.0"

### Strategic Decisions

1. **VBA Testing:** Accept "smoke tests only" approach for now, full automation in v1.0
2. **Performance:** Use GitHub Actions benchmark action (proven, maintained)
3. **Integration Tests:** Start with 5 critical paths, expand over time
4. **User Feedback:** Start lightweight (surveys, download stats), add telemetry in v1.0

### Don't Pursue (Yet)

1. **Full E2E testing** - Overkill for current scale, defer to v1.0+
2. **Advanced observability** (APM, distributed tracing) - Premature for library
3. **Multi-language support** - No evidence of demand
4. **Cloud deployment** - Streamlit app is local-first

---

## 8. Success Metrics

### Phase 1 Completion Criteria (Pre-v0.18.0)

- [ ] CI passes on Linux, Windows, macOS for all tests
- [ ] VBA tests run automatically (smoke tests minimum)
- [ ] Benchmark CI job runs nightly with 150% regression alerts
- [ ] 5-8 Streamlit integration tests pass in CI
- [ ] PyPI download stats accessible and documented
- [ ] User survey link in README and app

### Phase 2 Completion Criteria (v0.18-v1.0)

- [ ] API migration script for v0.17 → v0.18 works
- [ ] Changelog auto-generated from conventional commits
- [ ] Memory profiling dashboard shows no leaks
- [ ] SBOM published to PyPI and linked in docs
- [ ] Issue templates have auto-labeling

### Phase 3 Completion Criteria (v1.0+)

- [ ] Load testing shows app handles 50+ concurrent users
- [ ] Accessibility audit scores 90+ (Lighthouse)
- [ ] E2E tests cover all critical user journeys
- [ ] Opt-in telemetry provides usage insights

---

## 9. Risk Analysis

### Risks of Addressing Gaps

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **Cross-platform CI increases build time** | High | Medium | Use conditional jobs (quick check → full matrix) |
| **VBA automation brittle** | Medium | High | Start with minimal smoke tests, iterate |
| **Performance tracking noisy** | Medium | Low | Tune alert thresholds carefully |
| **Integration tests flaky** | Medium | Medium | Use retry logic, mock external deps |

### Risks of NOT Addressing Gaps

| Risk | Likelihood | Impact | Consequence |
|------|------------|--------|-------------|
| **Windows users report bugs** | High | High | Emergency hotfixes, trust damage |
| **VBA/Python parity breaks** | High | Critical | User code breaks, parity claims false |
| **Silent performance degradation** | Medium | Medium | User complaints, reputation damage |
| **Streamlit workflow breaks** | Medium | High | Production issues for app users |
| **Never know who's using library** | Certain | Medium | Blind roadmap, wasted effort |

---

## 10. Conclusion

**The Pattern Must Stop:**
- v0.8 → Discovered git workflow chaos
- v0.15 → Discovered folder structure issues
- v0.17 → Discovered agent onboarding gaps
- v0.18 → **We KNOW the gaps NOW. Let's fix them preemptively.**

**The Path Forward:**
1. **Accept:** 20-30 hours of infrastructure work before v0.18.0 is a GOOD investment
2. **Execute:** TASK-501 to TASK-505 (Phase 1) before any v0.18 feature work
3. **Prevent:** Establish quarterly infrastructure review (use this doc as template)

**Final Recommendation:** **Block v0.18.0 release until Phase 1 complete.** The 11-17x ROI justifies the delay.

---

## Appendix A: Detailed CI Matrix Example

```yaml
# .github/workflows/python-tests-cross-platform.yml
name: Cross-Platform Tests

on:
  push:
    branches: [main]
  pull_request:
    paths:
      - 'Python/**'
      - '.github/workflows/python-tests-cross-platform.yml'

jobs:
  test-matrix:
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: ['3.11', '3.12']

    steps:
      - uses: actions/checkout@v4

      - name: Setup Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          cd Python
          python -m pip install --upgrade pip
          pip install -e ".[dev]"

      - name: Run tests
        run: |
          cd Python
          pytest tests/ -v --cov=structural_lib --cov-report=xml

      - name: Upload coverage (Ubuntu + Python 3.12 only)
        if: matrix.os == 'ubuntu-latest' && matrix.python-version == '3.12'
        uses: codecov/codecov-action@v4
        with:
          file: Python/coverage.xml
```

---

## Appendix B: VBA Test Automation Approach

```powershell
# scripts/run_vba_tests.ps1
# Minimal VBA smoke test automation for CI

$ExcelPath = "Excel\StructEng_BeamDesign_v0.5.xlsm"
$VBATestMacro = "Test_RunAll.RunAllVBATests"

# Open Excel in automation mode
$Excel = New-Object -ComObject Excel.Application
$Excel.Visible = $false
$Excel.DisplayAlerts = $false

# Open workbook
$Workbook = $Excel.Workbooks.Open((Resolve-Path $ExcelPath))

# Run test macro and capture output
$Output = $Excel.Run($VBATestMacro)

# Check for FAIL in output
if ($Output -match "FAIL") {
    Write-Error "VBA tests failed!"
    exit 1
}

# Clean up
$Workbook.Close($false)
$Excel.Quit()
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($Excel) | Out-Null

Write-Host "VBA smoke tests passed!"
exit 0
```

---

## Appendix C: Benchmark Tracking Example

```yaml
# .github/workflows/performance-tracking.yml
name: Performance Tracking

on:
  push:
    branches: [main]
  schedule:
    - cron: '0 2 * * *'  # Nightly at 2 AM UTC

jobs:
  benchmark:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          cd Python
          pip install -e ".[dev]"

      - name: Run benchmarks
        run: |
          cd Python
          pytest tests/performance/ --benchmark-only --benchmark-json=benchmark.json

      - name: Store benchmark result
        uses: benchmark-action/github-action-benchmark@v1
        with:
          tool: 'pytest'
          output-file-path: Python/benchmark.json
          github-token: ${{ secrets.GITHUB_TOKEN }}
          auto-push: true
          alert-threshold: '150%'
          comment-on-alert: true
          fail-on-alert: false
          alert-comment-cc-users: '@Pravin-surawase'
```

---

**Next Steps:** Review this analysis, discuss priorities, create TASK-501+ in TASKS.md, schedule Phase 1 execution.


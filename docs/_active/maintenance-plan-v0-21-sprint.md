# Maintenance Plan — Post v0.20.0 Sprint

**Type:** Planning | **Status:** Draft | **Created:** 2026-03-31
**Audience:** All Agents | **Importance:** High
**Reviewed by:** @reviewer, @governance, @security, @orchestrator

---

## Executive Summary

v0.20.0 shipped successfully to PyPI on 2026-03-31. This plan covers post-release maintenance across 7 workstreams, prioritized by impact. Each item includes the agent pipeline, scripts to run, and docs to update.

**Project Health Score:** 62/100 (last scan 2026-03-28) — target: 80+
**Tests:** 3,399 passing | **CI:** 17/17 green | **Architecture:** 4-layer intact

---

## Workstream 1: Stale Reference Cleanup (Priority: HIGH)

### Problem
10+ active docs still reference `streamlit_app/` (removed in v0.20.0). 30+ VBA/Excel references remain after VBA extraction to separate repo. `docs-canonical.json` last updated 2026-01-23.

### Affected Files

| File | Issue | Lines |
|------|-------|-------|
| `docs/getting-started/agent-bootstrap.md` | Lists `streamlit_app/` as project component | L39, L68 |
| `docs/developers/platform-guide.md` | Contains `streamlit_app.py` code example | L402, L445 |
| `docs/reference/3d-visualization-performance.md` | References `streamlit_app/components/` | L24 |
| `docs/guidelines/file-operations-safety-guide.md` | Example uses `streamlit_app/` pattern | L131 |
| `docs/agents/guides/agent-workflow-master-guide.md` | pylint command for `streamlit_app/` | L435 |
| `docs/git-automation/git-workflow-single-source.md` | PR rules for Streamlit code | L416-417 |
| `docs/adr/0001-three-layer-architecture.md` | Architecture lists `streamlit_app/` as UI layer | L32 |
| `docs/docs-canonical.json` | `"streamlit-patterns"` topic still registered | L27 |
| `docs/developers/integration-examples.md` | "Excel VBA Integration" section | L35 |
| `docs/developers/README.md` | VBA references | L14, L58, L70 |

### Agent Pipeline

```
1. @governance   — Run: grep -r "streamlit_app" docs/ --include="*.md" -l
                   Run: grep -r "streamlit_app" docs/ --include="*.json" -l
                   Produce: complete list of files to update
2. @doc-master   — Edit each file: remove/update streamlit references
                   Update docs-canonical.json: remove "streamlit-patterns", add new topics
                   Run: .venv/bin/python scripts/check_links.py
3. @reviewer     — Verify no broken links, no stale references remain
4. @ops          — Commit as: docs: remove stale streamlit and VBA references
```

### Scripts to Use
```bash
grep -r "streamlit_app" docs/ --include="*.md" -l        # Find all stale refs
grep -r "VBA\|vba_adapter\|Excel VBA" docs/ -l           # Find VBA refs
.venv/bin/python scripts/check_links.py                   # Verify no broken links
.venv/bin/python scripts/check_doc_versions.py --fix      # Fix version refs
```

### Docs to Update
- `docs/docs-canonical.json` — Remove stale topics, add: torsion, BOQ, load-calculator, SSE-streaming
- `docs/getting-started/agent-bootstrap.md` — Remove Streamlit from project components list
- `docs/adr/0001-three-layer-architecture.md` — Update architecture to reflect V3 (React + FastAPI only)
- All files listed in the table above

### Estimated Effort: 2-3 hours

---

## Workstream 2: Test Health & Coverage (Priority: HIGH)

### Problem
- `test_stats.json` is 3 months stale (2026-01-06, shows 2,270 tests — actual is 3,399)
- 5 service modules have NO tests: `boq`, `dashboard`, `excel_bridge`, `intelligence`, `report_svg`
- 5 core modules lack direct tests: `data_types`, `errors`, `logging_config`, `registry`, `types`
- 2 skipped benchmark tests in `test_benchmarks.py`
- 1 failing test from stale stats (needs re-run to verify)

### Agent Pipeline

```
1. @tester       — Run: .venv/bin/pytest Python/tests/ -v --tb=short -q
                   Update: Python/test_stats.json with fresh results
                   Identify untested modules
2. @tester       — Write tests for: boq, dashboard, report_svg (highest priority)
                   Write tests for: data_types, errors, types (core modules)
                   Fix or remove the 2 skipped benchmarks
3. @reviewer     — Review new tests: check coverage, edge cases, IS 456 compliance
4. @ops          — Commit as: test: add missing tests for boq, dashboard, report_svg
```

### Scripts to Use
```bash
.venv/bin/pytest Python/tests/ -v --tb=short -q           # Full test run
.venv/bin/pytest Python/tests/ -v --co -q | wc -l         # Count test items
.venv/bin/pytest Python/tests/ --cov=structural_lib --cov-report=term-missing  # Coverage
grep -r "skip\|xfail" Python/tests/ -l                    # Find skipped tests
```

### Files to Create/Update
- `Python/tests/test_boq.py` — New test file
- `Python/tests/test_dashboard.py` — New test file
- `Python/tests/test_report_svg.py` — New test file
- `Python/tests/test_core_types.py` — Tests for core/data_types, core/errors, core/types
- `Python/test_stats.json` — Refresh with current numbers
- `Python/tests/performance/test_benchmarks.py` — Fix 2 skipped benchmarks

### Estimated Effort: 4-6 hours

---

## Workstream 3: FastAPI Version & API Hygiene (Priority: HIGH)

### Problem
- FastAPI internal version stuck at `0.1.0` in 3 places (vs library `0.20.0`)
- OpenAPI baseline (`openapi_baseline.json`, 5,598 lines) may be stale
- Rate limiting applied to only 2/38 endpoints
- No auth audit documentation

### Agent Pipeline

```
1. @api-developer — Update: fastapi_app/__init__.py → __version__ = "0.20.0"
                    Update: fastapi_app/config.py → api_version = "1.0.0" (or "0.20.0")
                    Regenerate: openapi_baseline.json
2. @security      — Audit: which endpoints need auth vs intentionally public
                    Document: create decision record in docs/adr/
3. @api-developer — Add: global rate limiting middleware (replace per-endpoint Depends)
4. @reviewer      — Review changes, verify OpenAPI schema is current
5. @ops           — Commit as: fix: sync FastAPI API version and add global rate limiting
```

### Scripts to Use
```bash
grep -r "@router" fastapi_app/routers/ | wc -l             # Count endpoints
grep -r "rate_limit\|RateLimiter" fastapi_app/ -l           # Find rate limiting usage
grep -r "require_auth\|get_current_user" fastapi_app/ -l    # Find auth usage
.venv/bin/python -c "from fastapi_app.main import app; import json; print(json.dumps(app.openapi(), indent=2))" > fastapi_app/openapi_baseline.json  # Regenerate OpenAPI
```

### Docs to Update
- `fastapi_app/__init__.py` — Version bump
- `fastapi_app/config.py` — API version update
- `fastapi_app/openapi_baseline.json` — Regenerate
- `docs/adr/` — New ADR: "Auth model for FastAPI endpoints" (document the intentional public access decision)

### Estimated Effort: 3-4 hours

---

## Workstream 4: Security Hardening (Priority: MEDIUM)

### Problem (from @security audit)
- JWT secret defaults to insecure value and app still starts
- `get_current_user()` silently returns `None` when no token (implicit public access)
- CORS `allow_headers=["*"]` is overly permissive
- Dependencies use `>=` only (no upper bounds, no lockfile)
- In-memory rate limiter doesn't scale across workers
- JWT error messages leak internal details

### Agent Pipeline

```
1. @security      — Define: exact changes needed for each finding
2. @backend       — Implement: JWT startup check (refuse to start with default key in production)
                    Implement: restrict CORS headers to ["Authorization", "Content-Type", "X-Request-ID"]
                    Implement: generic error message for JWT failures
3. @api-developer — Implement: global rate limiting middleware
4. @ops           — Create: requirements.lock via pip freeze
                    Add: pip-audit to CI pipeline
5. @reviewer      — Review all security changes
6. @ops           — Commit as: fix: security hardening — JWT, CORS, rate limiting
```

### Scripts to Use
```bash
.venv/bin/pip-audit                                         # Check for known CVEs
.venv/bin/pip freeze > requirements.lock                    # Generate lockfile
grep -r "allow_headers\|allow_origins" fastapi_app/ -n      # CORS config locations
```

### Files to Update
- `fastapi_app/auth.py` — JWT startup check, generic error messages
- `fastapi_app/main.py` — CORS header restriction
- `fastapi_app/config.py` — CORS config
- `requirements.lock` — New file (generated lockfile)
- `.github/workflows/security.yml` — Add pip-audit step

### Estimated Effort: 4-5 hours

---

## Workstream 5: Documentation & Session Infrastructure (Priority: MEDIUM)

### Problem
- `docs-canonical.json` is 2+ months stale (2026-01-23)
- `logs/handoff_latest.md` is empty (session end not being followed)
- `logs/feedback/` is empty (feedback system not generating output)
- `unified-cli-upgrade-plan.md` at 7-day WIP limit
- Health score 62/100 (target: 80+)

### Agent Pipeline

```
1. @governance    — Run: ./run.sh health
                   Run: ./run.sh health --fix (auto-fix what's possible)
                   Audit: docs-canonical.json — identify stale topics, missing topics
2. @doc-master    — Update: docs-canonical.json with new topics (torsion, BOQ, streaming, etc.)
                   Move: unified-cli-upgrade-plan.md → docs/architecture/ or archive
                   Verify: feedback system works (./run.sh feedback log --agent test)
3. @ops           — Verify: session-end scripts actually write to handoff_latest.md
                   Test: ./run.sh session end produces expected output
4. @reviewer      — Verify health score improved
5. @ops           — Commit as: docs: update canonical registry and fix session infrastructure
```

### Scripts to Use
```bash
./run.sh health                                             # Current health score
./run.sh health --fix                                       # Auto-fix issues
.venv/bin/python scripts/check_docs.py --budget             # Doc budget check
./run.sh feedback log --agent governance                     # Test feedback logging
./run.sh session summary                                    # Test summary generation
```

### Docs to Update
- `docs/docs-canonical.json` — Add 6+ new topics, remove stale ones
- `docs/_active/unified-cli-upgrade-plan.md` — Move or archive
- `logs/handoff_latest.md` — Populate with current state

### Estimated Effort: 2-3 hours

---

## Workstream 6: Code Cleanup (Priority: LOW)

### Problem
- Empty directories: `codes/is456/beam/`, `codes/is456/column/` (only `__pycache__`)
- `services/api.py` at 1,984 lines (approaching too-large threshold)
- `services/adapters.py` at 2,005 lines (same concern)
- `.egg-info/PKG-INFO` shows stale version (local dev artifact)
- `test_stats.json` date is 2026-01-06

### Agent Pipeline

```
1. @backend       — Delete: codes/is456/beam/__pycache__/, codes/is456/column/__pycache__/
                    Delete: the empty beam/ and column/ directories themselves
                    (These are planned for Phase 2 column work — recreate when needed)
2. @backend       — Refresh: pip install -e "Python/.[dev]" to update .egg-info
3. @reviewer      — Spot check: api.py and adapters.py for splitting opportunities
                    (Do NOT split now — just document recommendations)
4. @ops           — Commit as: chore: clean empty directories and refresh dev metadata
```

### Scripts to Use
```bash
find Python/structural_lib/codes/is456/ -type d -empty      # Find empty dirs
wc -l Python/structural_lib/services/api.py                  # Check file size
wc -l Python/structural_lib/services/adapters.py             # Check file size
pip install -e "Python/.[dev]"                                # Refresh egg-info
```

### Estimated Effort: 1 hour

---

## Workstream 7: Phase 1 Continuation (Priority: MEDIUM)

### Problem
Phase 1 Batch 4 (TASK-617/618/619) and quality scripts (TASK-622/623/624) are queued but not started. These unblock the Phase 2 column work.

### Agent Pipeline

```
1. @orchestrator  — Scope: TASK-617 (test assertion helpers), TASK-618 (top-level exports), TASK-619 (unit plausibility guards)
2. @structural-math — Implement: TASK-617/618/619 following /function-quality-pipeline
3. @tester        — Write tests for new helpers and guards
4. @backend       — Implement: TASK-622/623/624 (quality check scripts)
5. @reviewer      — Review all implementations
6. @doc-master    — Update TASKS.md, WORKLOG.md, next-session-brief.md
7. @ops           — Commit via PR (production code changes)
```

### Scripts to Use
```bash
.venv/bin/pytest Python/tests/ -v -k "test_assertion"       # Test new helpers
.venv/bin/python scripts/check_all.py --quick                # Quick validation
./run.sh check                                               # Full validation
```

### Tasks
- TASK-617: Test assertion helpers (reusable pytest helpers for IS 456 tests)
- TASK-618: Top-level exports (clean public API surface)
- TASK-619: Unit plausibility guards (runtime input sanity checks)
- TASK-622: `check_function_quality.py` script
- TASK-623: `check_clause_coverage.py` script
- TASK-624: `check_new_element_completeness.py` script

### Estimated Effort: 6-8 hours

---

## Execution Priority Matrix

| # | Workstream | Priority | Est. Hours | Dependencies | First Agent |
|---|-----------|----------|-----------|-------------|-------------|
| 1 | Stale Reference Cleanup | 🔴 HIGH | 2-3h | None | @governance |
| 2 | Test Health & Coverage | 🔴 HIGH | 4-6h | None | @tester |
| 3 | FastAPI Version & API Hygiene | 🔴 HIGH | 3-4h | None | @api-developer |
| 4 | Security Hardening | 🟡 MEDIUM | 4-5h | #3 (API changes) | @security |
| 5 | Doc & Session Infrastructure | 🟡 MEDIUM | 2-3h | #1 (stale refs) | @governance |
| 6 | Code Cleanup | 🟢 LOW | 1h | None | @backend |
| 7 | Phase 1 Continuation | 🟡 MEDIUM | 6-8h | #2 (tests) | @orchestrator |

**Recommended execution order:** 1 → 2 → 3 → 6 → 5 → 4 → 7
(Stale refs first, then tests, then API fixes. Security and Phase 1 can run in parallel after foundations.)

**Total estimated effort:** 22-30 hours across ~4-5 focused sessions

---

## Success Criteria

| Metric | Current | Target | How to Verify |
|--------|---------|--------|---------------|
| Health score | 62/100 | 80+ | `./run.sh health` |
| Test count | 3,399 | 3,500+ | `.venv/bin/pytest Python/tests/ -v -q` |
| Stale streamlit refs | 10+ files | 0 | `grep -r "streamlit_app" docs/ -l` |
| FastAPI API version | 0.1.0 | 1.0.0 | `grep "api_version" fastapi_app/config.py` |
| docs-canonical.json | 2 months stale | Current | Check `_updated` field |
| Untested modules | 5 service + 5 core | 0 service + 2 core | Coverage report |
| Feedback logs | Empty | Populated | `ls logs/feedback/` |
| Security findings (HIGH) | 2 | 0 | Security audit re-run |

---

## Post-Maintenance Checklist

After all workstreams complete:

```bash
# Verify everything
./run.sh check                                # Full 28-check validation
./run.sh health                               # Health score (target 80+)
.venv/bin/pytest Python/tests/ -v --tb=short  # All tests pass
cd react_app && npm run build                 # React builds clean
grep -r "streamlit_app" docs/ -l              # Should return nothing
grep -r "0.19" docs/reference/ -l             # Should return nothing (except historical)

# Session end
./run.sh session summary
./run.sh session sync
# Update: docs/planning/next-session-brief.md
# Update: docs/TASKS.md
./scripts/ai_commit.sh "docs: post-maintenance session end"
```

---

## Notes

- **DO NOT implement during this planning phase** — this document is the plan only
- Each workstream can be executed independently (except noted dependencies)
- All production code changes require PRs — `./run.sh pr status` before committing
- After each workstream, update WORKLOG.md with one line per change
- The Phase 2 column work (TASK-630+) should NOT start until Phase 1 Batch 4 is complete

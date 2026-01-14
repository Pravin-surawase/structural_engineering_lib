# Task Board

> Single source of truth for work. Keep it short and current.

**Updated:** 2026-01-13 (v0.17.0 Released!)

> **Note:** For detailed specifications, see [docs/planning/](planning/) folder.

---

## Rules (read first)
- **WIP = 2** (max 2 active tasks). Use WIP=2 only for independent tasks. For complex features, keep WIP=1.
- Move tasks between sections; do not duplicate.
- **Umbrella tasks:** Keep a single umbrella task in Active/Up Next and list included TASK IDs in description.
- Definition of Done: tests pass, docs updated, CHANGELOG/RELEASES updated when needed.
- **Archive rule:** Move "Recently Done" items to [docs/_archive/tasks-history.md](_archive/tasks-history.md) after 20+ items or 14+ days old. Keep last 10-15 items visible.

---

## Current Release

- **Version:** v0.17.5 ✅ Released (2026-01-15)
- **Focus:** Multi-Objective Optimization + API Validation Infrastructure
- **Next:** v0.18.0 (Q1 2026, Weeks 3-4)

---

## v0.17.5 Release Summary (2026-01-15)

**Key Features:**
- ✅ Multi-Objective Pareto Optimization (NSGA-II algorithm)
- ✅ API Signature Validation in CI/pre-commit
- ✅ Cost Optimizer UI Enhancement
- ✅ 1317 tests passing

**Commits:**
- `a99aa73` - ci: add API signature validation to pre-commit and CI workflow
- `d7f996f` - chore(release): bump version to 0.17.5

---

## v0.16.6 Maintenance Release - Python 3.11 Baseline

**Goal:** Raise minimum supported Python to 3.11 for faster runtime and simpler maintenance.

**Rationale (validated in repo):**
- CI already tests 3.11/3.12 (`.github/workflows/python-tests.yml`).
- Fast checks still run 3.9 only; dropping 3.9/3.10 cuts matrix 4 → 2 (≈50% CI time).
- Tooling already flags 3.9 compatibility in docs and lint config (ruff/mypy targets).

**Phase 1: Policy + Config (Low Risk)**
| ID | Task | Agent | Est | Priority | Status |
|----|------|-------|-----|----------|--------|
| **TASK-450** | Update Python baseline to 3.11 (pyproject requires-python, classifiers, ruff target-version, mypy python_version) | DEVOPS | 1-2 hrs | 🔴 HIGH | ✅ Session 19 |
| **TASK-451** | Update docs for new Python baseline (README, copilot-instructions, getting-started) | DOCS | 1 hr | 🟠 MEDIUM | ✅ Session 19 |

**Phase 2: CI + Automation (Medium Risk)**
| ID | Task | Agent | Est | Priority | Status |
|----|------|-------|-----|----------|--------|
| **TASK-452** | Update CI to 3.11 baseline (fast-checks uses 3.11, pytest matrix 3.11/3.12) | DEVOPS | 1 hr | 🔴 HIGH | ✅ Session 19 |
| **TASK-453** | Add python-version consistency check (script + CI hook) | DEVOPS | 1-2 hrs | 🟠 MEDIUM | ✅ Session 19 |

**Phase 3: Code & Lint Cleanup (If Needed)**
| ID | Task | Agent | Est | Priority | Status |
|----|------|-------|-----|----------|--------|
| **TASK-454** | Run ruff/mypy with py311 targets; fix any new lint/type issues | DEV | 1-2 hrs | 🟠 MEDIUM | ✅ Session 19 |

**Phase 4: Release v0.16.6**
| ID | Task | Agent | Est | Priority | Status |
|----|------|-------|-----|----------|--------|
| **TASK-455** | Release v0.16.6 (pre-release checks, version bump, changelog, release docs) | RELEASE | 1-2 hrs | 🔴 HIGH | ✅ Session 19 |
| **TASK-456** | README update (WIP banner + active roadmap links) | DOCS | 30m | 🟠 MEDIUM | ✅ Session 19 |

---

## v0.17.0 Release Target (Q1 2026 - Weeks 2-4)

**Goal:** Implement first professional engineering requirements

**Focus:** Security, legal compliance, traceability, developer productivity

**Key Deliverables:**
1. ✅ Security hardening baseline (input validation audit, dependency scanning) - **PR #331**
2. ✅ Professional liability framework (disclaimers, templates, certification guidance) - **DONE**
3. ✅ Code clause database (JSON DB, @clause decorator, traceability system) - **PR #333 merged**
4. ✅ Interactive testing UI (Streamlit clause traceability page) - **PR #334 merged**

**Success Metrics:**
- Security: Input validation audit complete, dependency scanning in CI ✅
- Legal: MIT+engineering disclaimer, templates in docs/legal/ ✅
- Traceability: Clause references in 80%+ design functions
- Developer UX: Working Streamlit app for manual validation
- API grade: A- → A (93/100)

---

## Active

### v0.18.0 Core Library Expansion

> **Goal:** Expand testing and templating capabilities for v0.18.0 release
> **Research:** [v018-library-expansion-feasibility.md](research/v018-library-expansion-feasibility.md)
> **Timeline:** Week 3-4 January 2026

| ID | Task | Agent | Est | Priority | Status |
|----|------|-------|-----|----------|--------|
| **TASK-520** | Hypothesis property-based testing (strategies + 43 tests) | DEV | 4h | 🟠 MEDIUM | ✅ Complete |
| **TASK-521** | Fix deprecated error_message/remarks test patterns (10 tests) | DEV | 1h | 🟠 MEDIUM | ✅ Complete |
| **TASK-522** | Add Jinja2 report templates (3 templates, 25 tests) | DEV | 4h | 🟠 MEDIUM | ✅ PR #360 |
| **TASK-523** | Hypothesis docs + CI integration | DOCS | 1h | 🟠 MEDIUM | ✅ PR #358 Merged |
| **TASK-524** | Beam slenderness check (IS 456 Cl 23.3, 50 tests) | DEV | 3h | 🟠 MEDIUM | ✅ PR #359 |

---

### v0.18.0 Pre-Release: Critical Infrastructure (Phase 1)

> **Goal:** Fix 5 critical infrastructure gaps BEFORE v0.18.0 to prevent post-release firefighting
> **Research:** [critical-infrastructure-gaps-v018.md](research/critical-infrastructure-gaps-v018.md)
> **Timeline:** 19-27 hours (2.4-3.4 work days)
> **ROI:** Fix now saves 296-456 hours of future reactive work (11-17x return)

| ID | Task | Agent | Est | Priority | Status |
|----|------|-------|-----|----------|--------|
| **TASK-501** | Cross-platform CI (macOS + Windows matrix) | DEVOPS | 4-6h | 🔴 P0-CRITICAL | ✅ Complete |
| **TASK-502** | VBA test automation (smoke tests) | DEVOPS | 6-8h | 🔴 P0-CRITICAL | ⏳ Deferred |
| **TASK-503** | Performance regression tracking in CI | DEVOPS | 3-4h | 🔴 P0-CRITICAL | ✅ Complete |
| **TASK-504** | Streamlit integration tests (5-8 tests) | DEV | 4-6h | 🔴 P0-CRITICAL | ✅ Complete |
| **TASK-505** | User feedback setup (PyPI stats, survey) | DOCS | 2-3h | 🔴 P0-CRITICAL | ✅ Complete |

**TASK-501 Subtasks (Cross-Platform CI):**
- [x] 501.1: Research current workflow structure (all 13 use ubuntu-latest)
- [x] 501.2: Add matrix strategy to python-tests.yml (ubuntu, windows, macos × 3.11, 3.12)
- [x] 501.3: Handle Windows path differences (PowerShell packaging check)
- [x] 501.4: Test and debug macOS-specific issues if any (excluded 3.11 on macOS)
- [x] 501.5: Update coverage to run only on ubuntu+3.12

**TASK-503 Subtasks (Performance Tracking):**
- [x] 503.1: Review existing test_benchmarks.py (13 benchmarks, pytest-benchmark)
- [x] 503.2: Add benchmark job to nightly.yml workflow
- [x] 503.3: Integrate github-action-benchmark for trend tracking + alerts
- [x] 503.4: Set alert threshold (150% = 50% slower triggers alert)
- [x] 503.5: Add benchmark artifact storage (90 day retention)

**TASK-504 Subtasks (Streamlit Integration Tests):**
- [x] 504.1: Create test_critical_journeys.py with 8 user journey test classes
- [x] 504.2: Add 16 tests covering core value proposition (beam design)
- [x] 504.3: Add error recovery tests (invalid inputs, zero values)
- [x] 504.4: All tests pass (11 pass, 5 skip for optional features)

**TASK-505 Subtasks (User Feedback):**
- [x] 505.1: Add PyPI download tracking documentation (pypistats.org)
- [x] 505.2: Convert issue templates to GitHub Issue Forms (YAML)
- [x] 505.3: Add auto-labeling to issue templates
- [x] 505.4: Add feedback links to README + Streamlit sidebar
- [x] 505.5: Add issue template chooser (config.yml)

**TASK-502 Notes (VBA Test Automation - Deferred):**
- Requires Windows CI runner or cross-platform VBA tooling
- Estimated 6-8 hours for proper implementation
- Will be addressed in v0.18.0 or as separate PR

**TASK-457 Details:****
- **Research:** Documentation redundancy analysis complete (525 files → target <400)
- **Phase 1 (Quick Wins):** ✅ **COMPLETE** - 46 files archived
- **Phase 2 (Streamlit/Agent Cleanup):** ✅ **COMPLETE** - 91 files archived (98% reduction in streamlit_app/docs)
  - streamlit_app/docs: 93 → 2 files
  - agents/agent-9: SUMMARY files archived
  - 48 broken links fixed
- **Phase 3 (Deduplication):** Merge remaining similar file pairs (2-3 hrs)
- **Expected Impact:** 35%+ reduction, 10-15 min saved per agent session

**TASK-458 Details:**
- **Phase 1:** ✅ Research + README auto-update in end_session.py + create_doc.py script
- **Phase 2:** ✅ Pre-commit metadata check (warning mode) - `scripts/check_doc_metadata.py`
- **Phase 3:** ⏳ Gradual metadata migration (~150 docs migrated, ~150 remaining)
  - Completed: reference/, planning/, guidelines/, contributing/, architecture/, getting-started/
  - Remaining: research/, _archive/, specs/, adr/
- **Automation Discovery:** Created `scripts/index.json` (128 scripts) + `workflows/README.md` (12 workflows)
- **Documentation:** See [metadata-migration-strategy.md](research/metadata-migration-strategy.md)

---

## Up Next

### Guide Consolidation (Complete)

| ID | Task | Agent | Est | Priority | Status |
|----|------|-------|-----|----------|--------|
| **DOC-ONB-01** | Consolidate onboarding guides (bootstrap + workflow) | DOCS | 3h | 🟠 MEDIUM | ✅ 2026-01-13 |
| **DOC-ONB-02** | Update cross-links + index references | DOCS | 1h | 🟡 LOW | ✅ 2026-01-13 |

**Result:** 4 guides → 3 guides (25% reduction), 1,404 → 1,119 active lines, clear hierarchy

### Improvements I recommend (compact, high-value)

| ID | Task | Agent | Est | Priority | Status |
|----|------|-------|-----|----------|--------|
| **IMP-02** | Add `collect_diagnostics.py` reminder to `agent_start.sh` and `end_session.py` failure paths | DEVOPS | 30m | 🟡 LOW | ✅ 2026-01-13 |
| **IMP-03** | Add a debug snapshot checklist to handoff docs (include logs + diagnostics bundle) | DOCS | 30m | 🟡 LOW | ✅ 2026-01-13 |

### v0.17.0 - Critical Path (Complete)

All core deliverables are complete (TASK-272/273/274/275). See `docs/_archive/tasks-history.md`.

### v0.18+ - Professional Features Pipeline

> **Goal:** Build on v0.17.0 foundation with advanced professional features
> **Timeline:** Q1-Q2 2026

TASK-276-279 are complete (Session 19). Streamlit integration PR is in progress; see
`streamlit_app/utils/input_bridge.py`, `streamlit_app/components/report_export.py`,
and `streamlit_app/tests/test_input_bridge.py`.

### v0.17.5 - Code Quality & Automation Enhancement (Agent 6 Focus)

> **Goal:** Improve scanner accuracy, create developer guidelines, enhance automation
> **Research:** [streamlit-code-quality-research.md](research/streamlit-code-quality-research.md), [streamlit-code-files-analysis.md](research/streamlit-code-files-analysis.md)
> **Onboarding:** [agent-6-comprehensive-onboarding.md](agents/guides/agent-6-comprehensive-onboarding.md)
> **Timeline:** Week 2-3, January 2026
> **Owner:** Agent 6 (Streamlit Specialist)

**Codebase Stats:** 12 pages (6,090 lines) + 26 utilities (11,312 lines) + 6 components (2,645 lines) = ~20,000 lines

**Phase A-D:** ✅ Complete (archived to `docs/_archive/tasks-history.md`)

**Phase E: True Positive Fixes (from code analysis)**
| ID | Task | Agent | Est | Priority | Status |
|----|------|-------|-----|----------|--------|
| **TASK-436** | Fix session_manager.py lines 675-676 int() error handling | AGENT_6 | 15m | 🟠 MEDIUM | ⏳ Queued (false positive - dataclass attrs) |

### v0.18+ - Governance & Observability (Agent 9)

> **Goal:** 80/20 governance cadence, proactive monitoring, sustainable velocity
> **Dependencies:** Phase A+B+C complete

| ID | Task | Agent | Est | Priority | Status |
|----|------|-------|-----|----------|--------|
| **TASK-284** | Weekly Governance Sessions (80/20 rule) | AGENT_9 | 3h | 🟠 P1-High | ⏳ Queued |
| **TASK-285** | Metrics Dashboard (trending, alerts) | AGENT_9 | 4h | 🟡 P2-Medium | ⏳ Blocked by 284 |
| **TASK-286** | Leading Indicator Alerts (6 metrics) | AGENT_9 | 2h | 🟡 P2-Medium | ⏳ Blocked by 285 |

---

## Backlog

### v1.0+ Long-Term (March 2026+)

**Agent 9 - Advanced Optimization:**
| ID | Task | Est | Priority | Status |
|----|------|-----|----------|--------|
| **TASK-287** | Predictive Velocity Modeling | 8h | 🔵 P3-Low | ⏳ Blocked by 286 |
| **TASK-288** | Release Cadence Optimization | 6h | 🔵 P3-Low | ⏳ Blocked by 287 |
| **TASK-289** | Governance Health Score | 4h | 🔵 P3-Low | ⏳ Blocked by 288 |
| **TASK-290** | Context Optimization for AI Agents | 6h | 🔵 P3-Low | ⏳ Blocked by 289 |
| **TASK-291** | Technical Debt Dashboard | 5h | 🔵 P3-Low | ⏳ Blocked by 290 |

**Visualization & Developer Tools:**
| ID | Task | Est | Priority |
|----|------|-----|----------|
| **TASK-305** | Re-run navigation study | 1h | 🟡 P2-Medium |
| **TASK-145** | Visualization Stack (BMD/SFD, etc.) | 3-4 days | 🟡 MEDIUM |
| **TASK-146** | DXF Quality Polish | 2-3 days | 🟡 MEDIUM |
| **TASK-147** | Developer Documentation | 2-3 days | 🟡 MEDIUM |

**Beam Scope Extensions:**
| ID | Task | Est | Priority |
|----|------|-----|----------|
| **TASK-081** | Level C Serviceability | 1-2 days | 🟡 MEDIUM |
| **TASK-082** | VBA parity harness | 1-2 days | 🟡 MEDIUM |
| **TASK-138** | ETABS mapping | 1-2 days | 🟡 MEDIUM |
| **TASK-085** | Torsion design | 2-3 days | 🟡 MEDIUM |
| **TASK-087** | Anchorage check | 1 day | 🟡 MEDIUM |
| **TASK-088** | Slenderness check | 4 hrs | 🟡 MEDIUM |

### Research Tasks (Deferred - User Validation Required)

> **Status:** Removed from active backlog until v1.0 ships
> **Research IDs:** TASK-220-227, TASK-231-234, TASK-241-244, TASK-250-253, TASK-262

---

## Recently Done

> **Archive Rule:** Move items to [tasks-history.md](_archive/tasks-history.md) after 20+ items or 14+ days old. Keep last 10-15 items.

| ID | Task | Agent | Status |
|----|------|-------|--------|
| **TASK-600** | Streamlit fixes: stirrup diameter selection, PDF report data, AppTest automation (46 tests) | MAIN | ✅ PR #TBD 2026-01-15 |
| **REL-0175** | Release v0.17.5: Multi-Objective Pareto Optimization, API Signature Validation CI, 1317 tests | MAIN | ✅ 2026-01-15 |
| **INFRA-01** | Add check-api-signatures hook to pre-commit + CI api-signature-check job | DEVOPS | ✅ 2026-01-15 |
| **IMPL-008** | Fix Streamlit API issues and UI improvements (advanced analysis, utilization display, session state) | DEV | ✅ PR #361 2026-01-14 |
| **TASK-520** | Hypothesis property-based testing (strategies + 43 tests for flexure/shear/ductile) | DEV | ✅ 2026-01-14 |
| **TASK-521** | Fix deprecated error_message/remarks test patterns (10 tests → all 2639 pass) | DEV | ✅ 2026-01-14 |
| **TASK-523** | Hypothesis docs + CI integration (testing-strategy.md, nightly.yml) | DOCS | ✅ PR #358 2026-01-14 |
| **TASK-506** | Session 20-21 Validation & Test Fixes (17 broken tests → all pass, lint fixes) | MAIN | ✅ PR #357 2026-01-13 |
| **IMP-02** | Add diagnostics reminders to agent_start.sh + end_session.py | DEVOPS | ✅ 2026-01-13 |
| **IMP-03** | Add debug snapshot checklist to handoff docs | DOCS | ✅ 2026-01-13 |
| **API-01** | Generate API manifest (public functions + signatures) | DEVOPS | ✅ 2026-01-13 |
| **API-02** | Pre-commit check: API changes require manifest update | DEVOPS | ✅ 2026-01-13 |
| **API-03** | Onboarding “API touchpoints” checklist | DOCS | ✅ 2026-01-13 |
| **IMP-01** | Guardrail: fail CI if new scripts are added without updating `scripts/index.json` | DEVOPS | ✅ 2026-01-13 |
| **DEBUG-01** | Diagnostics bundle script (env, versions, git, logs) | DEVOPS | ✅ 2026-01-13 |
| **DEBUG-02** | Debug mode toggle + logging guidance (Streamlit + CLI) | DEV | ✅ 2026-01-13 |
| **TASK-460** | Fix Streamlit runtime errors (page_header signature, reportlab, use_container_width deprecation, import checker) | DEV | ✅ PR #354 2026-01-13 |
| **TASK-457-P2** | Documentation Consolidation Phase 2: Archive 3 session-specific research files | DOCS | ✅ 2026-01-13 |
| **GITDOC-15-28** | Hook enforcement system: versioned hooks, git_ops.sh router, automation-first recovery, health check, test suite (14 tasks, 4 commits) | MAIN | ✅ 2026-01-12 |
| **GITDOC-01-14** | Git workflow automation-first: error clarity, hook capture, CI monitor, docs consolidation (14 tasks, PR #345) | MAIN | ✅ 2026-01-12 |
| **SESSION-19P4** | Git workflow improvements: error clarity, policy-aware merge, docs consistency, enforcement hook | MAIN | ✅ 2026-01-12 |
| **SESSION-19** | Python 3.11 Baseline Complete: v0.16.6 released, PR #343 merged | MAIN | ✅ 2026-01-12 |

> **Full History:** [docs/_archive/tasks-history.md](_archive/tasks-history.md)

---

## Archive

See full task history in [docs/_archive/tasks-history.md](_archive/tasks-history.md)

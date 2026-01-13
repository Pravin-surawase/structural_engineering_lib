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

- **Version:** v0.17.0 ✅ Released (2026-01-13)
- **Focus:** Professional API Features + Debug Infrastructure + Doc Consolidation
- **Next:** v0.18.0 (Q1 2026, Weeks 3-4)

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

No active tasks. Phase 1+2 (debug upgrades + API guardrails) and IMP-02/03 complete.

**Next focus:** Guide consolidation (DOC-ONB-01/02) or v0.17.5 Agent 6 tasks.

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

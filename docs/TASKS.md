# Task Board

> Single source of truth for work. Keep it short and current.

**Updated:** 2026-01-13 (Session 19P17: Streamlit Runtime Fixes)

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

- **Version:** v0.16.6 ✅ Released (2026-01-12)
- **Focus:** Python 3.11 Baseline + Type Modernization
- **Next:** v0.17.0 (Q1 2026, Weeks 2-4)

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

| ID | Task | Agent | Status |
|----|------|-------|--------|
| **TASK-274** | Security Hardening Baseline | DEVOPS | ✅ PR #331 merged |
| **TASK-457** | Documentation Consolidation (Phase 1-3) | DOCS | ✅ Phase 1 Complete (46 files archived) |
| **TASK-458** | File Metadata Standards & README Automation | DOCS | ⏳ Phase 3 in progress |

**TASK-457 Details:**
- **Research:** Documentation redundancy analysis complete (525 files → target <400)
- **Phase 1 (Quick Wins):** ✅ **COMPLETE** - 46 files archived (8 sessions + 12 PHASE + 26 completed)
  - Research folder: 118 → 72 files (-39% reduction)
  - All 877 links maintained (0 broken)
  - Added documentation guidelines to copilot-instructions.md
- **Phase 2 (Research Folder):** ⏳ Consolidate remaining SUMMARY files (3-4 hrs)
- **Phase 3 (Deduplication):** Merge remaining similar file pairs (2-3 hrs)
- **Expected Impact:** 30-35% reduction, 10-15 min saved per agent session
- **Documentation:** See [documentation-consolidation-research-2026-01-13.md](research/documentation-consolidation-research-2026-01-13.md)

**TASK-458 Details:**
- **Phase 1:** ✅ Research + README auto-update in end_session.py + create_doc.py script
- **Phase 2:** ✅ Pre-commit metadata check (warning mode) - `scripts/check_doc_metadata.py`
- **Phase 3:** ⏳ Gradual metadata migration for existing files
- **Documentation:** See [file-metadata-standards-research.md](research/file-metadata-standards-research.md)

---

## Active Research (Phase 1)

**Goal:** Establish theoretical and competitive baseline for MOO beam design.

| ID | Task | Status |
|----|------|--------|
| **PHASE 1.1** | Initial audit of MOO repository and foundational theory (NSGA-II) | ✅ COMPLETE |
| **PHASE 1.2** | 2025-2026 Web Research (qEHVI, PSL, ParetoLens) | ✅ COMPLETE |
| **PHASE 1.3** | Bridge to Structural Engineering (IS 456 compliance, Parhi et al. 2026) | ✅ COMPLETE |
| **PHASE 1.4** | Human-AI Interaction & Decision Support (Trust, UX) | ✅ COMPLETE |
| **PHASE 1.5** | Final Synthesis & Implementation Roadmap (v0.18+ integration) | ✅ COMPLETE |

---

## Up Next

### v0.17.0 - Critical Path (Must Complete)

> **Phase Approach:** Start with low-risk foundation (security, legal) before high-risk features (Streamlit)

**Phase 1 (Week 2): Foundation (Low Risk) ✅ COMPLETE**
| ID | Task | Agent | Est | Priority | Status |
|----|------|-------|-----|----------|--------|
| **TASK-274** | Security Hardening Baseline (input validation audit, dependency scanning, CI setup) | DEVOPS | 2-3 hrs | 🔴 HIGH | ✅ PR #331 |
| **TASK-275** | Professional Liability Framework (MIT+engineering disclaimer, templates, certification guidance) | DOCS | 2-3 hrs | 🔴 HIGH | ✅ Complete |

**Phase 2 (Week 3): Traceability (Medium Risk, 4-6 hours) ✅ COMPLETE**
| ID | Task | Agent | Est | Priority | Blockers |
|----|------|-------|-----|----------|----------|
| **TASK-272** | Code Clause Database (JSON DB, @clause decorator, traceability) | DEV | 4-6 hrs | 🔴 HIGH | ✅ PR #333 merged |

**Phase 3 (Week 4): Developer UX (High Value, 1-2 days) ✅ COMPLETE**
| ID | Task | Agent | Est | Priority | Blockers |
|----|------|-------|-----|----------|----------|
| **TASK-273** | Interactive Testing UI (Streamlit clause traceability page) | DEV | 1-2 days | 🔴 HIGH | ✅ PR #334 merged |

> **Note:** TASK-273 depends on stable test infrastructure. If blocked, deliver v0.17.0 with TASK-272/274/275 only.

### v0.18+ - Professional Features Pipeline

> **Goal:** Build on v0.17.0 foundation with advanced professional features
> **Timeline:** Q1-Q2 2026

| ID | Task | Agent | Est | Priority | Status |
|----|------|-------|-----|----------|--------|
| **TASK-276** | Input Flexibility (BeamInput dataclasses, import helpers) | DEV | 4-5 hrs | 🔴 HIGH | ✅ Session 19 |
| **TASK-277** | Calculation Report Generation (HTML/JSON/Markdown) | DEV | 4-5 hrs | 🔴 HIGH | ✅ Session 19 |
| **TASK-278** | Verification & Audit Trail (SHA-256, immutable logs) | DEV | 3-4 hrs | 🔴 HIGH | ✅ Session 19 |
| **TASK-279** | Engineering Testing Strategies (tolerance, property-based, regression) | TESTER | 4-5 hrs | 🔴 HIGH | ✅ Session 19 |

**TASK-276-279 Streamlit Integration:** (PR in progress)
- Library modules implemented: `inputs.py`, `calculation_report.py`, `audit.py`, `testing_strategies.py`
- **Integration added (Session 19P12):**
  - `streamlit_app/utils/input_bridge.py` - Bridge UI BeamInputs ↔ Library BeamInput
  - `streamlit_app/components/report_export.py` - Professional report export UI
  - `streamlit_app/tests/test_input_bridge.py` - Integration tests (8 passing)

### v0.17.5 - Code Quality & Automation Enhancement (Agent 6 Focus)

> **Goal:** Improve scanner accuracy, create developer guidelines, enhance automation
> **Research:** [streamlit-code-quality-research.md](research/streamlit-code-quality-research.md), [streamlit-code-files-analysis.md](research/streamlit-code-files-analysis.md)
> **Onboarding:** [agent-6-comprehensive-onboarding.md](agents/guides/agent-6-comprehensive-onboarding.md)
> **Timeline:** Week 2-3, January 2026
> **Owner:** Agent 6 (Streamlit Specialist)

**Codebase Stats:** 12 pages (6,090 lines) + 26 utilities (11,312 lines) + 6 components (2,645 lines) = ~20,000 lines

**Phase A: Quick Wins (1-2 hours total)**
| ID | Task | Agent | Est | Priority | Status |
|----|------|-------|-----|----------|--------|
| **TASK-401** | Fix scanner false positives (Path division, constant divisors, split pattern) | AGENT_6 | 1h | 🔴 HIGH | ✅ PR #339 Session 16 |
| **TASK-422** | Document PR auto-merge behavior in copilot-instructions | DOCS | 30m | 🔴 HIGH | ✅ Session 15 |
| **TASK-431** | Fix finish_task_pr.sh auto-merge behavior | DEVOPS | 30m | 🔴 HIGH | ✅ Session 15 |
| **TASK-432** | Archive outdated Agent 6 files (work-division-main-agent6-2026-01-09.md) | AGENT_6 | 15m | 🟠 MEDIUM | ✅ Session 15P3 |

**Phase B: Scanner Enhancement (6-8 hours)**
| ID | Task | Agent | Est | Priority | Status |
|----|------|-------|-----|----------|--------|
| **TASK-402** | Add type annotation checker to scanner | AGENT_6 | 2h | 🟠 MEDIUM | ✅ Session 18 |
| **TASK-403** | Add widget return type validation | AGENT_6 | 3h | 🔴 HIGH | ✅ Session 17 |
| **TASK-404** | Add circular import detection | AGENT_6 | 2h | 🟠 MEDIUM | ✅ Session 18 |
| **TASK-405** | Add performance issue detection | AGENT_6 | 4h | 🟡 LOW | ✅ Session 18 |

**Phase C: Streamlit Automation (10-12 hours)**
| ID | Task | Agent | Est | Priority | Status |
|----|------|-------|-----|----------|--------|
| **TASK-411** | Create streamlit_preflight.sh (combines scanner + pylint + tests) | AGENT_6 | 2h | 🔴 HIGH | ✅ Session 17 |
| **TASK-412** | Create generate_streamlit_page.py scaffold | AGENT_6 | 2h | 🟠 MEDIUM | ✅ Session 19 |
| **TASK-413** | Create validate_session_state.py (audit all session_state usage) | AGENT_6 | 3h | 🔴 HIGH | ✅ Session 17 |
| **TASK-414** | Create performance profiler | AGENT_6 | 4h | 🟠 MEDIUM | ✅ Session 19 |

**Phase D: Documentation & Onboarding (3-4 hours)**
| ID | Task | Agent | Est | Priority | Status |
|----|------|-------|-----|----------|--------|
| **TASK-421** | Create agent-coding-standards.md | DOCS | 2h | 🔴 HIGH | ✅ Session 15 |
| **TASK-423** | Update copilot-instructions with coding rules | DOCS | 1h | 🔴 HIGH | ✅ Session 15 |
| **TASK-433** | Create Agent 6 comprehensive onboarding guide | DOCS | 1h | 🔴 HIGH | ✅ Session 15 |
| **TASK-434** | Create Streamlit code files analysis (file-by-file research) | DOCS | 2h | 🔴 HIGH | ✅ Session 15 |

**Phase E: True Positive Fixes (from code analysis)**
| ID | Task | Agent | Est | Priority | Status |
|----|------|-------|-----|----------|--------|
| **TASK-435** | Fix session_manager.py line 646 division (cost_per_meter) | AGENT_6 | 15m | 🟠 MEDIUM | ✅ PR #337 |
| **TASK-436** | Fix session_manager.py lines 675-676 int() error handling | AGENT_6 | 15m | 🟠 MEDIUM | ⏳ Queued (false positive - dataclass attrs) |
| **TASK-437** | Move imports to module level (session_manager.py) | AGENT_6 | 30m | 🟠 MEDIUM | ✅ PR #337 |

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
| **TASK-460** | Fix Streamlit runtime errors (page_header signature, reportlab, use_container_width deprecation, import checker) | DEV | ✅ PR #354 2026-01-13 |
| **TASK-457-P2** | Documentation Consolidation Phase 2: Archive 3 session-specific research files | DOCS | ✅ 2026-01-13 |
| **RESEARCH-1.3** | Phase 1.3 Bridge to Structural Engineering Complete: Analyzed 4 key papers (Parhi et al. 2026, Hong & Nguyen 2023, etc.) on MOO for RC beams/IS 456. | MAIN | ✅ 2026-01-13 |
| **RESEARCH-1.2** | Phase 1.2 Web Research Complete: 2025-2026 MOO trends consolidated in `KEY-FINDINGS.md` and `PAPER-TRACKER.csv` (20+ papers) | MAIN | ✅ 2026-01-13 |
| **GITDOC-15-28** | Hook enforcement system: versioned hooks, git_ops.sh router, automation-first recovery, health check, test suite (14 tasks, 4 commits) | MAIN | ✅ 2026-01-12 |
| **GITDOC-01-14** | Git workflow automation-first: error clarity, hook capture, CI monitor, docs consolidation (14 tasks, PR #345) | MAIN | ✅ 2026-01-12 |
| **SESSION-19P4** | Git workflow improvements: error clarity, policy-aware merge, docs consistency, enforcement hook | MAIN | ✅ 2026-01-12 |
| **TASK-457** | Add future annotations to 12 core modules (PR #344) | DEV | ✅ 2026-01-12 |
| **SESSION-19** | Python 3.11 Baseline Complete: v0.16.6 released, PR #343 merged | MAIN | ✅ 2026-01-12 |
| **TASK-401** | Scanner Phase 4: Path division, max() patterns (PR #339) | AGENT_6 | ✅ 2026-01-12 |
| **SESSION-16** | PR workflow optimization for solo dev (150-line threshold, Streamlit category) | MAIN | ✅ 2026-01-12 |
| **TASK-435** | Fix session_manager.py division issue (PR #337) | AGENT_6 | ✅ 2026-01-11 |
| **TASK-437** | Move timedelta import to module level (PR #337) | AGENT_6 | ✅ 2026-01-11 |
| **TASK-432** | Archive outdated Agent 6 files | AGENT_6 | ✅ 2026-01-11 |
| **TASK-433** | Create Agent 6 comprehensive onboarding guide (PR #336) | DOCS | ✅ 2026-01-11 |
| **TASK-272** | Code Clause Database (67 clauses, 13 functions decorated, PR #333) | DEV | ✅ 2026-01-11 |
| **TASK-275** | Professional Liability Framework (docs/legal/) | DOCS | ✅ 2026-01-11 |
| **SESSION-14P3** | Git automation: docs/git-automation/ hub (6 files), ai_commit.sh --dry-run/--help, git_automation_health.sh, improvement plan, copilot-instructions update | MAIN | ✅ 2026-01-11 |
| **SESSION-14** | Phase 1: TASKS cleanup (50→15) + v0.17.0 roadmap (6 commits); Phase 2: Agent 8 research (8116 lines analyzed) + consolidation plan + archival + --quick default (5 commits) | MAIN | ✅ 2026-01-11 |
| **ONBOARD-03** | Agent start v2.1: full mode fix, worktree passthrough | DEVOPS | ✅ 2026-01-11 |
| **ONBOARD-02** | Agent start v2.0: unified script, proper preflight | DEVOPS | ✅ 2026-01-11 |
| **ONBOARD-01** | Unified agent_start.sh, consolidated 4 docs (PR #329) | DEVOPS | ✅ 2026-01-11 |
| **TASK-325** | Folder cleanup: archive 14 streamlit files (PR #325) | DEVOPS | ✅ 2026-01-11 |
| **TASK-313** | IS 456 Module Migration (7 modules, 3,048 lines, PR #323) | DEV | ✅ 2026-01-10 |
| **TASK-317** | Update codes/is456/__init__.py exports (PR #324) | DEV | ✅ 2026-01-11 |
| **TASK-312** | IS 456 migration research + automation scripts | ARCHITECT | ✅ 2026-01-10 |
| **TASK-311** | Folder cleanup automation scripts | DEVOPS | ✅ 2026-01-10 |
| **TASK-310** | Multi-code foundation: core/, codes/ (PR #322) | ARCHITECT | ✅ 2026-01-10 |
| **AGENT9-PHASE-B** | Folder Migration (5 commits) | AGENT_9 | ✅ 2026-01-10 |
| **GOV-001-015** | Folder Governance (11 tasks, 4 PRs, S11-S13) | AGENT_9 | ✅ 2026-01-11 |
| **TASK-270** | Fix 8 test failures from API refactoring | TESTER | ✅ 2026-01-10 |
| **TASK-271** | Fix 13 benchmark signature errors | TESTER | ✅ 2026-01-10 |
| **AGENT8-WEEK1** | Git workflow optimizations (4 PRs, 90% faster commits) | AGENT8 | ✅ 2026-01-09 |

> **Full History:** [docs/_archive/tasks-history.md](_archive/tasks-history.md)

---

## Archive

See full task history in [docs/_archive/tasks-history.md](_archive/tasks-history.md)

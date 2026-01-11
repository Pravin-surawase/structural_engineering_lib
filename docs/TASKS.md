# Task Board

> Single source of truth for work. Keep it short and current.

**Updated:** 2026-01-11 (Session 14: TASKS Cleanup & v0.17.0 Planning)

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

- **Version:** v0.16.5 ✅ Released (2026-01-08)
- **Focus:** Folder Structure Governance + Multi-Code Foundation
- **Next:** v0.17.0 (Q1 2026, Weeks 2-4) - Professional Requirements Foundation

---

## v0.17.0 Release Target (Q1 2026 - Weeks 2-4)

**Goal:** Implement first professional engineering requirements

**Focus:** Security, legal compliance, traceability, developer productivity

**Key Deliverables:**
1. 🔴 Security hardening baseline (input validation audit, dependency scanning)
2. 🔴 Professional liability framework (disclaimers, templates, certification guidance)
3. 🔴 Code clause database (JSON DB, @clause decorator, traceability system)
4. 🔴 Interactive testing UI (Streamlit/Gradio for design validation)

**Success Metrics:**
- Security: Input validation audit complete, dependency scanning in CI
- Legal: MIT+engineering disclaimer, templates in docs/legal/
- Traceability: Clause references in 80%+ design functions
- Developer UX: Working Streamlit app for manual validation
- API grade: A- → A (93/100)

---

## Active

*No active tasks. Pick from Up Next and move here when starting.*

---

## Up Next

### v0.17.0 - Critical Path (Must Complete)

> **Phase Approach:** Start with low-risk foundation (security, legal) before high-risk features (Streamlit)

**Phase 1 (Week 2): Foundation (Low Risk, 4-6 hours)**
| ID | Task | Agent | Est | Priority | Blockers |
|----|------|-------|-----|----------|----------|
| **TASK-274** | Security Hardening Baseline (input validation audit, dependency scanning, CI setup) | DEVOPS | 2-3 hrs | 🔴 HIGH | None |
| **TASK-275** | Professional Liability Framework (MIT+engineering disclaimer, templates, certification guidance) | DOCS | 2-3 hrs | 🔴 HIGH | None |

**Phase 2 (Week 3): Traceability (Medium Risk, 4-6 hours)**
| ID | Task | Agent | Est | Priority | Blockers |
|----|------|-------|-----|----------|----------|
| **TASK-272** | Code Clause Database (JSON DB, @clause decorator, traceability) | DEV | 4-6 hrs | 🔴 HIGH | None |

**Phase 3 (Week 4): Developer UX (High Value, 1-2 days)**
| ID | Task | Agent | Est | Priority | Blockers |
|----|------|-------|-----|----------|----------|
| **TASK-273** | Interactive Testing UI (Streamlit basic app with design validation) | DEV | 1-2 days | 🔴 HIGH | Test infrastructure |

> **Note:** TASK-273 depends on stable test infrastructure. If blocked, deliver v0.17.0 with TASK-272/274/275 only.

### v0.18+ - Professional Features Pipeline

> **Goal:** Build on v0.17.0 foundation with advanced professional features
> **Timeline:** Q1-Q2 2026

| ID | Task | Agent | Est | Priority | Status |
|----|------|-------|-----|----------|--------|
| **TASK-276** | Input Flexibility (BeamInput dataclasses, import helpers) | DEV | 4-5 hrs | 🔴 HIGH | ⏳ Queued |
| **TASK-277** | Calculation Report Generation (Jinja2, HTML/PDF) | DEV | 4-5 hrs | 🔴 HIGH | ⏳ Queued |
| **TASK-278** | Verification & Audit Trail (SHA-256, immutable logs) | DEV | 3-4 hrs | 🔴 HIGH | ⏳ Queued |
| **TASK-279** | Engineering Testing Strategies (visual regression, property-based) | TESTER | 4-5 hrs | 🔴 HIGH | ⏳ Queued |

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
| **TASK-280** | Repository hygiene implementation | DEVOPS | ✅ 2026-01-07 |

> **Full History:** [docs/_archive/tasks-history.md](_archive/tasks-history.md)

---

## Archive

See full task history in [docs/_archive/tasks-history.md](_archive/tasks-history.md)

# Task Board

> Single source of truth for work. Keep it short and current.

**Updated:** 2026-01-17 (Session 28)

> **Note:** For detailed specifications, see [docs/planning/](planning/) folder.

---

## Rules (read first)
- **WIP = 2** (max 2 active tasks). Use WIP=2 only for independent tasks.
- Definition of Done: tests pass, docs updated, scanner passes.
- **Archive rule:** Move completed items to [tasks-history.md](_archive/tasks-history.md) after 20+ items.

---

## Current Release

- **Version:** v0.17.5 ✅ Released
- **Focus:** Multi-Objective Optimization + API Validation
- **Next:** v0.18.0 (Q1 2026)

---

## Active

### TASK-602: Modern Streamlit Patterns Adoption (Session 28)

> **Goal:** Apply modern Streamlit patterns (st.fragment, st.dialog, st.badge) to key pages
> **Research:** [streamlit-modern-patterns-research.md](research/streamlit-modern-patterns-research.md)
> **Timeline:** Session 28 (2026-01-17)

| ID | Task | Agent | Est | Priority | Status |
|----|------|-------|-----|----------|--------|
| **TASK-602.1** | Add CacheStatsFragment to beam_design.py (auto-refresh 10s) | MAIN | 30m | 🔴 HIGH | ✅ `88ae05f` |
| **TASK-602.2** | Add show_status_badge for SAFE/UNSAFE display | MAIN | 15m | 🔴 HIGH | ✅ `88ae05f` |
| **TASK-602.4** | Add st.badge to cost_optimizer.py Pareto results | MAIN | 30m | 🟠 MEDIUM | ✅ `9425bc0` |
| **TASK-602.5** | Extract shared constants to utils/constants.py | MAIN | 45m | 🟠 MEDIUM | ✅ `f01ba3f` |
| **TASK-602.6** | Clean TASKS.md and update SESSION_LOG | MAIN | 30m | 🟠 MEDIUM | ⏳ In Progress |

**Key Deliverables:**
- ✅ Auto-refreshing cache stats fragment (replaces manual 30-line expander)
- ✅ Modern badge-based status indicators
- ✅ Centralized constants file for consistency
- ⏳ Clean task board focused on current work

---

## Up Next (Session 29+)

### TASK-603: Remaining Modern Patterns

> **Goal:** Continue modern Streamlit patterns across remaining pages
> **Estimated:** 4-6 hours across 2-3 sessions

| ID | Task | Agent | Est | Priority | Status |
|----|------|-------|-----|----------|--------|
| **TASK-603.1** | Add st.fragment to input sections (3-5 pages) | MAIN | 2h | 🟠 MEDIUM | ⏳ Queued |
| **TASK-603.2** | Add st.dialog for export modals | MAIN | 1h | 🟠 MEDIUM | ⏳ Queued |
| **TASK-603.3** | Apply CacheStatsFragment to other cached pages | MAIN | 1h | 🟡 LOW | ⏳ Queued |
| **TASK-603.4** | Performance optimization with fragments | MAIN | 1h | 🟡 LOW | ⏳ Queued |

### v0.18.0 Pending Work

| ID | Task | Agent | Est | Priority | Status |
|----|------|-------|-----|----------|--------|
| **TASK-502** | VBA test automation (smoke tests) | DEVOPS | 6-8h | 🔴 HIGH | ⏳ Deferred |
| **TASK-522** | Add Jinja2 report templates (3 templates, 25 tests) | DEV | 4h | 🟠 MEDIUM | ✅ PR #360 |
| **TASK-284** | Weekly Governance Sessions (80/20 rule) | AGENT_9 | 3h | 🟠 MEDIUM | ⏳ Queued |

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
| **TASK-601** | Enhanced AppTest framework: integration tests (14 new), fragment utilities, nightly workflow, code quality research | MAIN | ✅ PR #TBD 2026-01-16 |
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

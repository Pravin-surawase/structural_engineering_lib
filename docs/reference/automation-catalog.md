# Automation Script Catalog

**Type:** Reference
**Audience:** All Agents
**Status:** Production Ready
**Importance:** Critical
**Created:** 2025-12-01
**Last Updated:** 2026-01-24

---

> **Purpose:** Complete reference of all automation scripts in this project.
> **For AI Agents:** Use this to discover available automation before implementing manually.
>
> **⚠️ IMPORTANT:** See [Agent Automation Pitfalls](agent-automation-pitfalls.md) for common issues when running automation scripts (git pager lockup, interactive prompts, etc.)

---

## Quick Index

| Category | Scripts | Primary Use Case |
|----------|---------|------------------|
| [Session Management](#session-management) | 6 | Agent onboarding and handoff |
| [Git Workflow](#git-workflow) | 13 | Conflict-free commits and workflow decisions |
| [Documentation Quality](#documentation-quality) | 13 | Link checking, version drift, structure governance |
| [Release Management](#release-management) | 4 | Version bumping, release validation |
| [Testing & Quality](#testing--quality) | 9 | Local CI, pre-commit checks, validation |
| [Code Quality](#code-quality) | 5 | Error handling audits, linting, coverage, license headers |
| [Streamlit QA](#streamlit-qa) | 6 | Streamlit linting, AST validation, page checks |
| [Governance & Monitoring](#governance--monitoring) | 7 | Metrics, dashboards, repo health |
| [Specialized](#specialized) | 8 | DXF rendering, CLI testing, automation helpers |
| [API Validation & Migration](#api-validation--migration) | 10 | V3-critical API and migration validation |
| [Agent Discovery & Diagnostics](#agent-discovery--diagnostics) | 3 | Script discovery, diagnostics, session start |
| [Documentation Quality (Extended)](#documentation-quality-extended) | 8 | Doc creation, similarity, cleanup |
| [Code Quality (Extended)](#code-quality-extended) | 4 | Type checks, imports, circular deps |

**Total: 143 files in scripts/** (75 Python `.py` + 68 Shell `.sh` + README)

---

## AI Automation Audit Readiness Report (2026-01-24)

**Purpose:** Single source report for automation health, testing gaps, quality risks, audit readiness, and next steps.

### 1) Current State — What We Have

**Automation Coverage**
- **143 scripts total** covering git workflow, validation, docs governance, Streamlit QA, CI/CD helpers, and V3 migration.
- **Discovery:** `find_automation.py` + `automation-map.json` provides task→script routing.
- **Catalog:** This file serves as the authoritative reference for all scripts.

**V3 Migration Automation (Validated)**
- `validate_fastapi_schema.py` — 43/43 API functions FastAPI-compatible.
- `test_api_parity.py` — JSON round-trip parity tests pass (3/3).
- `benchmark_api_latency.py` — 0.01ms median, under V3 thresholds.
- `generate_api_routes.py` — scaffolds FastAPI routes + app skeleton.

**Quality & Safety Gates**
- Doc integrity: `check_doc_metadata.py`, `check_doc_similarity.py`, `check_links.py`.
- Streamlit runtime guards: `check_streamlit_issues.py`, `check_fragment_violations.py`.
- Git safety: `ai_commit.sh` (conflict-minimized workflow), PR decision script.

**Recent Finding (Environment Drift)**
- A secondary venv `.venv-1` was auto-created when the interpreter wasn’t pinned.
- Fix applied: workspace now pins `.venv` and auto-activates in terminals.

### 2) What the Project Still Needs (Gaps)

**Testing Infrastructure**
- **Contract tests** for API request/response models (beyond serialization parity).
- **Performance regression baselines** with thresholds enforced in CI.
- **Coverage-driven test matrix** (unit + integration + API-level tests).
- **Test environment parity** (dev/stage/prod config checks + deterministic seeds).
- **Data-driven test suites** for CSV import, adapters, and edge-case geometry.
- **Negative test coverage** for invalid inputs and error messaging consistency.

**Audit Readiness**
- Formal **evidence checklist** (tests run, scanners run, dependency status, linting, coverage).
- **Security posture summary** (dependencies, policies, secrets scanning, SBOM).
- **Traceable change control** summary per release (links to CI artifacts and validations).
- **Risk register** (open defects, mitigations, known limitations).
- **Release evidence bundle** (CI logs + benchmark reports + scanner reports).

**Duplication & Quality**
- Automated **duplication detection** in Python + docs (not just doc similarity).
- Consolidated **shared UI utilities** to prevent repeated logic across Streamlit pages.
- **Single source of truth** enforcement for adapters/import pipelines.

### 3) What Should Be Updated (High Impact)

**Testing & Validation (Priority)**
1. Add **API contract tests** (request/response model validation).
2. Add **benchmark baselines** (p95/p99 thresholds; fail CI on regressions).
3. Add **snapshot tests** for response stability on key API endpoints.
4. Add **test data packs** for import adapters (ETABS, SAFE, CSV).
5. Add **property-based tests** for geometry and load edge cases.

**Audit Readiness**
1. Add `audit_readiness_report.py` (single report output: versions, tests, scanners, coverage).
2. Create **evidence pack** in `docs/audit/` for external reviewers.
3. Add **dependency risk check** into CI (pinning + vulnerability scan summary).
4. Add **release evidence checklist** as part of `end_session.py --fix`.

**Quality & Duplication**
1. Add **duplication scanner** for Python (tokens or AST-level similarity).
2. Add **lint gate** for architectural boundaries (core/app/ui layer rules).
3. Extend Streamlit checks for **dataframe key safety** in UI transformations.
4. Add **adapter contract tests** to prevent regressions in import mapping.

### 4) Audit Readiness (Big Firm Perspective)

**Evidence required by auditors:**
- Test results with pass/fail logs, coverage metrics, and CI proof.
- Code quality reports (lint, static analysis, duplication).
- Dependency list + vulnerabilities (SBOM + advisory scan).
- Change history with PR linkage + validation evidence per release.

**Expected artifacts (proposed):**
- `docs/audit/audit-readiness.md` (summary)
- `docs/audit/audit-evidence-YYYY-MM-DD.md` (checklist with tool outputs)
- `scripts/audit_readiness_report.py` (machine-generated report)

### 5) Git Workflow Upgrade (World-Class)

**Goal:** Faster + safer workflow with auditable traceability.

**Improvements to implement:**
- Standardized **PR templates** with validation checklist.
- Auto-attach **CI artifacts** to releases.
- Enforced **conventional commit** types across all commits.
- Add **release gate** checklist script (one command to verify release readiness).
- Add **change impact report** (API surface diff + doc sync check) per PR.

### 6) Scanner Research Priorities

**Scope:** Define quality gates aligned to architecture + Streamlit rules.

**Research topics:**
- AST-based detection for **unsafe dataframe access** and **zero-division** risks.
- Scanner rules for **architecture boundary violations** (core/app/ui).
- Auto-suppression rules that require explicit justification.
- Add **unit-aware validation** (mm, kN, kN·m, N/mm²) for API parameter checks.

### 7) CI/CD Efficiency (Time Reduction)

**Current risk:** Validation is comprehensive but time-heavy.

**Optimizations:**
- Split CI by **changed paths** (docs vs core vs UI).
- Cache Python dependencies and test artifacts.
- Parallelize `pytest`, scanner checks, and doc validators.
- Add **incremental test selection** based on dependency graph.
- Move heavy validators to **nightly** and keep PR checks fast.

### 8) Additional Points (Audit-Driven)

- Formal **versioned API manifest** with change tracking.
- Track **breaking change risk** in release notes.
- Maintain **performance SLAs** for V3 APIs.
- Define **data retention & privacy** policy for logs/exports.
- Add **access control policy** for generated reports and artifacts.

### 9) Recommended Next Actions

1. Add **audit readiness automation** (report + evidence pack).
2. Add **contract tests** for FastAPI models.
3. Implement **CI path-based optimization**.
4. Create **duplication scanner** (code + docs).
5. Add **architecture boundary lint** for 3-layer enforcement.

### 10) Research Plan (No Implementation Until Complete)

**Research Objectives**
- Validate testing infrastructure maturity vs enterprise expectations.
- Identify duplication and quality hotspots with quantifiable evidence.
- Define audit-ready evidence bundles and automation coverage.
- Propose CI/CD efficiency improvements without reducing safety.

**Primary Evidence Sources (Read First)**
- [docs/contributing/testing-strategy.md](../contributing/testing-strategy.md)
- [docs/git-automation/README.md](../git-automation/README.md)
- [docs/guidelines/streamlit-fragment-best-practices.md](../guidelines/streamlit-fragment-best-practices.md)
- [docs/reference/api.md](../reference/api.md)
- [scripts/index.json](../../scripts/index.json)
- [scripts/automation-map.json](../../scripts/automation-map.json)

**Research Task Map (Automation-First)**

| Research Task | Automation to Use | Output Artifact | Notes |
|---|---|---|---|
| Test coverage posture | `pytest --cov` + `collect_metrics.sh` | coverage summary | Establish baseline and trend |
| CI bottleneck profiling | CI logs + `ci_monitor_daemon.sh` | timing report | Identify longest jobs |
| Duplication inventory | (new) duplication scanner | duplication report | Token/AST similarity |
| API stability review | `check_api_docs_sync.py`, `generate_api_manifest.py` | API diff summary | Track breaking risk |
| Streamlit risk scan | `check_streamlit_issues.py`, `check_fragment_violations.py` | scanner report | Focus on runtime errors |
| Audit evidence set | (new) `audit_readiness_report.py` | audit pack | Evidence bundle for reviewers |

**Key Research Questions**
1. Which tests are **missing for enterprise audit** (contract tests, negative tests, parity)?
2. Where does CI spend the most time, and what can be safely parallelized or cached?
3. Which modules show **duplication risk** or inconsistent error handling?
4. Are audit artifacts **traceable per release** (logs, coverage, scanner outputs)?

### 11) Implementation Gates (Must Pass Before Coding)

**Gate A — Research Complete**
- Documented findings with references and measurable evidence.
- Clear prioritized backlog with estimated impact and effort.

**Gate B — Audit Readiness Definition**
- Evidence checklist defined and mapped to automation scripts.
- Proposed audit pack structure approved.

**Gate C — CI Efficiency Plan**
- Safe path-based filters identified.
- Candidate jobs for nightly vs PR checks agreed.

**Gate D — Quality & Duplication Plan**
- Duplication detection approach chosen (token vs AST).
- Architecture boundary lint rule specification defined.

---

## Session Management

### 1. `start_session.py`

**Purpose:** Initialize AI agent with current project state at session start.

**When to Use:**
- ✅ At the beginning of EVERY session (first 30 seconds)
- ✅ When resuming work after handoff
- ✅ To check project health before starting work

**Usage:**
```bash
# Full check (recommended)
.venv/bin/python scripts/start_session.py

# Quick mode (skip test count check)
.venv/bin/python scripts/start_session.py --quick
```

**What It Does:**
1. Shows version, branch, git status
2. Checks/creates SESSION_LOG entry for today
3. Lists active tasks from TASKS.md
4. Shows blockers
5. Runs doc freshness checks
6. Displays test count (full mode only)

**Output Example:**
```
============================================================
🚀 SESSION START
============================================================
  Version:  v0.14.0
  Branch:   main
  Date:     2026-01-06
  Git:      Clean working tree

📝 Session Log:
  ✅ Entry exists for 2026-01-06

📋 Active Tasks:
  • No active tasks (clean slate)

📖 Read first: docs/handoff.md → docs/agent-bootstrap.md → docs/ai-context-pack.md
============================================================
```

**Related:** [end_session.py](#2-end_sessionpy), [handoff.md](../contributing/handoff.md)

---

### 2. `end_session.py`

**Purpose:** Validate session completeness before handoff to next agent.

**When to Use:**
- ✅ Before ending ANY session
- ✅ Before long breaks (>1 day)
- ✅ Before major handoffs

**Usage:**
```bash
# Check only
.venv/bin/python scripts/end_session.py

# Auto-fix issues
.venv/bin/python scripts/end_session.py --fix

# Quick mode
.venv/bin/python scripts/end_session.py --quick
```

**What It Checks:**
1. 📁 Uncommitted changes in git
2. 🔍 Handoff document freshness (handoff.md, next-session-brief.md)
3. 📝 SESSION_LOG entry completeness
4. 🔗 Doc link validity
5. 📊 Today's activity summary

**Output Example:**
```
============================================================
🛑 SESSION END CHECKS
============================================================

Checking handoff readiness...

✅ No uncommitted changes
✅ handoff.md is current
✅ next-session-brief.md updated within 7 days
✅ SESSION_LOG has entry for today
✅ TASKS.md reflects current state

📊 Today's Activity:
  • 1 commit (d05b48f)
  • 1 research document created
  • Documentation audit completed

✅ Ready for handoff!
============================================================
```

**Related:** [start_session.py](#1-start_sessionpy), [update_handoff.py](#3-update_handoffpy)

---

### 3. `update_handoff.py`

**Purpose:** Auto-generate handoff section in next-session-brief.md.

**When to Use:**
- ✅ After completing major tasks
- ✅ Before running end_session.py
- ✅ When handoff content needs refresh

**Usage:**
```bash
.venv/bin/python scripts/update_handoff.py
```

**What It Does:**
1. Reads recent git commits
2. Extracts task completions
3. Updates HANDOFF:START/END section in next-session-brief.md
4. Preserves manual content outside markers

**Note:** Usually called automatically by end_session.py with --fix flag.

**Related:** [end_session.py](#2-end_sessionpy)

---

### 4. `agent_setup.sh`

**Purpose:** Prepare the environment for agent work (repo checks, tooling sanity, worktree setup).

**When to Use:**
- ✅ Before starting a new agent session
- ✅ When creating a background worktree
- ✅ After major repo updates or environment changes

**Usage:**
```bash
./scripts/agent_setup.sh
./scripts/agent_setup.sh --worktree AGENT_5
./scripts/agent_setup.sh --quick
```

**What It Does:**
- Verifies repo location and required files
- Checks core tooling/venv availability
- Prints next-step guidance for session start

**Related:** [agent_preflight.sh](#5-agent_preflightsh), [start_session.py](#1-start_sessionpy)

---

### 5. `agent_preflight.sh`

**Purpose:** Pre-flight checklist to validate environment readiness before work.

**When to Use:**
- ✅ Right before starting a session
- ✅ After switching branches or worktrees
- ✅ When troubleshooting environment issues

**Usage:**
```bash
./scripts/agent_preflight.sh
./scripts/agent_preflight.sh --quick
./scripts/agent_preflight.sh --fix
```

**What It Does:**
- Runs a focused readiness checklist
- Flags missing dependencies or repo state issues
- Optionally applies safe auto-fixes

**Related:** [agent_setup.sh](#4-agent_setupsh), [start_session.py](#1-start_sessionpy)

---

### 6. `worktree_manager.sh`

**Purpose:** Manage parallel agent worktrees (create/list/submit/cleanup/status).

**When to Use:**
- ✅ Spinning up a background agent workspace
- ✅ Reviewing or cleaning old worktrees
- ✅ Submitting background agent work

**Usage:**
```bash
./scripts/worktree_manager.sh create AGENT_NAME
./scripts/worktree_manager.sh list
./scripts/worktree_manager.sh submit AGENT_NAME "summary"
./scripts/worktree_manager.sh cleanup AGENT_NAME
./scripts/worktree_manager.sh status AGENT_NAME
```

**Related:** [agent_setup.sh](#4-agent_setupsh)

---

## Git Workflow

### 7. `safe_push.sh` ⭐ MANDATORY

**Purpose:** Branch-aware commit and push with conflict prevention.

**When to Use:**
- ✅ **EVERY commit** (MANDATORY — never use manual git commands)
- ✅ Direct commits to main (docs, tests, scripts)
- ✅ Commits within PR branches

**Usage:**
```bash
# Use safe_push directly (it stages internally)
./scripts/safe_push.sh "commit message"

# Example
./scripts/safe_push.sh "docs: update API reference with new functions"
```

**What It Does (8 Steps):**
1. **Auto-stash local changes** (ensures clean sync)
2. **Sync with origin/main** (ff-only on main; feature branches rebase before first push, otherwise merge main)
3. **Stage files** (automation handles staging)
4. **Step 2.5: Pre-flight whitespace check** (detects and fixes before commit)
5. **Commit** (runs pre-commit hooks automatically)
6. **Sync again** (catch race conditions)
7. **Verify safety** (check fast-forward)
8. **Push** (conflict-minimized)

**Why It's Mandatory:**
- ✅ Prevents 90% of merge conflicts
- ✅ Handles pre-commit hook modifications automatically
- ✅ Pull-first workflow prevents divergence
- ✅ Auto-resolves conflicts safely
- ✅ Fixes whitespace BEFORE commit (prevents hash divergence)

**Never Do This:**
```bash
# ❌ WRONG: Manual add/commit/pull/push workflows
# This WILL cause conflicts and wasted time!
```

**Related:** [should_use_pr.sh](#8-should_use_prsh), [verify_git_fix.sh](#10-verify_git_fixsh)

---

### 8. `should_use_pr.sh`

**Purpose:** Decision helper for production-stage workflow (PR vs direct commit).

**When to Use:**
- ✅ Before committing (if unsure about PR requirement)
- ✅ When changing production code
- ✅ To understand decision reasoning
- ✅ Works with staged or unstaged changes

**Usage:**
```bash
# Check decision
./scripts/should_use_pr.sh

# Get explanation
./scripts/should_use_pr.sh --explain

# Optional: staged-only mode
./scripts/should_use_pr.sh --staged-only

# Optional: include untracked files
./scripts/should_use_pr.sh --include-untracked
```

**Exit Codes:**
- **Exit 0:** ✅ Direct commit OK (docs/tests/scripts only)
- **Exit 1:** 🔀 Pull request REQUIRED (production code)

**Decision Matrix:**

| File Type | Decision | Reason |
|-----------|----------|--------|
| docs/** | ✅ Direct commit | Documentation only |
| Python/tests/** | ✅ Direct commit | Tests only (no production code) |
| scripts/** | ✅ Direct commit | Tooling/automation |
| .github/copilot-instructions.md | ✅ Direct commit | Agent rules (low risk) |
| Python/structural_lib/** | 🔀 Pull request | Production code (needs CI validation) |
| VBA/**/*.bas | 🔀 Pull request | Production VBA code |
| Excel/**/*.xlsm | 🔀 Pull request | Production Excel files |
| .github/workflows/** | 🔀 Pull request | CI changes (critical) |
| pyproject.toml | 🔀 Pull request | Dependencies |

**Example:**
```bash
$ ./scripts/should_use_pr.sh --explain
✅ RECOMMENDATION: Direct commit (Documentation only)

Files analyzed:
  • docs/reference/api.md (Documentation)

Reasoning: All changes are low-risk documentation updates.
Safe for direct commit using safe_push.sh.
```

**Related:** [safe_push.sh](#7-safe_pushsh-mandatory), [create_task_pr.sh](#11-create_task_prsh)

---

### 9. `should_use_pr_old.sh`

**Purpose:** Legacy PR decision helper (deprecated).

**Status:** ⚠️ Deprecated — use [should_use_pr.sh](#8-should_use_prsh) instead.

**Usage:**
```bash
./scripts/should_use_pr_old.sh
./scripts/should_use_pr_old.sh --explain
```

**Notes:** Retained for historical reference and comparison testing.

**Related:** [should_use_pr.sh](#8-should_use_prsh)

---

### 10. `verify_git_fix.sh`

**Purpose:** Validate that Step 2.5 whitespace fix works correctly (prevents hash divergence).

**When to Use:**
- ✅ After modifying safe_push.sh
- ✅ To verify git workflow health
- ✅ In CI (runs automatically)

**Usage:**
```bash
./scripts/verify_git_fix.sh
```

**What It Tests (7 Tests):**
1. ✅ Step 2.5 exists in safe_push.sh
2. ✅ Create file with trailing whitespace
3. ✅ Git detects the problem
4. ✅ Apply Step 2.5 fix
5. ✅ Verify whitespace removed
6. ✅ No warnings after fix
7. ✅ Step 2.5 runs before commit

**Why This Exists:** Prevents regression of the git hash divergence bug (pre-commit hooks modifying files during commit, causing different SHA-1 hashes).

**CI Integration:** Runs in `.github/workflows/git-workflow-tests.yml` on every push.

**Related:** [safe_push.sh](#7-safe_pushsh-mandatory), [test_should_use_pr.sh](#8-test_should_use_prsh)

---

### 11. `create_task_pr.sh`

**Purpose:** Create pull request for a task with proper naming and structure.

**When to Use:**
- ✅ Starting work on production code tasks
- ✅ When PR is required (use should_use_pr.sh to check)

**Usage:**
```bash
./scripts/create_task_pr.sh TASK-XXX "short description"

# Example
./scripts/create_task_pr.sh TASK-171 "Add automation catalog"
```

**Preconditions:**
- Clean working tree (no uncommitted changes).
- If you already have changes, temporarily stash them:
  - `git stash push -u -m "temp: create task branch"`
  - Run `create_task_pr.sh`
  - `git stash pop`

**What It Does:**
1. Creates branch: `task/TASK-XXX`
2. Switches to new branch
3. Creates PR with title: `[TASK-XXX] Description`
4. Sets proper labels
5. Links to task in TASKS.md

**Related:** [finish_task_pr.sh](#12-finish_task_prsh), [should_use_pr.sh](#8-should_use_prsh)

---

### 12. `finish_task_pr.sh`

**Purpose:** Complete PR work and merge with proper workflow.

**When to Use:**
- ✅ When task work is complete
- ✅ After all tests pass in CI
- ✅ Before moving task to "Done" in TASKS.md

**Usage:**
```bash
./scripts/finish_task_pr.sh TASK-XXX "completion summary" --async
./scripts/finish_task_pr.sh TASK-XXX "completion summary" --wait
./scripts/finish_task_pr.sh TASK-XXX "completion summary" --with-session-docs

# Example
./scripts/finish_task_pr.sh TASK-171 "Automation catalog with 41 scripts documented" --async
```

**What It Does:**
1. Creates PR with a safe body file (no multiline shell issues)
2. `--async` registers PR with the CI daemon for auto-merge
3. `--wait` polls CI checks and merges when green
4. `--skip` leaves PR open for manual merge
5. `--with-session-docs` updates handoff and enforces session docs before PR

**Related:** [create_task_pr.sh](#11-create_task_prsh)

---

### 13. `cleanup_stale_branches.sh`

**Purpose:** Identify and optionally delete stale local/remote task branches.

**Usage:**
```bash
./scripts/cleanup_stale_branches.sh        # Dry run
./scripts/cleanup_stale_branches.sh --apply
```

**What It Does:**
1. Fetches `origin` with prune
2. Flags local branches merged into `origin/main`
3. Flags remote `origin/task/*` branches with no open PRs
4. Deletes only when `--apply` is passed

**Safety:** Dry-run by default; review before deleting.

---

### 14. `test_should_use_pr.sh`

**Purpose:** Comprehensive test suite for should_use_pr.sh decision logic.

**When to Use:**
- ✅ After modifying should_use_pr.sh
- ✅ To validate workflow decision rules
- ✅ In CI (runs automatically)

**Usage:**
```bash
bash scripts/test_should_use_pr.sh
```

**What It Tests (13 Scenarios):**
- ✅ Direct commit: docs only (5 scenarios)
- ✅ Pull request: production code (8 scenarios)

**Output:**
```
Tests run: 13
Tests passed: 13
Tests failed: 0
✅ ALL TESTS PASSED!
```

**CI Integration:** Runs in `.github/workflows/git-workflow-tests.yml`.

**Related:** [should_use_pr.sh](#8-should_use_prsh), [verify_git_fix.sh](#10-verify_git_fixsh)

---

### 14. `test_git_workflow.sh`

**Purpose:** End-to-end testing of complete git workflow.

**When to Use:**
- ✅ After major git workflow changes
- ✅ To validate entire workflow health
- ✅ Before releasing workflow improvements

**Usage:**
```bash
./scripts/test_git_workflow.sh
```

**What It Tests:**
- Safe push workflow
- PR creation/merge
- Conflict resolution
- Pre-commit hook handling

**Related:** All git workflow scripts

---

### 15. `test_branch_operations.sh`

**Purpose:** Test suite for git branch and worktree operations used by Agent 8.

**When to Use:**
- ✅ After modifying branch/worktree logic
- ✅ When debugging worktree issues
- ✅ As part of git workflow verification

**Usage:**
```bash
./scripts/test_branch_operations.sh
./scripts/test_branch_operations.sh --test N
./scripts/test_branch_operations.sh --verbose
./scripts/test_branch_operations.sh --quick
```

**Related:** [worktree_manager.sh](#6-worktree_managersh), [safe_push.sh](#7-safe_pushsh-mandatory)

---

### 16. `test_merge_conflicts.sh`

**Purpose:** Merge conflict scenario test suite for Agent 8 workflows.

**When to Use:**
- ✅ After changing merge/rebase logic
- ✅ Before rolling out git workflow updates
- ✅ To reproduce conflict handling

**Usage:**
```bash
./scripts/test_merge_conflicts.sh
./scripts/test_merge_conflicts.sh --verbose
./scripts/test_merge_conflicts.sh --test <num>
```

**Related:** [safe_push.sh](#7-safe_pushsh-mandatory), [recover_git_state.sh](#18-recover_git_statesh)

---

### 17. `check_unfinished_merge.sh`

**Purpose:** Detect unfinished merge state (MERGE_HEAD exists).

**When to Use:**
- ✅ Before starting new work
- ✅ When git seems in strange state
- ✅ Part of safe_push.sh checks

**Usage:**
```bash
./scripts/check_unfinished_merge.sh
```

**What It Checks:**
- Presence of `.git/MERGE_HEAD`
- Conflicted files
- Merge in progress

**Action:** If detected, run `./scripts/recover_git_state.sh` to complete the merge safely.

**Related:** [safe_push.sh](#7-safe_pushsh-mandatory)

---

### 18. `recover_git_state.sh`

**Purpose:** Print exact recovery commands for common broken git states.

**When to Use:**
- ✅ When merges/rebases are stuck
- ✅ When branches are diverged
- ✅ When unsure how to recover safely

**Usage:**
```bash
./scripts/recover_git_state.sh
```

**What It Outputs:**
- Specific commands for unfinished merges
- Specific commands for divergence
- Next safe step for clean states

**Related:** [validate_git_state.sh](#19-validate_git_statesh)

---

### 19. `validate_git_state.sh`

**Purpose:** Comprehensive git state validation before operations.

**When to Use:**
- ✅ Before complex git operations
- ✅ To diagnose git issues
- ✅ Part of release process

**Usage:**
```bash
./scripts/validate_git_state.sh
```

**What It Checks:**
- Clean working tree
- On correct branch
- Up to date with remote
- No unfinished merges
- No stashed changes

**Related:** [check_unfinished_merge.sh](#17-check_unfinished_mergesh), [recover_git_state.sh](#18-recover_git_statesh)

---

## Documentation Quality

### 20. `check_links.py`

**Purpose:** Detect broken links in all markdown files.

**When to Use:**
- ✅ Before releasing documentation
- ✅ After moving/renaming files
- ✅ Regular maintenance (weekly)

**Usage:**
```bash
.venv/bin/python scripts/check_links.py

# Check specific directory
.venv/bin/python scripts/check_links.py --dir docs/reference
```

**What It Checks:**
- Internal links (to other docs)
- File existence
- Anchor links (#sections)
- HTTP links (optional)

**Output:**
```
Checking links in 193 markdown files...
✅ All 450 links valid
```

**Related:** [check_docs_index_links.py](#17-check_docs_index_linkspy)

---

### 21. `check_docs_index.py`

**Purpose:** Validate docs/README.md index completeness and structure.

**When to Use:**
- ✅ After adding new documentation files
- ✅ Before release
- ✅ Part of pre-commit hooks

**Usage:**
```bash
.venv/bin/python scripts/check_docs_index.py
```

**What It Checks:**
- All docs listed in index
- Index structure correct
- Categories properly organized
- No orphaned docs

**Related:** [check_docs_index_links.py](#17-check_docs_index_linkspy)

---

### 22. `check_docs_index_links.py`

**Purpose:** Validate all links within docs/README.md index.

**When to Use:**
- ✅ After updating index
- ✅ Part of pre-commit hooks
- ✅ CI validation

**Usage:**
```bash
.venv/bin/python scripts/check_docs_index_links.py
```

**What It Checks:**
- Links point to existing files
- Anchor links valid
- No broken cross-references

**Related:** [check_docs_index.py](#21-check_docs_indexpy), [check_links.py](#20-check_linkspy)

---

### 23. `check_doc_versions.py`

**Purpose:** Detect version number drift in documentation.

**When to Use:**
- ✅ After version bump
- ✅ Before release
- ✅ Part of pre-commit hooks

**Usage:**
```bash
.venv/bin/python scripts/check_doc_versions.py
```

**What It Checks:**
- Version numbers in docs match current version
- No outdated version references
- Consistent version formatting

**Exclusions:**
- `docs/research/` — Allowed to reference external tool versions
- `docs/_archive/` — Historical, frozen content

**Output:**
```
Current version: 0.14.0
✓ No version drift found
```

**Related:** [bump_version.py](#25-bump_versionpy)

---

### 24. `check_api_docs_sync.py`

**Purpose:** Ensure API reference docs match actual code signatures.

**When to Use:**
- ✅ After API changes
- ✅ Before release
- ✅ Part of pre-commit hooks

**Usage:**
```bash
.venv/bin/python scripts/check_api_docs_sync.py
```

**What It Checks:**
- Function signatures match docs
- Parameter descriptions present
- Return types documented
- Examples use valid syntax

**Related:** [check_api_doc_signatures.py](#25-check_api_doc_signaturespy)

---

### 25. `check_api_doc_signatures.py`

**Purpose:** Validate API documentation function signatures are syntactically correct.

**When to Use:**
- ✅ After updating API docs
- ✅ Part of pre-commit hooks
- ✅ CI validation

**Usage:**
```bash
.venv/bin/python scripts/check_api_doc_signatures.py
```

**What It Checks:**
- Python syntax valid in doc code blocks
- Type hints correct
- Consistent formatting

**Related:** [check_api_docs_sync.py](#24-check_api_docs_syncpy)

---

### 26. `check_repo_hygiene.py`

**Purpose:** Ensure hygiene artifacts are not tracked in git.

**When to Use:**
- ✅ Before committing changes
- ✅ During cleanup passes
- ✅ Part of pre-commit hooks

**Usage:**
```bash
.venv/bin/python scripts/check_repo_hygiene.py
```

**What It Checks:**
- Tracked `.DS_Store` files
- Tracked `.coverage` files

**Output:**
```
✓ No tracked hygiene artifacts found
```

**Related:** `.gitignore`

---

### 27. `check_cli_reference.py`

**Purpose:** Validate CLI reference documentation completeness.

**When to Use:**
- ✅ After adding CLI commands
- ✅ Before release
- ✅ Part of pre-commit hooks

**Usage:**
```bash
.venv/bin/python scripts/check_cli_reference.py
```

**What It Checks:**
- All CLI commands documented
- Options/flags described
- Examples provided
- Help text matches docs

**Related:** [check_api_docs_sync.py](#24-check_api_docs_syncpy)

---

### 28. `check_next_session_brief_length.py`

**Purpose:** Ensure next-session-brief.md stays under target length (150 lines).

**When to Use:**
- ✅ After updating brief
- ✅ Part of pre-commit hooks
- ✅ Before handoff

**Usage:**
```bash
.venv/bin/python scripts/check_next_session_brief_length.py
```

**What It Checks:**
- File length < 150 lines (target)
- Warns if > 150 lines
- Suggests archiving old content to SESSION_LOG.md

**Output:**
```
next-session-brief.md: 142 lines ✅ (target <150)
```

**Related:** [end_session.py](#2-end_sessionpy)

---

### 29. `check_root_file_count.sh`

**Purpose:** Enforce root-directory file count limits to prevent sprawl.

**When to Use:**
- ✅ Monthly maintenance or cleanup passes
- ✅ Before adding new root-level files
- ✅ Governance validation

**Usage:**
```bash
./scripts/check_root_file_count.sh
```

**What It Checks:**
- Counts root `.md`, `.txt`, `.sh` files
- Fails if the count exceeds the configured limit

**Related:** [validate_folder_structure.py](#30-validate_folder_structurepy)

---

### 30. `validate_folder_structure.py`

**Purpose:** Validate repo folder structure against governance rules.

**When to Use:**
- ✅ After moving or renaming folders
- ✅ Before running migration phases
- ✅ CI or governance checks

**Usage:**
```bash
.venv/bin/python scripts/validate_folder_structure.py
.venv/bin/python scripts/validate_folder_structure.py --fix
.venv/bin/python scripts/validate_folder_structure.py --report
```

**What It Checks:**
- Root file limits and allowed extensions
- Required top-level folders
- Naming and folder structure rules

**Related:** [check_root_file_count.sh](#29-check_root_file_countsh)

---

### 31. `archive_old_files.sh`

**Purpose:** Archive old files from `docs/_active/` into `docs/_archive/`.

**When to Use:**
- ✅ Monthly maintenance
- ✅ Before repo cleanups
- ✅ When `docs/_active/` grows too large

**Usage:**
```bash
./scripts/archive_old_files.sh
./scripts/archive_old_files.sh --dry-run
```

**What It Does:**
- Moves files older than the retention window into the archive
- Supports dry-run for previewing changes

---

### 32. `archive_old_sessions.sh`

**Purpose:** Archive old session-related docs on a schedule.

**When to Use:**
- ✅ Weekly maintenance
- ✅ After long multi-agent sessions
- ✅ When session docs exceed the target age

**Usage:**
```bash
./scripts/archive_old_sessions.sh
DRY_RUN=1 ./scripts/archive_old_sessions.sh
```

**What It Does:**
- Moves older completion/handoff/session docs into `docs/_archive/`
- Uses age thresholds per document type

---

## Release Management

### 33. `release.py`

**Purpose:** One-command release helper for version bumping and release prep.

**When to Use:**
- ✅ When ready to release new version
- ✅ To automate release workflow
- ✅ Before creating release tag

**Usage:**
```bash
# Interactive mode (recommended)
.venv/bin/python scripts/release.py

# Specify version
.venv/bin/python scripts/release.py --version 0.15.0
```

**What It Does:**
1. Prompts for version number
2. Runs bump_version.py
3. Updates CHANGELOG.md
4. Updates releases.md
5. Updates documentation
6. Commits changes
7. Creates annotated git tag
8. Instructions for pushing tag

**Related:** [bump_version.py](#34-bump_versionpy), [verify_release.py](#35-verify_releasepy)

---

### 34. `bump_version.py`

**Purpose:** Bump version number across all files (Python, VBA, docs).

**When to Use:**
- ✅ Part of release process (called by release.py)
- ✅ Manual version updates

**Usage:**
```bash
.venv/bin/python scripts/bump_version.py 0.15.0
```

**What It Updates:**
- `Python/pyproject.toml`
- `VBA/M00_Version.bas`
- `docs/ai-context-pack.md`
- `docs/planning/next-session-brief.md`
- Other version references

**Related:** [release.py](#33-releasepy), [check_doc_versions.py](#23-check_doc_versionspy)

---

### 35. `verify_release.py`

**Purpose:** Validate release after publishing (local wheel or PyPI).

**When to Use:**
- ✅ After building wheel (before PyPI)
- ✅ After publishing to PyPI
- ✅ To verify installation works

**Usage:**
```bash
# Verify local wheel (pre-release)
.venv/bin/python scripts/verify_release.py --source wheel --wheel-dir Python/dist

# Verify PyPI (post-release)
.venv/bin/python scripts/verify_release.py --version 0.14.0 --source pypi
```

**What It Tests:**
1. Creates clean temporary venv
2. Installs package
3. Imports successfully
4. Runs basic API tests
5. Checks version string
6. Validates entry points

**Important:** Always use a **clean venv** for verification (not project venv).

**Related:** [release.py](#33-releasepy)

---

### 36. `check_release_docs.py`

**Purpose:** Validate release documentation consistency.

**When to Use:**
- ✅ Before release
- ✅ Part of pre-commit hooks
- ✅ CI validation

**Usage:**
```bash
.venv/bin/python scripts/check_release_docs.py
```

**What It Checks:**
- CHANGELOG.md format correct
- releases.md updated
- Version numbers consistent
- Release notes complete

**Related:** [release.py](#33-releasepy), [check_pre_release_checklist.py](#39-check_pre_release_checklistpy)

---

## Testing & Quality

### 37. `ci_local.sh`

**Purpose:** Run full CI suite locally before pushing.

**When to Use:**
- ✅ Before creating PR for major changes
- ✅ Before release
- ✅ To debug CI failures locally

**Usage:**
```bash
./scripts/ci_local.sh
```

**What It Runs:**
1. Python tests (pytest)
2. Coverage check (>80%)
3. Black formatting check
4. Ruff linting
5. Mypy type checking
6. Pre-commit hooks
7. Documentation validation

**Duration:** ~2-3 minutes

**Note:** Uses project venv (`.venv`), installs latest wheel from `Python/dist/`.

**Related:** [quick_check.sh](#38-quick_checksh)

---

### 38. `quick_check.sh`

**Purpose:** Fast pre-commit checks (subset of CI).

**When to Use:**
- ✅ Before every commit (part of workflow)
- ✅ Quick validation during development
- ✅ When full ci_local.sh too slow

**Usage:**
```bash
# Check code only
./scripts/quick_check.sh code

# Check docs only
./scripts/quick_check.sh docs

# Check coverage only
./scripts/quick_check.sh coverage

# All checks
./scripts/quick_check.sh
```

**What It Runs (by mode):**
- **code:** Black, ruff, mypy (30 seconds)
- **docs:** Link checks, version drift (20 seconds)
- **coverage:** Pytest with coverage (60 seconds)

**Related:** [ci_local.sh](#37-ci_localsh)

---

### 39. `check_pre_release_checklist.py`

**Purpose:** Validate pre-release checklist completeness.

**When to Use:**
- ✅ Before every release
- ✅ Part of release workflow
- ✅ CI validation on release tags

**Usage:**
```bash
.venv/bin/python scripts/check_pre_release_checklist.py
```

**What It Checks:**
- [ ] Tests pass (2231+)
- [ ] Coverage >80%
- [ ] Docs updated
- [ ] CHANGELOG.md entry
- [ ] Version bumped
- [ ] API docs synced
- [ ] Examples work

**Output:**
```
Pre-Release Checklist:
✅ Tests passing (2231/2231)
✅ Coverage 86% (target >80%)
✅ Documentation current
✅ CHANGELOG.md updated
✅ Version 0.14.0 consistent
✅ API docs synchronized

✅ Ready for release!
```

**Related:** [release.py](#33-releasepy)

---

### 40. `check_tasks_format.py`

**Purpose:** Validate TASKS.md structure and format.

**When to Use:**
- ✅ After updating TASKS.md
- ✅ Part of pre-commit hooks
- ✅ CI validation

**Usage:**
```bash
.venv/bin/python scripts/check_tasks_format.py
```

**What It Checks:**
- Markdown table format correct
- Task IDs sequential
- Status values valid
- No duplicate IDs
- Proper sections (Active, Up Next, Backlog, Done)

**Related:** [check_session_docs.py](#41-check_session_docspy)

---

### 41. `check_session_docs.py`

**Purpose:** Validate session document consistency (TASKS, SESSION_LOG, next-session-brief).

**When to Use:**
- ✅ Before handoff
- ✅ Part of end_session.py
- ✅ Pre-commit hooks

**Usage:**
```bash
.venv/bin/python scripts/check_session_docs.py
```

**What It Checks:**
- SESSION_LOG has entry for today
- next-session-brief.md updated recently (<7 days)
- TASKS.md reflects current state
- No conflicting task statuses

**Related:** [end_session.py](#2-end_sessionpy), [check_handoff_ready.py](#42-check_handoff_readypy)

---

### 42. `check_handoff_ready.py`

**Purpose:** Comprehensive handoff readiness validation.

**When to Use:**
- ✅ Part of end_session.py
- ✅ Before major handoffs
- ✅ Weekly health checks

**Usage:**
```bash
.venv/bin/python scripts/check_handoff_ready.py
```

**What It Checks:**
- All session docs current
- No uncommitted changes
- Recent work documented
- Links valid
- Tests passing

**Output:** Pass/fail with specific issues listed.

**Related:** [end_session.py](#2-end_sessionpy)

---

### 43. `test_agent_automation.sh`

**Purpose:** Integration test for agent automation workflows.

**When to Use:**
- ✅ After changing agent workflow scripts
- ✅ Before major automation refactors
- ✅ CI verification for agent tooling

**Usage:**
```bash
./scripts/test_agent_automation.sh
```

**What It Tests:**
- Session start/end workflows
- Handoff updates
- Automation script compatibility

---

### 44. `create_test_scaffold.py`

**Purpose:** Generate structured pytest scaffolds for new modules/pages.

**When to Use:**
- ✅ When adding new modules/classes
- ✅ To standardize new test files quickly
- ✅ During refactors that need coverage

**Usage:**
```bash
.venv/bin/python scripts/create_test_scaffold.py ClassName module.path
.venv/bin/python scripts/create_test_scaffold.py BeamDesign streamlit_app.pages.beam_design streamlit_page
```

**What It Does:**
- Generates class/test template with fixtures
- Adds edge-case and error placeholders
- Adds coverage checklist sections

---

### 45. `watch_tests.sh`

**Purpose:** Auto-run tests on file changes (watch mode).

**When to Use:**
- ✅ During rapid development
- ✅ When iterating on tests
- ✅ For instant feedback loops

**Usage:**
```bash
./scripts/watch_tests.sh
./scripts/watch_tests.sh streamlit_app tests/
```

**Requirements:** `fswatch` installed (macOS: `brew install fswatch`).

---

## Code Quality

### 46. `audit_error_handling.py`

**Purpose:** Audit codebase for error handling compliance by layer.

**When to Use:**
- ✅ After adding new modules
- ✅ Before major releases
- ✅ Code quality audits

**Usage:**
```bash
.venv/bin/python scripts/audit_error_handling.py
```

**What It Checks:**
- Core layer: Raises ValueError/TypeError
- App layer: Custom DesignError exceptions
- API layer: Serializes errors to dicts
- UI layer: User-friendly messages
- Compliance with layer architecture

**Output:**
```
Error Handling Audit:
✅ Core: 25/25 modules compliant
✅ App: 8/8 modules compliant
✅ API: 3/3 modules compliant

✅ All layers compliant with error handling strategy
```

**Related:** [Error handling in CONTRIBUTING.md](../contributing/development-guide.md)

---

### 47. `lint_vba.py`

**Purpose:** VBA code linting and style checks.

**When to Use:**
- ✅ After VBA code changes
- ✅ Before committing VBA
- ✅ Code quality audits

**Usage:**
```bash
.venv/bin/python scripts/lint_vba.py

# Check specific module
.venv/bin/python scripts/lint_vba.py VBA/M01_Flexure.bas
```

**What It Checks:**
- CDbl() wrapper usage (Mac safety)
- Variable naming conventions
- Comment presence
- Function complexity
- Code duplication

**Related:** [vba-guide.md](../contributing/vba-guide.md)

---

### 48. `update_test_stats.py`

**Purpose:** Update test statistics JSON file for tracking.

**When to Use:**
- ✅ After test runs
- ✅ Part of CI workflow
- ✅ For metrics tracking

**Usage:**
```bash
.venv/bin/python scripts/update_test_stats.py
```

**What It Does:**
1. Runs pytest with coverage
2. Parses results
3. Updates `Python/test_stats.json`
4. Tracks: count, passed, failed, coverage %

**Output File:** `Python/test_stats.json`
```json
{
  "timestamp": "2026-01-06T10:30:00",
  "total": 2231,
  "passed": 2231,
  "failed": 0,
  "coverage": 86.0
}
```

**Related:** [ci_local.sh](#37-ci_localsh)

---

### 49. `add_license_headers.py`

**Purpose:** Add standardized SPDX license headers to Python and VBA source files.

**When to Use:**
- ✅ After creating new modules
- ✅ One-time standardization (TASK-187)
- ✅ Ensuring license compliance

**Usage:**
```bash
# Dry run (show what would change)
.venv/bin/python scripts/add_license_headers.py --check

# Apply changes
.venv/bin/python scripts/add_license_headers.py --apply
```

**What It Does:**
- Adds SPDX-License-Identifier: MIT header
- Adds copyright notice (c) 2024-2026 Pravin Surawase
- Preserves existing docstrings/comments
- Idempotent (safe to run multiple times)
- Handles Python (.py) and VBA (.bas) files

**Python Header Format:**
```python
# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Module docstring
"""
```

**VBA Header Format:**
```vb
' ==============================================================================
' SPDX-License-Identifier: MIT
' Copyright (c) 2024-2026 Pravin Surawase
' ==============================================================================
```

**Output:**
```
License Header Standardization
Mode: APPLY CHANGES

Processing Python files...
✅ Python/structural_lib/api.py
✅ Python/structural_lib/flexure.py
...

Python: 40 files modified

Processing VBA files...
✅ VBA/Modules/M01_Constants.bas
...

VBA: 33 files modified

Summary:
  Total: 73 modified
```

**Related:** [professional-repo-standards.md](../_archive/research-completed/professional-repo-standards.md), [LICENSE](../../LICENSE)

---

### 50. `check_not_main.sh`

**Purpose:** Prevent accidental commits to main branch (when using PR workflow).

**When to Use:**
- ✅ Part of pre-commit hooks
- ✅ During PR development
- ✅ CI validation

**Usage:**
```bash
./scripts/check_not_main.sh
```

**What It Checks:**
- Current branch is NOT main
- Exits with error if on main (when using PR workflow)

**Note:** Not used when direct commits to main are allowed (docs/tests/scripts).

**Related:** [should_use_pr.sh](#8-should_use_prsh)

---

## Streamlit QA

### 51. `check_streamlit_issues.py`

**Purpose:** Scan Streamlit pages for common AST-level issues.

**When to Use:**
- ✅ Before committing Streamlit changes
- ✅ As part of Streamlit QA checks
- ✅ CI validation for page safety

**Usage:**
```bash
.venv/bin/python scripts/check_streamlit_issues.py --all-pages
.venv/bin/python scripts/check_streamlit_issues.py --page beam_design
.venv/bin/python scripts/check_streamlit_issues.py --all-pages --fail-on critical,high
```

**What It Checks:**
- Undefined variables, unsafe dict access, division-by-zero risks
- Import errors and API signature mismatches
- Streamlit session state patterns

**Related:** [validate_streamlit_page.py](#52-validate_streamlit_pagepy)

---

### 52. `validate_streamlit_page.py`

**Purpose:** Validate a single Streamlit page without launching the UI.

**When to Use:**
- ✅ Quick validation of a specific page
- ✅ Debugging page failures
- ✅ Pre-commit or CI checks

**Usage:**
```bash
.venv/bin/python scripts/validate_streamlit_page.py streamlit_app/pages/01_beam_design.py
```

**Related:** [check_streamlit_issues.py](#51-check_streamlit_issuespy)

---

### 53. `pylint_streamlit.sh`

**Purpose:** Run pylint with Streamlit-focused configuration.

**When to Use:**
- ✅ Linting Streamlit pages
- ✅ Catching static issues before runtime
- ✅ Comparing lint output during refactors

**Usage:**
```bash
./scripts/pylint_streamlit.sh --all-pages
./scripts/pylint_streamlit.sh --page beam_design
./scripts/pylint_streamlit.sh --compare
```

**Related:** [check_streamlit_issues.py](#51-check_streamlit_issuespy)

---

### 54. `test_page.sh`

**Purpose:** Run a focused test pass for a single Streamlit page.

**When to Use:**
- ✅ Fast iteration on a page
- ✅ Pre-commit checks for a specific page
- ✅ Debugging page regressions

**Usage:**
```bash
./scripts/test_page.sh beam_design
```

**What It Runs:**
- Streamlit AST scan
- Imports and lightweight checks
- Page-specific tests (if present)

---

### 55. `auto_fix_page.py`

**Purpose:** Auto-fix common Streamlit page issues in-place.

**When to Use:**
- ✅ After running page validation
- ✅ For common, repetitive fixes
- ✅ Before manual cleanup

**Usage:**
```bash
.venv/bin/python scripts/auto_fix_page.py streamlit_app/pages/01_beam_design.py
```

**What It Fixes:**
- Import path issues
- Theme conflicts
- Missing dependencies
- Syntax errors

---

### 56. `check_cost_optimizer_issues.py`

**Purpose:** Detect common cost-optimizer issues (AST-based).

**When to Use:**
- ✅ Before committing cost-optimizer changes
- ✅ As part of Streamlit QA
- ✅ Pre-commit hooks

**Usage:**
```bash
.venv/bin/python scripts/check_cost_optimizer_issues.py streamlit_app/pages/cost_optimizer.py
```

**What It Checks:**
- Unsafe dict access
- Division without zero checks
- Missing type hints and validation

---

## Governance & Monitoring

### 57. `collect_metrics.sh`

**Purpose:** Collect governance metrics into `metrics/metrics_YYYY-MM-DD.json`.

**When to Use:**
- ✅ Weekly governance sessions
- ✅ Monthly reporting
- ✅ Before generating dashboards

**Usage:**
```bash
./scripts/collect_metrics.sh
```

**Related:** [generate_dashboard.sh](#58-generate_dashboardsh)

---

### 58. `generate_dashboard.sh`

**Purpose:** Generate a metrics dashboard for governance reporting.

**When to Use:**
- ✅ After collecting metrics
- ✅ Monthly review cycles
- ✅ Governance reporting

**Usage:**
```bash
./scripts/generate_dashboard.sh
```

**Output:** `agents/agent-9/governance/METRICS_DASHBOARD.md`

**Related:** [collect_metrics.sh](#57-collect_metricssh)

---

### 59. `repo_health_check.sh`

**Purpose:** Report repository size, file counts, and large file inventory.

**When to Use:**
- ✅ Monthly repo health check
- ✅ Before large migrations
- ✅ Troubleshooting repo bloat

**Usage:**
```bash
./scripts/repo_health_check.sh
```

---

### 60. `governance_session.sh`

**Purpose:** Run weekly governance sessions and track governance ratio.

**When to Use:**
- ✅ Every 4th session (80/20 rule)
- ✅ Governance retrospectives
- ✅ Before major migrations

**Usage:**
```bash
./scripts/governance_session.sh
```

**Related:** [collect_metrics.sh](#57-collect_metricssh)

---

### 61. `comprehensive_validator.py`

**Purpose:** Deep Streamlit page validator with multi-stage analysis.

**When to Use:**
- ✅ Before shipping Streamlit changes
- ✅ When diagnosing complex page failures
- ✅ As part of validation pipelines

**Usage:**
```bash
.venv/bin/python scripts/comprehensive_validator.py streamlit_app/pages/01_beam_design.py
```

---

### 62. `ci_monitor_daemon.sh`

**Purpose:** Background CI monitor for auto-merge workflow.

**When to Use:**
- ✅ When monitoring CI on PRs
- ✅ During agent 8 optimization workflows
- ✅ Long-running PR validation

**Usage:**
```bash
./scripts/ci_monitor_daemon.sh
```

---

### 63. `risk_cache.sh`

**Purpose:** Cache risk scores for faster PR decision checks.

**When to Use:**
- ✅ When optimizing should_use_pr.sh performance
- ✅ In automation scripts that compute risk scores

**Usage:**
```bash
source scripts/risk_cache.sh
```

**Related:** [should_use_pr.sh](#8-should_use_prsh)

---

## Specialized

### 64. `dxf_render.py`

**Purpose:** Render DXF files to PNG/PDF for visual verification.

**When to Use:**
- ✅ After DXF export changes
- ✅ Visual QA of detailing
- ✅ Documentation screenshots

**Usage:**
```bash
# Render to PNG
.venv/bin/python scripts/dxf_render.py input.dxf output.png

# Render to PDF
.venv/bin/python scripts/dxf_render.py input.dxf output.pdf
```

**Requirements:** Optional dependencies (ezdxf + matplotlib or reportlab)

**Install:**
```bash
pip install ezdxf matplotlib reportlab
```

**Related:** DXF export module

---

### 65. `external_cli_test.py`

**Purpose:** Test CLI from external user perspective (S-007 task).

**When to Use:**
- ✅ Before major releases
- ✅ CLI interface changes
- ✅ External validation

**Usage:**
```bash
# Run from repository
.venv/bin/python scripts/external_cli_test.py

# Or test installed package
.venv/bin/python scripts/external_cli_test.py
```

**What It Tests:**
1. CLI commands work
2. Input/output correct
3. Error messages clear
4. Help text accurate
5. Performance acceptable

**Output:** Test report with pass/fail for each scenario.

**Related:** S-007 task in TASKS.md

---

### 66. `autonomous_fixer.py`

**Purpose:** Auto-fix common Streamlit page issues detected by validators.

**When to Use:**
- ✅ After running comprehensive_validator.py
- ✅ For bulk cleanup of Streamlit pages
- ✅ During QA automation

**Usage:**
```bash
.venv/bin/python scripts/autonomous_fixer.py streamlit_app/pages/01_beam_design.py
.venv/bin/python scripts/autonomous_fixer.py streamlit_app/pages --dry-run
```

**Options:**
- `--dry-run` to report fixes without applying
- `--pattern` to select file patterns

**Related:** [comprehensive_validator.py](#61-comprehensive_validatorpy)

---

### 67. `ai_commit.sh`

**Purpose:** Primary entrypoint for safe commits (stages, enforces PR rules, calls safe_push.sh).

**When to Use:**
- ✅ Default for all commits
- ✅ Enforces PR-first workflow rules
- ✅ Avoids manual git usage

**Usage:**
```bash
./scripts/ai_commit.sh "docs: update guide"
```

**What It Does:**
1. Stages all changes
2. Runs `should_use_pr.sh --explain`
3. Blocks if PR is required on main; warns if on a feature branch
4. Delegates to safe_push.sh

**Related:** [safe_push.sh](#7-safe_pushsh-mandatory), [should_use_pr.sh](#8-should_use_prsh)

---

### 68. `quick_push.sh`

**Purpose:** Deprecated legacy script.

**Status:** ⚠️ BLOCKED — Use [ai_commit.sh](#67-ai_commitsh) or [safe_push.sh](#7-safe_pushsh-mandatory).

**Why Deprecated:** Skipped safety checks that caused conflicts.

**Migration:** Replace all `quick_push.sh` calls with `ai_commit.sh`.

**Related:** [ai_commit.sh](#67-ai_commitsh), [safe_push.sh](#7-safe_pushsh-mandatory)

---

### 69. `safe_push_v2.sh`

**Purpose:** Experimental version of safe_push.sh (NOT USED).

**Status:** ⚠️ Experimental — Not in production use.

**Note:** Testing ground for new workflow features. Use [safe_push.sh](#7-safe_pushsh-mandatory) in production.

**Related:** [safe_push.sh](#7-safe_pushsh-mandatory)

---

### 70. `pre_commit_check.sh`

**Purpose:** Manual pre-commit validation (for debugging hooks).

**When to Use:**
- ✅ Debugging pre-commit issues
- ✅ Running hooks manually
- ✅ Testing hook changes

**Usage:**
```bash
./scripts/pre_commit_check.sh
```

**What It Runs:**
- All pre-commit hooks manually
- Same checks as `pre-commit run --all-files`

**Note:** Usually don't need this — pre-commit runs automatically on commit.

**Related:** `.pre-commit-config.yaml`

---

### 71. `pre-push-hook.sh`

**Purpose:** Git pre-push hook (installed in `.git/hooks/`).

**When to Use:**
- ✅ Automatically runs before every push
- ✅ Part of git hooks setup

**What It Checks:**
- Tests passing locally
- No uncommitted changes
- Branch up to date

**Installation:**
```bash
# Usually installed automatically
ln -s ../../scripts/pre-push-hook.sh .git/hooks/pre-push
```

**Note:** Part of git hooks infrastructure.

**Related:** [safe_push.sh](#7-safe_pushsh-mandatory)

---

## API Validation & Migration

### 72. `generate_api_manifest.py`

**Purpose:** Generate or validate the public API manifest for structural_lib.api.

**When to Use:**
- ✅ After adding new API functions
- ✅ Before V3 migration to document stable APIs
- ✅ For FastAPI wrapper generation

**Usage:**
```bash
.venv/bin/python scripts/generate_api_manifest.py
.venv/bin/python scripts/generate_api_manifest.py --validate
.venv/bin/python scripts/generate_api_manifest.py --output docs/reference/api-manifest.json
```

**What It Does:**
1. Introspects `structural_lib.api` module
2. Extracts function signatures and docstrings
3. Generates JSON manifest of public API
4. Validates existing manifest against code

**V3 Relevance:** **Critical** — Documents API surface for FastAPI wrapper generation.

**Related:** [check_api_signatures.py](#73-check_api_signaturespy), [check_api_docs_sync.py](#24-check_api_docs_syncpy)

---

### 73. `check_api_signatures.py`

**Purpose:** Validate that Streamlit pages use correct API signatures and response keys.

**When to Use:**
- ✅ Before committing UI code that calls library
- ✅ Part of pre-commit hooks
- ✅ Ensuring API contract compliance

**Usage:**
```bash
.venv/bin/python scripts/check_api_signatures.py              # Check all pages
.venv/bin/python scripts/check_api_signatures.py --fix        # Show suggested fixes
.venv/bin/python scripts/check_api_signatures.py page.py      # Check specific file
```

**What It Checks:**
- API function call signatures match library
- Response key access matches actual return types
- Type compatibility between UI and library

**V3 Relevance:** **Critical** — Ensures API stability for React migration.

**Related:** [generate_api_manifest.py](#72-generate_api_manifestpy)

---

### 74. `validate_migration.py`

**Purpose:** Validate IS 456 module migration status and correctness.

**When to Use:**
- ✅ After module refactoring
- ✅ Before releases with structural changes
- ✅ V3 migration validation

**Usage:**
```bash
.venv/bin/python scripts/validate_migration.py
.venv/bin/python scripts/validate_migration.py --verbose
.venv/bin/python scripts/validate_migration.py --run-tests
```

**What It Checks:**
1. All expected modules are migrated
2. Re-export stubs work correctly
3. Old import paths still work
4. New import paths work
5. Tests pass

**V3 Relevance:** **Critical** — Module migration validation for V3.

**Related:** [pre_migration_check.py](#75-pre_migration_checkpy), [migrate_module.py](#76-migrate_modulepy)

---

### 75. `pre_migration_check.py`

**Purpose:** Pre-migration validation before making structural changes.

**When to Use:**
- ✅ Before starting migration work
- ✅ Safety checks before refactoring
- ✅ V3 prerequisite validation

**Usage:**
```bash
.venv/bin/python scripts/pre_migration_check.py
.venv/bin/python scripts/pre_migration_check.py --strict
```

**What It Checks:**
- Clean git state
- All tests passing
- No uncommitted changes
- Dependencies stable

**V3 Relevance:** **Critical** — Safety checks before V3 migration.

**Related:** [validate_migration.py](#74-validate_migrationpy)

---

### 76. `migrate_module.py`

**Purpose:** Migrate module to new location with link and import updates.

**When to Use:**
- ✅ Relocating library modules
- ✅ Reorganizing package structure
- ✅ V3 module restructuring

**Usage:**
```bash
.venv/bin/python scripts/migrate_module.py old/path.py new/path.py
.venv/bin/python scripts/migrate_module.py --dry-run old/path.py new/path.py
```

**What It Does:**
1. Moves module to new location
2. Updates all imports across codebase
3. Creates re-export stub at old location
4. Updates documentation links

**V3 Relevance:** **High** — Automates module restructuring for V3.

**Related:** [validate_migration.py](#74-validate_migrationpy)

---

### 77. `validate_stub_exports.py`

**Purpose:** Validate stub module exports for backward compatibility.

**When to Use:**
- ✅ After creating re-export stubs
- ✅ Ensuring backward compatibility
- ✅ V3 export path validation

**Usage:**
```bash
.venv/bin/python scripts/validate_stub_exports.py
```

**Related:** [create_reexport_stub.py](#78-create_reexport_stubpy)

---

### 78. `create_reexport_stub.py`

**Purpose:** Create re-export stub module for backward compatibility.

**When to Use:**
- ✅ After moving modules
- ✅ Maintaining old import paths
- ✅ Migration transition period

**Usage:**
```bash
.venv/bin/python scripts/create_reexport_stub.py old/path.py new/path.py
```

**Related:** [migrate_module.py](#76-migrate_modulepy)

---

### 79. `validate_fastapi_schema.py` 🆕

**Purpose:** Validate all API functions are FastAPI-compatible for V3 migration.

**When to Use:**
- ✅ Before V3 FastAPI implementation starts
- ✅ After adding new API functions
- ✅ V3 readiness checks

**Usage:**
```bash
.venv/bin/python scripts/validate_fastapi_schema.py
.venv/bin/python scripts/validate_fastapi_schema.py --verbose
.venv/bin/python scripts/validate_fastapi_schema.py --generate-stubs
```

**What It Checks:**
1. All API functions have type hints
2. Parameters are JSON-serializable types
3. Return types are dataclasses (serializable)
4. No incompatible types (e.g., untyped Any)

**V3 Relevance:** **CRITICAL** — Must pass before FastAPI wrapper generation.

**Related:** [test_api_parity.py](#80-test_api_paritypy), [benchmark_api_latency.py](#81-benchmark_api_latencypy)

---

### 80. `test_api_parity.py` 🆕

**Purpose:** Test that FastAPI endpoints return identical results to direct library calls.

**When to Use:**
- ✅ After FastAPI wrapper changes
- ✅ V3 serialization validation
- ✅ Regression testing before releases

**Usage:**
```bash
.venv/bin/python scripts/test_api_parity.py
.venv/bin/python scripts/test_api_parity.py --verbose
.venv/bin/python scripts/test_api_parity.py --function design_beam_is456
```

**What It Does:**
1. Calls library function directly
2. Simulates FastAPI JSON round-trip (serialize → deserialize)
3. Compares results with tolerance for floats
4. Handles Enum↔string and dataclass conversion

**V3 Relevance:** **CRITICAL** — Ensures React frontend gets same results as Streamlit.

**Related:** [validate_fastapi_schema.py](#79-validate_fastapi_schemapy)

---

### 81. `benchmark_api_latency.py` 🆕

**Purpose:** Benchmark API function latency against V3 thresholds.

**When to Use:**
- ✅ V3 performance validation
- ✅ After optimization changes
- ✅ CI performance regression checks

**Usage:**
```bash
.venv/bin/python scripts/benchmark_api_latency.py
.venv/bin/python scripts/benchmark_api_latency.py --iterations 100
.venv/bin/python scripts/benchmark_api_latency.py --detailed
```

**What It Measures:**
- Min/max/mean/median/p95/p99 latency
- V3 threshold validation (<50ms for simple, <75ms for complex)
- Warmup runs to exclude JIT effects

**V3 Relevance:** **CRITICAL** — V3 requires <100ms for smooth 3D preview.

**Related:** [validate_fastapi_schema.py](#79-validate_fastapi_schemapy)

---

## Agent Discovery & Diagnostics

### 82. `find_automation.py`

**Purpose:** Find automation scripts for a given task description.

**When to Use:**
- ✅ Before doing any task manually
- ✅ Agent onboarding / discovery
- ✅ Finding the right script for a job

**Usage:**
```bash
.venv/bin/python scripts/find_automation.py "your task"
.venv/bin/python scripts/find_automation.py --list
.venv/bin/python scripts/find_automation.py --category git_workflow
```

**What It Does:**
1. Searches automation-map.json for matching tasks
2. Returns relevant scripts with usage examples
3. Shows context docs for the task

**V3 Relevance:** **High** — Essential for agent onboarding.

**Related:** [automation-map.json](../../scripts/automation-map.json)

---

### 83. `collect_diagnostics.py`

**Purpose:** Bundle debug context (environment, git state, logs) for troubleshooting.

**When to Use:**
- ✅ When debugging issues
- ✅ Before asking for help
- ✅ CI failure analysis

**Usage:**
```bash
.venv/bin/python scripts/collect_diagnostics.py
.venv/bin/python scripts/collect_diagnostics.py --output diagnostics.json
```

**What It Collects:**
- Python version and environment
- Git state and recent commits
- Recent error logs
- Dependency versions

**Related:** [repo_health_check.sh](#59-repo_health_checksh)

---

### 84. `agent_start.sh`

**Purpose:** Unified session start combining setup, preflight, and session initialization.

**When to Use:**
- ✅ **EVERY session start** (first command)
- ✅ Quick onboarding (30 seconds)

**Usage:**
```bash
./scripts/agent_start.sh --quick     # Fast mode (recommended)
./scripts/agent_start.sh             # Full validation
./scripts/agent_start.sh --agent 9   # Agent-specific guidance
```

**What It Does:**
1. Installs git hooks
2. Runs environment setup
3. Runs pre-flight checks
4. Starts session tracking
5. Shows active tasks and blockers

**V3 Relevance:** **High** — Tier 0 daily script.

**Related:** [end_session.py](#2-end_sessionpy)

---

## Documentation Quality (Extended)

### 85. `create_doc.py`

**Purpose:** Create new document with proper metadata headers.

**When to Use:**
- ✅ Creating any new documentation file
- ✅ Ensures consistent metadata format
- ✅ Prevents duplicate document creation

**Usage:**
```bash
.venv/bin/python scripts/create_doc.py docs/path/file.md "Document Title"
.venv/bin/python scripts/create_doc.py docs/research/topic.md "Topic Research" --type=Research --status=Draft
```

**Options:**
- `--type`: Research, Guide, Reference, Architecture, Decision
- `--status`: Draft, Approved, Deprecated
- `--importance`: Critical, High, Medium, Low
- `--tasks`: Related task IDs

**What It Does:**
1. Checks for similar existing documents
2. Creates file with proper metadata header
3. Updates docs-index.json if needed

**Related:** [check_doc_similarity.py](#83-check_doc_similaritypy)

---

### 86. `check_doc_similarity.py`

**Purpose:** Find similar documents before creating new ones (prevents duplicates).

**When to Use:**
- ✅ Before creating any new document
- ✅ Part of create_doc.py workflow
- ✅ Finding canonical docs for a topic

**Usage:**
```bash
.venv/bin/python scripts/check_doc_similarity.py "your topic"
```

**What It Does:**
1. Checks docs-canonical.json for existing topic
2. Searches for similar document titles
3. Returns potential duplicates to review

**Related:** [create_doc.py](#82-create_docpy), [docs-canonical.json](../docs-canonical.json)

---

### 87. `check_doc_metadata.py`

**Purpose:** Validate document metadata headers are complete and correct.

**When to Use:**
- ✅ Pre-commit hooks
- ✅ Documentation quality audits
- ✅ Before releases

**Usage:**
```bash
.venv/bin/python scripts/check_doc_metadata.py
.venv/bin/python scripts/check_doc_metadata.py --fix
```

**What It Checks:**
- Type, Audience, Status, Importance fields
- Created/Last Updated dates
- Proper format and values

**Related:** [check_doc_frontmatter.py](#85-check_doc_frontmatterpy)

---

### 88. `check_doc_frontmatter.py`

**Purpose:** Check document frontmatter format and completeness.

**When to Use:**
- ✅ Documentation validation
- ✅ Pre-commit hooks

**Usage:**
```bash
.venv/bin/python scripts/check_doc_frontmatter.py
```

**Related:** [check_doc_metadata.py](#84-check_doc_metadatapy)

---

### 89. `fix_broken_links.py`

**Purpose:** Find and auto-fix broken internal markdown links.

**When to Use:**
- ✅ After moving/renaming files
- ✅ Regular documentation maintenance
- ✅ Before releases

**Usage:**
```bash
.venv/bin/python scripts/fix_broken_links.py           # Check only
.venv/bin/python scripts/fix_broken_links.py --fix     # Auto-fix
.venv/bin/python scripts/fix_broken_links.py --dry-run # Preview fixes
```

**What It Does:**
1. Scans all markdown files for links
2. Identifies broken internal links
3. Attempts to find correct target
4. Updates links automatically with --fix

**Related:** [check_links.py](#20-check_linkspy)

---

### 90. `find_orphan_files.py`

**Purpose:** Find files that are not referenced from any other document.

**When to Use:**
- ✅ Documentation cleanup
- ✅ Identifying unused files
- ✅ Before archiving

**Usage:**
```bash
.venv/bin/python scripts/find_orphan_files.py
.venv/bin/python scripts/find_orphan_files.py --dir docs/research
```

**Related:** [consolidate_docs.py](#88-consolidate_docspy)

---

### 91. `consolidate_docs.py`

**Purpose:** Consolidate similar or redundant documentation files.

**When to Use:**
- ✅ Documentation cleanup
- ✅ Reducing doc sprawl
- ✅ Archiving completed research

**Usage:**
```bash
.venv/bin/python scripts/consolidate_docs.py analyze    # Find redundancy
.venv/bin/python scripts/consolidate_docs.py archive    # Move completed to archive
.venv/bin/python scripts/consolidate_docs.py merge      # Merge similar docs
```

**Related:** [analyze_doc_redundancy.py](#89-analyze_doc_redundancypy)

---

### 92. `analyze_doc_redundancy.py`

**Purpose:** Analyze documentation for redundant content.

**When to Use:**
- ✅ Documentation audits
- ✅ Cleanup planning

**Usage:**
```bash
.venv/bin/python scripts/analyze_doc_redundancy.py
```

**Related:** [consolidate_docs.py](#88-consolidate_docspy)

---

## Code Quality (Extended)

### 93. `check_circular_imports.py`

**Purpose:** Detect circular import issues in the codebase.

**When to Use:**
- ✅ After adding new modules
- ✅ Debugging import errors
- ✅ Architecture validation

**Usage:**
```bash
.venv/bin/python scripts/check_circular_imports.py
.venv/bin/python scripts/check_circular_imports.py --verbose
```

**V3 Relevance:** **High** — Clean architecture is essential for FastAPI.

**Related:** [check_type_annotations.py](#91-check_type_annotationspy)

---

### 94. `check_type_annotations.py`

**Purpose:** Validate type annotations across the codebase.

**When to Use:**
- ✅ Before V3 migration
- ✅ Type safety audits
- ✅ FastAPI requires good types

**Usage:**
```bash
.venv/bin/python scripts/check_type_annotations.py
.venv/bin/python scripts/check_type_annotations.py --strict
```

**V3 Relevance:** **High** — FastAPI relies on type annotations for validation.

**Related:** [check_circular_imports.py](#90-check_circular_importspy)

---

### 95. `check_fragment_violations.py`

**Purpose:** Detect Streamlit fragment API violations.

**When to Use:**
- ✅ After using @st.fragment decorator
- ✅ Preventing runtime errors
- ✅ Pre-commit hooks

**Usage:**
```bash
.venv/bin/python scripts/check_fragment_violations.py
```

**What It Checks:**
- st.sidebar usage inside @st.fragment
- st.tabs usage inside @st.fragment
- Other forbidden patterns

**Related:** [streamlit-fragment-best-practices.md](../guidelines/streamlit-fragment-best-practices.md)

---

### 96. `check_streamlit_imports.py`

**Purpose:** Validate Streamlit page imports are correct.

**When to Use:**
- ✅ Before committing Streamlit changes
- ✅ Debugging import errors
- ✅ Pre-commit hooks

**Usage:**
```bash
.venv/bin/python scripts/check_streamlit_imports.py
.venv/bin/python scripts/check_streamlit_imports.py --all-pages
```

**Related:** [check_streamlit_issues.py](#51-check_streamlit_issuespy)

---

## Best Practices

### When Starting Work
1. ✅ Run [start_session.py](#1-start_sessionpy) (30 seconds)
2. ✅ Check [TASKS.md](../TASKS.md) for active work
3. ✅ Review [next-session-brief.md](../planning/next-session-brief.md)

### During Development
1. ✅ Use [ai_commit.sh](#67-ai_commitsh) for ALL commits
2. ✅ Check [should_use_pr.sh](#8-should_use_prsh) if unsure about PR
3. ✅ Run [quick_check.sh](#38-quick_checksh) before commits
4. ✅ Use [ci_local.sh](#37-ci_localsh) before major changes

### Before Ending Session
1. ✅ Run [end_session.py](#2-end_sessionpy) --fix
2. ✅ Update [next-session-brief.md](../planning/next-session-brief.md)
3. ✅ Move tasks to Done in [TASKS.md](../TASKS.md)
4. ✅ Commit all doc changes

### Before Release
1. ✅ Run [ci_local.sh](#37-ci_localsh)
2. ✅ Run [check_pre_release_checklist.py](#39-check_pre_release_checklistpy)
3. ✅ Use [release.py](#33-releasepy) for version bump
4. ✅ Verify with [verify_release.py](#35-verify_releasepy)

---

## Troubleshooting

### "Command not found" Error
```bash
# Ensure you're in project root
cd /path/to/structural_engineering_lib

# Make scripts executable
chmod +x scripts/*.sh

# Use full path for Python scripts
.venv/bin/python scripts/script_name.py
```

### Git Workflow Issues
- Always use [ai_commit.sh](#67-ai_commitsh) — never manual git
- Run [check_unfinished_merge.sh](#17-check_unfinished_mergesh) if git seems stuck
- Use [recover_git_state.sh](#18-recover_git_statesh) for exact recovery steps
- Use [validate_git_state.sh](#19-validate_git_statesh) to diagnose

### Pre-commit Hook Issues
- Run [pre_commit_check.sh](#70-pre_commit_checksh) manually to debug
- Check `.pre-commit-config.yaml` is up to date
- Re-install hooks: `pre-commit install`

### CI Failures
- Run [ci_local.sh](#37-ci_localsh) to reproduce locally
- Check [quick_check.sh](#38-quick_checksh) for specific failures
- Review CI logs on GitHub

---

## Related Documentation

- [Git Workflow for AI Agents](../contributing/git-workflow-ai-agents.md) (canonical)
- [Development Guide](../contributing/development-guide.md)
- [handoff.md](../contributing/handoff.md) — Session management workflow
- [ai-context-pack.md](../getting-started/ai-context-pack.md) — Agent entrypoint

---

**Last Updated:** 2026-01-24
**Maintained By:** Project automation
**Questions?** See [troubleshooting.md](troubleshooting.md) or [SUPPORT.md](../../.github/SUPPORT.md)

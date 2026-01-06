# Automation Script Catalog

> **Purpose:** Complete reference of all 41 automation scripts in this project.
> **For AI Agents:** Use this to discover available automation before implementing manually.
> **Last Updated:** 2026-01-06

---

## Quick Index

| Category | Scripts | Primary Use Case |
|----------|---------|------------------|
| [Session Management](#session-management) | 3 | Agent onboarding and handoff |
| [Git Workflow](#git-workflow) | 9 | Conflict-free commits and workflow decisions |
| [Documentation Quality](#documentation-quality) | 8 | Link checking, version drift, consistency |
| [Release Management](#release-management) | 4 | Version bumping, release validation |
| [Testing & Quality](#testing--quality) | 5 | Local CI, pre-commit checks, validation |
| [Code Quality](#code-quality) | 4 | Error handling audits, linting, coverage |
| [Specialized](#specialized) | 8 | DXF rendering, CLI testing, VBA linting |

**Total: 41 scripts** (17 shell `.sh` + 24 Python `.py`)

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

📖 Read first: docs/HANDOFF.md → docs/AGENT_BOOTSTRAP.md → docs/AI_CONTEXT_PACK.md
============================================================
```

**Related:** [end_session.py](#2-end_sessionpy), [HANDOFF.md](../HANDOFF.md)

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
2. 🔍 Handoff document freshness (HANDOFF.md, next-session-brief.md)
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
✅ HANDOFF.md is current
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

## Git Workflow

### 4. `safe_push.sh` ⭐ MANDATORY

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
3. **Stage files** (git add)
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
# ❌ WRONG: Manual git workflow
git add .
git commit -m "message"
git pull
git push
# This WILL cause conflicts and wasted time!
```

**Related:** [should_use_pr.sh](#5-should_use_prsh), [verify_git_fix.sh](#6-verify_git_fixsh)

---

### 5. `should_use_pr.sh`

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
$ git add docs/reference/api.md
$ ./scripts/should_use_pr.sh --explain
✅ RECOMMENDATION: Direct commit (Documentation only)

Files analyzed:
  • docs/reference/api.md (Documentation)

Reasoning: All changes are low-risk documentation updates.
Safe for direct commit using safe_push.sh.
```

**Related:** [safe_push.sh](#4-safe_pushsh-mandatory), [create_task_pr.sh](#7-create_task_prsh)

---

### 6. `verify_git_fix.sh`

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

**Related:** [safe_push.sh](#4-safe_pushsh-mandatory), [test_should_use_pr.sh](#8-test_should_use_prsh)

---

### 7. `create_task_pr.sh`

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
1. Creates branch: `task-XXX-description`
2. Switches to new branch
3. Creates PR with title: `[TASK-XXX] Description`
4. Sets proper labels
5. Links to task in TASKS.md

**Related:** [finish_task_pr.sh](#8-finish_task_prsh), [should_use_pr.sh](#5-should_use_prsh)

---

### 8. `finish_task_pr.sh`

**Purpose:** Complete PR work and merge with proper workflow.

**When to Use:**
- ✅ When task work is complete
- ✅ After all tests pass in CI
- ✅ Before moving task to "Done" in TASKS.md

**Usage:**
```bash
./scripts/finish_task_pr.sh TASK-XXX "completion summary"

# Example
./scripts/finish_task_pr.sh TASK-171 "Automation catalog with 41 scripts documented"
```

**What It Does:**
1. Verifies CI passed
2. Squash merges PR
3. Deletes branch
4. Updates TASKS.md (moves to Done)
5. Switches back to main

**Related:** [create_task_pr.sh](#7-create_task_prsh)

---

### 9. `test_should_use_pr.sh`

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

**Related:** [should_use_pr.sh](#5-should_use_prsh), [verify_git_fix.sh](#6-verify_git_fixsh)

---

### 10. `test_git_workflow.sh`

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

### 11. `check_unfinished_merge.sh`

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

**Action:** If detected, complete merge with `git commit --no-edit` then push.

**Related:** [safe_push.sh](#4-safe_pushsh-mandatory)

---

### 12. `recover_git_state.sh`

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

**Related:** [validate_git_state.sh](#13-validate_git_statesh)

---

### 13. `validate_git_state.sh`

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

**Related:** [check_unfinished_merge.sh](#11-check_unfinished_mergesh), [recover_git_state.sh](#12-recover_git_statesh)

---

## Documentation Quality

### 13. `check_links.py`

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

### 14. `check_docs_index.py`

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

### 15. `check_docs_index_links.py`

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

**Related:** [check_docs_index.py](#14-check_docs_indexpy), [check_links.py](#13-check_linkspy)

---

### 16. `check_doc_versions.py`

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

### 17. `check_api_docs_sync.py`

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

**Related:** [check_api_doc_signatures.py](#18-check_api_doc_signaturespy)

---

### 18. `check_api_doc_signatures.py`

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

**Related:** [check_api_docs_sync.py](#17-check_api_docs_syncpy)

---

### 19. `check_cli_reference.py`

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

**Related:** [check_api_docs_sync.py](#17-check_api_docs_syncpy)

---

### 20. `check_next_session_brief_length.py`

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

## Release Management

### 21. `release.py`

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
4. Updates RELEASES.md
5. Updates documentation
6. Commits changes
7. Creates annotated git tag
8. Instructions for pushing tag

**Related:** [bump_version.py](#22-bump_versionpy), [verify_release.py](#23-verify_releasepy)

---

### 22. `bump_version.py`

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
- `docs/AI_CONTEXT_PACK.md`
- `docs/planning/next-session-brief.md`
- Other version references

**Related:** [release.py](#21-releasepy), [check_doc_versions.py](#16-check_doc_versionspy)

---

### 23. `verify_release.py`

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

**Related:** [release.py](#21-releasepy)

---

### 24. `check_release_docs.py`

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
- RELEASES.md updated
- Version numbers consistent
- Release notes complete

**Related:** [release.py](#21-releasepy), [check_pre_release_checklist.py](#27-check_pre_release_checklistpy)

---

## Testing & Quality

### 25. `ci_local.sh`

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

**Related:** [quick_check.sh](#26-quick_checksh)

---

### 26. `quick_check.sh`

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

**Related:** [ci_local.sh](#25-ci_localsh)

---

### 27. `check_pre_release_checklist.py`

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

**Related:** [release.py](#21-releasepy)

---

### 28. `check_tasks_format.py`

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

**Related:** [check_session_docs.py](#29-check_session_docspy)

---

### 29. `check_session_docs.py`

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

**Related:** [end_session.py](#2-end_sessionpy), [check_handoff_ready.py](#30-check_handoff_readypy)

---

### 30. `check_handoff_ready.py`

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

## Code Quality

### 31. `audit_error_handling.py`

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

### 32. `lint_vba.py`

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

**Related:** [VBA_GUIDE.md](../VBA_GUIDE.md)

---

### 33. `update_test_stats.py`

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

**Related:** [ci_local.sh](#25-ci_localsh)

---

### 34. `check_not_main.sh`

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

**Related:** [should_use_pr.sh](#5-should_use_prsh)

---

## Specialized

### 35. `dxf_render.py`

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

### 36. `external_cli_test.py`

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
python scripts/external_cli_test.py
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

### 37. `ai_commit.sh`

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

**Related:** [safe_push.sh](#4-safe_pushsh-mandatory), [should_use_pr.sh](#5-should_use_prsh)

---

### 38. `quick_push.sh`

**Purpose:** Deprecated legacy script.

**Status:** ⚠️ BLOCKED — Use [ai_commit.sh](#37-ai_commitsh) or [safe_push.sh](#4-safe_pushsh-mandatory).

**Why Deprecated:** Skipped safety checks that caused conflicts.

**Migration:** Replace all `quick_push.sh` calls with `ai_commit.sh`.

**Related:** [ai_commit.sh](#37-ai_commitsh), [safe_push.sh](#4-safe_pushsh-mandatory)

---

### 39. `safe_push_v2.sh`

**Purpose:** Experimental version of safe_push.sh (NOT USED).

**Status:** ⚠️ Experimental — Not in production use.

**Note:** Testing ground for new workflow features. Use [safe_push.sh](#4-safe_pushsh-mandatory) in production.

**Related:** [safe_push.sh](#4-safe_pushsh-mandatory)

---

### 40. `pre_commit_check.sh`

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

### 41. `pre-push-hook.sh`

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

**Related:** [safe_push.sh](#4-safe_pushsh-mandatory)

---

## Best Practices

### When Starting Work
1. ✅ Run [start_session.py](#1-start_sessionpy) (30 seconds)
2. ✅ Check [TASKS.md](../TASKS.md) for active work
3. ✅ Review [next-session-brief.md](../planning/next-session-brief.md)

### During Development
1. ✅ Use [ai_commit.sh](#37-ai_commitsh) for ALL commits
2. ✅ Check [should_use_pr.sh](#5-should_use_prsh) if unsure about PR
3. ✅ Run [quick_check.sh](#26-quick_checksh) before commits
4. ✅ Use [ci_local.sh](#25-ci_localsh) before major changes

### Before Ending Session
1. ✅ Run [end_session.py](#2-end_sessionpy) --fix
2. ✅ Update [next-session-brief.md](../planning/next-session-brief.md)
3. ✅ Move tasks to Done in [TASKS.md](../TASKS.md)
4. ✅ Commit all doc changes

### Before Release
1. ✅ Run [ci_local.sh](#25-ci_localsh)
2. ✅ Run [check_pre_release_checklist.py](#27-check_pre_release_checklistpy)
3. ✅ Use [release.py](#21-releasepy) for version bump
4. ✅ Verify with [verify_release.py](#23-verify_releasepy)

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
- Always use [ai_commit.sh](#37-ai_commitsh) — never manual git
- Run [check_unfinished_merge.sh](#11-check_unfinished_mergesh) if git seems stuck
- Use [recover_git_state.sh](#12-recover_git_statesh) for exact recovery steps
- Use [validate_git_state.sh](#13-validate_git_statesh) to diagnose

### Pre-commit Hook Issues
- Run [pre_commit_check.sh](#40-pre_commit_checksh) manually to debug
- Check `.pre-commit-config.yaml` is up to date
- Re-install hooks: `pre-commit install`

### CI Failures
- Run [ci_local.sh](#25-ci_localsh) to reproduce locally
- Check [quick_check.sh](#26-quick_checksh) for specific failures
- Review CI logs on GitHub

---

## Related Documentation

- [Git Workflow Quick Reference](../contributing/git-workflow-quick-reference.md)
- [Git Workflow for AI Agents](../contributing/git-workflow-for-ai-agents.md)
- [Development Guide](../contributing/development-guide.md)
- [HANDOFF.md](../HANDOFF.md) — Session management workflow
- [AI_CONTEXT_PACK.md](../AI_CONTEXT_PACK.md) — Agent entrypoint

---

**Last Updated:** 2026-01-06
**Maintained By:** Project automation
**Questions?** See [TROUBLESHOOTING.md](../TROUBLESHOOTING.md) or [SUPPORT.md](../../SUPPORT.md)

# Git Automation Scripts Reference

**Type:** Reference
**Audience:** All Agents
**Status:** Production Ready
**Importance:** High
**Version:** 0.16.6
**Created:** 2026-01-11
**Last Updated:** 2026-01-11
**Related Tasks:** Documentation consolidation

---

## Overview

Complete reference for all 103 git automation scripts. Organized by use case for quick lookup.

**Script Location:** All scripts are in `scripts/` (project root)

---

## 🎯 Quick Reference (Most Used)

| Command | Purpose | Time |
|---------|---------|------|
| `./scripts/ai_commit.sh "msg"` | **Commit & push** | ~10s |
| `./scripts/agent_start.sh --quick` | **Session setup** | ~6s |
| `./scripts/should_use_pr.sh --explain` | **PR decision** | ~2s |
| `./scripts/recover_git_state.sh` | **Emergency recovery** | ~5s |
| `./scripts/git_ops.sh --status` | **State analysis & recommendation** | ~2s |
| `./scripts/git_automation_health.sh` | **Check all automation** | ~3s |

---

## 📋 Scripts by Category

### 1. Core Workflow Scripts

**`ai_commit.sh`** (2.6KB) - Primary Entry Point
```bash
./scripts/ai_commit.sh "your commit message"
```
- **Purpose:** Single entry point for ALL commits
- **Features:**
  - Decides PR vs direct commit automatically
  - Calls `safe_push.sh` for direct commits
  - Calls `create_task_pr.sh` for PR workflow
  - Logs all operations to `git_operations_log/`
- **Success Rate:** 100%
- **See:** [workflow-guide.md](workflow-guide.md) for protocol

**`safe_push.sh`** (13KB) - Core Workflow Engine
```bash
./scripts/safe_push.sh "commit message"
```
- **Purpose:** 7-step conflict-minimized push workflow
- **Steps:**
  1. Stash local changes
  2. Background fetch (parallel)
  3. Stage files
  4. Pre-flight whitespace check & fix
  5. Commit (pre-commit hooks run)
  6. Pull (sync with remote)
  7. Push (fast-forward only)
- **Features:**
  - Auto-fixes whitespace (226-413 files typical)
  - Handles pre-commit modifications
  - Prevents divergence (pull before & after commit)
  - Never rewrites pushed history
- **Success Rate:** 100% (zero merge commits since implementation)

**`should_use_pr.sh`** (13KB) - Decision Helper
```bash
./scripts/should_use_pr.sh --explain
```
- **Purpose:** Analyzes changes and recommends PR vs direct commit
- **Analysis Factors:**
  - File type (production vs docs/tests/scripts)
  - Change size (lines added/removed)
  - File count (multiple files = higher impact)
  - Complexity (new files, substantial edits)
- **Thresholds:**
  - Production code: ALWAYS PR
  - VBA/CI/deps: ALWAYS PR
  - Docs >500 lines: PR
  - Tests/scripts >50 lines: PR
  - Small edits: Direct commit OK

---

### 2. Session Management Scripts

**`agent_start.sh`** (NEW - Unified)
```bash
./scripts/agent_start.sh --quick    # 6s, recommended
./scripts/agent_start.sh            # 13s, full validation
./scripts/agent_start.sh --agent 9  # With agent guidance
```
- **Purpose:** Unified session initialization
- **Combines:** `agent_setup.sh` + `agent_preflight.sh` + `start_session.py`
- **Quick mode:** 54% faster (6s vs 13s)

**`agent_setup.sh`** (8.1KB) - Legacy Setup
```bash
./scripts/agent_setup.sh
./scripts/agent_setup.sh --worktree AGENT_NAME  # Worktree mode
```
- **Purpose:** Session initialization
- **Features:**
  - Verifies Python venv
  - Checks git state
  - Validates scripts
  - Shows session context

**`agent_preflight.sh`** (10KB) - Pre-Task Validation
```bash
./scripts/agent_preflight.sh
```
- **Purpose:** Pre-task validation checks
- **Checks:**
  - Git state clean
  - No unfinished merges
  - Branch up to date
  - Tests passing (optional)
  - Python environment
- **Exit Codes:** 0 = ready, non-zero = issues

**`agent_mistakes_report.sh`** - Mistake Reminder
```bash
./scripts/agent_mistakes_report.sh
```
- **Purpose:** Quick reminder of common agent mistakes and fixes
- **Use when:** Start of session (automatically shown by agent_start.sh)

**`end_session.py`** - Session End
```bash
.venv/bin/python scripts/end_session.py
.venv/bin/python scripts/end_session.py --fix   # Auto-fix issues
.venv/bin/python scripts/end_session.py --quick # Skip slow checks
```
- **Purpose:** Session cleanup and handoff
- **Checks:**
  - Uncommitted changes
  - Handoff doc freshness
  - SESSION_LOG entry
  - Doc link validity

---

### 3. PR Management Scripts

**`create_task_pr.sh`** (1.8KB)
```bash
./scripts/create_task_pr.sh TASK-270 "Fix benchmarks"
```
- **Purpose:** Start PR workflow (create branch)
- **Creates:** Branch `task/TASK-270`
- **Updates:** TASKS.md with in-progress status

**`finish_task_pr.sh`** (3.0KB)
```bash
./scripts/finish_task_pr.sh TASK-270 "Fix benchmarks"
```
- **Purpose:** Submit PR (open pull request)
- **Creates:** GitHub PR with:
  - Link to task
  - Labels
  - Push to remote

**After PR Created:**
```bash
# Wait for CI
gh pr checks <num> --watch

# Merge when green
gh pr merge <num> --squash --delete-branch
```

---

### 4. Recovery & Validation Scripts

**`recover_git_state.sh`** (3.4KB) - Emergency Recovery
```bash
./scripts/recover_git_state.sh
```
- **Purpose:** Emergency recovery from git issues
- **Detects:**
  - Diverged branches
  - Unfinished merges
  - Uncommitted changes
  - Conflicted files
- **Provides:** Step-by-step recovery instructions

**`validate_git_state.sh`** (8.3KB) - State Validation
```bash
./scripts/validate_git_state.sh
```
- **Purpose:** Comprehensive git state validation
- **Checks:**
  - Branch status
  - Remote sync
  - Uncommitted changes
  - Merge conflicts
  - Stash state
  - Detached HEAD
- **Output:** Detailed state report

**`check_unfinished_merge.sh`** - Merge Detection
```bash
./scripts/check_unfinished_merge.sh
```
- **Purpose:** Detect unfinished merge state
- **Use when:** Git behavior seems suspicious

**`git_ops.sh`** (NEW) - State-Aware Router
```bash
./scripts/git_ops.sh --status
```
- **Purpose:** Analyze git state and recommend correct script
- **Detects:** Rebase/merge in progress, divergence, uncommitted changes, ahead/behind
- **Recommends:** `recover_git_state.sh`, `ai_commit.sh`, or "no action needed"
- **Use when:** Unsure what to do

**`git_automation_health.sh`** (NEW) - Comprehensive Health Check
```bash
./scripts/git_automation_health.sh
```
- **Purpose:** Verify all automation systems are working
- **Checks:**
  - Git configuration
  - Script availability
  - Hook enforcement status
  - Pre-commit hooks
- **Output:** Detailed status report with pass/fail counts

**`install_git_hooks.sh`** (NEW) - Hook Enforcement Setup
```bash
./scripts/install_git_hooks.sh          # Install
./scripts/install_git_hooks.sh --status # Check status
./scripts/install_git_hooks.sh --uninstall
```
- **Purpose:** Install versioned git hooks that block manual git commands
- **Features:**
  - Blocks `git commit` and `git push` unless using automation scripts
  - Sets `core.hooksPath` to `scripts/git-hooks/`
  - Auto-bypass when `AI_COMMIT_ACTIVE` or `SAFE_PUSH_ACTIVE` is set
  - Hard enforcement (no bypass option)
- **Installed by:** `agent_start.sh` automatically
- **Install once:** Hook persists across sessions
- **Bypass flags:** `AI_COMMIT_ACTIVE=1` or `SAFE_PUSH_ACTIVE=1`
- **Use case:** Reinforce automation-first workflow

---

### 5. Worktree Management Scripts

**`worktree_manager.sh`** (15KB)
```bash
# Create worktree for background agent
./scripts/worktree_manager.sh create AGENT_5

# Submit completed work via PR
./scripts/worktree_manager.sh submit AGENT_5 "Work description"

# List all worktrees
./scripts/worktree_manager.sh list

# Cleanup after merge
./scripts/worktree_manager.sh cleanup AGENT_5
```
- **Purpose:** Manage git worktrees for parallel agent work
- **Features:**
  - Creates isolated workspaces
  - Branch naming: `worktree-{AGENT}-{timestamp}`
  - Submits work via PR
  - Cleans up automatically
- **See:** [advanced-coordination.md](advanced-coordination.md) for patterns

---

### 6. Testing Scripts

**`test_should_use_pr.sh`** (7.6KB)
```bash
./scripts/test_should_use_pr.sh
```
- **Tests:** PR decision logic, thresholds, edge cases

**`test_merge_conflicts.sh`**
```bash
./scripts/test_merge_conflicts.sh
```
- **Tests:** All merge conflict scenarios

**`test_branch_operations.sh`**
```bash
./scripts/test_branch_operations.sh
```
- **Tests:** Git workflow edge cases

---

### 7. Validation & Quality Scripts

**`check_links.py`** - Link Validation
```bash
.venv/bin/python scripts/check_links.py
```
- **Purpose:** Validate all internal markdown links
- **Checks:** 831+ internal links across 238 files

**`check_doc_versions.py`** - Version Drift
```bash
.venv/bin/python scripts/check_doc_versions.py
.venv/bin/python scripts/check_doc_versions.py --fix  # Auto-fix
```
- **Purpose:** Detect version inconsistencies

**`fix_broken_links.py`** - Link Repair
```bash
.venv/bin/python scripts/fix_broken_links.py --fix
```
- **Purpose:** Auto-fix broken links

**`safe_file_move.py`** - Safe File Operations
```bash
.venv/bin/python scripts/safe_file_move.py old.md new.md
.venv/bin/python scripts/safe_file_move.py old.md new.md --dry-run
```
- **Purpose:** Move files while preserving links
- **Updates:** All references automatically

---

## 📊 Script Dependencies

```
ai_commit.sh
├── should_use_pr.sh (decision logic)
├── safe_push.sh (direct commit path)
└── create_task_pr.sh (PR path)

safe_push.sh
├── git (all operations)
└── Pre-commit hooks (formatting, validation)

agent_start.sh (unified)
├── agent_setup.sh (environment)
├── agent_preflight.sh (validation)
└── start_session.py (session tracking)

agent_setup.sh
├── Python venv
├── git
└── validate_git_state.sh

agent_preflight.sh
├── git
└── validate_git_state.sh
```

---

## ⚡ Performance Metrics

| Metric | Value |
|--------|-------|
| **Commit speed** | 90-95% faster than manual |
| **Error rate** | 97.5% reduction |
| **Merge commits** | 0 (zero since implementation) |
| **Conflict resolution** | Automatic |
| **Whitespace fixes** | Auto-fixed (226-413 files) |
| **Pre-commit handling** | Automatic |

---

## 🗂️ Legacy Scripts (Reference Only)

**`safe_push_v2.sh`** (11KB)
- Version 2 of safe_push.sh (kept for reference)

**`should_use_pr_old.sh`** (7.6KB)
- Old version of should_use_pr.sh (kept for reference)

---

## 📁 Related Infrastructure

**Git Operations Log** (`git_operations_log/`)
- All operations logged automatically
- Format: `YYYY-MM-DD.md`
- Contains: Commit hashes, messages, timestamps

**CI Monitor Daemon** (`ci_monitor_daemon.sh`)
- Background CI monitoring (optimization)
- Auto-merges when CI passes

---

## 🔗 Related Documentation

- [Workflow Guide](workflow-guide.md) - Core workflow and decision trees
- [Mistakes Prevention](mistakes-prevention.md) - Historical lessons learned
- [Advanced Coordination](advanced-coordination.md) - Multi-agent patterns

---

**Script Location:** `scripts/` (project root)
**Total Scripts:** 103 (59 .py + 43 .sh)

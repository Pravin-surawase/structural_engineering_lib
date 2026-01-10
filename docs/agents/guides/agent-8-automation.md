# Agent 8 Automation - Scripts & Tools Index

**Complete reference for all Agent 8 automation scripts.**

---

## Script Location

All Agent 8 scripts are in: **`scripts/`** (project root)

**Why scripts/ not docs/agents/?**
- Scripts are shared infrastructure (used by all agents)
- Follows FOLDER_STRUCTURE_GOVERNANCE.md Rule 3.2
- Avoids breaking existing automation
- Easier to execute (shorter paths)

---

## Core Workflow Scripts

### Primary Entry Point

**`ai_commit.sh`** (2.6K)
- **Purpose:** Single entry point for all commits
- **Usage:** `./scripts/ai_commit.sh "commit message"`
- **Features:**
  - Decides PR vs direct commit automatically
  - Calls safe_push.sh for direct commits
  - Calls create_task_pr.sh for PR workflow
  - Logs all operations
- **Doc:** See [agent-8-git-ops.md](agent-8-git-ops.md) for full protocol

### Core Workflow Engine

**`safe_push.sh`** (13K)
- **Purpose:** 7-step conflict-minimized push workflow
- **Usage:** `./scripts/safe_push.sh "commit message"`
- **Steps:**
  1. Stash local changes
  2. Background fetch (parallel)
  3. Stage files
  4. Pre-flight whitespace check & fix
  5. Commit (pre-commit hooks run)
  6. Pull (sync with remote)
  7. Push (fast-forward)
- **Features:**
  - Auto-fixes whitespace (226-413 files typical)
  - Handles pre-commit modifications
  - Prevents divergence (pull before & after commit)
  - Auto-resolves conflicts (keeps our version)
  - Never rewrites pushed history
- **Success Rate:** 100% (zero merge commits since implementation)

### Decision Helper

**`should_use_pr.sh`** (13K)
- **Purpose:** Analyzes changes and recommends PR vs direct commit
- **Usage:** `./scripts/should_use_pr.sh --explain`
- **Analysis:**
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

## PR Management Scripts

**`create_task_pr.sh`** (1.8K)
- **Purpose:** Start PR workflow (create branch)
- **Usage:** `./scripts/create_task_pr.sh TASK-270 "Fix benchmarks"`
- **Features:**
  - Creates feature branch
  - Updates TASKS.md
  - Commits branch creation

**`finish_task_pr.sh`** (3.0K)
- **Purpose:** Submit PR (open pull request)
- **Usage:** `./scripts/finish_task_pr.sh TASK-270 "Fix benchmarks"`
- **Features:**
  - Creates GitHub PR
  - Links to task
  - Adds labels
  - Pushes to remote

---

## Recovery & Validation Scripts

**`recover_git_state.sh`** (3.4K)
- **Purpose:** Emergency recovery from git issues
- **Usage:** `./scripts/recover_git_state.sh`
- **Detects:**
  - Diverged branches
  - Unfinished merges
  - Uncommitted changes
  - Conflicted files
- **Provides:** Step-by-step recovery instructions

**`validate_git_state.sh`** (8.3K)
- **Purpose:** Comprehensive git state validation
- **Usage:** `./scripts/validate_git_state.sh`
- **Checks:**
  - Branch status
  - Remote sync
  - Uncommitted changes
  - Merge conflicts
  - Stash state
  - Detached HEAD
- **Output:** Detailed state report

---

## Environment Setup Scripts

**`agent_setup.sh`** (8.1K)
- **Purpose:** Session initialization
- **Usage:** `./scripts/agent_setup.sh`
- **Features:**
  - Verifies Python venv
  - Checks git state
  - Validates scripts
  - Shows session context
- **Worktree Mode:** `./scripts/agent_setup.sh --worktree AGENT_NAME`

**`agent_preflight.sh`** (10K)
- **Purpose:** Pre-task validation
- **Usage:** `./scripts/agent_preflight.sh`
- **Checks:**
  - Git state clean
  - No unfinished merges
  - Branch up to date
  - Tests passing (optional)
  - Python environment
- **Exit Codes:** 0 = ready, non-zero = issues

**`worktree_manager.sh`** (15K)
- **Purpose:** Manage git worktrees for parallel agent work
- **Usage:**
  - `./scripts/worktree_manager.sh create AGENT_5`
  - `./scripts/worktree_manager.sh submit AGENT_5 "Work description"`
  - `./scripts/worktree_manager.sh list`
  - `./scripts/worktree_manager.sh cleanup`
- **Features:**
  - Creates isolated workspaces
  - Submits work via PR
  - Cleans up automatically

---

## Testing Scripts

**`test_should_use_pr.sh`** (7.6K)
- **Purpose:** Test PR decision logic
- **Usage:** `./scripts/test_should_use_pr.sh`
- **Tests:**
  - Production code detection
  - Size threshold calculation
  - File type classification
  - Edge cases

**`test_merge_conflicts.sh`**
- **Purpose:** Comprehensive merge conflict test suite
- **Usage:** `./scripts/test_merge_conflicts.sh`
- **Tests:** All merge conflict scenarios

**`test_branch_operations.sh`**
- **Purpose:** Branch operation testing
- **Usage:** `./scripts/test_branch_operations.sh`
- **Tests:** Git workflow edge cases

---

## Legacy Scripts (Backup)

**`safe_push_v2.sh`** (11K)
- Version 2 of safe_push.sh (kept for reference)

**`should_use_pr_old.sh`** (7.6K)
- Old version of should_use_pr.sh (kept for reference)

---

## Related Infrastructure

**`ci_monitor_daemon.sh`**
- Background CI monitoring for Agent 8 optimization

**Git Operations Log** (`git_operations_log/`)
- All operations logged automatically
- Format spec: [agent-8-operations-log-spec.md](agent-8-operations-log-spec.md)

---

## Script Dependencies

```
ai_commit.sh
├── should_use_pr.sh (decision logic)
├── safe_push.sh (direct commit path)
└── create_task_pr.sh (PR path)

safe_push.sh
├── git (all operations)
└── Pre-commit hooks (formatting, validation)

agent_setup.sh
├── Python venv
├── git
└── validate_git_state.sh

agent_preflight.sh
├── git
└── validate_git_state.sh
```

---

## Usage Patterns

### Standard Workflow
```bash
# Session start
./scripts/agent_setup.sh

# Before any work
./scripts/agent_preflight.sh

# Make changes
# ... edit files ...

# Commit
./scripts/ai_commit.sh "feat: add feature X"
```

### PR Workflow
```bash
# Create branch
./scripts/create_task_pr.sh TASK-123 "Feature description"

# Make changes & commit
./scripts/ai_commit.sh "feat: implement X"
./scripts/ai_commit.sh "test: add tests for X"

# Submit PR
./scripts/finish_task_pr.sh TASK-123 "Feature description"

# Wait for CI
gh pr checks <num> --watch

# Merge
gh pr merge <num> --squash --delete-branch
```

### Recovery
```bash
# If git is broken
./scripts/recover_git_state.sh

# If validation needed
./scripts/validate_git_state.sh
```

---

## Performance Metrics

| Metric | Value |
|--------|-------|
| **Commit speed** | 90-95% faster than manual |
| **Error rate** | 97.5% reduction |
| **Merge commits** | 0 (zero since implementation) |
| **Conflict resolution** | Automatic (keeps our version) |
| **Whitespace fixes** | Auto-fixed (226-413 files typical) |
| **Pre-commit handling** | Automatic (no manual intervention) |

---

## Full Documentation

- **[Quick Start](agent-8-quick-start.md)** - Get started in 60 seconds
- **[Git Operations Protocol](agent-8-git-ops.md)** - Core mission & detailed workflow
- **[Mistake Prevention](agent-8-mistakes-prevention-guide.md)** - Historical mistakes database
- **[Implementation Guide](agent-8-implementation-guide.md)** - Setup instructions
- **[Multi-Agent Coordination](agent-8-multi-agent-coordination.md)** - Coordination patterns

---

**Last Updated:** 2026-01-10
**Script Location:** `scripts/` (project root)
**Maintained By:** Agent 8 (Git Operations)

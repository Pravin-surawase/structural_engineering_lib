# Efficient Agent Usage for Git Automation

**Type:** Guide
**Audience:** All Agents
**Status:** Production Ready
**Importance:** High
**Version:** 0.16.6
**Created:** 2026-01-11
**Last Updated:** 2026-01-11
**Related Tasks:** SESSION-14P3
**Location Rationale:** Part of git-automation hub consolidation

---

## Quick Decision Matrix

| Agent Type | Session Start | Primary Commit | Workflow Pattern |
|------------|---------------|----------------|------------------|
| **Main Agent** | `./scripts/agent_start.sh --quick` | `./scripts/ai_commit.sh "msg"` | Direct commit for docs, PR for code |
| **Implementation Agent** | `./scripts/agent_start.sh --quick` | Same | Always PR for production code |
| **Background Agent** | `./scripts/worktree_manager.sh create` | Same | Worktree isolation |
| **Governance Agent** | `./scripts/agent_start.sh --agent 9` | Same | Direct for governance docs |

---

## 1. The 3-Command Session

For 95% of agent sessions, you need only 3 commands:

```bash
# 1. START (6 seconds)
./scripts/agent_start.sh --quick

# 2. COMMIT (after each work chunk)
./scripts/ai_commit.sh "scope: description"

# 3. END (30 seconds)
.venv/bin/python scripts/session.py end
```

**That's it.** Everything else is automated.

---

## 2. Agent-Specific Patterns

### 2.1 Main Agent (Interactive Sessions)

**Characteristics:** Responds to user requests, works on diverse tasks.

```bash
# Start
./scripts/agent_start.sh --quick

# Work on docs (direct commit)
./scripts/ai_commit.sh "docs: update guide"

# Work on code (PR workflow)
./scripts/create_task_pr.sh TASK-XXX "description"
# ... make changes ...
./scripts/ai_commit.sh "feat: implementation"
./scripts/finish_task_pr.sh TASK-XXX "description"
gh pr merge <num> --squash --delete-branch

# End
.venv/bin/python scripts/session.py end
```

### 2.2 Implementation Agent (Code Focus)

**Characteristics:** Focused on Python/VBA code changes.

```bash
# Start
./scripts/agent_start.sh --quick

# ALWAYS use PR workflow for code
./scripts/create_task_pr.sh IMPL-XXX "feature name"

# Multiple commits per PR (batch related changes)
./scripts/ai_commit.sh "feat: add core function"
./scripts/ai_commit.sh "test: add unit tests"
./scripts/ai_commit.sh "docs: update API reference"

# Single PR for complete feature
./scripts/finish_task_pr.sh IMPL-XXX "feature name"

# Wait for CI, then merge
gh pr checks <num> --watch
gh pr merge <num> --squash --delete-branch
```

### 2.3 Background Agent (Long-Running Tasks)

**Characteristics:** Works independently, doesn't interfere with main.

```bash
# Create isolated workspace
./scripts/worktree_manager.sh create AGENT_5

# Work in worktree
cd worktree-AGENT_5-*

# Commit normally (paths adjust automatically)
./scripts/ai_commit.sh "feat: complete module"

# When done, submit from project root
cd $PROJECT_ROOT
./scripts/worktree_manager.sh submit AGENT_5 "Work description"
```

### 2.4 Governance Agent (Agent 9)

**Characteristics:** Folder governance, metrics, docs organization.

```bash
# Start with agent-specific guidance
./scripts/agent_start.sh --agent 9 --quick

# Governance docs (direct commit)
./scripts/ai_commit.sh "docs(governance): update folder spec"

# Structural changes (PR required)
./scripts/create_task_pr.sh GOV-XXX "folder migration"
# ... make changes ...
./scripts/finish_task_pr.sh GOV-XXX "folder migration"
```

---

## 3. Efficiency Rules

### 3.1 Batch Related Changes

❌ **Inefficient:**
```bash
./scripts/ai_commit.sh "add function"
./scripts/ai_commit.sh "add test for function"
./scripts/ai_commit.sh "add docs for function"
```

✅ **Efficient:**
```bash
# Make all related changes, then one commit
./scripts/ai_commit.sh "feat: add function with tests and docs"
```

### 3.2 Use PR for Multi-Commit Features

❌ **Inefficient:** Multiple PRs for one feature
```bash
# PR 1: function
# PR 2: tests
# PR 3: docs
```

✅ **Efficient:** One PR with multiple commits
```bash
./scripts/create_task_pr.sh FEAT-001 "new feature"
./scripts/ai_commit.sh "feat: core implementation"
./scripts/ai_commit.sh "test: comprehensive tests"
./scripts/ai_commit.sh "docs: API and examples"
./scripts/finish_task_pr.sh FEAT-001 "new feature"
```

### 3.3 Skip Unnecessary Checks

When you're certain (small doc edits):
```bash
# Quick mode is default now (--quick is redundant but explicit)
./scripts/agent_start.sh --quick  # 6s vs 13s full mode
```

### 3.4 Parallelize When Safe

```bash
# Safe: Run validation in background while working
./scripts/git_automation_health.sh &  # Background check
# ... continue work ...
```

---

## 4. Command Cheat Sheet

### Session Lifecycle
| Phase | Command | Time |
|-------|---------|------|
| Start | `./scripts/agent_start.sh --quick` | 6s |
| Preflight | `./scripts/agent_start.sh` | 2s |
| End | `.venv/bin/python scripts/session.py end` | 30s |

### Commit Workflow
| Action | Command | Time |
|--------|---------|------|
| Simple commit | `./scripts/ai_commit.sh "msg"` | 10-30s |
| Preview only | `./scripts/ai_commit.sh "msg" --dry-run` | 2s |
| Check PR needed | `./scripts/should_use_pr.sh --explain` | 1s |

### PR Workflow
| Action | Command | Time |
|--------|---------|------|
| Start PR | `./scripts/create_task_pr.sh TASK-XXX "desc"` | 5s |
| Finish PR | `./scripts/finish_task_pr.sh TASK-XXX "desc"` | 30s |
| Wait CI | `gh pr checks <num> --watch` | 1-5min |
| Merge | `gh pr merge <num> --squash --delete-branch` | 5s |

### Recovery
| Issue | Command | Time |
|-------|---------|------|
| Git broken | `./scripts/recover_git_state.sh` | 30s |
| Health check | `./scripts/git_automation_health.sh` | 5s |
| Merge conflict | `./scripts/recover_git_state.sh` | 30s |
| State check | `./scripts/git_ops.sh --status` | 2s |

---

## 5. Time Optimization

### Session Time Budget

| Session Type | Typical Duration | Commits Target |
|--------------|-----------------|----------------|
| Quick fix | 15-30 min | 1-2 |
| Standard | 1-2 hours | 3-6 |
| Extended | 2-4 hours | 6-10+ |

### Time-Saving Tips

1. **Use --quick always** (default now): Saves 7s per session start
2. **Batch commits**: One commit with 3 related changes > 3 separate commits
3. **Trust the scripts**: Don't check git status manually, scripts do it
4. **Use --dry-run for learning**: Preview without executing
5. **Pre-stage mentally**: Know what you'll commit before starting

---

## 6. Common Workflows

### Workflow A: Doc Update (2 minutes)
```bash
./scripts/agent_start.sh --quick  # 6s
# Edit docs
./scripts/ai_commit.sh "docs: update X"  # 15s
```

### Workflow B: Bug Fix (10-15 minutes)
```bash
./scripts/agent_start.sh --quick
./scripts/create_task_pr.sh BUG-XXX "fix issue"
# Fix code + add test
./scripts/ai_commit.sh "fix: resolve issue #XXX"
./scripts/finish_task_pr.sh BUG-XXX "fix issue"
gh pr checks <num> --watch  # Wait for CI
gh pr merge <num> --squash --delete-branch
```

### Workflow C: Feature (30-60 minutes)
```bash
./scripts/agent_start.sh --quick
./scripts/create_task_pr.sh FEAT-XXX "new feature"

# Incremental commits
./scripts/ai_commit.sh "feat: add data types"
./scripts/ai_commit.sh "feat: add core logic"
./scripts/ai_commit.sh "test: add unit tests"
./scripts/ai_commit.sh "docs: add API docs"

./scripts/finish_task_pr.sh FEAT-XXX "new feature"
gh pr merge <num> --squash --delete-branch
```

---

## 7. Anti-Patterns to Avoid

| Anti-Pattern | Why It's Bad | Better Approach |
|--------------|--------------|-----------------|
| Manual git commands | Merge conflicts, hook issues | Always use ai_commit.sh |
| Micro-commits | Pollutes history, slow | Batch related changes |
| Skip preflight | Miss issues early | Run agent_start.sh |
| Direct push for code | Skips CI validation | Use PR workflow |
| Multiple PRs for one feature | Review overhead | One PR, multiple commits |
| Not ending session | Missing updates | Always run session.py end |

---

## 8. Troubleshooting

### "Script not found"
```bash
# Run from project root
cd "/Users/Pravin/Library/Mobile Documents/com~apple~CloudDocs/pravin/projects/project_21_dec_25/structural_engineering_lib"
```

### "Permission denied"
```bash
chmod +x scripts/*.sh
```

### "Git state weird"
```bash
./scripts/recover_git_state.sh
```

### "Pre-commit failed"
```bash
# Script handles this automatically
# If manual fix needed:
.venv/bin/python -m black Python/
.venv/bin/python -m ruff check --fix Python/
./scripts/ai_commit.sh "style: apply fixes"
```

---

## Related Documents

- [README.md](README.md) - Navigation hub
- [workflow-guide.md](workflow-guide.md) - 7-step workflow details
- [automation-scripts.md](automation-scripts.md) - All 103 scripts
- [mistakes-prevention.md](mistakes-prevention.md) - Lessons learned

---

*Last validated: 2026-01-11 | 103 scripts operational | 17/17 health checks passing*

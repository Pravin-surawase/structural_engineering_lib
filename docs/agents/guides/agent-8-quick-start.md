# Agent 8 Quick Start - Git Operations Automation

**Get started with Agent 8 in 60 seconds.**

---

## What is Agent 8?

Agent 8 is the **single source of truth for all git operations**, preventing merge conflicts, divergence, and wasted time through automated workflows.

**Key Result:** 90-95% faster commits, 97.5% fewer errors, zero merge commits.

---

## Quick Start

### 1. Setup (Once per session)
```bash
./scripts/agent_setup.sh
```

### 2. Pre-flight Check (Before any work)
```bash
./scripts/agent_preflight.sh
```

### 3. Commit & Push (Every commit)
```bash
./scripts/ai_commit.sh "your commit message"
```

**That's it!** The script handles:
- ✅ Staging files
- ✅ Pre-commit hooks
- ✅ Pull before push (prevents conflicts)
- ✅ Whitespace fixes
- ✅ PR vs direct commit decision
- ✅ Fast-forward push

---

## The One Rule

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ NEVER use manual git commands!                 ┃
┃ ALWAYS use ./scripts/ai_commit.sh "message"    ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

**Why?** Manual git causes:
- Merge conflicts (wastes 10-30 minutes)
- Pre-commit hook failures
- Diverged history
- Lost work

---

## Decision Tree (30 Seconds)

```
Is this production code/VBA/CI/deps?
    ├─ YES → PR Workflow
    └─ NO  → ./scripts/ai_commit.sh "msg"

Is this >50 lines OR 2+ files?
    ├─ YES → PR Workflow
    └─ NO  → ./scripts/ai_commit.sh "msg"
```

---

## Essential Commands

| Command | Purpose |
|---------|---------|
| `./scripts/agent_setup.sh` | Start session |
| `./scripts/agent_preflight.sh` | Pre-task check |
| `./scripts/ai_commit.sh "msg"` | Commit & push |
| `./scripts/should_use_pr.sh --explain` | PR decision helper |
| `./scripts/recover_git_state.sh` | Emergency recovery |

---

## PR Workflow (Production Code)

```bash
# 1. Create branch
./scripts/create_task_pr.sh TASK-270 "Fix benchmarks"

# 2. Make changes & commit
./scripts/ai_commit.sh "fix: update signatures"

# 3. Submit PR
./scripts/finish_task_pr.sh TASK-270 "Fix benchmarks"

# 4. Wait for CI & merge
gh pr checks <num> --watch
gh pr merge <num> --squash --delete-branch
```

---

## Common Mistakes (Avoid These!)

| ❌ DON'T | ✅ DO |
|---------|------|
| `git add . && git commit` | `./scripts/ai_commit.sh "msg"` |
| `git commit --amend` after push | Never amend after push |
| Skip pre-flight check | Always run `agent_preflight.sh` |
| Manual merge conflict resolution | Use `recover_git_state.sh` |

---

## Emergency Recovery

**Git is broken?**
```bash
./scripts/recover_git_state.sh
# Follow printed instructions
```

**Merge conflict?**
```bash
# Check state
./scripts/check_unfinished_merge.sh

# Keep our version (usually)
git checkout --ours <file>
git add <file>
git commit --no-edit
```

---

## Full Documentation

- **[Git Operations Protocol](agent-8-git-ops.md)** (1,320 lines) - Core mission & workflow
- **[Automation Index](agent-8-automation.md)** - All scripts & tools
- **[Mistake Prevention](agent-8-mistakes-prevention-guide.md)** (1,096 lines) - Historical mistakes DB
- **[Implementation Guide](agent-8-implementation-guide.md)** - Setup & implementation
- **[Multi-Agent Coordination](agent-8-multi-agent-coordination.md)** - Coordination workflows

---

## Related

- [Scripts Directory](../../../scripts/) - All automation scripts
- [Git Operations Log](../../../git_operations_log/) - Operational logs
- [Research](../../research/) - Agent 8 research documents

---

**Last Updated:** 2026-01-10
**Status:** Production-ready, actively maintained

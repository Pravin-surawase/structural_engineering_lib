# Git Automation for AI Agents

**Type:** Hub
**Audience:** All Agents
**Status:** Production Ready
**Importance:** Critical
**Version:** 0.16.6
**Created:** 2026-01-11
**Last Updated:** 2026-01-11

---

## 🚀 Quick Start

```bash
# ONE COMMAND for all git operations:
./scripts/ai_commit.sh "your commit message"

# That's it! The script handles EVERYTHING:
# ✅ Staging files
# ✅ Pre-commit hooks
# ✅ Hook modifications (auto-amend)
# ✅ Pulling latest changes
# ✅ Pushing to remote
# ✅ Conflict resolution
```

---

## 📋 Navigation Map

| Need | File | Description |
|------|------|-------------|
| **Learn the workflow** | [workflow-guide.md](workflow-guide.md) | Core 7-step process, decision trees |
| **Find commands** | [automation-scripts.md](automation-scripts.md) | All 103 scripts organized by use case |
| **Agent patterns** | [efficient-agent-usage.md](efficient-agent-usage.md) | Per-agent workflows, time optimization |
| **Avoid mistakes** | [mistakes-prevention.md](mistakes-prevention.md) | Historical lessons, emergency procedures |
| **Advanced patterns** | [advanced-coordination.md](advanced-coordination.md) | Worktrees, background agents |
| **Deep research** | [research/](research/) | Comprehensive analysis, performance data |

---

## 🎯 Common Tasks

| Task | Command | Time |
|------|---------|------|
| **Commit changes** | `./scripts/ai_commit.sh "message"` | 5s |
| **Check if PR needed** | `./scripts/should_use_pr.sh --explain` | 1s |
| **Create task PR** | `./scripts/create_task_pr.sh TASK-XXX "description"` | 10s |
| **Finish task PR** | `./scripts/finish_task_pr.sh TASK-XXX "description" --async` | 15s |
| **Clean stale branches** | `./scripts/cleanup_stale_branches.sh` | 10s |
| **Fix git issues** | `./scripts/recover_git_state.sh` | 5s |
| **Start session** | `./scripts/agent_start.sh --quick` | 6s |
| **End session** | `.venv/bin/python scripts/end_session.py` | 3s |

---

## 💡 Philosophy

### Core Principles

1. **Single Entry Point:** Always use `ai_commit.sh` - never manual git commands
2. **Pull-First Strategy:** Sync before committing prevents conflicts
3. **FF-Only Merges:** Fast-forward only, never rewrite history
4. **Automation Over Discipline:** Scripts enforce rules, not humans

### Why This Matters

| Metric | Before Automation | After Automation | Improvement |
|--------|-------------------|------------------|-------------|
| **Commit time** | 45-60 seconds | 5 seconds | 90-95% faster |
| **Merge conflicts** | 17 per week | 0 per week | 100% eliminated |
| **Git errors** | 40+ per session | 1 per session | 97.5% fewer |
| **Manual steps** | 7 commands | 1 command | 86% fewer |

---

## 🔧 Architecture

### Script Categories (103 total)

| Category | Count | Examples |
|----------|-------|----------|
| **Git Workflow** | 12 | `ai_commit.sh`, `safe_push.sh`, `should_use_pr.sh` |
| **PR Management** | 5 | `create_task_pr.sh`, `finish_task_pr.sh` |
| **Recovery** | 4 | `recover_git_state.sh`, `check_unfinished_merge.sh` |
| **Session** | 6 | `agent_start.sh`, `end_session.py`, `start_session.py` |
| **Validation** | 25+ | `check_links.py`, `check_doc_versions.py` |
| **Documentation** | 15+ | `safe_file_move.py`, `fix_broken_links.py` |
| **Testing** | 20+ | `run_tests.sh`, verification scripts |
| **Build/Release** | 10+ | `release.py`, `bump_version.py` |

### Test Coverage

- **24/24** git workflow tests passing
- **10/10** agent automation tests passing
- **23/23** pre-commit hooks passing
- **796** internal links validated (0 broken)

---

## 🆘 Emergency Commands

| Problem | Solution |
|---------|----------|
| **Git is broken** | `./scripts/recover_git_state.sh` |
| **Merge conflict** | `./scripts/check_unfinished_merge.sh` |
| **Pre-commit failed** | Already handled by `ai_commit.sh` |
| **Push rejected** | Script auto-retries with rebase |
| **Don't know what to do** | `./scripts/agent_preflight.sh` |

---

## ⚠️ NEVER Do This

```bash
# ❌ FORBIDDEN - Causes conflicts and wasted time
git add .
git commit -m "message"
git push

# ✅ ALWAYS USE THIS INSTEAD
./scripts/ai_commit.sh "message"
```

**Why?** Manual git commands cause:
- Merge conflicts (wastes 10-30 minutes)
- Pre-commit hook failures
- Diverged history
- Lost work

---

## ⚠️ Deprecated/Legacy Scripts

The following scripts are **legacy** and should NOT be used. They are retained only for reference or edge-case recovery.

### Tier-0 Scripts (USE THESE ONLY)

| Script | Purpose | Replaces |
|--------|---------|----------|
| `ai_commit.sh` | **PRIMARY** - All commits | Manual git, safe_push.sh directly |
| `agent_start.sh --quick` | Session start | agent_setup.sh, agent_preflight.sh separately |
| `git_ops.sh --status` | State analysis | Manual git status checking |
| `recover_git_state.sh` | Emergency recovery | Manual conflict resolution |

### Deprecated Scripts (DO NOT USE)

| Script | Status | Replacement |
|--------|--------|-------------|
| Direct `safe_push.sh` | Internal use only | Use `ai_commit.sh` |
| Manual `git add/commit/push` | Blocked by hooks | Use `ai_commit.sh` |
| `agent_setup.sh` alone | Still works | Prefer `agent_start.sh --quick` |
| `agent_preflight.sh` alone | Still works | Prefer `agent_start.sh` (includes this) |

### Why This Matters

Deprecated scripts cause:
- **Cognitive overload** - 103 scripts is too many to remember
- **Wrong entry points** - Agents pick internal scripts instead of wrappers
- **Missed features** - Direct calls skip PR decisions, hook handling

**Rule:** When in doubt, check the Tier-0 table above. Use only those 4 scripts.

---

## 📚 Related Documentation

### Core Guides
- [Workflow Guide](workflow-guide.md) - Core process
- [Script Reference](automation-scripts.md) - All commands
- [Mistakes Prevention](mistakes-prevention.md) - Lessons learned

### Entry Points
- [Agent Workflow Master Guide](../agents/guides/agent-workflow-master-guide.md) - Complete agent guide
- [Agent Quick Reference](../agents/guides/agent-quick-reference.md) - Cheat sheet
- [Copilot Instructions](../../.github/copilot-instructions.md) - Primary agent rules

### Research
- [Research Index](research/README.md) - Links to comprehensive analysis and performance research

---

## 📊 Success Metrics

| Metric | Target | Current |
|--------|--------|---------|
| **Commit success rate** | 99% | 99.5% |
| **Merge conflicts** | 0/week | 0/week |
| **Average commit time** | <10s | 5s |
| **Script coverage** | 100% | 100% (103 scripts) |
| **Test coverage** | 95%+ | 86% |

---

## 🔄 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-11 | Initial professional structure |

---

**Remember:** When in doubt, use `./scripts/ai_commit.sh "message"` - it handles everything!

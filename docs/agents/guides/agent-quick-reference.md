# Agent Workflow Quick Reference Card
**Version:** 1.1.0 | **Print this and keep it visible!**

---

## 🚀 Session Start (ONE COMMAND)

```bash
./scripts/agent_start.sh --quick              # RECOMMENDED (6s, 54% faster)
./scripts/agent_start.sh                      # Full validation (13s, optional)
./scripts/agent_start.sh --agent 9 --quick    # With agent-specific guidance
```

---

## ⚡ Essential Commands (Memorize These)

| Command | Purpose |
|---------|---------|
| `./scripts/agent_start.sh --quick` | **Start session (NEW - replaces 4 commands)** |
| `./scripts/ai_commit.sh "msg"` | **Commit changes** |
| `./scripts/should_use_pr.sh --explain` | **PR or direct?** |
| `./scripts/git_ops.sh --status` | **Analyze git state & get recommendation** |
| `./scripts/agent_mistakes_report.sh` | **Common mistakes reminder** |
| `.venv/bin/python scripts/end_session.py` | **End session** |

---

## 🚨 THE ONE RULE

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ NEVER use manual git commands!                 ┃
┃ ALWAYS use ./scripts/ai_commit.sh "message"    ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

---

## 📋 Decision Tree (30 Second Version)

```
Is this production code/VBA/CI/deps?
    ├─ YES → PR Workflow (below)
    └─ NO  → Direct Commit: ./scripts/ai_commit.sh "msg"

Is this >50 lines OR 2+ files?
    ├─ YES → PR Workflow (below)
    └─ NO  → Direct Commit: ./scripts/ai_commit.sh "msg"
```

---

## 🔄 Workflow Patterns

### Pattern 1: Simple Direct Commit (80% of work)
```bash
# 1. Make changes
# 2. Commit
./scripts/ai_commit.sh "docs: update guide"
# Done!
```

### Pattern 2: PR Workflow (Production Code)
```bash
# 1. Create branch
./scripts/create_task_pr.sh TASK-270 "Fix benchmarks"

# 2. Make changes & commit
./scripts/ai_commit.sh "fix: update signatures"

# 3. Submit PR
./scripts/finish_task_pr.sh TASK-270 "Fix benchmarks" --async

# 4. Check CI status
./scripts/pr_async_merge.sh status
```

### Pattern 3: Background Agent (Long Tasks)
```bash
# 1. Create worktree
./scripts/worktree_manager.sh create AGENT_5

# 2. Work in worktree
cd worktree-AGENT_5-*
# ... make changes ...
../scripts/ai_commit.sh "feat: module complete"

# 3. Submit when done
cd $PROJECT_ROOT
./scripts/worktree_manager.sh submit AGENT_5 "Work description"
```

---

## 🆘 Emergency Commands

| Problem | Solution |
|---------|----------|
| **Git is broken** | `./scripts/recover_git_state.sh` |
| **Merge conflict** | `./scripts/check_unfinished_merge.sh` |
| **Don't know what to do** | `./scripts/git_ops.sh --status` |
| **Check git health** | `./scripts/git_automation_health.sh` |
| **CI failed on format** | `cd Python && python -m black . && cd .. && ./scripts/ai_commit.sh "style: format"` |
| **Version drift** | `python scripts/check_doc_versions.py --fix` |
| **Hooks not installed** | `./scripts/install_git_hooks.sh` |

---

## 📊 Cheat Sheet Matrix

| Scenario | Command |
|----------|---------|
| Start day | `./scripts/agent_setup.sh` |
| Before task | `./scripts/agent_preflight.sh` |
| Simple doc edit | `./scripts/ai_commit.sh "docs: fix typo"` |
| Production code | `./scripts/create_task_pr.sh → ... → finish_task_pr.sh` |
| Long background task | `./scripts/worktree_manager.sh create AGENT_N` |
| Check worktrees | `./scripts/worktree_manager.sh list` |
| Submit agent work | `./scripts/worktree_manager.sh submit AGENT_N "desc"` |
| End day | `./scripts/end_session.py` |

---

## 🎯 Critical Dos and Don'ts

### ✅ DO
- Use ai_commit.sh for ALL commits
- Run agent_preflight.sh before starting
- Check should_use_pr.sh when unsure
- Use worktrees for parallel work
- End session with end_session.py

### ❌ DON'T
- Use `git add/commit/push` manually
- Skip pre-flight checks
- Commit unrelated changes together
- Work on main for production code
- Leave uncommitted changes

---

## 📂 File Locations

```
scripts/
├── agent_setup.sh           # Start session
├── agent_preflight.sh       # Pre-task check
├── ai_commit.sh             # Commit wrapper
├── safe_push.sh             # Core git logic
├── should_use_pr.sh         # Decision helper
├── create_task_pr.sh        # Start PR
├── finish_task_pr.sh        # Submit PR
├── worktree_manager.sh      # Agent workspaces
├── recover_git_state.sh     # Emergency recovery
└── end_session.py           # End session

docs/agents/
└── agent-workflow-master-guide.md  # Full guide
```

---

## 🔗 Quick Links

- **Full Guide:** [agent-workflow-master-guide.md](agent-workflow-master-guide.md)
- **Tasks:** [TASKS.md](../../TASKS.md)
- **Git Workflow:** [git-workflow-ai-agents.md](../../contributing/git-workflow-ai-agents.md)
- **Session Log:** [SESSION_LOG.md](../../SESSION_LOG.md)

---

## 💡 Pro Tips

1. **Batch related changes** - One commit for related work
2. **Use worktrees** - Parallel work = separate worktrees
3. **Check PR decision** - `should_use_pr.sh --explain` when unsure
4. **Auto-fix issues** - Most scripts have `--fix` flag
5. **Read output** - Scripts tell you what went wrong

---

## 🧠 Automation-First Principles

> **10+ similar issues = Write automation script FIRST!**

| Principle | Action |
|-----------|--------|
| **Pattern Recognition** | See 10+ issues → automate, don't fix manually |
| **Research First** | Check `scripts/` before writing new tools |
| **Build Once, Use Many** | `fix_broken_links.py` fixed 213 links in 5 sec |
| **Full Sessions** | 5-10+ commits per session, don't stop early |
| **Document Always** | Update TASKS.md, SESSION_LOG after work |

### Quick Automation Commands
```bash
python scripts/fix_broken_links.py --fix      # Fix links
python scripts/validate_folder_structure.py   # Check structure
python scripts/check_doc_versions.py --fix    # Fix versions
```

---

## 🎓 Learning Resources

### Day 1: Basics
- Run agent_setup.sh
- Make doc change
- Use ai_commit.sh
- Understand output

### Day 2: PR Workflow
- Create task branch
- Make changes
- Submit PR
- Watch CI

### Day 3: Worktrees
- Create worktree
- Work independently
- Submit via manager

---

## 📞 Help & Support

**When stuck:**
1. Check terminal output (scripts are verbose)
2. Check `logs/git_workflow.log`
3. Run `./scripts/agent_preflight.sh`
4. Run `./scripts/recover_git_state.sh`
5. Review [agent-workflow-master-guide.md](agent-workflow-master-guide.md)

**Common issues solved in <2 minutes:**
- Git conflicts → recover_git_state.sh
- Format failures → black + commit
- Version drift → check_doc_versions.py --fix
- Unfinished merge → recover_git_state.sh

---

## 📏 Size Thresholds (When PR Required)

| File Type | PR Threshold | Direct OK |
|-----------|--------------|-----------|
| Production code | ANY change | Never |
| VBA | ANY change | Never |
| CI workflows | ANY change | Never |
| Dependencies | ANY change | Never |
| Documentation | 500+ lines | <500 lines |
| Tests | 50+ lines | <50 lines |
| Scripts | 50+ lines | <50 lines |

---

## ⏱️ Time Estimates

| Task | Time |
|------|------|
| Setup session | 30s |
| Simple commit | 10s |
| PR workflow | 2-5min |
| Worktree creation | 1min |
| Recovery from error | 1-2min |

---

**Remember:** Automation prevents errors. Trust the scripts!

**Last Updated:** 2026-01-12 | **Version:** 1.1.0

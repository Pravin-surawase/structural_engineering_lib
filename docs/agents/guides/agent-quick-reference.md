# Agent Workflow Quick Reference Card
**Version:** 1.2.0 | **Print this and keep it visible!**

---

## 📚 Guide Hierarchy

**You are here:** Quick Reference Card (Cheat Sheet)

| Need | Guide | Use When |
|------|-------|----------|
| **Quick Start** | [agent-bootstrap.md](../../getting-started/agent-bootstrap.md) | First 30 seconds, immediate productivity |
| **Quick Reference** | This document | Cheat sheet, emergency commands, first session ← **YOU ARE HERE** |
| **Complete Guide** | [agent-workflow-master-guide.md](agent-workflow-master-guide.md) | Decision trees, troubleshooting, deep patterns |

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
|---------|--------|
| `./run.sh session start` | **Start session** |
| `./run.sh commit "msg"` | **Commit changes** |
| `./run.sh check --quick` | **Fast validation (<30s)** |
| `./run.sh check` | **Full validation (28 checks)** |
| `./run.sh pr create TASK-XXX "desc"` | **Create PR** |
| `./run.sh find "topic"` | **Find scripts** |
| `./run.sh find --api func` | **Get API signatures** |
| `./run.sh test` | **Run tests** |
| `./run.sh session end` | **End session** |
| `./run.sh --help` | **Full command reference** |

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

## ✅ First Session Checklist

### Before Starting Work (5 minutes)
- [ ] Read [agent-bootstrap.md](../../getting-started/agent-bootstrap.md) - **CANONICAL BOOTSTRAP**
- [ ] Read [TASKS.md](../../TASKS.md) - Current work items
- [ ] Run `./scripts/agent_start.sh --quick` - Validates environment

### Your First Task (Pattern: Simple Direct Commit)
```bash
# 1. Make a small change (e.g., fix typo in docs)
# 2. Commit
./scripts/ai_commit.sh "docs: fix typo in guide"
# 3. Done! ✓ Script handles staging, hooks, push
```

### After Your First Commit
- [ ] Verified commit appeared in `git log`
- [ ] No errors during push
- [ ] Understand what the script did (staging → hooks → pull → push)
- [ ] Ready for more complex work

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

# 3. Submit PR (polls CI, auto-merges when green)
./scripts/finish_task_pr.sh TASK-270 "Fix benchmarks"

# 4. Check CI status manually if needed
gh pr checks <PR_NUMBER>
```

**Session docs rule:** Update `SESSION_LOG.md` + `next-session-brief.md` in this PR and log the PR number.

### Pattern 3: Long Tasks (Same Branch)
```bash
# 1. Create branch
./scripts/create_task_pr.sh TASK-XXX "Long task description"

# 2. Make changes & commit frequently
./scripts/ai_commit.sh "feat: step 1 done"
./scripts/ai_commit.sh "feat: step 2 done"

# 3. Submit PR when all work is complete
./scripts/finish_task_pr.sh TASK-XXX "Long task description"
```

---

## 🆘 Emergency Commands

| Problem | Solution |
|---------|----------|
| **Git is broken** | `./scripts/recover_git_state.sh` |
| **Merge conflict** | `./scripts/check_unfinished_merge.sh` |
| **Don't know what to do** | `git status && git log --oneline -5` |
| **Check git health** | `./scripts/validate_git_state.sh` |
| **CI failed on format** | `cd Python && python -m black . && cd .. && ./scripts/ai_commit.sh "style: format"` |
| **Version drift** | `.venv/bin/python scripts/check_doc_versions.py --fix` |
| **Hooks not installed** | `./scripts/install_git_hooks.sh` |

---

## ✅ API Touchpoints (Public API Changes)

1. Update exports in `Python/structural_lib/api.py` (`__all__`).
2. Update docs in `docs/reference/api.md` and `docs/reference/api-stability.md`.
3. Regenerate manifest: `./.venv/bin/python scripts/generate_api_manifest.py`.
4. Run checks: `./.venv/bin/python scripts/check_api.py --docs`.

Keep public signatures stable unless explicitly approved.

---

## 🔎 Scanner & Validation (Streamlit)

- Run: `.venv/bin/python scripts/check_streamlit.py --all-pages`
- False positives: `.scanner-ignore.yml`
- Research: `docs/research/scanner-improvements.md`

---

## 📊 Cheat Sheet Matrix

| Scenario | Command |
|----------|---------|
| Start day | `./scripts/agent_start.sh --quick` |
| Before task | *(included in agent_start.sh)* |
| Simple doc edit | `./scripts/ai_commit.sh "docs: fix typo"` |
| Production code | `./scripts/create_task_pr.sh → ... → finish_task_pr.sh` |
| Long multi-step task | `./scripts/create_task_pr.sh TASK-XXX "desc"` |
| Check PR status | `gh pr checks <PR_NUMBER>` |
| Submit & merge PR | `./scripts/finish_task_pr.sh TASK-XXX "desc"` |
| End day | `.venv/bin/python scripts/session.py end` |

---

## 🎯 Critical Dos and Don'ts

### ✅ DO
- Use ai_commit.sh for ALL commits
- Run agent_start.sh --quick before starting
- Check should_use_pr.sh when unsure
- End session with session.py end
- Use `find_automation.py` when unsure which script to use

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
├── agent_start.sh            # Start session (unified)
├── ai_commit.sh              # Commit wrapper
├── safe_push.sh             # Core git logic
├── should_use_pr.sh         # Decision helper
├── create_task_pr.sh        # Start PR
├── finish_task_pr.sh        # Submit PR
├── recover_git_state.sh     # Emergency recovery
├── find_automation.py       # Find the right script
└── session.py               # End session

docs/agents/
└── agent-workflow-master-guide.md  # Full guide
```

---

## 📇 Machine-Readable Indexes

- `scripts/automation-map.json` (task → script)
- `docs/docs-canonical.json` (topic → canonical doc)
- `scripts/index.json` + `docs/docs-index.json` (automation + docs catalog)

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
| **Build Once, Use Many** | `check_links.py` fixed 213 links in 5 sec |
| **Full Sessions** | 5-10+ commits per session, don't stop early |
| **Document Always** | Update TASKS.md, SESSION_LOG after work |

### Quick Automation Commands
```bash
.venv/bin/python scripts/check_links.py --fix              # Fix links
.venv/bin/python scripts/check_governance.py --structure    # Check structure
.venv/bin/python scripts/check_doc_versions.py --fix    # Fix versions
```

---

## 🎓 Learning Resources

### Day 1: Basics
- Run agent_start.sh --quick
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
3. Run `./scripts/agent_start.sh --quick`
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

**Last Updated:** 2026-01-13 | **Version:** 1.1.0

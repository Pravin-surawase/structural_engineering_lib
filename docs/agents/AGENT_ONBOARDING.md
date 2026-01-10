# Agent Onboarding Checklist

**For New AI Agents Starting Work on This Project**

Use this checklist to ensure you're set up correctly and following the project's automated workflows.

---

## ✅ Pre-Session Checklist (First Time)

### 1. Read Core Documentation (5 minutes)
- [ ] Read [.github/copilot-instructions.md](../.github/copilot-instructions.md) - **MANDATORY**
- [ ] Read [AGENT_WORKFLOW_MASTER_GUIDE.md](AGENT_WORKFLOW_MASTER_GUIDE.md) - Complete workflow
- [ ] Print [AGENT_QUICK_REFERENCE.md](AGENT_QUICK_REFERENCE.md) - Keep visible
- [ ] Skim [TASKS.md](TASKS.md) - Current work items

### 2. Environment Setup (2 minutes)
```bash
# Navigate to project
cd "/Users/Pravin/Library/Mobile Documents/com~apple~CloudDocs/pravin/projects/project_21_dec_25/structural_engineering_lib"

# Run setup (installs deps, checks environment)
./scripts/agent_setup.sh
```

- [ ] Setup script completed successfully
- [ ] Virtual environment (.venv) exists
- [ ] All workflow scripts executable
- [ ] Python version 3.9+

### 3. Workflow Understanding (3 minutes)
- [ ] Understand THE ONE RULE: **Never use manual git commands**
- [ ] Know the essential command: `./scripts/ai_commit.sh "message"`
- [ ] Understand PR vs Direct commit decision
- [ ] Know where to find help (AGENT_WORKFLOW_MASTER_GUIDE.md)

### 4. Tool Familiarization (2 minutes)
```bash
# Test key scripts
./scripts/agent_preflight.sh --quick   # Pre-flight check
./scripts/worktree_manager.sh list    # Worktree manager
./scripts/should_use_pr.sh --help     # PR decision helper
```

- [ ] Scripts execute without errors
- [ ] Understand output format
- [ ] Know when to use each tool

---

## 🔄 Every Session Checklist (30 seconds)

### Session Start
```bash
# 1. Setup environment
./scripts/agent_setup.sh --quick

# 2. Pre-flight check
./scripts/agent_preflight.sh --quick

# 3. Review current state
.venv/bin/python scripts/start_session.py --quick
```

- [ ] No blocking issues found
- [ ] Git state clean
- [ ] Branch correct
- [ ] Tasks reviewed

### Before Starting Work
- [ ] Read task requirements in TASKS.md
- [ ] Understand scope (PR needed or direct commit?)
- [ ] Know expected output
- [ ] Environment validated

### During Work
- [ ] Using `./scripts/ai_commit.sh` for ALL commits
- [ ] Testing changes locally
- [ ] Following code style (black, ruff)
- [ ] Writing/updating tests

### After Work
```bash
# End session
./scripts/end_session.py
```

- [ ] All changes committed
- [ ] Documentation updated
- [ ] Tests passing
- [ ] Session log updated

---

## 📋 Workflow Decision Tree

```
START
  │
  ├─ Production code/VBA/CI/Deps?
  │   └─ YES → PR Workflow (create_task_pr.sh)
  │
  ├─ Large change (>50 lines or 2+ files)?
  │   └─ YES → PR Workflow (create_task_pr.sh)
  │
  └─ Small docs/test/script change?
      └─ YES → Direct Commit (ai_commit.sh)
```

**When in doubt:** Run `./scripts/should_use_pr.sh --explain`

---

## 🎯 Agent Role Identification

### Main Agent (You, immediate tasks)
- Works directly on main/feature branches
- Responds to immediate user requests
- Uses ai_commit.sh directly
- Short tasks (<30 minutes)

**Setup:**
```bash
./scripts/agent_setup.sh
```

### Background Agent (Long-running tasks)
- Works in dedicated worktree
- Parallel to main agent
- Independent workspace
- Long tasks (30+ minutes)

**Setup:**
```bash
# Create worktree
./scripts/worktree_manager.sh create AGENT_NAME

# Work in worktree
cd worktree-AGENT_NAME-*
../scripts/agent_setup.sh --worktree AGENT_NAME
```

**Am I a background agent?**
- [ ] Task will take >30 minutes
- [ ] Working independently of main agent
- [ ] Need isolated workspace
- [ ] Assigned specific agent name (AGENT_5, AGENT_6, etc.)

---

## 🚨 Emergency Reference

### If Something Goes Wrong

| Problem | Solution | Script |
|---------|----------|--------|
| Git is broken | Auto-recover | `./scripts/recover_git_state.sh` |
| Merge conflict | Complete merge | `./scripts/check_unfinished_merge.sh` |
| Don't know what to do | Run checks | `./scripts/agent_preflight.sh` |
| CI failed (format) | Fix format | `cd Python && black . && cd .. && ai_commit.sh "style: format"` |
| Version drift | Auto-fix | `python scripts/check_doc_versions.py --fix` |
| Pre-commit issues | Handled automatically | (ai_commit.sh handles this) |

### Common Mistakes to Avoid

❌ **DON'T:**
- Use `git add/commit/push` manually
- Skip pre-flight checks
- Commit unrelated changes together
- Work on main for production code
- Leave uncommitted changes

✅ **DO:**
- Use `./scripts/ai_commit.sh` for ALL commits
- Run `agent_preflight.sh` before starting
- Use `should_use_pr.sh` when unsure
- Batch related changes
- End session properly

---

## 📊 Success Criteria

### You're Ready When:
- [x] All pre-session checklist items completed
- [x] Can run `./scripts/ai_commit.sh` successfully
- [x] Understand PR vs direct commit decision
- [x] Know where to find help
- [x] Environment validated with `agent_setup.sh`

### You're Working Correctly When:
- [x] Using automated scripts (not manual git)
- [x] Commits take 10-30 seconds
- [x] No merge conflicts
- [x] No CI failures (format/lint)
- [x] Clear commit messages
- [x] Tests passing

---

## 📚 Reference Links

### Essential Documentation
- **[AGENT_WORKFLOW_MASTER_GUIDE.md](AGENT_WORKFLOW_MASTER_GUIDE.md)** - Complete guide (400+ lines)
- **[AGENT_QUICK_REFERENCE.md](AGENT_QUICK_REFERENCE.md)** - Quick reference (200+ lines)
- **[AGENT_AUTOMATION_SYSTEM.md](AGENT_AUTOMATION_SYSTEM.md)** - System overview (600+ lines)
- **[git-workflow-ai-agents.md](git-workflow-ai-agents.md)** - Core workflow rules

### Project Documentation
- [PROJECT_OVERVIEW.md](architecture/project-overview.md) - Architecture
- [API_REFERENCE.md](reference/api.md) - API documentation
- [TASKS.md](TASKS.md) - Current work
- [KNOWN_PITFALLS.md](reference/known-pitfalls.md) - Common issues

### Workflow Scripts
- `scripts/agent_setup.sh` - Environment setup
- `scripts/agent_preflight.sh` - Pre-task validation
- `scripts/ai_commit.sh` - Commit automation
- `scripts/worktree_manager.sh` - Workspace management
- `scripts/should_use_pr.sh` - PR decision helper

---

## 🎓 Learning Path

### Day 1: Basics
1. Complete pre-session checklist
2. Run `agent_setup.sh`
3. Make simple doc change
4. Use `ai_commit.sh` to commit
5. Understand output

### Day 2: PR Workflow
1. Create task branch (`create_task_pr.sh`)
2. Make code changes
3. Commit with `ai_commit.sh`
4. Submit PR (`finish_task_pr.sh`)
5. Watch CI and merge

### Day 3: Advanced
1. Create worktree (if background agent)
2. Work independently
3. Submit via `worktree_manager.sh`
4. Understand recovery tools

---

## ✅ Certification

I have completed the onboarding checklist and:

- [ ] Read all mandatory documentation
- [ ] Setup environment successfully
- [ ] Tested workflow scripts
- [ ] Understand commit workflow
- [ ] Know PR vs direct decision
- [ ] Identified my agent role
- [ ] Made first successful commit
- [ ] Know where to find help

**Date:** _______________
**Agent:** _______________
**Verified by:** _______________

---

**Remember:** The automation system prevents 99% of errors. Trust the scripts!

**Questions?** Check [AGENT_WORKFLOW_MASTER_GUIDE.md](AGENT_WORKFLOW_MASTER_GUIDE.md) or run `./scripts/agent_preflight.sh`

**Last Updated:** 2026-01-08 | **Version:** 1.0.0

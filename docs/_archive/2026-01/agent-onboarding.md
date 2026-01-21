# Agent Onboarding Checklist

**For New AI Agents Starting Work on This Project**

Use this checklist to ensure you're set up correctly and following the project's automated workflows.

---

## ✅ Pre-Session Checklist (First Time)

### 1. Read Core Documentation (5 minutes)
- [ ] Read [.github/copilot-instructions.md](../../../.github/copilot-instructions.md) - **MANDATORY**
- [ ] Read [agent-workflow-master-guide.md](../../agents/guides/agent-workflow-master-guide.md) - Complete workflow
- [ ] Print [agent-quick-reference.md](../../agents/guides/agent-quick-reference.md) - Keep visible
- [ ] Skim [TASKS.md](../../TASKS.md) - Current work items

### 2. Environment Setup (30 seconds - ONE COMMAND!)
```bash
# Navigate to project
cd "/Users/Pravin/Library/Mobile Documents/com~apple~CloudDocs/pravin/projects/project_21_dec_25/structural_engineering_lib"

# Single unified command that does everything!
./scripts/agent_start.sh

# Or with options:
./scripts/agent_start.sh --quick             # Fast mode (skip detailed checks)
./scripts/agent_start.sh --agent 8           # Agent-specific guidance
./scripts/agent_start.sh --worktree AGENT_5  # Background agent worktree
```

- [ ] Setup script completed successfully
- [ ] Virtual environment (.venv) exists
- [ ] All workflow scripts executable
- [ ] Python version 3.9+

<details>
<summary>🔧 Fallback: Legacy 4-Command Flow (if agent_start.sh fails)</summary>

```bash
# Only use this if agent_start.sh has issues:
./scripts/agent_setup.sh              # Environment setup
./scripts/agent_preflight.sh --quick  # Pre-flight check
.venv/bin/python scripts/start_session.py --quick  # Session start
```

</details>

### 3. Workflow Understanding (3 minutes)
- [ ] Understand THE ONE RULE: **Never use manual git commands**
- [ ] Know the essential command: `./scripts/ai_commit.sh "message"`
- [ ] Understand PR vs Direct commit decision
- [ ] Know where to find help (agent-workflow-master-guide.md)

### 4. Tool Familiarization (2 minutes)
```bash
# Test key scripts (already run by agent_start.sh, but for reference)
./scripts/should_use_pr.sh --help     # PR decision helper
./scripts/worktree_manager.sh list    # Worktree manager
```

- [ ] Scripts execute without errors
- [ ] Understand output format
- [ ] Know when to use each tool

---

## 🔄 Every Session Checklist (30 seconds)

### Session Start (ONE COMMAND!)
```bash
# Start of every session - this does everything!
./scripts/agent_start.sh --quick

# Or with agent-specific guidance:
./scripts/agent_start.sh --agent 9 --quick  # Agent 9 (Governance)
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
- **[agent-workflow-master-guide.md](../../agents/guides/agent-workflow-master-guide.md)** - Complete guide (400+ lines)
- **[agent-quick-reference.md](../../agents/guides/agent-quick-reference.md)** - Quick reference (200+ lines)
- **[agent-automation-system.md](../../agents/guides/agent-automation-system.md)** - System overview (600+ lines)
- **[git-workflow-ai-agents.md](../../contributing/git-workflow-ai-agents.md)** - Core workflow rules

### Project Documentation
- [project-overview.md](../../architecture/project-overview.md) - Architecture
- [api-reference.md](../../reference/api.md) - API documentation
- [TASKS.md](../../TASKS.md) - Current work
- [known-pitfalls.md](../../reference/known-pitfalls.md) - Common issues

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

## 🧠 Automation-First Mindset

**Critical principle: 10+ similar issues = Build automation FIRST!**

### What This Means

| See This... | Do This... |
|-------------|------------|
| 10+ broken links | Run `python scripts/fix_broken_links.py --fix` |
| 10+ file renames needed | Write a rename script first |
| Repetitive manual task | Check if automation exists in `scripts/` |
| New pattern of issues | Create a script, document it, use it |

### Session Duration Expectations

- **Minimum:** 5+ commits or 30+ minutes of substantial work
- **Don't stop early** — complete a full task or meaningful chunk
- **If blocked:** Move to the next task, don't end the session
- **Before ending:** Update TASKS.md, SESSION_LOG.md, run `end_session.py`

### Example Automation
```bash
python scripts/fix_broken_links.py --fix      # Fixed 213 links in 5 seconds
python scripts/validate_folder_structure.py   # Validates entire repo structure
python scripts/check_doc_versions.py --fix    # Syncs doc versions automatically
```

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

**Questions?** Check [agent-workflow-master-guide.md](../../agents/guides/agent-workflow-master-guide.md) or run `./scripts/agent_start.sh`

**Last Updated:** 2026-01-11 | **Version:** 2.0.0

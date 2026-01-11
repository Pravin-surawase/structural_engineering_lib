# Agent Workflow Master Guide
**Version:** 2.1.0
**Last Updated:** 2026-01-11
**Status:** ✅ Production Ready

> **FOR ALL AI AGENTS:** This is your ONE SOURCE OF TRUTH for all operations.
> Read this FIRST before any work. Following these rules prevents 99% of errors.

---

## 🎯 Quick Start (30 Seconds)

### Step 1: Setup Your Environment
```bash
# DEFAULT: Quick mode (6s, 54% faster, sufficient for 95% of sessions)
./scripts/agent_start.sh --quick

# OPTIONAL: Full validation (13s, use when debugging)
./scripts/agent_start.sh

# With agent-specific guidance:
./scripts/agent_start.sh --agent 9 --quick  # For governance agents

# Legacy commands (still work):
./scripts/agent_setup.sh
./scripts/agent_preflight.sh
.venv/bin/python scripts/start_session.py
```

### Step 2: Work & Commit
```bash
# Make changes, then:
./scripts/ai_commit.sh "feat: your description"
```

### Step 3: End Session
```bash
# Run BEFORE ending session:
.venv/bin/python scripts/end_session.py
```

---

## 🚨 CRITICAL RULES (Read These!)

### Rule 1: NEVER Use Manual Git Commands
❌ **FORBIDDEN:**
```bash
git add .
git commit -m "message"
git pull
git push
```

✅ **ALWAYS USE:**
```bash
./scripts/ai_commit.sh "message"
```

**Why?** Manual git causes:
- Merge conflicts (wastes 10-30 minutes)
- Pre-commit hook failures
- Diverged history
- Lost work

### Rule 2: Know Your Decision Path
```bash
# Is this a PR-worthy change?
./scripts/should_use_pr.sh --explain

# Results tell you:
# → Direct commit (docs/tests/scripts)
# → PR required (production code/VBA/CI)
```

### Rule 3: Use Worktrees for Long-Running Work
```bash
# Main agent: works directly on main
# Background agents (Agent 5, 6, etc.): use worktrees
./scripts/worktree_manager.sh create AGENT_NAME
```

---

## 🧠 Automation-First Mentality (CRITICAL)

> **If you see 10+ similar issues → Build automation FIRST, never fix manually!**

### Core Principles

| Principle | What It Means |
|-----------|---------------|
| **Pattern Recognition** | 10+ similar issues = automation script, not manual fixes |
| **Research First** | Check `scripts/` for existing tools before writing new ones |
| **Build Once, Use Many** | Scripts like `fix_broken_links.py` save hours of future work |
| **Commit Incrementally** | Use `ai_commit.sh` frequently, don't accumulate changes |
| **Full Sessions** | Aim for 5-10+ commits per session, don't stop early |
| **Document Everything** | Update TASKS.md, SESSION_LOG.md after significant work |

### Example Automation Scripts
```bash
# Fix broken links automatically (fixed 213 links in 5 seconds)
python scripts/fix_broken_links.py --fix

# Validate folder structure
python scripts/validate_folder_structure.py

# Check doc version drift
python scripts/check_doc_versions.py
```

### Session Duration Guidelines
- **Minimum:** 5+ commits or 30+ minutes of substantial work
- **Target:** Complete a full task or meaningful chunk before stopping
- **If blocked:** Move to next task instead of ending session
- **Before stopping:** Update TASKS.md, SESSION_LOG.md, run end_session.py

---

## 📋 Decision Trees

### Decision Tree 1: What Workflow?

```
START
  │
  ├─ Making production code changes? ──YES→ PR Workflow
  ├─ Changing VBA files? ──YES→ PR Workflow
  ├─ Changing CI workflows? ──YES→ PR Workflow
  ├─ Updating dependencies? ──YES→ PR Workflow
  │
  ├─ Only docs? ──YES→ Direct Commit
  ├─ Only tests? ──YES→ Check size
  │   ├─ <50 lines? ──YES→ Direct Commit
  │   └─ 50+ lines? ──YES→ PR Workflow
  │
  └─ Scripts only? ──YES→ Check size
      ├─ <50 lines? ──YES→ Direct Commit
      └─ 50+ lines? ──YES→ PR Workflow
```

### Decision Tree 2: Am I Main or Background Agent?

```
START
  │
  ├─ Working on immediate user request? ──YES→ Main Agent
  │   └─ Use: ai_commit.sh directly
  │
  └─ Long-running task (30+ min)? ──YES→ Background Agent
      └─ Use: Worktree + agent_setup.sh --worktree
```

---

## 🔄 Workflow Patterns

### Pattern A: Direct Commit (Docs/Small Changes)
```bash
# 1. Preflight check
./scripts/agent_preflight.sh

# 2. Make changes
# ... edit files ...

# 3. Commit (script handles staging, hooks, push)
./scripts/ai_commit.sh "docs: update guide"

# 4. Done! ✓
```

### Pattern B: PR Workflow (Production Code)
```bash
# 1. Preflight check
./scripts/agent_preflight.sh

# 2. Create task branch
./scripts/create_task_pr.sh TASK-270 "Fix benchmark signatures"

# 3. Make changes and commit
# ... edit files ...
./scripts/ai_commit.sh "fix: update benchmark function calls"

# 4. Finish and create PR
./scripts/finish_task_pr.sh TASK-270 "Fix benchmark signatures"

# 5. Wait for CI
gh pr checks $(gh pr list --head task/TASK-270 --json number -q '.[0].number') --watch

# 6. Merge when green
gh pr merge $(gh pr list --head task/TASK-270 --json number -q '.[0].number') --squash --delete-branch
```

### Pattern C: Worktree Workflow (Background Agents)
```bash
# 1. Setup worktree environment
./scripts/agent_setup.sh --worktree AGENT_5

# 2. Work in worktree
cd worktree-AGENT_5-$(date +%Y-%m-%d)

# 3. Commit as usual
./scripts/ai_commit.sh "feat: learning curriculum module 3"

# 4. When ready, submit work
cd $PROJECT_ROOT
./scripts/worktree_manager.sh submit AGENT_5 "Learning Curriculum Module 3"

# 5. Manager creates PR and cleans up worktree
```

---

## 🛠️ Automation Scripts Reference

### Core Workflow Scripts

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `agent_setup.sh` | Setup environment | Once per session |
| `agent_preflight.sh` | Pre-task validation | Before every task |
| `ai_commit.sh` | Safe commit & push | Every commit |
| `should_use_pr.sh` | Decision helper | When unsure |
| `end_session.py` | Session cleanup | End of session |

### PR Management Scripts

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `create_task_pr.sh` | Start PR workflow | Before production changes |
| `finish_task_pr.sh` | Create PR | When work complete |
| `gh pr checks --watch` | Monitor CI | After PR creation |
| `gh pr merge --squash` | Merge PR | When CI passes |

### Worktree Management Scripts

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `worktree_manager.sh create` | Create agent workspace | Background agents |
| `worktree_manager.sh submit` | Submit work via PR | Work complete |
| `worktree_manager.sh list` | Show all worktrees | Status check |
| `worktree_manager.sh cleanup` | Remove worktrees | Cleanup |

### Recovery Scripts

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `recover_git_state.sh` | Fix git issues | Git errors |
| `check_unfinished_merge.sh` | Detect merge state | Suspicious behavior |
| `validate_git_state.sh` | Comprehensive check | After recovery |

---

## 🔍 Common Scenarios & Solutions

### Scenario 1: Pre-commit Hook Modified Files
**Symptom:** "Files modified after staging"

**Solution:** Nothing! `safe_push.sh` handles this automatically:
```bash
./scripts/ai_commit.sh "message"
# Script detects changes, re-stages, amends commit
# All automatic!
```

### Scenario 2: Push Rejected (Non-Fast-Forward)
**Symptom:** `! [rejected] main -> main (non-fast-forward)`

**Solution:**
```bash
./scripts/recover_git_state.sh
# Follows the printed recovery steps
```

### Scenario 3: Merge Conflict in TASKS.md
**Symptom:** Multiple agents editing same file

**Solution:**
```bash
# 1. Check state
./scripts/check_unfinished_merge.sh

# 2. If unfinished merge detected:
git checkout --ours docs/TASKS.md  # Keep our version
git add docs/TASKS.md
git commit --no-edit
git push

# 3. Or use recovery script:
./scripts/recover_git_state.sh
```

### Scenario 4: Worktree Agent Work Ready
**Symptom:** Agent 6 completed UI-003/004/005

**Solution:**
```bash
# 1. Navigate to worktree
cd worktree-2026-01-08T06-07-26

# 2. Check status
git status

# 3. Commit if changes staged
./scripts/ai_commit.sh "feat(ui): UI-003/004/005 complete"

# 4. Return to main and create PR
cd $PROJECT_ROOT
./scripts/worktree_manager.sh submit AGENT_6 "UI-003/004/005 Modernization"
```

### Scenario 5: CI Fails on Formatting
**Symptom:** Format check failed on PR

**Solution:**
```bash
# 1. Run formatters locally
cd Python
.venv/bin/python -m black .
.venv/bin/python -m ruff check --fix .

# 2. Commit fixes
cd ..
./scripts/ai_commit.sh "style: apply black/ruff formatting"

# 3. CI will re-run automatically
```

### Scenario 6: Version Drift Error
**Symptom:** Pre-commit hook: "Version drift detected"

**Solution:**
```bash
# Auto-fix all version references
.venv/bin/python scripts/check_doc_versions.py --fix

# Commit the fixes
./scripts/ai_commit.sh "chore: sync version references"
```

---

## 🎭 Agent Role Patterns

### Main Agent (You)
**Characteristics:**
- Responds to immediate user requests
- Works directly on main branch (for docs)
- Uses PR workflow for production code
- Manages other agents' work

**Workflow:**
```bash
# Start session
./scripts/agent_setup.sh

# Work on request
./scripts/ai_commit.sh "..."

# End session
./scripts/end_session.py
```

### Background Agent (Agent 5, 6, etc.)
**Characteristics:**
- Long-running tasks (30+ minutes)
- Works in dedicated worktree
- Independent of main agent
- Submits work when complete

**Workflow:**
```bash
# Setup (once)
./scripts/agent_setup.sh --worktree AGENT_N

# Work (in worktree)
cd worktree-AGENT_N-*
./scripts/ai_commit.sh "..."

# Submit (from project root)
cd $PROJECT_ROOT
./scripts/worktree_manager.sh submit AGENT_N "Work description"
```

---

## 📊 Quality Gates

### Pre-Commit Gates (Automatic)
- ✅ Code formatting (black, ruff)
- ✅ Version consistency check
- ✅ Document length limits
- ✅ No merge conflict markers
- ✅ No trailing whitespace

### Pre-Push Gates (Manual)
```bash
# Run before pushing
./scripts/agent_preflight.sh

# Checks:
# - Git state clean
# - No unfinished merges
# - Branch up to date
# - Tests passing (optional)
```

### Streamlit Validation (Automatic in CI/Pre-commit)
```bash
# AST Scanner - detects runtime errors before they happen
.venv/bin/python scripts/check_streamlit_issues.py --all-pages

# Pylint - code quality checks
.venv/bin/python -m pylint --rcfile=.pylintrc-streamlit streamlit_app/

# Both run automatically on commit and in CI
# CRITICAL issues block the commit/PR
# HIGH issues are warnings only
```

**Scanner Intelligence (Zero False Positives):**
- Recognizes zero-validation patterns: `x / y if y > 0 else 0`
- Handles compound conditions: `if x > 0 and y > 0:`
- Tracks validated variables in if-blocks
- Understands ternary expressions, dict access, complex denominators
- Phase 1B complete (2026-01-09): 100% accurate division safety detection

### Pre-Release Gates
```bash
# Comprehensive check
.venv/bin/python scripts/check_handoff_ready.py

# Checks:
# - All session docs updated
# - No uncommitted changes
# - Version numbers consistent
# - Links valid
```

---

## 🚀 Performance Tips

### Tip 1: Batch Related Changes
❌ **Bad:**
```bash
# 5 separate commits for one feature
./scripts/ai_commit.sh "add function"
./scripts/ai_commit.sh "add test"
./scripts/ai_commit.sh "add docs"
./scripts/ai_commit.sh "fix typo"
./scripts/ai_commit.sh "another typo"
```

✅ **Good:**
```bash
# Make all related changes, then one commit
# ... add function, test, docs ...
./scripts/ai_commit.sh "feat: add feature X with tests and docs"
```

### Tip 2: Use Worktrees for Parallel Work
❌ **Bad:** Switching branches frequently
```bash
git checkout task/UI-003
# work...
git checkout main
git checkout task/API-002
# work...
```

✅ **Good:** Separate worktrees
```bash
# UI work in worktree
cd worktree-AGENT_6

# API work in main repo
cd $PROJECT_ROOT
```

### Tip 3: Leverage Automation
❌ **Bad:** Manual steps
```bash
git fetch
git pull
git add file1 file2
git commit -m "message"
git push
```

✅ **Good:** Single command
```bash
./scripts/ai_commit.sh "message"
```

---

## 📚 Additional Resources

### Essential Docs
- [TASKS.md](../../TASKS.md) - Current work items
- [SESSION_LOG.md](../../SESSION_LOG.md) - Session history
- [next-session-brief.md](../../planning/next-session-brief.md) - Handoff doc

### Workflow Docs
- [git-workflow-ai-agents.md](../../contributing/git-workflow-ai-agents.md) - Core workflow
- [agent-bootstrap.md](../../getting-started/agent-bootstrap.md) - Initial setup guide

### Testing Docs
- [testing-strategy.md](../../contributing/testing-strategy.md) - Testing approach
- [vba-testing-guide.md](../../contributing/vba-testing-guide.md) - VBA testing

### Architecture Docs
- [project-overview.md](../../architecture/project-overview.md) - System architecture
- [api-reference.md](../../reference/api.md) - API documentation

---

## 🐛 Troubleshooting

### Problem: Script not executable
```bash
chmod +x scripts/*.sh
```

### Problem: Can't find script
```bash
# Always run from project root
cd "/Users/Pravin/Library/Mobile Documents/com~apple~CloudDocs/pravin/projects/project_21_dec_25/structural_engineering_lib"
```

### Problem: Python venv not found
```bash
# Setup environment first
./scripts/agent_setup.sh
```

### Problem: Git state corrupted
```bash
# Recovery script
./scripts/recover_git_state.sh

# Follow printed instructions
```

### Problem: Merge conflict
```bash
# Check merge state
./scripts/check_unfinished_merge.sh

# Keep our version (usually)
git checkout --ours <file>
git add <file>
git commit --no-edit
```

---

## ✅ Success Checklist

### Before Starting Work
- [ ] Ran `./scripts/agent_setup.sh`
- [ ] Ran `./scripts/agent_preflight.sh`
- [ ] Read relevant task in TASKS.md
- [ ] Understand PR vs direct commit decision

### During Work
- [ ] Using `./scripts/ai_commit.sh` for all commits
- [ ] NOT using manual git commands
- [ ] Testing changes locally
- [ ] Following code style guidelines

### After Work
- [ ] All tests passing
- [ ] CI checks passing (if PR)
- [ ] Documentation updated
- [ ] Ran `./scripts/end_session.py`

### Before Handoff
- [ ] TASKS.md reflects current state
- [ ] SESSION_LOG.md has today's entry
- [ ] NEXT_SESSION_BRIEF.md updated
- [ ] No uncommitted changes

---

## 🎓 Learning Path

### Level 1: Basics (Day 1)
1. Run agent_setup.sh
2. Use ai_commit.sh for simple docs change
3. Understand should_use_pr.sh output

### Level 2: PR Workflow (Day 2-3)
1. Create task branch with create_task_pr.sh
2. Make code changes
3. Submit PR with finish_task_pr.sh
4. Monitor CI and merge

### Level 3: Worktrees (Day 4-5)
1. Create worktree for background task
2. Work independently
3. Submit work via worktree_manager.sh

### Level 4: Recovery (Ongoing)
1. Practice with recover_git_state.sh
2. Understand merge conflict resolution
3. Master pre-commit hook handling

---

## 🏗️ Folder Structure Governance

> **Reference:** [folder-structure-governance.md](../../guidelines/folder-structure-governance.md)

All agents MUST follow the published governance spec. Key rules:

### Root Files (max 10)
- Keep root clean: only top-level project files
- All role files go in `agents/roles/` (not `agents/`)
- All workflow guides go in `docs/agents/guides/` (not `docs/agents/`)

### Creating New Documents
**ALWAYS check:** Does this file need folder migration pre-approval?
```bash
# BEFORE creating a file:
python scripts/check_governance_compliance.py --strict

# WHEN creating a file:
# Include metadata header (see next section)
# Choose correct folder per governance spec
# Run validators after creation
```

### Safe File Operations (CRITICAL)
**NEVER use:** `rm`, `mv`, or `git rm` manually
```bash
# ✅ ALWAYS USE these scripts:
python scripts/safe_file_move.py old.md new.md
python scripts/safe_file_delete.py old.md

# Why? Auto-updates all links (789+ internal links to protect!)
```

### Pre-Migration Checklist
Before moving files or creating new folder structures:
- [ ] Check [folder-structure-governance.md](../../guidelines/folder-structure-governance.md)
- [ ] Run `python scripts/check_governance_compliance.py --strict`
- [ ] Verify target folder is compliant with governance
- [ ] Document migration in TASKS.md
- [ ] Use safe_file_move.py for all moves
- [ ] Validate links after migration: `python scripts/check_links.py`

---

## 📄 Document Metadata Standard

All NEW documents MUST include this metadata block at the top:

```markdown
# Document Title
**Type:** [Implementation|Guide|Research|Architecture|Reference|Decision]
**Audience:** [All Agents|Implementation Agents|Architects|Support Agents]
**Status:** [Draft|Review|Approved|Deprecated]
**Importance:** [Critical|High|Medium|Low]
**Version:** 1.0.0
**Created:** YYYY-MM-DD
**Last Updated:** YYYY-MM-DD
**Related Tasks:** Task identifiers (see docs/planning/TASKS.md)
| **Type** | Classifies document purpose | Implementation, Guide, Research, Decision, Architecture |
| **Audience** | Who should read this? | All Agents, Implementation Agents, Architects |
| **Status** | Development stage | Draft, Review, Approved, Deprecated, Production Ready |
| **Importance** | Priority level | Critical (blocks work), High, Medium, Low |
| **Version** | Semantic versioning | 1.0.0, 2.1.3 (increment on breaking changes) |
| **Created** | When written | YYYY-MM-DD format |
| **Last Updated** | When last edited | YYYY-MM-DD format (update on any change) |
| **Related Tasks** | Links to tracker | Task identifiers (see docs/planning/TASKS.md) |
| **Location Rationale** | Why this folder? | Reference folder-structure-governance.md |

### When to Update Metadata
- ✅ **Last Updated:** Every time document changes
- ✅ **Version:** When breaking changes made (major) or new sections added (minor)
- ✅ **Status:** When development stage changes

### Example: Well-Formatted Document
```markdown
# Beam Design Integration Guide
**Type:** Implementation
**Audience:** Implementation Agents
**Status:** Approved
**Importance:** High
**Version:** 2.1.0
**Created:** 2025-06-15
**Last Updated:** 2026-01-11
**Related Tasks:** IMPL-003, IMPL-004 (see docs/planning/TASKS.md)
---

## 📝 Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.0.0 | 2026-01-11 | Added governance compliance rules, document metadata standard, safe file operations section, pre-migration checklist |
| 1.0.0 | 2026-01-08 | Initial comprehensive guide |

---

**Remember:** When in doubt, ask! Better to clarify than to break things.

**Emergency Contact:** Check terminal output, logs/git_workflow.log, or recover_git_state.sh

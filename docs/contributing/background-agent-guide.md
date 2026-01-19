# Background Agent Parallel Work Guide

**Purpose:** Enable safe parallel work without conflicts, CI failures, or duplicated effort.

**Scope:** AI agents (Claude, Copilot, ChatGPT instances) working in parallel with the MAIN agent/user.

**Important:** "Background agents" = other AI assistant instances, NOT human developers. These AI agents work locally on branches; MAIN agent/user handles all remote operations (push, PR, merge).

**Status:** v2.0 - Updated for multi-agent collaboration framework (2026-01-07)

---

## How This Works

### Roles
- **Background AI Agents:** Other AI assistant instances (Claude, Copilot, ChatGPT) working on assigned tasks
- **MAIN Agent/User:** You (the project owner) coordinating work and handling all remote Git operations

### Simple Workflow
1. **Background agent:** Creates branch locally → Makes changes → Commits → Runs checks → Notifies MAIN
2. **MAIN agent/user:** Reviews work → Pushes to remote → Creates PR → Monitors CI → Merges

### Why This Works
✅ **Safe:** Background agents can't push broken code to remote
✅ **Simple:** Background agents work locally only, no GitHub access needed
✅ **Clean:** Single point of control (you) for all remote operations
✅ **Efficient:** Background agents work in parallel, you handle coordination

### Example in Practice

**Scenario:** You want to fix 8 test failures (TASK-270)

**You (MAIN agent) say to background Claude instance:**
> "Create branch feature/TASK-270-fix-tests, fix the 8 test failures from API refactoring, commit locally, run all checks, and hand off to me. Don't push anything."

**Background Claude does:**
```bash
./scripts/worktree_manager.sh create AGENT_2
cd worktree-AGENT_2-*
# ... fixes tests ...
../scripts/ai_commit.sh "test: fix exception types in 8 failing tests"
python -m pytest  # ✅ All pass
# Notifies you with handoff message
```

**You (MAIN agent) do:**
```bash
./scripts/worktree_manager.sh submit AGENT_2 "Fix TASK-270 test failures"
./scripts/pr_async_merge.sh status
```

**Result:** Background agent did the work, you maintained control of the repository.

---

## Research Foundation

This guide implements evidence-based practices from comprehensive research analyzing 12 years of industry data, academic studies, and empirical findings on parallel agent coordination.

**📊 For detailed analysis, see:** [Background Agent Parallel Work Research](../research/background-agent-parallel-work.md) (1,800+ lines, 30+ citations)

**Key Research-Backed Findings:**
1. **WIP Limits:** Optimal WIP=2 (1 MAIN + 1 background) reduces context switching 40% vs. WIP=3+ (Anderson, 2010; Kanban research)
2. **File Ownership:** Clear boundaries reduce merge conflicts 85% (Microsoft Research, 2016)
3. **Quality Gates:** Pre-commit automation catches 90% of integration issues before CI (IBM DevOps, 2023)
4. **Context Management:** Persistent context documents reduce onboarding time 60% (CMU SEI, 2018)
5. **Communication:** Structured handoffs reduce context loss from 50% to 10% (Basecamp Remote Research, 2024)

The practical workflows below implement these research-validated practices.

---

## Quick Start (5 minutes)

### 1. Understand Your Role

Read the comprehensive framework first:
- **[Agent Collaboration Framework](agent-collaboration-framework.md)** - Multi-agent system, workflows, coordination protocols

Then review your specific role:
- **RESEARCHER:** Create research documents in `docs/research/` (800+ lines)
- **DEV:** Implement features following API guidelines, all tests pass
- **TESTER:** Write comprehensive test suites, benchmarks, visual regression
- **DEVOPS:** Maintain CI/CD, automation scripts, security scanning
- **PM:** Create roadmaps, break down epics, estimate effort

### 2. Bootstrap Your Session

```bash
# Start session with context loading
.venv/bin/.venv/bin/python scripts/start_session.py

# Read persistent context
cat docs/planning/memory.md
```

### 3. Confirm Task Assignment

With MAIN agent, confirm:
- **Task ID:** TASK-XXX
- **Agent Role:** Your role (RESEARCHER, DEV, TESTER, DEVOPS, PM)
- **File Boundary:** What you may edit, what to avoid
- **Acceptance Criteria:** Definition of done
- **Blockers:** Dependencies on other tasks

### 4. Review Git Workflow

Read: `docs/git-workflow-ai-agents.md`

Key rule: **Never run manual git commands.** Use workflow scripts only.

---

## Task Selection (Parallel-Safe)

### RESEARCHER Agent
✅ **Safe:**
- Research documents in `docs/research/`
- Guideline documents in `docs/guidelines/`
- Standalone analysis documents

❌ **Avoid:**
- Implementation code
- Test files
- Shared tracking files (TASKS.md, SESSION_LOG.md)

### DEV Agent
✅ **Safe:**
- Single-module changes with clear boundaries
- New feature modules with isolated scope
- Refactoring within assigned module

❌ **Avoid:**
- Multi-module refactors overlapping other work
- Core API changes during other API work
- Shared utility modules without coordination

### TESTER Agent
✅ **Safe:**
- Test files for specific modules
- Benchmarks for isolated features
- Test utilities and fixtures

❌ **Avoid:**
- Changing implementation code
- Modifying test infrastructure during other test work
- Shared conftest.py without coordination

### DEVOPS Agent
✅ **Safe:**
- CI/CD workflow files
- Automation scripts in `scripts/`
- Security scanning configuration

❌ **Avoid:**
- Application code changes
- Test code changes
- Documentation beyond DevOps scope

### PM Agent
✅ **Safe:**
- Roadmap documents in `docs/planning/`
- Task breakdown documents
- Effort estimation documents

❌ **Avoid:**
- Implementation decisions
- Code changes
- TASKS.md updates without MAIN approval

---

## Branching and Isolation

### Background Agent Workflow (Local Work Only)

**Background AI agents work locally, MAIN agent/user handles remote operations.**

```bash
# 1. Create worktree locally
./scripts/worktree_manager.sh create AGENT_NAME
cd worktree-AGENT_NAME-*

# 2. Make changes in isolated scope
# ... edit files ...

# 3. Commit locally (pre-commit hooks run automatically)
../scripts/ai_commit.sh "feat: describe change"

# 4. Run local checks
cd Python && python -m pytest  # All tests
python -m black .              # Format
python -m ruff check .         # Lint
python -m mypy                 # Type check

# 5. Notify MAIN agent with handoff (see Communication section below)
# STOP HERE - Do not push or create PR
```

### MAIN Agent/User Workflow (Remote Operations)

**After receiving handoff from background agent:**

```bash
# 1. Submit worktree via automation (push + PR creation)
./scripts/worktree_manager.sh submit AGENT_NAME "TASK-XXX: description"

# 2. Wait for CI checks
./scripts/pr_async_merge.sh status

# 5. Merge when ready
gh pr merge --squash
```

### Direct Commit Workflow (Research/Docs Only)

**For non-code changes (research docs, guidelines) - background agents can work on main:**

```bash
# Background agent makes changes on main branch
# ... edit docs/research/file.md ...
./scripts/ai_commit.sh "docs: add research for topic X"

# STOP - notify MAIN agent (no manual push)
```

**Rule:** Background agents NEVER push to remote. All remote operations (push, PR, merge) done by MAIN agent/user only.

---

## Quality Guardrails (Avoid CI Failures)

### Before Every Commit

**For Python code changes:**
```bash
# Format with Black
.venv/bin/python -m black Python/

# Lint with Ruff (auto-fix)
.venv/bin/python -m ruff check --fix Python/

# Type check with mypy
.venv/bin/python -m mypy Python/structural_lib

# Run affected tests
.venv/bin/python -m pytest Python/tests/unit/test_your_module.py -v
```

**For all changes:**
```bash
# Let pre-commit hooks run automatically
./scripts/ai_commit.sh "type: message"

# Fix any reported issues before retry
```

### Common Failure Modes (Lessons Learned)

| Issue | Cause | Prevention |
|-------|-------|------------|
| **Formatting drift** | Black/Ruff not run after merge | Run formatters before commit |
| **Mypy errors** | Return type changes not propagated | Update all call sites |
| **Import sorting** | Manual imports added | Use `ruff --fix` |
| **Test failures** | Exception types changed | Update tests for new exceptions |
| **Benchmark errors** | Function signatures changed | Update benchmark calls |

### When CI Fails

1. **Check GitHub Actions logs** for specific error
2. **Reproduce locally** with same command
3. **Fix issue** in your branch
4. **Re-run checks** locally before push
5. **Push fix** with `./scripts/ai_commit.sh`

### Always Monitor CI (Required)

After every push or PR update, monitor checks to completion and report status.

**For PR branches:**
```bash
gh pr checks <PR_NUMBER> --watch
```

**For direct pushes to main:**
```bash
gh run list -w "Fast PR Checks" -L 1
gh run list -w "CodeQL" -L 1
```

---

## Communication + Handoff

### Task Completion Handoff

When your task is complete (committed locally, checks passed), notify MAIN agent with this template:

```markdown
## Handoff: [ROLE] → MAIN

**Task:** TASK-XXX
**Agent Role:** [RESEARCHER/DEV/TESTER/DEVOPS/PM]
**Branch:** worktree-AGENT_NAME-* (auto)
**Status:** ✅ Committed locally, all checks passed

### Summary
[2-3 sentences: what changed and why]

### Files Changed
- `path/to/file1.py` - [purpose]
- `path/to/file2.py` - [purpose]

### Key Decisions
- **Decision 1:** [rationale]
- **Decision 2:** [rationale]

### Local Test Results
- X tests passing locally
- Y new tests added
- Coverage: Z%
- Black/Ruff/Mypy: ✅ Clean

### Open Questions
- [Any unresolved items or needed clarifications]

### Action Required by MAIN
1. Review changes in worktree
2. Submit via automation: `./scripts/worktree_manager.sh submit AGENT_NAME "TASK-XXX: description"`
3. Monitor CI: `./scripts/pr_async_merge.sh status`
```

**Important:** Background agents do NOT push to remote or create PRs. MAIN agent/user handles all remote operations.

### During Development Questions

If background agent has questions during work, notify MAIN agent with this format:

```markdown
## Question: [ROLE] → MAIN

**Task:** TASK-XXX
**Current Progress:** [what's done so far]

**Question:** [specific question with context]

**Options Considered:**
1. [option A] - [pros/cons]
2. [option B] - [pros/cons]

**Recommendation:** [option] because [rationale]

**Waiting for guidance before proceeding.**
```

MAIN agent responds with decision, background agent continues work.

---

## Parallel Coordination Rules (Strict)

### WIP Limits
- **One task per background agent** (WIP=1)
- **Default total WIP=2** (MAIN + 1 background)
- **WIP=3 only with MAIN approval** and fully isolated tasks

### File Ownership (Avoid Conflicts)

**High-churn files** (MAIN agent only):
- `docs/TASKS.md`
- `docs/SESSION_LOG.md`
- `docs/planning/next-session-brief.md`
- `docs/planning/memory.md` (MAIN updates, agents read)

**Agent-owned files** (safe for parallel work):
- `docs/research/TASK-XXX-*.md` (RESEARCHER)
- `Python/structural_lib/module_name.py` (DEV on assigned module)
- `Python/tests/*/test_module.py` (TESTER for assigned module)
- `.github/workflows/*.yml` (DEVOPS)
- `docs/planning/roadmap-*.md` (PM)

### Merge Protocol

**Background agents NEVER push or merge.** Only MAIN agent/user handles remote operations.

**Sequence:**
1. Background agent commits locally and notifies MAIN with handoff
2. MAIN agent reviews local commits in the worktree
3. MAIN submits via automation: `./scripts/worktree_manager.sh submit AGENT_NAME "TASK-XXX: description"`
4. MAIN monitors CI: `./scripts/pr_async_merge.sh status`
5. MAIN merges when ready (or daemon auto-merges)
6. MAIN updates TASKS.md and memory.md

### Conflict Resolution

If conflicts appear:
1. **Stop work immediately**
2. **Notify MAIN agent** with context
3. **Wait for coordination** before proceeding
4. **Never force push** to resolve conflicts

---

## Context Management (2026 Best Practices)

### Before Starting Work

**Read persistent context:**
```bash
# Project state and challenges
cat docs/planning/memory.md

# Current task board
cat docs/TASKS.md

# API guidelines (if implementing features)
cat docs/guidelines/api-design-guidelines.md
```

### During Work

**Keep context focused:**
- Read only files relevant to your task
- Use `rg` for search (faster for specific queries)
- Document decisions in your PR description

### Fresh Sessions

**Start fresh when context drifts:**
```bash
# In your terminal, use /clear command to reset context
# Then reload essential context from memory.md
```

**Signs of context drift:**
- Repeating previous suggestions
- Forgetting task constraints
- Mixing up file locations

---

## Agent-Specific Workflows

See [Agent Collaboration Framework](agent-collaboration-framework.md) for detailed workflows:

- **Section 2.1:** RESEARCHER workflow (research documents)
- **Section 2.2:** DEV workflow (feature implementation)
- **Section 2.3:** TESTER workflow (test creation)
- **Section 2.4:** DEVOPS workflow (CI/CD maintenance)
- **Section 2.5:** PM workflow (roadmap creation)

---

## Success Metrics

### RESEARCHER Agent
- ✅ Research docs 800+ lines minimum
- ✅ Code examples included
- ✅ Direct commits to main (or PR if requested)

### DEV Agent
- ✅ All tests passing locally before PR
- ✅ Black + Ruff clean
- ✅ Mypy passes
- ✅ CHANGELOG updated

### TESTER Agent
- ✅ Coverage maintained or improved
- ✅ All new tests passing
- ✅ Benchmarks passing (if added)

### DEVOPS Agent
- ✅ CI checks passing
- ✅ Scripts tested locally
- ✅ Documentation updated

### PM Agent
- ✅ Roadmap clear and actionable
- ✅ Effort estimates included
- ✅ Dependencies identified

---

## Troubleshooting

### Issue: "File has not been read yet"

**Cause:** Trying to Edit before Read
**Fix:** Always Read file first, then Edit/Write

### Issue: Pre-commit hooks fail

**Cause:** Formatting/lint issues
**Fix:**
```bash
cd Python
python -m black .
python -m ruff check --fix .
./scripts/ai_commit.sh "type: message"  # Retry
```

### Issue: Test failures after merge

**Cause:** API signature changes not propagated
**Fix:** Update all call sites (CLI, tests, examples)

### Issue: Benchmark errors

**Cause:** Function signatures changed
**Fix:** Update benchmark function calls to match new signatures

### Issue: Merge conflicts

**Cause:** Parallel work on same files
**Fix:** Stop, notify MAIN, wait for coordination

---

## Quick Reference

### Background Agent Commands (Local Only)

```bash
# Start session - read context
cat docs/planning/memory.md
cat docs/TASKS.md

# Create feature branch
./scripts/worktree_manager.sh create AGENT_NAME
cd worktree-AGENT_NAME-*

# Make changes, then commit
../scripts/ai_commit.sh "type: message"

# Run local checks
cd Python
python -m pytest              # All tests
python -m black .             # Format
python -m ruff check --fix .  # Lint
python -m mypy                # Type check

# STOP - Notify MAIN agent with handoff
# Do NOT push or create PR
```

### MAIN Agent/User Commands (Remote Operations)

```bash
# Review background agent's work
# Review worktree locally, then submit:
./scripts/worktree_manager.sh submit AGENT_NAME "TASK-XXX: description"

# Monitor CI
./scripts/pr_async_merge.sh status

# Merge when ready (or daemon auto-merges)
```

### File Boundaries Quick Ref

| Agent | Safe to Edit | Avoid |
|-------|--------------|-------|
| **RESEARCHER** | `docs/research/*`, `docs/guidelines/*` | Implementation, tests, TASKS.md |
| **DEV** | Assigned modules, new features | Multi-module without coordination |
| **TESTER** | Test files, benchmarks | Implementation code, test infra |
| **DEVOPS** | CI/CD workflows, scripts | Application code, tests |
| **PM** | Roadmap docs, planning | Implementation, TASKS.md |

---

## Next Steps

1. **Read:** [Agent Collaboration Framework](agent-collaboration-framework.md) - Comprehensive 5-agent system
2. **Read:** [Project Memory](../planning/memory.md) - Current project state
3. **Confirm:** Task assignment with MAIN agent
4. **Start:** Follow your role-specific workflow
5. **Communicate:** Use handoff template when complete

---

**Version:** 2.0 (2026-01-07)
**Changelog:**
- v2.0: Multi-agent framework, 5 specialized roles, 2026 best practices, research-backed guidelines
- v1.0: Initial 1-2 agent parallel work guide

# Background Agent Parallel Work Guide

**Purpose:** Enable safe parallel work without conflicts, CI failures, or duplicated effort.

**Scope:** 1-2 background agents (RESEARCHER, DEV, TESTER, DEVOPS, PM) working in parallel with the MAIN agent.

**Status:** v2.0 - Updated for multi-agent collaboration framework (2026-01-07)

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
.venv/bin/python scripts/start_session.py

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

Read: `docs/GIT_WORKFLOW_AI_AGENTS.md`

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

### Standard PR Workflow (Code/Tests/CI Changes)

```bash
# 1. Create feature branch and PR
./scripts/create_task_pr.sh TASK-XXX "short description"

# 2. Make changes in isolated scope
# ... edit files ...

# 3. Commit with pre-commit hooks
./scripts/ai_commit.sh "feat: describe change"

# 4. Finish task (pushes branch, opens PR)
./scripts/finish_task_pr.sh TASK-XXX "short description"

# 5. Notify MAIN agent for review/merge
```

### Direct Commit Workflow (Research/Docs Only)

```bash
# For research docs approved for direct commit
./scripts/ai_commit.sh "docs: add research for topic X"
```

If unsure, run:
```bash
./scripts/should_use_pr.sh --explain
```

**Rule:** Only use direct commits if explicitly approved by MAIN agent. When in doubt, use PR workflow.

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

---

## Communication + Handoff

### Task Completion Handoff

When your task is complete, use this template in PR description or direct message to MAIN:

```markdown
## Handoff: [ROLE] → MAIN

**Task:** TASK-XXX
**Agent Role:** [RESEARCHER/DEV/TESTER/DEVOPS/PM]
**Branch:** feature/TASK-XXX-description

### Summary
[2-3 sentences: what changed and why]

### Files Changed
- `path/to/file1.py` - [purpose]
- `path/to/file2.py` - [purpose]

### Key Decisions
- **Decision 1:** [rationale]
- **Decision 2:** [rationale]

### Test Results
- X tests passing
- Y new tests added
- Coverage: Z%

### Open Questions
- [Any unresolved items or needed clarifications]

### Action Required
[Next step for MAIN agent - review, merge, assign follow-up task]
```

### During Development Communication

**Use PR comments** for questions/updates during development:
```markdown
@MAIN - Question on [topic]:
[specific question with context]

Options:
1. [option A] - [pros/cons]
2. [option B] - [pros/cons]

Recommend: [option] because [rationale]
```

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

**Never self-merge.** Only MAIN agent merges PRs.

**Sequence:**
1. Background agent creates PR
2. Background agent notifies MAIN with handoff
3. MAIN reviews (may request changes)
4. MAIN merges when approved
5. MAIN updates TASKS.md and memory.md

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

### Essential Commands

```bash
# Start session
.venv/bin/python scripts/start_session.py

# Read context
cat docs/planning/memory.md
cat docs/TASKS.md

# Create PR
./scripts/create_task_pr.sh TASK-XXX "description"

# Commit changes
./scripts/ai_commit.sh "type: message"

# Finish task
./scripts/finish_task_pr.sh TASK-XXX "description"

# Run tests (Python/)
python -m pytest tests/unit/test_module.py -v

# Format code (Python/)
python -m black .
python -m ruff check --fix .
python -m mypy
```

### File Boundaries Quick Ref

| Agent | Safe to Edit | Avoid |
|-------|--------------|-------|
| **RESEARCHER** | `docs/research/*`, `docs/guidelines/*` | Implementation, tests, TASKS.md |
| **DEV** | Assigned modules, new features | Multi-module without coordination |
| **TESTER** | Test files, benchmarks | Implementation code, test infra |
| **DEVOPS** | CI/CD workflows, scripts | Application code, tests |
| **PM** | Roadmap docs, planning | Implementation, TASKS.md |

### Automation Scripts

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `scripts/create_task_pr.sh` | Create feature branch + PR | Start code/test/CI task |
| `scripts/ai_commit.sh` | Commit with pre-commit hooks | Every commit |
| `scripts/finish_task_pr.sh` | Update CHANGELOG + push | Complete task |
| `scripts/start_session.py` | Load context for new session | Start work session |

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
- v2.0: Multi-agent framework, 5 specialized roles, 2026 best practices
- v1.0: Initial 1-2 agent parallel work guide

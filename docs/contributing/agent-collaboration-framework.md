# Agent Collaboration Framework

**Version:** 1.0
**Last Updated:** 2026-01-07
**Status:** ACTIVE
**Purpose:** Enable professional multi-agent maintenance with parallel workflows

---

## Executive Summary

This project uses **agent-driven maintenance** where specialized AI agents (researcher, tester, devops, pm, dev) work in parallel on isolated tasks. This framework defines roles, workflows, and coordination protocols for up to **5 concurrent agents** working safely without conflicts.

**Key Principles:**
1. **Specialization:** Each agent has a defined role and expertise
2. **Isolation:** Tasks have clear boundaries to prevent conflicts
3. **Automation:** Workflows are scripted and reproducible
4. **Quality:** All changes pass CI before merging
5. **Transparency:** All agents document decisions and handoffs

---

## Table of Contents

1. [Agent Roles](#1-agent-roles)
2. [Workflow Patterns](#2-workflow-patterns)
3. [Parallel Coordination](#3-parallel-coordination)
4. [Context Management](#4-context-management)
5. [Quality Standards](#5-quality-standards)
6. [Troubleshooting](#6-troubleshooting)

---

## 1. Agent Roles

### 1.1 MAIN Agent (Coordinator)

**Primary Role:** Project coordination, user interaction, high-level decisions

**Responsibilities:**
- Communicate with user
- Assign tasks to background agents
- Review PRs and merge approved work
- Maintain TASKS.md and SESSION_LOG.md
- Resolve conflicts between agents
- Make architectural decisions

**Tools:**
- Full access to all files
- Git merge permissions
- Task assignment authority

**Files Owned:**
- `docs/TASKS.md`
- `docs/SESSION_LOG.md`
- `docs/planning/next-session-brief.md`

---

### 1.2 RESEARCHER Agent

**Primary Role:** Research, analysis, documentation of design decisions

**Responsibilities:**
- Create research documents in `docs/research/`
- Analyze codebases, libraries, patterns
- Document findings with code examples
- Provide recommendations to DEV agents
- Update research index

**Tools:**
- Web search for latest patterns/libraries
- Code reading across repos
- Documentation tools

**Typical Tasks:**
- TASK-200 through TASK-207 (API research)
- TASK-230, 238, 240, 242, 245, 252, 260, 261 (professional requirements)
- Technology evaluations
- Best practice documentation

**Files Owned:**
- `docs/research/*.md` (can commit directly)
- `docs/research/README.md`

**Quality Standards:**
- 800+ lines minimum for research docs
- 10+ code examples
- Comparison tables with 3+ options
- Actionable recommendations section
- References to authoritative sources

---

### 1.3 DEV Agent

**Primary Role:** Implementation of features, refactoring, bug fixes

**Responsibilities:**
- Implement features per guidelines
- Refactor code following standards
- Fix bugs and issues
- Update tests for code changes
- Follow API design guidelines

**Tools:**
- Python code modification
- Test creation/updates
- Git branching via scripts

**Typical Tasks:**
- TASK-210, 211 (API implementation)
- TASK-212, 213, 214 (error handling, base classes)
- Feature implementation
- Bug fixes

**Files Owned:**
- `Python/structural_lib/*.py` (requires PR)
- Implementation code

**Quality Standards:**
- All tests pass locally before PR
- Black + Ruff formatting
- Mypy type checking clean
- Test coverage maintained or improved
- Docstrings for new public APIs

---

### 1.4 TESTER Agent

**Primary Role:** Test creation, quality assurance, regression prevention

**Responsibilities:**
- Write comprehensive test suites
- Create regression tests
- Property-based testing
- Performance benchmarks
- Visual regression tests (DXF/reports)
- Test organization and markers

**Tools:**
- pytest, pytest-cov, pytest-benchmark
- Hypothesis for property testing
- pytest markers for organization

**Typical Tasks:**
- TASK-191 (test restructuring)
- TASK-192 (coverage + benchmarks)
- TASK-230 (testing strategies)
- Bug verification tests
- Regression test creation

**Files Owned:**
- `Python/tests/**/*.py` (requires PR)
- Test utilities and fixtures

**Quality Standards:**
- Tests must be isolated (no side effects)
- Clear docstrings explaining what's tested
- Parametrization for multiple scenarios
- Coverage improvement measurable
- Benchmarks tracked for performance regression

---

### 1.5 DEVOPS Agent

**Primary Role:** CI/CD, automation, tooling, infrastructure

**Responsibilities:**
- Maintain CI/CD pipelines
- Create automation scripts
- Manage pre-commit hooks
- Release automation
- Docker/deployment configurations
- Security scanning

**Tools:**
- GitHub Actions workflows
- Shell scripting
- Docker
- pre-commit framework

**Typical Tasks:**
- TASK-215 (workflow updates)
- TASK-260 (security best practices)
- CI/CD improvements
- Automation script creation
- Release management

**Files Owned:**
- `.github/workflows/*.yml` (requires PR)
- `scripts/*.sh`, `scripts/*.py` (requires PR)
- `.pre-commit-config.yaml` (requires PR)

**Quality Standards:**
- Workflows tested locally first
- Scripts have error handling
- Documentation for all automation
- No breaking changes to existing workflows
- Rollback plan for critical changes

---

### 1.6 PM Agent (Project Manager)

**Primary Role:** Planning, roadmaps, milestone tracking, prioritization

**Responsibilities:**
- Create implementation roadmaps
- Break down epics into tasks
- Estimate effort and timeline
- Track progress and blockers
- Create release plans
- Stakeholder communication templates

**Tools:**
- Planning documents
- Gantt charts / timelines
- Issue tracking

**Typical Tasks:**
- TASK-209 (implementation roadmap)
- Release planning
- Epic breakdown
- Milestone tracking

**Files Owned:**
- `docs/planning/*.md` (can commit directly)
- `docs/RELEASES.md` (coordination with MAIN)

**Quality Standards:**
- Clear acceptance criteria for all tasks
- Realistic time estimates
- Dependencies identified
- Risk assessment included
- Measurable success metrics

---

## 2. Workflow Patterns

### 2.1 Research Workflow (RESEARCHER Agent)

**Use Case:** Investigate technology/pattern, document findings

**Workflow:**
```bash
# 1. Receive task assignment from MAIN
# MAIN: "Start TASK-XXX: Research topic Y, output docs/research/topic-y.md"

# 2. Create research branch (optional for large research)
./scripts/create_task_pr.sh TASK-XXX "research: topic Y"

# 3. Conduct research
- Web search for latest patterns (2026)
- Read relevant codebases
- Create comparison tables
- Document code examples

# 4. Write research document
- Minimum 800 lines
- Executive summary
- Table of contents
- Detailed sections
- Code examples (10+)
- Recommendations
- References

# 5. Commit directly (if allowed) or via PR
./scripts/ai_commit.sh "docs: add research for topic Y (TASK-XXX)"

# 6. Handoff to MAIN
- Update docs/research/README.md
- Notify MAIN with summary
```

**Output:** `docs/research/topic-name.md` (800-2000 lines)

---

### 2.2 Implementation Workflow (DEV Agent)

**Use Case:** Implement feature per guidelines

**Workflow:**
```bash
# 1. Receive task assignment from MAIN
# MAIN: "Implement TASK-XXX per guidelines in docs/research/feature.md"

# 2. Create feature branch
./scripts/create_task_pr.sh TASK-XXX "feat: feature name"

# 3. Read guidelines and requirements
- Review research docs
- Check API design guidelines
- Understand acceptance criteria

# 4. Implement feature
- Write code following guidelines
- Add type hints
- Write docstrings
- Handle errors properly

# 5. Create tests
- Unit tests for new functions
- Integration tests for workflows
- Update existing tests if needed

# 6. Quality checks
.venv/bin/python -m black Python/
.venv/bin/python -m ruff check --fix Python/
.venv/bin/python -m mypy
.venv/bin/python -m pytest

# 7. Commit and create PR
./scripts/ai_commit.sh "feat: implement feature X (TASK-XXX)"
./scripts/finish_task_pr.sh TASK-XXX "feature X implemented"

# 8. Handoff to MAIN for review
```

**Output:** Code + tests, PR ready for review

---

### 2.3 Testing Workflow (TESTER Agent)

**Use Case:** Add test coverage for module/feature

**Workflow:**
```bash
# 1. Receive task assignment
# MAIN: "Add tests for module X, target 90% coverage (TASK-XXX)"

# 2. Create test branch
./scripts/create_task_pr.sh TASK-XXX "test: comprehensive tests for module X"

# 3. Analyze current coverage
cd Python
python -m pytest --cov=structural_lib.module --cov-report=html
# Review HTML report to find gaps

# 4. Write tests
- Unit tests for each function
- Edge cases and error conditions
- Property-based tests (Hypothesis)
- Integration tests for workflows

# 5. Verify coverage improved
python -m pytest --cov=structural_lib.module --cov-report=term
# Must show improvement

# 6. Run full suite
python -m pytest

# 7. Commit and create PR
./scripts/ai_commit.sh "test: comprehensive tests for module X (TASK-XXX)"
./scripts/finish_task_pr.sh TASK-XXX "module X test coverage improved"

# 8. Handoff with coverage metrics
```

**Output:** Tests in `Python/tests/`, coverage increased

---

### 2.4 DevOps Workflow (DEVOPS Agent)

**Use Case:** Automate repetitive task

**Workflow:**
```bash
# 1. Receive task assignment
# MAIN: "Create automation for X (TASK-XXX)"

# 2. Create automation branch
./scripts/create_task_pr.sh TASK-XXX "ci: automate X"

# 3. Design automation
- Identify manual steps
- Design script interface
- Plan error handling

# 4. Implement script
- Write shell/Python script
- Add error handling
- Test locally

# 5. Document usage
- Add to scripts/README.md or automation catalog
- Include examples
- Document edge cases

# 6. Test script multiple times
./scripts/new_automation.sh --test

# 7. Commit and create PR
./scripts/ai_commit.sh "ci: add automation for X (TASK-XXX)"
./scripts/finish_task_pr.sh TASK-XXX "X automation complete"

# 8. Handoff with usage documentation
```

**Output:** Script in `scripts/`, documentation

---

### 2.5 Planning Workflow (PM Agent)

**Use Case:** Break down epic into implementation tasks

**Workflow:**
```bash
# 1. Receive epic from MAIN
# MAIN: "Plan implementation for feature X"

# 2. Research requirements
- Read user stories
- Review technical constraints
- Check dependencies

# 3. Create implementation plan
- Break into tasks (TASK-XXX format)
- Estimate effort per task
- Identify dependencies
- Assign to agent types

# 4. Write planning doc
docs/planning/feature-x-implementation-plan.md
- Goal and scope
- Task breakdown
- Timeline (weeks 1-4)
- Dependencies
- Risks
- Success metrics

# 5. Commit planning doc directly
./scripts/ai_commit.sh "docs: feature X implementation plan"

# 6. Handoff to MAIN with task IDs
```

**Output:** Planning doc with task breakdown

---

## 3. Parallel Coordination

### 3.1 Task Selection (Avoid Conflicts)

**Parallel-Safe Task Combinations:**

✅ **SAFE:**
- RESEARCHER + DEV (different modules)
- TESTER + DEVOPS (different areas)
- PM + RESEARCHER (different outputs)
- Multiple RESEARCHERs (different topics)

❌ **UNSAFE (conflicts likely):**
- 2 DEVs on same module
- DEV + TESTER on same new feature (sequence instead)
- Multiple agents editing same file

**Coordination Protocol:**
1. MAIN assigns tasks with clear boundaries
2. Each agent confirms file ownership
3. Agents check `docs/TASKS.md` for active work
4. If overlap detected, ask MAIN to reassign

### 3.2 Branch Strategy

**Pattern:** `feature/TASK-XXX-short-description`

**Examples:**
- `feature/TASK-230-testing-strategies` (RESEARCHER)
- `feature/TASK-240-clause-database` (DEV)
- `feature/TASK-241-load-combinations` (PM planning)

**Rules:**
- One branch per agent at a time
- Branch from `main`
- Merge to `main` via PR after MAIN review
- Delete branch after merge

### 3.3 Communication Protocol

**Handoff Template:**
```markdown
## Handoff: [AGENT-TYPE] → MAIN

**Task:** TASK-XXX
**Summary:** [2-3 sentences]
**Files Changed:**
- path/to/file1.py (added feature X)
- path/to/file2.md (documented Y)

**Key Decisions:**
1. Chose approach A over B because [rationale]
2. Deferred Z for future work

**Tests:**
- ✅ 2337 tests passing
- ✅ Coverage increased from 85% to 86%
- ⚠️ 3 tests skipped (reason: X)

**Next Steps:**
1. MAIN: Review PR #XXX
2. After merge: Update TASKS.md to Recently Done

**Open Questions:** None / [list if any]
```

---

## 4. Context Management

### 4.1 Shared Context Documents

**Purpose:** Maintain continuity across agent sessions

**Key Documents:**

1. **`docs/AI_CONTEXT_PACK.md`**
   - Project overview
   - Technology stack
   - Quick reference links
   - Updated: Rarely (major changes only)

2. **`docs/AGENT_BOOTSTRAP.md`**
   - Agent onboarding guide
   - First steps for new agents
   - Tool locations
   - Updated: When workflow changes

3. **`docs/TASKS.md`**
   - Current task state
   - Active work (WIP)
   - Backlog priorities
   - Updated: By MAIN after each session

4. **`docs/SESSION_LOG.md`**
   - Session-by-session progress
   - Decisions made
   - Problems encountered
   - Updated: By MAIN at session end

5. **`docs/planning/memory.md`** (NEW - recommended)
   - Current project state
   - Active goals
   - Blockers
   - Updated: By MAIN after major changes

### 4.2 Agent-Specific Context

Each agent should:
1. Read `AI_CONTEXT_PACK.md` first
2. Read role-specific sections in this document
3. Check `TASKS.md` for active work
4. Review relevant research docs
5. Confirm task boundaries with MAIN

---

## 5. Quality Standards

### 5.1 Pre-Commit Checklist

**Before every commit, verify:**

✅ **Code Quality:**
- [ ] Black formatting applied
- [ ] Ruff checks passed
- [ ] Mypy type checking clean
- [ ] No commented-out code
- [ ] No debug print statements

✅ **Testing:**
- [ ] All tests pass locally
- [ ] New tests for new features
- [ ] Coverage maintained or improved
- [ ] Benchmarks updated if needed

✅ **Documentation:**
- [ ] Docstrings for new public APIs
- [ ] CHANGELOG updated (if user-facing change)
- [ ] README updated (if new feature)
- [ ] Research docs complete (if research task)

✅ **Git:**
- [ ] Commit message follows convention
- [ ] Changes scoped to task
- [ ] No accidental file inclusions

### 5.2 Code Review Standards

**MAIN reviews PRs for:**
- Adherence to guidelines
- Test coverage adequate
- No breaking changes (unless planned)
- Documentation complete
- CI passing

**Approval criteria:**
- ✅ All checks pass
- ✅ Tests demonstrate correctness
- ✅ Code follows project standards
- ✅ No unresolved questions

---

## 6. Troubleshooting

### 6.1 Common Issues

**Issue:** CI fails after merge
**Solution:** Run `./scripts/ci_local.sh` before creating PR

**Issue:** Merge conflict with main
**Solution:**
```bash
git fetch origin
git rebase origin/main
# Resolve conflicts
./scripts/ai_commit.sh "fix: resolve merge conflicts"
```

**Issue:** Two agents editing same file
**Solution:** Second agent stops work, asks MAIN to reassign

**Issue:** Tests pass locally but fail in CI
**Solution:** Check Python version, dependencies, environment variables

**Issue:** Pre-commit hook blocks commit
**Solution:** Fix reported issue, run `./scripts/ai_commit.sh` again

### 6.2 Emergency Procedures

**Broken main branch:**
1. Identify breaking commit
2. Create fix PR immediately
3. Fast-track review and merge
4. Post-mortem: update CI to prevent

**Agent unsure of boundaries:**
1. Stop work immediately
2. Ask MAIN for clarification
3. Document decision for future

---

## References

- [Advanced Claude Code Techniques - Multi-Agent Workflows](https://medium.com/@salwan.mohamed/advanced-claude-code-techniques-multi-agent-workflows-and-parallel-development-for-devops-89377460252c)
- [Claude Code Subagents Documentation](https://code.claude.com/docs/en/sub-agents)
- [Anthropic: Claude Code Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices)
- [Enterprise AI Agents 2026](https://claude.com/blog/how-enterprises-are-building-ai-agents-in-2026)
- [Effective Harnesses for Long-Running Agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)

---

## Version History

- **1.0 (2026-01-07):** Initial framework with 5 agent roles, parallel workflows

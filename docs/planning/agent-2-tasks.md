# Background Agent 2 Tasks (DEV/TESTER)

**Agent Role:** DEV / TESTER (flexible based on assignment)
**Primary Focus:** Feature implementation, test creation, code quality
**Status:** Ready
**Last Updated:** 2026-01-07

---

## Active Tasks

### Currently Available for Assignment

Agent 2 is available for DEV or TESTER tasks. MAIN agent will assign tasks as needed based on priorities from main TASKS.md.

**Typical Task Types:**
- Feature implementation (isolated modules)
- Test suite expansion
- Bug fixes (with clear reproduction)
- Performance optimization (specific functions)
- Code refactoring (single module scope)

---

## Guidelines for Agent 2

### Working Locally (No Remote Operations)

**When starting a task:**
```bash
# 1. Confirm task assignment with MAIN agent
#    - Task ID, acceptance criteria, file boundaries

# 2. Create feature branch locally
git checkout -b feature/TASK-XXX-description

# 3. Make changes (implementation or tests)
# ... edit files ...

# 4. Commit locally
git add Python/structural_lib/module.py Python/tests/unit/test_module.py
git commit -m "feat: implement feature X"

# 5. Run local checks (REQUIRED before handoff)
cd Python
python -m black .              # Format
python -m ruff check --fix .   # Lint
python -m mypy structural_lib  # Type check
python -m pytest tests/unit/test_module.py -v  # Tests

# 6. Verify all checks pass locally
pytest  # Full test suite (optional but recommended)

# 7. Notify MAIN agent with handoff
# STOP - Do NOT push or create PR
```

### Handoff Template for DEV/TESTER Tasks

When task complete, notify MAIN agent:

```markdown
## Handoff: DEV/TESTER (Agent 2) → MAIN

**Task:** TASK-XXX (from main TASKS.md)
**Branch:** feature/TASK-XXX-description
**Status:** ✅ Complete, all checks passed locally

### Summary
[2-3 sentences: what was implemented/tested, why]

### Files Changed
- `Python/structural_lib/module.py` - [what changed]
- `Python/tests/unit/test_module.py` - [tests added]
- `docs/reference/api.md` - [docs updated, if applicable]

### Key Decisions
- **Decision 1:** [implementation choice and rationale]
- **Decision 2:** [trade-off made]

### Local Test Results
- ✅ X tests passing (Y new tests added)
- ✅ Coverage: Z% on changed modules
- ✅ Black/Ruff/Mypy: Clean
- ✅ Benchmark: [performance numbers if applicable]

### Open Questions
- [Any items needing MAIN agent input]

### Action Required by MAIN
1. Review: `git checkout feature/TASK-XXX-description`
2. Verify changes align with requirements
3. Push: `git push origin feature/TASK-XXX-description`
4. Create PR: `gh pr create`
5. Monitor CI: `gh pr checks --watch`
6. Merge: `gh pr merge --squash` (after CI passes)
```

### File Boundaries (Agent 2 - DEV/TESTER)

**✅ Safe to Create/Edit (when assigned):**
- `Python/structural_lib/<assigned-module>.py` (single module only)
- `Python/tests/unit/test_<module>.py` (corresponding tests)
- `Python/tests/integration/test_<feature>.py` (integration tests)
- `docs/reference/api.md` (API documentation updates)
- `CHANGELOG.md` (if significant feature/fix)

**✅ Safe to Read (for context):**
- Any existing code, tests, docs (read-only for reference)
- `docs/planning/memory.md` (current project state)
- `docs/TASKS.md` (main task board - read-only)
- `docs/reference/known-pitfalls.md` (coding guidelines)

**❌ Do NOT Edit (without coordination):**
- `docs/TASKS.md` (MAIN agent owns this)
- `docs/SESSION_LOG.md` (MAIN agent owns this)
- `Python/structural_lib/api.py` (high-churn, needs coordination)
- Multiple modules simultaneously (one module per task)
- Core utilities (`types.py`, `constants.py` without approval)
- CI workflows (`.github/workflows/*.yml`)

### Quality Checklist (Before Handoff)

**REQUIRED - All items must pass:**

```bash
# 1. Format code
cd Python && python -m black .
# Expect: "All done! ✨ 🍰 ✨"

# 2. Lint code
python -m ruff check --fix .
# Expect: No errors remaining

# 3. Type check
python -m mypy structural_lib/
# Expect: "Success: no issues found"

# 4. Run affected tests
python -m pytest tests/unit/test_<module>.py -v
# Expect: All tests PASSED

# 5. (Optional) Full test suite
python -m pytest
# Expect: 2231+ tests PASSED
```

**If ANY check fails:**
- Fix the issue locally
- Re-run checks
- Do NOT hand off until all checks pass

---

## Example Task Assignment (From MAIN Agent)

```markdown
## Task Assignment: MAIN → Agent 2 (DEV)

**Task ID:** TASK-XXX (from main TASKS.md)
**Agent Role:** DEV
**Priority:** HIGH
**Estimated Effort:** 3-4 hours

**Objective:** Implement feature X in module Y

**Acceptance Criteria:**
- [ ] Function `do_something()` implemented in `module.py`
- [ ] 5+ unit tests covering happy path + edge cases
- [ ] Type annotations added (mypy clean)
- [ ] Docstring with Google Style format
- [ ] CHANGELOG updated

**File Boundaries:**
- ✅ Edit: `Python/structural_lib/module.py`
- ✅ Edit: `Python/tests/unit/test_module.py`
- ✅ Edit: `CHANGELOG.md`
- ❌ Avoid: `api.py`, other modules

**Blockers:** None

**Context:**
- See `docs/planning/memory.md` for project state
- Reference implementation: `Python/structural_lib/similar_module.py`

**Expected Handoff:**
- Local branch with commits
- All quality checks passing
- Handoff message using template above
```

---

## Coordination with Agent 1

**If both agents working simultaneously:**

1. **Different file scopes:**
   - Agent 1: `docs/research/*`, `docs/blog-drafts/*`
   - Agent 2: `Python/structural_lib/<module>`, `Python/tests/*`

2. **No file conflicts expected** (completely isolated paths)

3. **Notify MAIN if:**
   - You need to edit a file Agent 1 might touch
   - Merge conflicts appear
   - Task scope changes

4. **Merge order:** MAIN agent will merge in logical order (usually Agent 2's code changes first, then Agent 1's docs)

---

## Common DEV/TESTER Tasks

### DEV Tasks (Implementation):
- Add new calculation functions
- Refactor existing modules for clarity
- Optimize performance-critical functions
- Add new API endpoints/wrappers
- Implement new features from TASKS.md

### TESTER Tasks (Quality):
- Expand unit test coverage
- Add integration tests
- Create regression test suites
- Add property-based tests (Hypothesis)
- Benchmark performance-critical code
- Add contract tests (API stability)

---

## Quick Reference Commands

```bash
# Quality checks (run before every handoff)
cd Python
python -m black .                    # Format
python -m ruff check --fix .         # Lint
python -m mypy structural_lib        # Type check
python -m pytest tests/unit/test_module.py -v  # Test

# Create feature branch
git checkout -b feature/TASK-XXX-description

# Commit changes
git add <files>
git commit -m "type: message"

# STOP - Notify MAIN agent
# Do NOT push or create PR yourself
```

---

**Version:** 1.0
**Created:** 2026-01-07
**Agent:** DEV/TESTER (Agent 2)
**Status:** Ready for assignment

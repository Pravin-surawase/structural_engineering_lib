# GitHub Workflow Guide

**Type:** Guide
**Audience:** All Agents
**Status:** Approved
**Importance:** High
**Version:** 1.0.0
**Created:** 2026-01-06
**Last Updated:** 2026-01-13
**Related Tasks:** TASK-421

---

**Research:** See [git-workflow-production-stage.md](../research/git-workflow-production-stage.md)
**Canonical:** [git-workflow-ai-agents.md](git-workflow-ai-agents.md)

## 🎯 Quick Decision: Direct Commit or PR?

```bash
# Let the tool decide for you:
./scripts/should_use_pr.sh --explain
```

---

## ✅ Direct Commits (Low-Risk Only)

### When to Use
- **Documentation ONLY** (no code): docs/
- **Tests ONLY** (no production code): Python/tests/
- **Scripts ONLY** (tooling): scripts/

### Requirements
- Changes affect ONE category above
- No production code (Python/structural_lib/)
- No VBA code
- No CI changes
- No dependency changes

### How
```bash
./scripts/ai_commit.sh "docs: fix typo in README"
```

---

## 🔀 Pull Requests (All Production Code)

### When to Use (REQUIRED)
- **Production code**: Python/structural_lib/**/*.py
- **VBA code**: VBA/**/*.bas, Excel/**/*.xlsm
- **CI workflows**: .github/workflows/**/*.yml
- **Dependencies**: pyproject.toml, requirements.txt
- **API changes**: Function signatures, breaking changes
- **Multi-module changes**: Coordinated refactoring

### Why
- ✅ CI validates before merge
- ✅ Audit trail for production changes
- ✅ Easy rollback if needed
- ✅ Contract tests catch breaking changes

### How
```bash
./scripts/create_task_pr.sh TASK-163 "Add return type annotations"
# Make changes, commit with ai_commit.sh
./scripts/finish_task_pr.sh TASK-163 "Add return type annotations" --with-session-docs
```

---

## 🎯 When to Use Direct Commits vs PRs

### ✅ Direct to Main (for small, low-risk changes):
- Documentation updates (typos, clarifications)
- Test additions (no production code changes)
- Script improvements
- Pre-commit hook fixes
- Small refactorings (<50 lines)

**How:** `./scripts/ai_commit.sh "commit message"`

### 🔀 Pull Request (for task completion):
- Feature implementation (TASK-XXX)
- API changes
- Significant refactoring
- Breaking changes
- Multi-file coordinated changes

**How:**
1. `./scripts/create_task_pr.sh TASK-162 "Add TypedDict support"`
2. Make changes and commit: `./scripts/ai_commit.sh "feat: implement X"`
3. When done: `./scripts/finish_task_pr.sh TASK-162 "Add TypedDict support" --with-session-docs`

---

## ⚡ Fast CI Strategy

### Problem
Full CI on PRs takes 45-50 seconds and runs 4 Python versions. This slows down the feedback loop.

### Solution: Two-Tier CI

#### 1. Fast Checks (PRs only) - ~20-30 seconds
**File:** `.github/workflows/fast-checks.yml`

Runs on Python 3.9 only:
- ✅ Format/lint (black, ruff, mypy)
- ✅ Contract tests (breaking change detection)
- ✅ Core tests (flexure, shear, detailing)
- ✅ Doc checks (parallel execution)

**Result:** Quick feedback for PRs

#### 2. Full Test Matrix (main branch only) - ~50 seconds
**File:** `.github/workflows/python-tests.yml`

Runs on Python 3.9, 3.10, 3.11, 3.12:
- ✅ All 2200 tests
- ✅ Coverage reporting
- ✅ All lint/doc checks
- ✅ Packaging smoke test

**Result:** Comprehensive validation after merge

### Why This Works
1. **Fast feedback**: PR checks complete in 20-30s vs 50s
2. **Same safety**: Contract tests catch breaking changes
3. **Full coverage**: After merge, all Python versions tested
4. **Best practice**: Match Python 3.9 (project minimum version)

---

## 📋 Typical Workflows

### Workflow 1: Small Doc Fix
```bash
# Make change
vim docs/README.md

# Commit and push
./scripts/ai_commit.sh "docs: fix typo in README"

# Done! ✅ (pushes directly to main)
```

### Workflow 2: Complete a Task
```bash
# Start task on feature branch
./scripts/create_task_pr.sh TASK-162 "Replace Dict[str, Any] with TypedDicts"

# Make changes
vim Python/structural_lib/data_types.py

# Commit progress
./scripts/ai_commit.sh "feat: add BarDict and StirrupDict TypedDicts"

# Continue working...
./scripts/ai_commit.sh "feat: add DeflectionParams TypedDict"

# Finish and create PR
./scripts/finish_task_pr.sh TASK-162 "Replace Dict[str, Any] with TypedDicts" --with-session-docs

# Script will:
# 1. Push branch
# 2. Create PR
# 3. Watch CI (fast checks, ~20-30s)
# 4. Ask if you want to merge
# 5. If yes: squash merge, delete branch, return to main

# Note: Reviews are not required in this repo. If enabled later, GitHub blocks self-approval.
```

### Workflow 3: Emergency Hotfix
```bash
# For critical fixes that need to skip PR review:
vim Python/structural_lib/critical.py
./scripts/ai_commit.sh "fix: critical bug in calculation"

# Full CI runs after push to main
```

---

## 🛡️ Safety Features

### AI Commit Script (`ai_commit.sh`)
**Prevents:** Merge conflicts, divergence, pre-commit issues

**How:**
1. Stages changes and runs should_use_pr.sh
2. Delegates to safe_push.sh
3. safe_push.sh handles sync, commit, amend, and push

**Result:** Zero merge conflicts guaranteed

### Fast CI Checks
**Prevents:** Breaking changes merging to main

**How:**
- Contract tests on every PR
- Core tests verify critical paths
- Type checking catches regressions

**Result:** Fast feedback, same safety

### Full Test Matrix
**Prevents:** Python version incompatibilities

**How:**
- Runs after merge to main
- Tests Python 3.9-3.12
- Coverage enforcement (85%+)

**Result:** Production-ready code

---

## 📊 Performance Comparison

| Scenario | Old Way | New Way | Time Saved |
|----------|---------|---------|------------|
| PR feedback | 50s (4 Python versions) | 20-30s (Python 3.9 only) | ~25-30s |
| Post-merge validation | Same 50s | Same 50s | 0s (but deferred) |
| Overall PR cycle | 50s + review + 50s merge | 20-30s + review (merge runs async) | ~30s+ |

**Key insight:** You get PR feedback in half the time, and full validation happens async after merge.

---

## 🎓 Best Practices

### For AI Agents
1. **Always use `ai_commit.sh`** for commits (never manual git commands)
2. **Use PRs for TASK-XXX completion** (feature branches)
3. **Direct commits OK for docs/tests** (low-risk changes)
4. **Wait for fast checks** before merging PRs (~20-30s)

### For Humans
1. **Review PR description** - ensure it matches actual changes
2. **Check fast CI passes** before approving
3. **Squash merge** to keep history clean
4. **Delete branch** after merge

### For Both
- Small, focused commits (one logical change)
- Clear commit messages (`feat:`, `fix:`, `docs:`)
- Update TASKS.md when completing work
- Run tests locally before pushing

---

## 🔧 Troubleshooting

### "Fast checks failed but I think it's fine"
- Check the specific failure in GitHub Actions
- If it's a flaky test, rerun the workflow
- If it's real, fix before merging

### "I need to test all Python versions before merge"
- Push to your branch without creating PR
- Manually trigger full tests: `gh workflow run python-tests.yml --ref your-branch`

### "CI is still too slow"
- Fast checks: 20-30s is near-optimal (can't parallelize more)
- Full tests: 50s is reasonable for 4 Python versions + 2200 tests
- If consistently slow, check GitHub Actions queue time

### "Merge conflict after using ai_commit.sh"
- Shouldn't happen! That's the whole point
- If it does, check you're using latest version of script
- Report as bug - the pull-first workflow prevents this

---

## 📈 Metrics to Track

1. **PR feedback time**: Target <30s for fast checks
2. **Merge-to-prod time**: Full CI should complete <5min after merge
3. **Conflict rate**: Should be 0% with `ai_commit.sh`
4. **False positive rate**: Fast checks should match full tests 99%+

---

*Last updated: 2026-01-06*
*Scripts: `ai_commit.sh`, `create_task_pr.sh`, `finish_task_pr.sh`*

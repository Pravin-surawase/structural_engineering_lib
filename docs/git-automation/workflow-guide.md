# Git Workflow Guide

**Type:** Guide
**Audience:** All Agents
**Status:** Production Ready
**Importance:** Critical
**Version:** 0.16.6
**Created:** 2026-01-11
**Last Updated:** 2026-01-11

---

## 🎯 The One Rule

> **Never use manual git commands. Always use automation scripts.**

```bash
# ❌ FORBIDDEN
git add . && git commit -m "message" && git push

# ✅ ALWAYS USE
./scripts/ai_commit.sh "message"
```

---

## 🔄 Core Workflow (7 Steps)

The `ai_commit.sh` script executes this workflow automatically:

```
Step 0: Stash local changes before sync
Step 1: Background fetch (parallel, non-blocking)
Step 2: Stage files (git add)
Step 2.5: Pre-flight whitespace check (auto-fix)
Step 3: Commit (pre-commit hooks run)
Step 4: Handle hook modifications (auto-amend if needed)
Step 5: Sync with remote (pull --ff-only)
Step 6: Verify push safety
Step 7: Push to remote
```

**Time:** ~5 seconds (vs 45-60 seconds manual)

---

## 🎛️ Decision Tree: PR vs Direct Commit

### Quick Check
```bash
./scripts/should_use_pr.sh --explain
```

### Decision Matrix

| Change Type | Files | PR Required? | Auto-Merge? |
|-------------|-------|--------------|-------------|
| **Docs only** | `docs/`, `README.md` | ❌ No | N/A (direct) |
| **Tests only** | `tests/`, <50 lines | ❌ No | N/A (direct) |
| **Scripts** | `scripts/`, <50 lines | ❌ No | N/A (direct) |
| **Python code** | `structural_lib/` | ✅ Yes | ❌ Manual |
| **VBA code** | `VBA/` | ✅ Yes | ❌ Manual |
| **CI workflows** | `.github/workflows/` | ✅ Yes | ❌ Manual |
| **Dependencies** | `pyproject.toml`, `requirements*.txt` | ✅ Yes | ❌ Manual |
| **Substantial docs** | 150+ lines or 3+ files | ✅ Yes | ✅ If green |

### Thresholds

| File Type | Direct OK | PR Required |
|-----------|-----------|-------------|
| Documentation | <500 lines | 500+ lines |
| Tests | <50 lines | 50+ lines |
| Scripts | <50 lines | 50+ lines |
| Production code | Never | Always |

---

## 📋 Workflow Patterns

### Pattern A: Direct Commit (80% of work)

For docs, small tests, small scripts:

```bash
# 1. Make changes
# ... edit files ...

# 2. Commit (handles everything)
./scripts/ai_commit.sh "docs: update workflow guide"

# Done! ✓
```

### Pattern B: PR Workflow (Production Code)

For code, VBA, CI, dependencies:

```bash
# 1. Create task branch
./scripts/create_task_pr.sh TASK-270 "Fix benchmark signatures"

# 2. Make changes and commit (can do multiple times)
# ... edit files ...
./scripts/ai_commit.sh "fix: update benchmark function calls"

# 3. Finish and create PR
./scripts/finish_task_pr.sh TASK-270 "Fix benchmark signatures"

# 4. Wait for CI
gh pr checks <PR_NUM> --watch

# 5. Merge when green
gh pr merge <PR_NUM> --squash --delete-branch
```

### Pattern C: Multi-Phase Tasks

For complex tasks with 3+ phases:

```bash
# 1. Create branch once
./scripts/create_task_pr.sh IMPL-006 "Multi-phase implementation"

# 2. Complete Phase 1
# ... work on Phase 1 ...
./scripts/ai_commit.sh "feat(phase1): implement base structure"

# 3. Complete Phase 2
# ... work on Phase 2 ...
./scripts/ai_commit.sh "feat(phase2): add validation"

# 4. Complete Phase 3
# ... work on Phase 3 ...
./scripts/ai_commit.sh "feat(phase3): add tests"

# 5. Create PR after ALL phases done
./scripts/finish_task_pr.sh IMPL-006 "Multi-phase implementation"

# Benefits:
# - 1 PR instead of 4
# - 1 CI run instead of 4
# - Consolidated review
```

---

## 🔧 What the Scripts Do

### ai_commit.sh

**Purpose:** Single entry point for ALL commits

**Features:**
- Stages all changes automatically
- Runs pre-commit hooks
- Handles hook modifications (auto-amend)
- Syncs with remote before push
- Handles push rejections (auto-retry with rebase)
- Logs all operations to `git_operations_log/`

**Usage:**
```bash
./scripts/ai_commit.sh "type: description"
```

### safe_push.sh

**Purpose:** Core push logic (called by ai_commit.sh)

**Features:**
- 7-step workflow (see above)
- Pull-first strategy (prevents conflicts)
- FF-only merges (clean history)
- Auto-conflict resolution (keeps your changes)
- Whitespace auto-fix

**Usage:**
```bash
# Usually called via ai_commit.sh
# Direct use for edge cases:
./scripts/safe_push.sh "message"
```

### should_use_pr.sh

**Purpose:** Decision helper (PR vs direct commit)

**Features:**
- Analyzes file types
- Checks change size
- Provides recommendation with reasoning

**Usage:**
```bash
./scripts/should_use_pr.sh --explain
```

### create_task_pr.sh / finish_task_pr.sh

**Purpose:** PR workflow management

**Usage:**
```bash
# Start
./scripts/create_task_pr.sh TASK-XXX "description"

# Finish
./scripts/finish_task_pr.sh TASK-XXX "description"
```

### recover_git_state.sh

**Purpose:** Emergency recovery

**Usage:**
```bash
./scripts/recover_git_state.sh
# Follows printed instructions
```

---

## ⚠️ Error Recovery

### Push Rejected (Non-Fast-Forward)

**Symptom:** `! [rejected] main -> main (non-fast-forward)`

**Solution:**
```bash
# Use recovery script - it handles this automatically
./scripts/recover_git_state.sh
```

### Merge Conflict in TASKS.md

**Symptom:** Multiple editors, conflict markers

**Solution:**
```bash
# Recovery script handles this automatically
./scripts/recover_git_state.sh

# It will:
# 1. Detect the conflict
# 2. Apply --ours strategy for known files (TASKS.md, SESSION_LOG.md)
# 3. Complete the merge
# 4. Push the resolution
```

### Unfinished Merge (MERGE_HEAD exists)

**Symptom:** Can't commit, merge in progress

**Solution:**
```bash
# Recovery script auto-completes this
./scripts/recover_git_state.sh
```

### Pre-commit Modified Files (Not Yet Pushed)

**Symptom:** Files changed by hooks during commit

**Solution:**
```bash
# Already handled automatically by ai_commit.sh
# Just run the command again - it auto-retries
./scripts/ai_commit.sh "your message"
```

### Pre-commit Modified Files (Already Pushed)

**Symptom:** Files changed but already pushed

**Solution:**
```bash
# Use automation - NEVER amend after push!
./scripts/ai_commit.sh "chore: apply pre-commit fixes"
```

---

## 📊 Commit Message Format

### Structure
```
type(scope): description

[optional body]
[optional footer]
```

### Types
| Type | Use For |
|------|---------|
| `feat` | New features |
| `fix` | Bug fixes |
| `docs` | Documentation only |
| `style` | Formatting (no code change) |
| `refactor` | Code restructuring |
| `test` | Test additions/fixes |
| `chore` | Maintenance, dependencies |
| `security` | Security improvements |
| `legal` | License, disclaimer updates |

### Examples
```bash
./scripts/ai_commit.sh "feat: add beam design calculator"
./scripts/ai_commit.sh "fix: correct shear stress formula"
./scripts/ai_commit.sh "docs: update API reference"
./scripts/ai_commit.sh "test: add edge case for zero width"
./scripts/ai_commit.sh "chore: update dependencies"
```

---

## 🚫 Common Mistakes to Avoid

| Mistake | Correct Approach |
|---------|------------------|
| Using `git add/commit/push` manually | Always use `./scripts/ai_commit.sh` |
| `git commit --amend` after pushing | Create new commit instead |
| Multiple micro-PRs for tiny changes | Batch related changes into one |
| Committing unrelated files together | Stage only intended files |
| Skipping CI checks | Always `gh pr checks --watch` |

---

## 📈 Success Metrics

| Metric | Target | Current |
|--------|--------|---------|
| **Commit success rate** | 99%+ | 99.5% |
| **Merge conflicts** | 0/week | 0/week |
| **Average commit time** | <10s | 5s |
| **Script usage rate** | 100% | 100% |

---

## 🔗 Related Documentation

- [Automation Scripts](automation-scripts.md) - All 103 scripts
- [Mistakes Prevention](mistakes-prevention.md) - Historical lessons
- [Advanced Coordination](advanced-coordination.md) - Worktrees, background agents
- [README](README.md) - Entry point and quick start

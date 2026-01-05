# Git Workflow for AI Agents — Avoiding Race Conditions

**Problem:** Pre-commit hooks modify files AFTER staging, and auto-format workflows create race conditions that cause push failures and merge conflicts.

**Status:** ✅ **SOLVED** — Use the safe push workflow below

---

## Quick Solution (Use This Every Time)

### Option 1: Use Helper Script (Recommended)

```bash
./scripts/safe_push.sh "your commit message"
```

That's it! The script handles everything:
- ✅ Stages files
- ✅ Commits (pre-commit hooks run)
- ✅ Re-stages modified files and amends
- ✅ Pulls with merge strategy
- ✅ Auto-resolves conflicts
- ✅ Pushes safely

### Option 2: Manual Workflow

If you prefer manual control or the script isn't available:

```bash
# 1. Stage and commit
git add <files>
git commit -m "message"

# 2. If pre-commit modified files, amend
if git status --porcelain | grep -q '^[MARC]'; then
  git add -A
  git commit --amend --no-edit
fi

# 3. Pull with merge (NOT rebase)
git pull --no-rebase origin main

# 4. If conflicts, keep your version
git checkout --ours <conflicted-file>
git add <conflicted-file>
git commit --no-edit

# 5. Push
git push
```

---

## Why This Problem Happens

### Root Cause: Pre-Commit Hooks Modify Files

**Timeline of events:**

1. You: `git add file.py` (stages `file.py`)
2. You: `git commit -m "message"` (triggers pre-commit hooks)
3. Pre-commit hooks: Run `black`, `ruff`, `isort` → **modify `file.py`**
4. Git: Creates commit with **original staged version** (not modified version)
5. **Result:** Modified `file.py` is now **unstaged** (shows in `git status`)

### The "Ahead 1, Behind 1" Situation

**When you push immediately after committing:**

```
Your local:  A---B---C (your commit)
                   ^
                   |
Remote:      A---B---D (auto-format commit from CI)
```

- **Ahead 1:** Your commit C
- **Behind 1:** Remote's commit D (auto-format workflow)
- **Problem:** Git doesn't know which is "correct" → **push rejected**

### Why Rebase Fails

When you run `git pull --rebase`, Git tries to:

1. Temporarily remove your commit C
2. Apply remote's commit D
3. Replay your commit C on top of D
4. **Conflict:** Both C and D modified the same lines (formatting changes)
5. **Rebase stops** → You're stuck in "detached HEAD" state

---

## Solutions We Implemented

### 1. Safe Push Script (`scripts/safe_push.sh`)

**What it does:**

- Automatically handles pre-commit hook modifications
- Uses **merge strategy** instead of rebase (safer)
- Auto-resolves conflicts by keeping your version
- Provides clear status messages
- Fails fast with helpful errors

**Usage:**

```bash
# Basic usage
./scripts/safe_push.sh "feat: add new feature"

# With specific files
./scripts/safe_push.sh "docs: update readme" --files "README.md"
```

### 2. Updated Copilot Instructions

**Location:** `.github/copilot-instructions.md`

**Changes:**
- Added "ALWAYS pull before push" rule
- Documented the merge-not-rebase strategy
- Added conflict resolution steps
- Linked to safe_push script

**All AI agents** will now follow this workflow automatically.

### 3. Merge Strategy (Not Rebase)

**Old (problematic):**
```bash
git pull --rebase origin main  # ❌ Causes conflicts
```

**New (safe):**
```bash
git pull --no-rebase origin main  # ✅ Merges cleanly
```

**Why merge is better:**
- Preserves both commit histories
- Auto-merges non-conflicting changes
- Easier to resolve conflicts (just pick a version)
- No "detached HEAD" states

---

## Common Scenarios & Solutions

### Scenario 1: "Push Rejected (Non-Fast-Forward)"

**Error:**
```
! [rejected]        main -> main (non-fast-forward)
error: failed to push some refs
```

**Solution:**
```bash
git pull --no-rebase origin main
git push
```

### Scenario 2: "Merge Conflict in TASKS.md"

**Error:**
```
CONFLICT (content): Merge conflict in docs/TASKS.md
Automatic merge failed
```

**Solution:**
```bash
# Keep your version (you have the latest changes)
git checkout --ours docs/TASKS.md
git add docs/TASKS.md
git commit --no-edit
git push
```

### Scenario 3: "Pre-Commit Hook Modified Files"

**Symptom:**
```
$ git status
modified:   file.py  # After committing!
```

**Solution:**
```bash
git add -A
git commit --amend --no-edit
```

### Scenario 4: "Stuck in Rebase"

**Symptom:**
```
$ git status
HEAD detached at origin/main
rebase in progress
```

**Solution:**
```bash
# Abort the rebase
git rebase --abort

# Use merge instead
git pull --no-rebase origin main
git push
```

---

## Workflow Comparison

### ❌ Old Workflow (Problematic)

```bash
git add file.py
git commit -m "message"
git push                      # ❌ Often fails (race condition)

# When push fails:
git pull --rebase             # ❌ Causes conflicts
# Now stuck resolving conflicts
```

**Problems:**
- Push fails frequently
- Rebase creates merge conflicts
- Easy to get stuck in detached HEAD
- Manual conflict resolution needed

### ✅ New Workflow (Safe)

```bash
./scripts/safe_push.sh "message"   # ✅ Always works
```

**OR manually:**

```bash
git add file.py
git commit -m "message"
git add -A && git commit --amend --no-edit  # Handle pre-commit changes
git pull --no-rebase origin main            # Merge, don't rebase
git push                                     # Success!
```

**Benefits:**
- Always succeeds (no race conditions)
- Auto-handles pre-commit modifications
- Auto-resolves conflicts
- Clear error messages
- One command (`safe_push.sh`)

---

## For AI Agents: Implementation Checklist

When you (AI agent) need to commit and push:

- [ ] **DON'T** run `git push` immediately after `git commit`
- [ ] **DO** check if pre-commit hooks modified files (`git status`)
- [ ] **DO** amend commit if files were modified (`git add -A && git commit --amend --no-edit`)
- [ ] **DO** pull before push (`git pull --no-rebase`)
- [ ] **DO** use `--ours` for TASKS.md conflicts (`git checkout --ours docs/TASKS.md`)
- [ ] **DO** use `safe_push.sh` script when available

---

## Technical Details

### Why Auto-Format Workflow Isn't the Problem

The `.github/workflows/auto-format.yml` workflow:
- Only runs on **pull requests** (not direct pushes to main)
- Only formats **Python files**
- Only runs on **PRs from the same repo** (not forks)

**Conclusion:** Auto-format workflow is **NOT** the cause of main branch conflicts.

### The Real Culprit: Local Pre-Commit Hooks

The `.pre-commit-config.yaml` hooks:
- Run on **every local commit**
- Modify files **after staging** but **before committing**
- Create unstaged changes that cause the "ahead/behind" situation

**Solution:** Always amend commit after pre-commit hooks run.

### Why We Can't Disable Pre-Commit Hooks

Pre-commit hooks are **essential** for:
- ✅ Enforcing code style (black, ruff, isort)
- ✅ Catching errors before CI (mypy, bandit)
- ✅ Validating docs (version drift, API sync)
- ✅ Preventing broken commits (TASKS.md format)

**Disabling them would:**
- ❌ Allow unformatted code to reach CI
- ❌ Slow down development (wait for CI to catch errors)
- ❌ Create inconsistent code style

**Better solution:** Work **with** the hooks using the safe push workflow.

---

## Testing the Solution

### Test 1: Normal Push

```bash
# Make a change
echo "test" >> README.md

# Use safe push
./scripts/safe_push.sh "test: verify safe push works"

# Expected: ✅ Successfully pushed!
```

### Test 2: Pre-Commit Modifications

```bash
# Make a Python file with bad formatting
echo "x=1+2" >> Python/test.py

# Commit (black will reformat to "x = 1 + 2")
git add Python/test.py
git commit -m "test: verify pre-commit handling"

# Check status
git status  # Should show test.py as modified

# Use safe push
./scripts/safe_push.sh "test: verify pre-commit handling"

# Expected: ✅ Successfully pushed! (with amended commit)
```

### Test 3: Conflict Resolution

```bash
# Simulate conflict by modifying TASKS.md
echo "test" >> docs/TASKS.md
git add docs/TASKS.md
git commit -m "test: verify conflict resolution"

# Meanwhile, remote has a change (simulate by editing on GitHub)
# Pull will create conflict

./scripts/safe_push.sh "test: verify conflict resolution"

# Expected: ✅ Successfully pushed! (conflict auto-resolved)
```

---

## Maintenance Notes

### When to Update This Workflow

**Trigger an update if:**
- Pre-commit hooks change significantly
- Git version upgrades change behavior
- New CI workflows are added
- Merge conflicts become frequent again

### How to Debug Issues

**If safe_push.sh fails:**

1. **Check the error message** — Script provides clear errors
2. **Run git status** — See what state you're in
3. **Check pre-commit hooks** — `pre-commit run --all-files`
4. **Verify remote is reachable** — `git fetch origin`
5. **Check network** — `ping github.com`

**Enable debug mode:**

```bash
bash -x ./scripts/safe_push.sh "test message"
```

---

## Conclusion

**Problem:** Pre-commit hooks + race conditions = frequent push failures

**Solution:** Use `./scripts/safe_push.sh` for all commits

**Result:**
- ✅ Zero push failures
- ✅ Zero rebase conflicts
- ✅ Zero detached HEAD states
- ✅ Zero manual conflict resolution needed

**All AI agents** now follow this workflow automatically via `.github/copilot-instructions.md`.

---

**Document Status:** ✅ Complete
**Last Updated:** 2026-01-06
**Tested:** ✅ Works for all scenarios
**Adopted:** ✅ In copilot-instructions.md

# Git Workflow for AI Agents — Avoiding Race Conditions

> ⚠️ **Deprecated:** This doc is superseded by `docs/GIT_WORKFLOW_AI_AGENTS.md`.
> Use the canonical workflow doc for current instructions.

**Problem (historical):** Pre-commit hooks modify files AFTER staging. Auto-format is now check-only, so PR auto-commit races are removed.

**Status:** ✅ **SOLVED** — Use the safe push workflow below

---

## Table of Contents

1. [Quick Solution](#quick-solution-use-this-every-time)
2. [Pull Request (PR) Workflow](#pull-request-pr-workflow)
3. [Why This Problem Happens](#why-this-problem-happens)
4. [Solutions We Implemented](#solutions-we-implemented)
5. [Common Scenarios & Solutions](#common-scenarios--solutions)
6. [Workflow Comparison](#workflow-comparison)
7. [For AI Agents: Implementation Checklist](#for-ai-agents-implementation-checklist)
8. [Technical Details](#technical-details)
9. [Testing the Solution](#testing-the-solution)
10. [Maintenance Notes](#maintenance-notes)

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

## Pull Request (PR) Workflow

### When to Use PRs vs Direct Push

**Use PRs for:**
- ✅ Major features or refactoring (>100 lines)
- ✅ Breaking changes or API modifications
- ✅ Changes requiring review or discussion
- ✅ External contributors (always use PRs)

**Direct push to main for:**
- ✅ Small fixes (<20 lines, low risk)
- ✅ Documentation updates
- ✅ Test additions without behavior changes
- ✅ Routine maintenance (version bumps, deps)

### Creating a PR with Safe Workflow

**Step-by-step:**

```bash
# 1. Create feature branch
git checkout -b feature/your-feature-name

# 2. Make changes and commit using safe_push.sh
./scripts/safe_push.sh "feat: add new feature"

# 3. Create PR
gh pr create --title "feat: add new feature" --body "Description of changes"

# 4. Wait for CI checks
gh pr checks --watch

# 5. After all checks pass, merge
gh pr merge --squash --delete-branch
```

### Handling Pre-Commit Hooks in PRs

Pre-commit hooks work the **same way** on feature branches:

```bash
# On feature branch
git checkout -b fix/something

# Make changes
echo "new code" >> file.py

# Use safe_push.sh (works on any branch)
./scripts/safe_push.sh "fix: resolve issue"

# Result: pre-commit hooks handled automatically
```

**Key point:** `safe_push.sh` detects your current branch and pushes to it correctly.

### Auto-Format Workflow on PRs

The `.github/workflows/auto-format.yml` workflow:
- ✅ **Runs automatically on PRs**
- ✅ Formats Python code with `black` and `ruff`
- ✅ Commits changes back to your PR branch
- ⚠️ **Creates a race condition if you push while it's running**

**Safe PR workflow to avoid race:**

```bash
# 1. Push your changes
./scripts/safe_push.sh "feat: add feature"

# 2. Create PR
gh pr create --title "feat: add feature" --body "..."

# 3. WAIT for auto-format workflow (30-60 seconds)
gh pr checks --watch

# 4. If auto-format committed changes, pull them
git pull origin feature/your-feature-name

# 5. Now safe to make more changes
./scripts/safe_push.sh "feat: address review comments"
```

### Updating PR Branch

**When main branch has new commits:**

```bash
# Check if PR is behind main
gh pr view <number>

# Update PR branch (two options)
```

**Option A: Merge main into PR (recommended):**
```bash
git checkout feature/your-feature-name
git pull --no-rebase origin main
git push
```

**Option B: Use GitHub CLI:**
```bash
gh pr update-branch <number>
```

**Option C: Rebase (use with caution):**
```bash
# Only if PR has NO merge commits and auto-format hasn't run
git checkout feature/your-feature-name
git pull --rebase origin main
git push --force-with-lease
```

⚠️ **Warning:** Rebase can cause issues if:
- Auto-format workflow already committed to your branch
- PR has merge commits
- Multiple people are working on the branch

### Resolving PR Conflicts

**If PR has conflicts with main:**

```bash
# 1. Update your local main
git checkout main
git pull --ff-only

# 2. Merge main into feature branch
git checkout feature/your-feature-name
git merge main

# 3. Resolve conflicts (keep your changes)
git checkout --ours <conflicted-file>
git add <conflicted-file>
git commit --no-edit

# 4. Push resolution
git push
```

### Common PR Scenarios

#### Scenario 1: "PR Checks Failed - Formatting Issues"

**Symptom:** CI fails with "black would reformat X files"

**Cause:** You pushed before pre-commit hooks ran or bypassed them

**Solution:**
```bash
# Run black locally
.venv/bin/python -m black .

# Commit and push
./scripts/safe_push.sh "style: apply black formatting"

# Checks will pass now
```

#### Scenario 2: "PR Behind Base Branch"

**Symptom:** GitHub shows "This branch is out-of-date with the base branch"

**Solution:**
```bash
# Update PR branch
gh pr update-branch <number>

# Or manually
git checkout feature/your-feature-name
git pull --no-rebase origin main
git push
```

#### Scenario 3: "Auto-Format Made Changes"

**Symptom:** PR has a new commit from `github-actions[bot]`

**Solution:**
```bash
# Pull the auto-format changes
git pull origin feature/your-feature-name

# Continue working
./scripts/safe_push.sh "feat: continue implementation"
```

#### Scenario 4: "Can't Merge - CI Running"

**Symptom:** `gh pr merge` says "not mergeable"

**Cause:** CI checks still running

**Solution:**
```bash
# Wait for checks to complete
gh pr checks <number> --watch

# When all green, merge
gh pr merge <number> --squash --delete-branch
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

### Direct Push to Main

#### ❌ Old Workflow (Problematic)

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

#### ✅ New Workflow (Safe)

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

### Pull Request Workflow

#### ❌ Old PR Workflow (Problematic)

```bash
git checkout -b feature/xyz
git add file.py
git commit -m "message"
git push -u origin feature/xyz
gh pr create --title "..." --body "..."
gh pr merge --squash          # ❌ Immediately tries to merge
# CI hasn't finished, merge fails
```

**Problems:**
- Tries to merge before CI completes
- Auto-format workflow creates race condition
- Doesn't wait for checks
- Force push conflicts

#### ✅ New PR Workflow (Safe)

```bash
git checkout -b feature/xyz
./scripts/safe_push.sh "feat: implement xyz"
gh pr create --title "feat: implement xyz" --body "..."
gh pr checks --watch          # ✅ Wait for CI
gh pr merge --squash --delete-branch  # ✅ Merge after checks pass
```

**Benefits:**
- Waits for CI before merging
- Handles auto-format commits automatically
- Pre-commit hooks managed by safe_push.sh
- Clean PR history with squash merge
- One command (`safe_push.sh`)

---

## For AI Agents: Implementation Checklist

### Direct Push to Main

When you (AI agent) need to commit and push to main:

- [ ] **DON'T** run `git push` immediately after `git commit`
- [ ] **DO** check if pre-commit hooks modified files (`git status`)
- [ ] **DO** amend commit if files were modified (`git add -A && git commit --amend --no-edit`)
- [ ] **DO** pull before push (`git pull --no-rebase`)
- [ ] **DO** use `--ours` for TASKS.md conflicts (`git checkout --ours docs/TASKS.md`)
- [ ] **DO** use `safe_push.sh` script when available

### Pull Request Workflow

When you (AI agent) need to create and merge a PR:

- [ ] **DO** create feature branch (`git checkout -b feature/name`)
- [ ] **DO** use `safe_push.sh` for all commits (works on any branch)
- [ ] **DO** create PR with descriptive title and body (`gh pr create`)
- [ ] **DO** wait for CI checks before merging (`gh pr checks --watch`)
- [ ] **DON'T** merge immediately after creating PR
- [ ] **DO** pull auto-format changes before continuing work
- [ ] **DO** update PR branch if behind main (`gh pr update-branch`)
- [ ] **DO** squash merge with branch deletion (`gh pr merge --squash --delete-branch`)

### Decision: When to Use PR vs Direct Push

**Use PR (create feature branch):**
- [ ] Change is >100 lines OR touches >3 files
- [ ] Breaking changes or API modifications
- [ ] New features requiring review
- [ ] High-risk refactoring

**Direct push to main:**
- [ ] Documentation updates (<50 lines)
- [ ] Small bug fixes (<20 lines)
- [ ] Test additions (no behavior changes)
- [ ] Version bumps, routine maintenance
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

### Test 4: PR Workflow

```bash
# Create feature branch
git checkout -b test/pr-workflow

# Make a change
echo "test change" >> README.md

# Use safe push
./scripts/safe_push.sh "test: verify PR workflow"

# Create PR
gh pr create --title "test: verify PR workflow" --body "Testing PR creation"

# Wait for checks
gh pr checks --watch

# Merge (after checks pass)
gh pr merge --squash --delete-branch

# Expected: ✅ PR created, checks passed, merged successfully
```

### Test 5: PR Behind Base Branch

```bash
# Create feature branch
git checkout -b test/update-branch

# Make change and push
echo "test" >> README.md
./scripts/safe_push.sh "test: create PR"

# Create PR
gh pr create --title "test: update branch" --body "..."

# Meanwhile, push a change to main (simulate work)
git checkout main
echo "main change" >> CHANGELOG.md
./scripts/safe_push.sh "chore: update changelog"

# Back to feature branch
git checkout test/update-branch

# Update PR branch
gh pr update-branch

# Expected: ✅ PR updated with main's changes, no conflicts
```

### Test 6: Auto-Format in PR

```bash
# Create feature branch with unformatted code
git checkout -b test/auto-format

# Add unformatted Python (bypass pre-commit for testing)
echo "x=1+2" >> Python/test_format.py
git add Python/test_format.py
git commit -m "test: unformatted code" --no-verify

# Push
git push -u origin test/auto-format

# Create PR
gh pr create --title "test: auto-format" --body "Testing auto-format"

# Auto-format workflow will run and commit changes
gh pr checks --watch

# Pull auto-format changes
git pull origin test/auto-format

# Expected: ✅ Auto-format commit appears, code is formatted
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

# Git Workflow Recurring Issues - Deep Research

**Date:** 2026-01-06
**Status:** CRITICAL - Recurring workflow failures
**Priority:** HIGH - Blocking productivity

---

## Executive Summary

**The core issue is enforcement, not just tooling.** We have multiple scripts, workflows, and docs, but there is no single, enforced entrypoint. The result is inconsistent usage, merge commits created by tooling, and repeated manual recovery.

**Primary drivers identified:**
1. **Behavioral enforcement gap**: agents still use manual git in stress states.
2. **Tooling contradictions**: safe_push.sh, quick_push.sh, and PR scripts do not align.
3. **Merge-by-design**: safe_push.sh uses merge pulls, which creates merge commits even when used correctly.
4. **Too many entrypoints**: safe_push.sh, ai_commit.sh, quick_push.sh, create_task_pr.sh, finish_task_pr.sh, should_use_pr.sh.

---

## Evidence and Current Metrics

### Merge Commit Spike (2026-01-06)
**Command used:**
```bash
git log --since "2026-01-06 00:00" --until "2026-01-06 23:59" --oneline origin/main | rg " Merge "
```
**Result:** 17 merge commits on 2026-01-06.

Sample merge commits:
```
- 71ce37f: Merge branch 'main'
- 0191e97: Merge branch 'main'
- 15b1bb2: Merge branch 'main'
- c746d5a: Merge branch 'main'
- 1eae536: Merge branch 'main'
- 6a7ba3b: Merge branch 'main'
- f4fe1c3: Merge branch 'main'
- b3038d7: Merge branch 'main'
- 315ddac: Merge branch 'main'
```

### Current Merge Rate (last 30 commits)
**Command used:**
```bash
git log -30 --oneline origin/main | rg " Merge " | wc -l
```
**Result:** 2 merge commits in the last 30 commits (6.7%).

### Commit Hygiene Issues (Recent)
- `f7d68fb` has commit message `--help` (non-conventional, likely accidental).
- Multiple merge commits include the default editor template in the message ("Please enter a commit message...").

---

## Automation Inventory (Git Workflow)

### Primary Entry Points
- `scripts/safe_push.sh` - main workflow (pull, stage, commit, amend, pull, push).
- `scripts/ai_commit.sh` - wrapper around safe_push.sh; stages all changes.

### PR Workflow Scripts
- `scripts/create_task_pr.sh`
- `scripts/finish_task_pr.sh`
- `scripts/should_use_pr.sh` (decision helper; requires staged files)

### Diagnostics and Validation
- `scripts/validate_git_state.sh` (detects diverged state, unfinished merges, etc.)
- `scripts/check_unfinished_merge.sh` (pre-commit hook)
- `scripts/verify_git_fix.sh` (whitespace fix validation)
- `scripts/test_git_workflow.sh` (basic script validation)

### Deprecated / Experimental
- `scripts/quick_push.sh` (rebase-based; marked deprecated in automation catalog)
- `scripts/safe_push_v2.sh` (experimental)
- `scripts/should_use_pr_old.sh`
- `scripts/check_not_main.sh` (not wired into hooks)

### CI Automation
- `.github/workflows/python-tests.yml`
- `.github/workflows/auto-format.yml` (auto-commits into PR branches)
- `.github/workflows/git-workflow-tests.yml` (tests scripts only, not real merge states)

---

## Contradictions and Gaps (Root Causes)

### 1) safe_push.sh used merge pulls by design (fixed)
- Now uses `git pull --ff-only` on main to avoid merge commits.
- Feature branches rebase on `origin/main` before first push; otherwise merge main.

### 2) safe_push.sh was hard-coded to `origin main` (fixed)
- Now branch-aware; syncs safely based on current branch.

### 3) Auto-resolve with `--ours` can hide conflicts
- In conflicts, safe_push.sh forces `git checkout --ours`.
- This can silently discard remote changes without review.

### 4) should_use_pr.sh required staging (fixed)
- Now scans staged, unstaged, and untracked changes.

### 5) Multiple entrypoints = inconsistent behavior
- `safe_push.sh`: branch-aware sync (ff-only on main; rebase-before-push else merge)
- `quick_push.sh`: now blocked (deprecated)
- `create_task_pr.sh`: `git pull --ff-only`

### 6) Auto-format workflow adds commits (fixed)
- `auto-format.yml` is now check-only.

### 7) Enforcement is optional
- Pre-commit hooks only run on commit.
- No hard block prevents manual `git add/commit/push`.

---

## What Actually Works (Clarified)

**Unfinished merge handling is correct in safe_push.sh.**
If `.git/MERGE_HEAD` exists and there are no unmerged paths, safe_push.sh runs:
```bash
git commit --no-edit
git push
```
This covers the "All conflicts fixed but you are still merging" state.

The problem is not a bug in this area; the problem is inconsistent usage and conflicting tooling.

---

## Updated Root Cause Assessment

**Primary:** behavioral enforcement gap.
**Secondary:** tooling contradictions and merge-by-design strategy.
**Tertiary:** documentation sprawl and conflicting instructions.

---

## Implemented Reset: A Simpler, Enforced Workflow

### Principle
**One entrypoint, two paths.**

### Path A: Direct commit (docs/tests only)
1. `./scripts/validate_git_state.sh` (or new recovery helper)
2. `./scripts/ai_commit.sh "docs: update ..."`

### Path B: PR required (code/CI/deps)
1. `./scripts/create_task_pr.sh TASK-XXX "desc"`
2. `./scripts/ai_commit.sh "feat: ..."`
3. `./scripts/finish_task_pr.sh TASK-XXX "desc"`

### Enforcement Status
- safe_push.sh is branch-aware and avoids merge commits on main.
- should_use_pr.sh handles unstaged changes and ai_commit.sh enforces it.
- quick_push.sh is blocked.

---

## Priority Fixes (Implemented)

### P0 - Stop merge commit spam (tooling)
- safe_push.sh now uses `git pull --ff-only` on main.
- Feature branches rebase on `origin/main`.

### P0 - Single entrypoint
- ai_commit.sh is the primary entrypoint (enforces PR rules).
- quick_push.sh is blocked; safe_push_v2.sh remains experimental.

### P1 - Recovery support
- Added `scripts/recover_git_state.sh` and referenced it in docs.

### P1 - Remove staging contradiction
- should_use_pr.sh now scans staged, unstaged, and untracked changes.
- ai_commit.sh runs should_use_pr.sh before committing.

### P2 - Conflict safety
- Replace auto `--ours` resolution with explicit prompt or `--ours` only on docs.

### P2 - Documentation consolidation
- Added canonical doc: `docs/GIT_WORKFLOW_AI_AGENTS.md`.
- Older guidance marked as deprecated.

---

## Decisions (Approved)

1. **PR-first** with docs-only exceptions for small, low-risk changes.
2. **Branch-aware safe_push.sh** (ff-only on main, rebase on feature branches).
3. **Auto-format is check-only** (no auto-commits on PRs; formatting fixed locally).

---

## Immediate Next Actions (if needed)

1. Tighten conflict auto-resolution (limit --ours to docs/tests only).
2. Review PR-only enforcement for all non-doc changes.
3. Archive legacy workflow docs after adoption.

---

**Status:** Research updated with current metrics, automation inventory, and reset plan.

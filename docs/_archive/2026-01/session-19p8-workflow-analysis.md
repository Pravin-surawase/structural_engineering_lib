# Session 19P8 Git Workflow Analysis

**Type:** Research
**Audience:** All Agents
**Status:** Draft
**Importance:** High
**Version:** 1.0.0
**Created:** 2026-01-12
**Last Updated:** 2026-01-12
**Related Tasks:** P8-PHASE2, workflow improvement
**Archive Condition:** After fixes applied and verified

---

## Summary

Analysis of git workflow issues from Session 19P8 Phase 2 to identify root causes and permanent solutions. Updated to reflect fixes now in automation scripts.

---

## Issues Identified

### Issue 1: Branch Naming Inconsistency

**What happened:**
- Started on branch `task/P8-PHASE2-v2`
- `finish_task_pr.sh` expected `task/P8-PHASE2`
- Script prompted "Continue anyway?" which agent answered "N" (wrong answer in non-interactive context)

**Root cause:**
- Branch was created manually or with `-v2` suffix instead of using `create_task_pr.sh`
- Script uses `read -p` which doesn't work well in automated contexts

**Solution:**
1. Always use `create_task_pr.sh` to create branches (enforces naming)
2. When continuing work on existing branch, use branch name directly
3. ✅ `finish_task_pr.sh` now supports `--force` for non-interactive use

### Issue 2: Direct `gh pr create` with Multiline Body

**What happened:**
- Agent tried `gh pr create --body "multiline..."` which caused terminal parsing issues
- Command echoed partial input repeatedly, creating garbled output

**Root cause:**
- Multiline strings in shell commands are fragile
- The terminal tool simplifies commands, breaking multiline handling

**Solution:**
1. ✅ `finish_task_pr.sh` now uses `--body-file` to avoid multiline parsing issues
2. Alternative: use a simple one-line body and edit PR description later

### Issue 3: Orphan Remote Branches

**What happened:**
- Multiple remote branches left over: `task/P8-PHASE2`, `task/P8-PHASE2-v2`, `task/DOC-P7`, etc.

**Root cause:**
- Branches not cleaned up after PR merge
- `--delete-branch` flag not always used
- Some branches from failed/abandoned PRs

**Solution:**
1. ✅ Use `cleanup_stale_branches.sh` (dry run by default)
2. Ensure all merges use `--delete-branch`

### Issue 4: Using `gh pr checks --watch` in Terminal

**What happened:**
- Command opened "alternate buffer" which doesn't produce output
- Agent couldn't see CI status

**Root cause:**
- `gh pr checks --watch` uses TUI mode incompatible with captured output

**Solution:**
1. ✅ `finish_task_pr.sh` now polls `gh pr view --json statusCheckRollup`
2. Avoid TUI commands in automated workflows

### Issue 5: Local Stale Branches

**What happened:**
- Multiple local branches exist that are no longer needed:
  - `task/P8-PHASE2` (old)
  - `task/FIX-002` (old)
  - `backup/ui-layout-20260108` (old)
  - `copilot-worktree-2026-01-09T11-52-46` (orphan worktree)

**Root cause:**
- Branches not cleaned after work complete
- No automation for local cleanup

**Solution:**
1. ✅ `cleanup_stale_branches.sh` detects and deletes stale local branches

---

## Correct Workflow (For Reference)

### Option A: Using PR Scripts (Preferred, Automation-First)

```bash
# 1. Ensure git state is clean
./scripts/git_ops.sh --status

# 2. Create task branch (ALWAYS use this script)
./scripts/create_task_pr.sh TASK-XXX "description"

# 3. Work and commit (can have multiple commits)
./scripts/ai_commit.sh "feat: implement X"
./scripts/ai_commit.sh "fix: handle edge case"

# 4. Finish and create PR (use SAME task ID)
./scripts/finish_task_pr.sh TASK-XXX "description" --async
# Choose: A (async), W (wait), or S (skip)

# 5. After merge, clean up
./scripts/cleanup_stale_branches.sh
# (run with --apply only after verifying the list)
```

### Option B: Existing Task Branch

```bash
# If already on a task branch with commits:
./scripts/ai_commit.sh "final commit"

# Create PR + wait/merge using the script (non-interactive safe)
./scripts/finish_task_pr.sh TASK-XXX "description" --wait
```

---

## Action Items

1. ✅ Document these issues (this file)
2. ✅ Clean up orphan remote branches (via cleanup script)
3. ✅ Clean up stale local branches (via cleanup script)
4. ✅ Add `--force` flag to finish_task_pr.sh for non-interactive use
5. ✅ Create branch cleanup script
6. 🔲 Update workflow documentation

---

## Prevention

### Pre-Session Checklist Addition

Add to `agent_start.sh`:
- Check for stale local branches
- Warn if not on main branch
- Show orphan remote branch count

### Post-Merge Checklist

After any PR merge:
1. Ensure clean state: `./scripts/git_ops.sh --status`
2. Clean stale branches: `./scripts/cleanup_stale_branches.sh` (use `--apply` only after review)
3. Verify remote deleted (should be automatic with `--delete-branch`)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-12 | Initial analysis |

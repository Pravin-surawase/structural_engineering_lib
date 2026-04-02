# Git Workflow Hardening Plan v1.0

**Type:** Architecture
**Audience:** All Agents
**Status:** Active
**Importance:** Critical
**Created:** 2026-04-02
**Last Updated:** 2026-04-02
**Related Tasks:** TASK-900 through TASK-913
**Abstract:** Comprehensive improvement plan for git automation infrastructure based on 9-script audit and TASK-640 root-cause analysis

---

> Comprehensive improvement plan for the git automation infrastructure.
> Based on audit of 9 scripts (2,408 lines), 4-agent review, and root-cause analysis of the TASK-640 incident.

## Executive Summary

During Phase 2 Column Design, the git workflow broke down when:
1. `safe_push.sh` said "Push ready" for a diverged branch
2. Push failed with non-fast-forward (no actionable guidance)
3. Agent fell back to FORBIDDEN manual git commands (`git rebase --skip`, `git push --force-with-lease`)
4. Multiple recovery attempts before PR was finally created

This plan addresses 19 identified gaps across 4 severity levels, organized into 4 implementation phases.

---

## Root Cause Analysis: TASK-640 Incident

### What Happened
1. Agent committed on `task/TASK-640` branch
2. Concurrent PR #490 was squash-merged into main, changing commit hashes
3. `safe_push.sh` Step 6 said "Push ready" (false — branches were diverged)
4. Step 7 push failed: "rejected (non-fast-forward)"
5. Error message: "Push later with `ai_commit.sh --push`" (unhelpful — same failure)
6. Agent tried manual `git pull --rebase` → conflicts
7. Agent ran `git rebase --skip` (DANGEROUS — skips commits)
8. Agent used `git push --force-with-lease` (FORBIDDEN)

### Root Cause
`safe_push.sh` Step 6 divergence detection has a bug:
```bash
# Current code (line ~400):
else
  if [[ -z "$REMOTE" ]]; then
    echo "No remote branch yet"
  else
    echo "Push ready"  # ← THIS IS WRONG — branches are DIVERGED
  fi
fi
```
The `else` clause catches the diverged state but reports "Push ready" instead of detecting the divergence and offering recovery.

---

## Gap Inventory (19 Gaps, Prioritized)

### CRITICAL (4 gaps — fix first, cause real incidents)

| ID | Gap | Root Script | Impact |
|----|-----|-------------|--------|
| G-01 | Diverged branch not detected in Step 6 | `safe_push.sh` L400 | **Direct cause of TASK-640** — agents fall back to manual git |
| G-02 | `--push` bypasses safe_push.sh | `ai_commit.sh` L133 | No retry logic, no logging, no divergence detection |
| G-03 | `--amend` force-pushes on any branch (including main) | `ai_commit.sh` L181 | History rewriting on main, bypasses safe_push.sh entirely |
| G-04 | Push error messages are non-actionable | `safe_push.sh` L460 | "Push later with --push" fails the same way; agents improvise with dangerous manual git |

### HIGH (5 gaps — fix soon, prevent future incidents)

| ID | Gap | Root Script | Impact |
|----|-----|-------------|--------|
| G-05 | No squash-merge divergence detection | `safe_push.sh` | Common after PR merge; silent divergence |
| G-06 | `--finish` state not persisted | `finish_task_pr.sh` | Lost PR number on terminal session reset |
| G-07 | `validate_git_state.sh` is dead code (252 lines) | standalone | Never called by automated workflow; checks exist but unused |
| G-08 | `git rebase --skip` not warned/blocked | agent instructions | Agents use this when rebase fails; loses commits silently |
| G-09 | No pre-commit divergence check | `ai_commit.sh` | Agent commits, then push fails — wasted effort |

### MEDIUM (6 gaps — fix when in area)

| ID | Gap | Root Script | Impact |
|----|-----|-------------|--------|
| G-10 | Push errors not categorized | `safe_push.sh` L460 | Auth, diverged, network, protection lumped into one message |
| G-11 | CI timeout has no state persistence | `finish_task_pr.sh` | After 20min timeout, agent must remember PR number |
| G-12 | Env var bypass not logged | `pre-push` hook | `AI_COMMIT_ACTIVE=1` bypasses silently — no audit trail |
| G-13 | `finish_task_pr.sh` has 30-line duplicate code | `finish_task_pr.sh` | Maintenance burden, divergence risk |
| G-14 | Auto-stash message not agent-specific | `safe_push.sh` L260 | Concurrent agents could pop wrong stash |
| G-15 | Task ID not validated | `create_task_pr.sh` | Malformed branch names possible |

### LOW (4 gaps — defer or skip)

| ID | Gap | Rationale for Deferral |
|----|-----|----------------------|
| G-16 | Orphaned commit detection | `git reflog` preserves for 90 days |
| G-17 | Multi-agent branch protection | Single-agent per branch is enforced by process |
| G-18 | Stale remote tracking after squash-merge | `finish_task_pr.sh` already runs `git fetch --prune` |
| G-19 | Zero tests for 2,400+ lines of bash | Important but medium-term effort |

---

## Agent Review Summary

### Structural Engineer (user perspective)
- Gap 1+4+9 = one incident chain: divergence → bad error → manual git fallback
- Added Gap 16 (`--amend` has no "already pushed" safety) — merged into G-03
- Added Gap 17 (auto-stash loses context) — tracked as G-14
- Added Gap 18 (no `--finish` state persistence) — tracked as G-06
- **Priority: Fix the error flow first.** Everything else follows.

### Reviewer (architecture perspective)
- "Error flow is the weakest area (3/10 score)"
- `ai_commit.sh --push` and `--amend` both bypass `safe_push.sh` — leaky abstraction
- `validate_git_state.sh` is dead code — wire in or delete
- Recommended `bats-core` tests for failure paths
- **Root fix: make safe_push.sh the ONLY push path**

### Security Agent
- Pre-push hook IS installed via `core.hooksPath` (initial audit was wrong)
- `--amend` on main = Medium risk (force-with-lease on protected branch)
- Env var bypass should log events (`AI_COMMIT_ACTIVE` is silent)
- Task ID injection: branch name sanitization needed
- `git_workflow.log` needs rotation and restrictive permissions
- **Priority: Block `--amend` on main, log bypass events**

### Governance Agent
- Corrected Finding #1 — hooks are installed, not missing
- Set script line budget: 2,000 total, 400 per script
- Net-zero line rule: every fix must consolidate elsewhere
- Dead code tolerance: 0 (validate_git_state.sh must be wired in or deleted)
- Proposed TASK-900 series for tracking
- Added 5 new weekly governance metrics
- **Priority: Phase 1 can be done in 1 session. Don't over-engineer.**

---

## Implementation Plan

### Phase 1: Emergency Fixes (Next Session — ~2-3 hours)

**Goal:** Prevent the TASK-640 incident class from recurring.

#### TASK-900: Fix safe_push.sh Step 6 divergence detection
**File:** `scripts/safe_push.sh` lines ~395-410
**Change:** Replace the false "Push ready" with actual divergence detection and actionable guidance.

```bash
# BEFORE (broken):
else
  if [[ -z "$REMOTE" ]]; then
    echo "No remote branch yet; will set upstream"
  else
    echo "Push ready"  # ← LIE
  fi
fi

# AFTER (fixed):
else
  if [[ -z "$REMOTE" ]]; then
    echo "No remote branch yet; will set upstream"
  else
    # DIVERGED: local and remote have independent commits
    AHEAD=$(git rev-list --count "$REMOTE_NAME/$CURRENT_BRANCH"..HEAD)
    BEHIND=$(git rev-list --count HEAD.."$REMOTE_NAME/$CURRENT_BRANCH")
    echo "ERROR: Branch diverged from remote ($AHEAD ahead, $BEHIND behind)"
    echo ""
    echo "  RECOVERY: ./scripts/recover_git_state.sh"
    echo ""
    echo "  DO NOT use: git push --force, git rebase --skip"
    log_message "ERROR" "Branch diverged: $AHEAD ahead, $BEHIND behind"
    exit 1
  fi
fi
```

**Tests:** Manually verify by creating a diverged state in a test repo.

#### TASK-901: Block --amend on main/develop/release branches
**File:** `scripts/ai_commit.sh` lines ~168-185
**Change:** Add branch guard before force-with-lease.

```bash
if [[ "$AMEND" == "true" ]]; then
    CURRENT_BRANCH=$(git branch --show-current)
    if [[ "$CURRENT_BRANCH" == "main" || "$CURRENT_BRANCH" == "develop" || "$CURRENT_BRANCH" =~ ^release/ ]]; then
        echo "ERROR: Cannot --amend on protected branch '$CURRENT_BRANCH'"
        echo "  Use a task branch: ./scripts/ai_commit.sh --branch TASK-XXX 'desc'"
        exit 1
    fi
    # ... existing amend logic ...
fi
```

#### TASK-902: Route --push through safe_push.sh
**File:** `scripts/ai_commit.sh` lines ~130-140
**Change:** Replace direct `git push` with `safe_push.sh` invocation.

```bash
# BEFORE:
if [[ "$PUSH_ONLY" == "true" ]]; then
    export SAFE_PUSH_ACTIVE=1
    git push
    exit $?
fi

# AFTER:
if [[ "$PUSH_ONLY" == "true" ]]; then
    # Route through safe_push.sh for retry logic and divergence detection
    exec "$PROJECT_ROOT/scripts/safe_push.sh" "--push-only"
fi
```
Also add `--push-only` flag support to `safe_push.sh` (skip commit, just push).

#### TASK-903: Wire or delete validate_git_state.sh
**Decision:** Inline the essential checks (divergence, unfinished merge) into safe_push.sh Step 0, then delete `validate_git_state.sh` as standalone script.
**Alternative:** Keep as a standalone diagnostic tool but remove from dead-code count.

**Line budget target:** Phase 1 should be net-zero lines (+divergence detection, -validate dead code).

---

### Phase 2: Recovery & Resilience (Session +1 — ~2 hours)

#### TASK-904: Persist --finish state
**File:** `scripts/finish_task_pr.sh`
**Change:** Write `.git/FINISH_STATE` at each stage.

```bash
STATE_FILE=".git/FINISH_STATE"
echo "PR_NUMBER=$PR_NUMBER" > "$STATE_FILE"
echo "TASK_ID=$TASK_ID" >> "$STATE_FILE"
echo "STAGE=ci_polling" >> "$STATE_FILE"
echo "TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$STATE_FILE"
```
On failure/timeout, print: `Resume: ./scripts/ai_commit.sh --continue $(grep PR_NUMBER .git/FINISH_STATE | cut -d= -f2)`

On success, delete the state file.

Also teach `ai_commit.sh --status` to read `.git/FINISH_STATE` if present.

#### TASK-905: Squash-merge divergence detection
**File:** `scripts/safe_push.sh` (integrate with G-01 fix)
**Change:** When divergence detected, check if all local-only commits are already in main (content-identical, different hashes). If yes, the safe recovery is `git reset --hard origin/$BRANCH`.

```bash
# After detecting divergence in Step 6:
if [[ "$AHEAD" -gt 0 && "$BEHIND" -gt 0 ]]; then
    # Check if this is a squash-merge divergence (all content in main)
    LOCAL_ONLY_PATCHES=$(git log --format="%H" "$REMOTE_NAME/$CURRENT_BRANCH"..HEAD | \
        while read sha; do
            git diff-tree --no-commit-id -r "$sha" | md5sum
        done)
    # If patches are empty (all changes already in main), suggest reset
    if git diff HEAD "$REMOTE_NAME/$CURRENT_BRANCH" --stat | grep -q "files changed"; then
        echo "  LIKELY CAUSE: Squash-merge of concurrent PR changed commit hashes"
        echo "  SAFE FIX: git fetch origin && git reset --hard origin/$CURRENT_BRANCH"
    fi
fi
```

#### TASK-906: Actionable error messages
**File:** `scripts/safe_push.sh` lines ~460
**Change:** Categorize push errors with specific recovery commands.

```bash
if echo "$PUSH_ERROR" | grep -qiE "non-fast-forward|diverge"; then
    echo "CAUSE: Branch diverged from remote"
    echo "FIX:   ./scripts/recover_git_state.sh"
elif echo "$PUSH_ERROR" | grep -qiE "denied|forbidden|401|403"; then
    echo "CAUSE: Authentication failed"
    echo "FIX:   gh auth status && gh auth login"
elif echo "$PUSH_ERROR" | grep -qiE "protected|required"; then
    echo "CAUSE: Branch protection requires PR"
    echo "FIX:   ./scripts/ai_commit.sh --branch TASK-XXX 'description'"
elif echo "$PUSH_ERROR" | grep -qiE "timeout|network|reset|connection"; then
    echo "CAUSE: Network error (transient)"
    echo "FIX:   ./scripts/ai_commit.sh --push  # retry"
fi
```

---

### Phase 3: Observability & Testing (Session +2 — ~3 hours)

#### TASK-907: Log all bypass events
**Files:** `scripts/git-hooks/pre-push`, `scripts/git-hooks/pre-commit`
**Change:** Log when `AI_COMMIT_ACTIVE`/`SAFE_PUSH_ACTIVE` allows bypass.

```bash
# At the top of pre-push, before exit 0:
if [[ -n "$AI_COMMIT_ACTIVE" ]] || [[ -n "$SAFE_PUSH_ACTIVE" ]]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] BYPASS: Push allowed via ${AI_COMMIT_ACTIVE:+AI_COMMIT_ACTIVE}${SAFE_PUSH_ACTIVE:+ SAFE_PUSH_ACTIVE} (caller: ${BASH_SOURCE[1]:-unknown})" >> "$LOG_FILE"
    exit 0
fi
```

#### TASK-908: bats-core tests for failure paths
**Directory:** `scripts/tests/`
**Framework:** bats-core (Bash Automated Testing System)
**Priority tests:**
1. `test_diverged_branch_detection.bats` — verify Step 6 catches divergence
2. `test_push_error_categories.bats` — verify error messages match error types
3. `test_amend_branch_guard.bats` — verify --amend blocked on main
4. `test_recovery_scenarios.bats` — verify recover_git_state.sh handles all states

#### TASK-909: Consolidate finish_task_pr.sh duplicates
**File:** `scripts/finish_task_pr.sh`
**Change:** Extract the 30-line merge+cleanup block into a function.

#### TASK-910: Script line budget in check_all.py
**File:** `scripts/check_all.py`
**Change:** Add check for total git script line count (budget: 2,000).

---

### Phase 4: Hardening (Ongoing)

#### TASK-911: Task ID validation
**File:** `scripts/create_task_pr.sh`
**Change:** Validate `TASK_ID` matches `^[A-Z]+-[A-Z0-9-]+$`.

#### TASK-912: Log rotation for git_workflow.log
**File:** `scripts/safe_push.sh` or new `scripts/rotate_logs.sh`
**Change:** Rotate when >1MB, keep 3 old copies.

#### TASK-913: Agent instruction updates
**Files:** `.github/agents/ops.agent.md`, AGENTS.md, CLAUDE.md
**Change:** Add `git rebase --skip` to FORBIDDEN commands list. Document recovery workflow.

---

## Governance Metrics (New)

Add to weekly maintenance:

| Metric | Target | Check |
|--------|--------|-------|
| Git script total lines | ≤2,000 | `wc -l scripts/safe_push.sh scripts/ai_commit.sh scripts/finish_task_pr.sh scripts/create_task_pr.sh scripts/recover_git_state.sh scripts/git-hooks/* \| tail -1` |
| Dead git scripts | 0 | Manual: is any script never called? |
| Git workflow errors/week | 0 new BLOCKED events | `tail -50 logs/git_workflow.log \| grep -c BLOCKED` |
| `core.hooksPath` verified | Yes | `git config --get core.hooksPath` |
| Bypass events/week | 0 unjustified | `grep -c BYPASS logs/git_workflow.log` |

---

## Agent Instruction Updates Required

### ops.agent.md — Add to FORBIDDEN commands:
```
NEVER: git rebase --skip  ← silently drops conflicting commits
NEVER: git push --force-with-lease (outside ai_commit.sh --amend)
```

### ops.agent.md — Add to Error Recovery table:
```
| Branch diverged (non-fast-forward) | ./scripts/recover_git_state.sh |
| Squash-merge divergence | git fetch origin && git reset --hard origin/$BRANCH |
| --finish interrupted | ./scripts/ai_commit.sh --continue PR_NUM |
| --finish PR number lost | Check .git/FINISH_STATE or: gh pr list --head $(git branch --show-current) |
```

### AGENTS.md / CLAUDE.md — Add to FORBIDDEN section:
```
NEVER: git rebase --skip  ← deletes conflicting commits silently
```

### All agent files — Add recovery guidance:
```
When git operations fail:
1. Run: ./scripts/recover_git_state.sh
2. If that fails: ./scripts/validate_git_state.sh --fix
3. Report the issue to @ops
NEVER: attempt manual git rebase, skip, or force push
```

---

## Implementation Notes

- **Net-zero line rule:** Every change that adds lines must consolidate elsewhere
- **WIP limit:** Max 2 tasks active simultaneously
- **Testing:** Phase 1 tasks tested manually (create diverged state in temp repo); Phase 3 adds automated tests
- **Rollout:** Phase 1 in next session (emergency). Phase 2-4 can spread across 2-3 sessions.

---

## Related Documents

- [git-workflow-single-source.md](../git-automation/git-workflow-single-source.md) — current workflow documentation
- [ops.agent.md](../../.github/agents/ops.agent.md) — ops agent instructions
- [TASKS.md](../TASKS.md) — task tracking (add TASK-900 series)

---

*This document follows the metadata standard defined in copilot-instructions.md.*

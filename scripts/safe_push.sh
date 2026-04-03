#!/bin/bash
# Safe push workflow for AI agents - PREVENTS ALL MERGE CONFLICTS
# This script implements a foolproof workflow that minimizes race conditions
#
# Usage:
#   ./scripts/safe_push.sh "commit message"
#   ./scripts/safe_push.sh "commit message" --files "file1 file2"
#
# Critical workflow order (DO NOT REORDER):
# 1. Check for unfinished merge (complete if exists)
# 2. Pull/fetch latest remote state (branch-aware)
# 3. Stage files
# 4. Commit (pre-commit hooks may modify files)
# 5. Re-stage hook modifications and amend (BEFORE any push)
# 6. Sync again (branch-aware)
# 7. Push safely
#
# Why this order matters:
# - Syncing BEFORE commit ensures we start with latest remote
# - Amending BEFORE push means we never rewrite pushed history
# - Syncing AGAIN before push catches changes during commit
# - Avoids merge commits on main by using --ff-only

set -e

# Mark that we're running from automation (for pre-push hook bypass)
export SAFE_PUSH_ACTIVE=1

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Logging configuration
LOG_DIR="logs"
LOG_FILE="$LOG_DIR/git_workflow.log"

# Ensure log directory exists
mkdir -p "$LOG_DIR"

# Log rotation: rotate when >1MB, keep 3 old copies (TASK-912)
if [[ -f "$LOG_FILE" ]]; then
    LOG_SIZE=$(wc -c < "$LOG_FILE" 2>/dev/null || echo 0)
    if [[ "$LOG_SIZE" -gt 1048576 ]]; then
        [[ -f "${LOG_FILE}.3" ]] && rm -f "${LOG_FILE}.3"
        [[ -f "${LOG_FILE}.2" ]] && mv "${LOG_FILE}.2" "${LOG_FILE}.3"
        [[ -f "${LOG_FILE}.1" ]] && mv "${LOG_FILE}.1" "${LOG_FILE}.2"
        mv "$LOG_FILE" "${LOG_FILE}.1"
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] [INFO] Log rotated (previous log exceeded 1MB)" > "$LOG_FILE"
    fi
fi

# Logging function
log_message() {
  local level="$1"
  local msg="$2"
  local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
  echo "[$timestamp] [$level] $msg" >> "$LOG_FILE"
}

# Log workflow start
WORKFLOW_START_TIME=$(date +%s)
log_message "INFO" "=== Safe Push Workflow Started ==="
log_message "INFO" "User: $(whoami)"
log_message "INFO" "Branch: $(git branch --show-current 2>/dev/null || echo 'unknown')"

# Check for stale lock files
if [[ -f .git/index.lock ]]; then
    LOCK_AGE=$(( $(date +%s) - $(stat -f %m .git/index.lock 2>/dev/null || stat -c %Y .git/index.lock 2>/dev/null || echo "0") ))
    if [[ "$LOCK_AGE" -gt 300 ]]; then
        echo -e "${YELLOW}⚠️  Stale .git/index.lock detected (${LOCK_AGE}s old)${NC}"
        echo -e "${YELLOW}   Removing stale lock file...${NC}"
        rm -f .git/index.lock
        log_message "WARNING" "Removed stale .git/index.lock (${LOCK_AGE}s old)"
    else
        echo -e "${RED}ERROR: .git/index.lock exists (another git process may be running)${NC}"
        echo -e "${YELLOW}If no other git process is running, remove it:${NC}"
        echo "  rm .git/index.lock"
        log_message "ERROR" ".git/index.lock exists (${LOCK_AGE}s old)"
        exit 1
    fi
fi

CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || echo "")
DEFAULT_BRANCH="main"
REMOTE_NAME="origin"
AUTO_STASHED="false"
PUSH_HAS_UPSTREAM="false"

# Parse flags
PUSH_ONLY_MODE="false"
for arg in "$@"; do
    case "$arg" in
        --push-only) PUSH_ONLY_MODE="true" ;;
    esac
done

# Detect if we're in a worktree (for background agents)
IS_WORKTREE="false"
AGENT_NAME=""
if git rev-parse --git-common-dir >/dev/null 2>&1; then
  GIT_COMMON_DIR=$(git rev-parse --git-common-dir)
  GIT_DIR=$(git rev-parse --git-dir)
  if [[ "$GIT_COMMON_DIR" != "$GIT_DIR" ]]; then
    IS_WORKTREE="true"
    # Try to detect agent name from .agent_marker or branch name
    if [[ -f ".agent_marker" ]]; then
      AGENT_NAME=$(head -1 .agent_marker 2>/dev/null || echo "unknown")
    else
      # Extract from branch name (e.g., worktree-AGENT_5-2026-01-09)
      AGENT_NAME=$(echo "$CURRENT_BRANCH" | grep -oE 'AGENT_[0-9]+|worktree-[^-]+' | head -1)
    fi
    log_message "INFO" "Worktree detected: $AGENT_NAME on branch $CURRENT_BRANCH"
  fi
fi

if [[ -z "$CURRENT_BRANCH" ]]; then
  echo -e "${RED}ERROR: Detached HEAD state detected${NC}"
  echo "Checkout a branch before committing."
  exit 1
fi

pull_main_ff_only() {
  git pull --ff-only "$REMOTE_NAME" "$DEFAULT_BRANCH"
}

sync_with_main_branch() {
  git fetch "$REMOTE_NAME" "$DEFAULT_BRANCH"
  if [[ "$CURRENT_BRANCH" == "$DEFAULT_BRANCH" ]]; then
    pull_main_ff_only
  else
    if git rev-parse --abbrev-ref "@{u}" >/dev/null 2>&1; then
      git merge --no-edit "$REMOTE_NAME/$DEFAULT_BRANCH"
    else
      git rebase "$REMOTE_NAME/$DEFAULT_BRANCH"
    fi
  fi
}

complete_sync_resolution() {
  if [[ -d .git/rebase-merge ]] || [[ -d .git/rebase-apply ]]; then
    git rebase --continue
  else
    git commit --no-edit
  fi
}

has_upstream() {
  git rev-parse --abbrev-ref "@{u}" >/dev/null 2>&1
}

remote_ref_exists() {
  git show-ref --verify --quiet "refs/remotes/$REMOTE_NAME/$CURRENT_BRANCH"
}

# WEEK 1 OPTIMIZATION: Parallel git fetch
# Fetch runs in background while we stage files, saving 15-30s per commit
FETCH_PID=""

parallel_fetch_start() {
  log_message "INFO" "Starting parallel fetch in background"
  git fetch "$REMOTE_NAME" "$DEFAULT_BRANCH" >> "$LOG_FILE" 2>&1 &
  FETCH_PID=$!
  log_message "INFO" "Fetch started with PID: $FETCH_PID"
}

parallel_fetch_complete() {
  # Wait for background fetch to complete
  if [ -n "${FETCH_PID}" ] && kill -0 $FETCH_PID 2>/dev/null; then
    log_message "INFO" "Waiting for background fetch (PID: $FETCH_PID) to complete..."
    wait $FETCH_PID
    local exit_code=$?
    if [[ $exit_code -ne 0 ]]; then
      log_message "ERROR" "Fetch failed with exit code: $exit_code"
      return 1
    fi
    log_message "INFO" "Fetch completed successfully"
  else
    # Not an error - fetch likely completed quickly or was skipped
    log_message "INFO" "Fetch completed (no PID to wait on)"
  fi

  # Now merge the fetched changes (branch-aware)
  if [[ "$CURRENT_BRANCH" == "$DEFAULT_BRANCH" ]]; then
    # On main: fast-forward only
    git pull --ff-only "$REMOTE_NAME" "$DEFAULT_BRANCH"
  else
    # On feature branch: merge or rebase depending on tracking
    if git rev-parse --abbrev-ref "@{u}" >/dev/null 2>&1; then
      git merge --no-edit "$REMOTE_NAME/$DEFAULT_BRANCH"
    else
      git rebase "$REMOTE_NAME/$DEFAULT_BRANCH"
    fi
  fi
}

# Step 0: Pre-flight — detect ALL incomplete git operations (TASK-903)
# Catches rebase, cherry-pick, and merge states before any work begins
if [[ -d .git/rebase-merge ]] || [[ -d .git/rebase-apply ]]; then
  echo -e "${RED}ERROR: Rebase in progress${NC}"
  echo -e "${YELLOW}RECOVERY: ./scripts/recover_git_state.sh${NC}"
  echo -e "${RED}DO NOT use: git rebase --skip (drops commits silently)${NC}"
  log_message "ERROR" "Rebase in progress — blocking safe_push"
  exit 1
fi

if [[ -f .git/CHERRY_PICK_HEAD ]]; then
  echo -e "${RED}ERROR: Cherry-pick in progress${NC}"
  echo -e "${YELLOW}RECOVERY: ./scripts/recover_git_state.sh${NC}"
  log_message "ERROR" "Cherry-pick in progress — blocking safe_push"
  exit 1
fi

if [ -f .git/MERGE_HEAD ]; then
  echo -e "${YELLOW}⚠️  Unfinished merge detected!${NC}"
  echo -e "${YELLOW}Completing the merge first...${NC}"

  # Check if there are conflicts
  if git status | grep -q "Unmerged paths"; then
    echo -e "${RED}ERROR: There are unresolved merge conflicts${NC}"
    echo -e "${YELLOW}RECOVERY: ./scripts/recover_git_state.sh${NC}"
    log_message "ERROR" "Unfinished merge with conflicts detected"
    exit 1
  fi

  # Complete the merge
  git commit --no-edit
  echo -e "${GREEN}Merge completed${NC}"
  log_message "SUCCESS" "Completed unfinished merge"

  # Now push
  echo -e "${YELLOW}Pushing merged changes...${NC}"
  git push
  WORKFLOW_END_TIME=$(date +%s)
  TOTAL_DURATION=$((WORKFLOW_END_TIME - WORKFLOW_START_TIME))
  echo -e "${GREEN}✅ Successfully pushed merged changes!${NC}"
  echo -e "⏱️  Total time: ${TOTAL_DURATION}s"
  log_message "TIMING" "Total workflow duration: ${TOTAL_DURATION}s"
  exit 0
fi

# Push-only mode: skip commit steps, go straight to sync + push (TASK-902)
if [[ "$PUSH_ONLY_MODE" == "true" ]]; then
  log_message "INFO" "Push-only mode: skipping commit steps"
  echo -e "${GREEN}=== Push-Only Workflow ===${NC}"
  echo -e "${BLUE}📍 Branch: $CURRENT_BRANCH${NC}"

  # Fetch latest remote state
  echo -e "${YELLOW}Step 1/3: Fetching remote state...${NC}"
  git fetch "$REMOTE_NAME" --quiet 2>/dev/null || true

  # Step 2: Safety check (reuses Step 6 logic)
  echo -e "${YELLOW}Step 2/3: Verifying push safety...${NC}"
  LOCAL=$(git rev-parse HEAD)
  REMOTE=""
  BASE=""
  if remote_ref_exists; then
    REMOTE=$(git rev-parse "$REMOTE_NAME/$CURRENT_BRANCH")
    BASE=$(git merge-base HEAD "$REMOTE_NAME/$CURRENT_BRANCH")
  fi

  if [[ -n "$REMOTE" && "$LOCAL" = "$REMOTE" ]]; then
    echo -e "${GREEN}✓ Already synced with remote - nothing to push${NC}"
    log_message "INFO" "Push-only: already synced"
    exit 0
  elif [[ -n "$REMOTE" && "$BASE" = "$REMOTE" ]]; then
    echo -e "${GREEN}Fast-forward push ready${NC}"
  elif [[ -n "$REMOTE" && "$BASE" = "$LOCAL" ]]; then
    echo -e "${YELLOW}Local behind remote - pulling latest${NC}"
    git pull --ff-only "$REMOTE_NAME" "$CURRENT_BRANCH"
  elif [[ -z "$REMOTE" ]]; then
    echo -e "${YELLOW}No remote branch yet; will set upstream on push${NC}"
  else
    AHEAD=$(git rev-list --count "$REMOTE_NAME/$CURRENT_BRANCH"..HEAD 2>/dev/null || echo "?")
    BEHIND=$(git rev-list --count HEAD.."$REMOTE_NAME/$CURRENT_BRANCH" 2>/dev/null || echo "?")
    echo -e "${RED}ERROR: Branch '$CURRENT_BRANCH' has diverged from remote${NC}"
    echo -e "${RED}       ($AHEAD commit(s) ahead, $BEHIND commit(s) behind)${NC}"
    echo ""
    echo -e "${YELLOW}RECOVERY: ./scripts/recover_git_state.sh${NC}"
    echo -e "${RED}DO NOT use: git push --force, git rebase --skip${NC}"
    log_message "ERROR" "Push-only: branch diverged ($AHEAD ahead, $BEHIND behind)"
    exit 1
  fi

  # Step 3: Push with retry
  echo -e "${YELLOW}Step 3/3: Pushing to remote...${NC}"
  if ! git ls-remote --exit-code "$REMOTE_NAME" >/dev/null 2>&1; then
    echo -e "${RED}ERROR: Cannot reach remote '$REMOTE_NAME'${NC}"
    echo -e "${YELLOW}💡 Push later with: ./scripts/ai_commit.sh --push${NC}"
    log_message "ERROR" "Push-only: remote connectivity failed"
    exit 1
  fi

  if has_upstream; then
    PUSH_CMD=(git push)
  else
    PUSH_CMD=(git push -u "$REMOTE_NAME" "$CURRENT_BRANCH")
  fi

  MAX_RETRIES=3
  RETRY_DELAYS=(2 5 10)
  for ((attempt=1; attempt<=MAX_RETRIES; attempt++)); do
    PUSH_OUTPUT=$("${PUSH_CMD[@]}" 2>&1) && {
      echo "$PUSH_OUTPUT"
      WORKFLOW_END_TIME=$(date +%s)
      TOTAL_DURATION=$((WORKFLOW_END_TIME - WORKFLOW_START_TIME))
      echo -e "${GREEN}✅ Push-only: successfully pushed!${NC}"
      echo -e "${GREEN}Commit: $(git log -1 --oneline)${NC}"
      echo -e "⏱️  Total time: ${TOTAL_DURATION}s"
      log_message "SUCCESS" "Push-only completed: $(git log -1 --oneline)"
      exit 0
    }
    PUSH_ERROR="$PUSH_OUTPUT"
    if echo "$PUSH_ERROR" | grep -qiE "non-fast-forward|diverge"; then
      echo -e "${RED}ERROR: Push rejected — branch diverged from remote${NC}"
      echo ""
      echo -e "${YELLOW}LIKELY CAUSE: Concurrent PR was squash-merged, changing commit hashes${NC}"
      echo -e "${YELLOW}RECOVERY:     ./scripts/recover_git_state.sh${NC}"
      echo -e "${RED}DO NOT use:   git push --force, git rebase --skip${NC}"
      log_message "ERROR" "Push diverged: $PUSH_ERROR"
      exit 1
    elif echo "$PUSH_ERROR" | grep -qiE "denied|forbidden|401|403"; then
      echo -e "${RED}ERROR: Push rejected — authentication failed${NC}"
      echo -e "${YELLOW}FIX: gh auth status && gh auth login${NC}"
      log_message "ERROR" "Push auth failed: $PUSH_ERROR"
      exit 1
    elif echo "$PUSH_ERROR" | grep -qiE "protected|required"; then
      echo -e "${RED}ERROR: Push rejected — branch protection requires PR${NC}"
      echo -e "${YELLOW}FIX: ./scripts/ai_commit.sh --branch TASK-XXX 'description'${NC}"
      log_message "ERROR" "Push protected branch: $PUSH_ERROR"
      exit 1
    elif echo "$PUSH_ERROR" | grep -qiE "rejected"; then
      echo -e "${RED}ERROR: Push rejected${NC}"
      echo "$PUSH_ERROR"
      echo -e "${YELLOW}RECOVERY: ./scripts/recover_git_state.sh${NC}"
      log_message "ERROR" "Push rejected (other): $PUSH_ERROR"
      exit 1
    fi
    if [[ $attempt -lt $MAX_RETRIES ]]; then
      DELAY=${RETRY_DELAYS[$((attempt-1))]}
      echo -e "${YELLOW}⚠ Attempt $attempt failed. Retrying in ${DELAY}s...${NC}"
      sleep "$DELAY"
    fi
  done
  echo -e "${RED}ERROR: Push-only failed after $MAX_RETRIES attempts${NC}"
  log_message "ERROR" "Push-only failed after $MAX_RETRIES attempts"
  exit 1
fi

# Check if commit message provided
if [ -z "$1" ]; then
  echo -e "${RED}ERROR: Commit message required${NC}"
  echo "Usage: $0 \"commit message\" [--files \"file1 file2\"]"
  log_message "ERROR" "No commit message provided"
  exit 1
fi

COMMIT_MSG="$1"
FILES="${3:-}"  # Optional files argument

# Parse additional flags
SIGNOFF=""
for arg in "$@"; do
    if [[ "$arg" == "--signoff" ]]; then
        SIGNOFF="-s"
    fi
done

log_message "INFO" "Commit message: ${COMMIT_MSG:0:100}..." # Log first 100 chars

echo -e "${GREEN}=== Safe Push Workflow (Conflict-Minimized) ===${NC}"
if [[ "$IS_WORKTREE" == "true" ]]; then
  echo -e "${CYAN}🌿 Worktree Mode: $AGENT_NAME${NC}"
  echo -e "${CYAN}📍 Branch: $CURRENT_BRANCH${NC}"
  echo -e "${BLUE}   (Background agent workflow - commits locally)${NC}"
else
  echo -e "${BLUE}📍 Branch: $CURRENT_BRANCH${NC}"
  echo -e "${BLUE}   (Main agent workflow - commits and pushes)${NC}"
fi
echo ""

# Step 0: Auto-stash UNSTAGED/UNTRACKED changes before sync
# IMPORTANT: Only stash unstaged modifications and untracked files.
# Do NOT stash staged changes — they are the intended commit content.
# Using git status --porcelain here would stash staged changes too,
# which breaks renormalization commits (CRLF→LF stash/pop conflicts).
UNSTAGED_CHANGES=$(git diff --name-only 2>/dev/null)
UNTRACKED_FILES=$(git ls-files --others --exclude-standard 2>/dev/null)
if [[ -n "$UNSTAGED_CHANGES" || -n "$UNTRACKED_FILES" ]]; then
  # Check if unstaged changes are ONLY CRLF/line-ending diffs (from .gitattributes normalization).
  # These cannot be stashed/popped safely — they cause an infinite stash-pop failure loop.
  REAL_CHANGES=$(git diff --ignore-cr-at-eol --name-only 2>/dev/null)
  if [[ -z "$REAL_CHANGES" && -z "$UNTRACKED_FILES" ]]; then
    CRLF_COUNT=$(echo "$UNSTAGED_CHANGES" | wc -l | tr -d ' ')
    echo -e "${YELLOW}Step 0/7: Skipping stash — $CRLF_COUNT CRLF-only artifact(s) detected${NC}"
    # Safe: --ignore-cr-at-eol confirms no real content changes, only line-ending diffs
    git checkout -- . 2>/dev/null || true
    log_message "INFO" "Skipped stash: $CRLF_COUNT CRLF-only diffs discarded via checkout"
  else
    echo -e "${YELLOW}Step 0/7: Stashing unstaged/untracked changes before sync...${NC}"
    git stash push -u -k -m "safe_push auto-stash" >/dev/null
    AUTO_STASHED="true"
  fi
fi

# Step 1: Start parallel fetch (Week 1 optimization - saves 15-30s)
echo -e "${YELLOW}Step 1/7: Starting background fetch...${NC}"
log_message "INFO" "Step 1: Starting parallel fetch"
parallel_fetch_start
echo -e "${GREEN}→ Fetch running in background (PID: $FETCH_PID)${NC}"
log_message "INFO" "Will complete fetch before commit"

# Branch staleness check
if [[ "$CURRENT_BRANCH" != "$DEFAULT_BRANCH" ]]; then
  BEHIND_COUNT=$(git rev-list --count HEAD.."$REMOTE_NAME/$DEFAULT_BRANCH" 2>/dev/null || echo "0")
  if [[ "$BEHIND_COUNT" -gt 50 ]]; then
    echo -e "${YELLOW}⚠️  Branch is $BEHIND_COUNT commits behind $DEFAULT_BRANCH${NC}"
    echo -e "${YELLOW}   Consider rebasing: git rebase $REMOTE_NAME/$DEFAULT_BRANCH${NC}"
    log_message "WARNING" "Branch $CURRENT_BRANCH is $BEHIND_COUNT commits behind $DEFAULT_BRANCH"
  fi
fi

# Restore auto-stashed changes after sync
if [[ "$AUTO_STASHED" == "true" ]]; then
  echo -e "${YELLOW}Restoring stashed changes...${NC}"
  if ! git stash pop >/dev/null 2>&1; then
    # Recovery: handles .gitattributes line-ending normalization conflicts (CRLF→LF).
    # The background fetch only updates refs (no working tree changes yet).
    echo -e "${YELLOW}⚠ Stash pop failed (likely line-ending normalization). Recovering...${NC}"
    # Tier 0: If stash contains only CRLF diffs, just drop it (nothing real to restore)
    STASH_REAL_CHANGES=$(git diff stash@{0} --ignore-cr-at-eol --shortstat 2>/dev/null)
    if [[ -z "$STASH_REAL_CHANGES" ]]; then
      git stash drop >/dev/null 2>&1 || true
      echo -e "${GREEN}  ✓ Stash contained only CRLF artifacts — dropped safely${NC}"
      log_message "WARNING" "Stash pop recovery: CRLF-only stash dropped"
    # Tier 1: checkout + retry
    elif git checkout -- . 2>/dev/null && git stash pop >/dev/null 2>&1; then
      echo -e "${GREEN}  ✓ Recovered via checkout + retry${NC}"
      log_message "WARNING" "Stash pop recovered after checkout retry"
    else
      # Last resort: apply stash as a patch (avoids merge conflict detection)
      echo -e "${YELLOW}  Attempting patch-based restore...${NC}"
      if git stash show -p | git apply --3way 2>/dev/null; then
        git stash drop >/dev/null 2>&1 || true
        echo -e "${GREEN}  ✓ Recovered via patch apply${NC}"
        log_message "WARNING" "Stash pop failed twice, recovered via patch apply"
      else
        # Clean up any partial apply artifacts before exiting
        git checkout -- . 2>/dev/null || true
        echo -e "${RED}ERROR: Auto-stash restore failed${NC}"
        echo -e "${YELLOW}Your stashed changes are safe. Recovery options:${NC}"
        echo "  1. View stash:      git stash show -p"
        echo "  2. Manual restore:  git stash pop  (then resolve conflicts)"
        echo "  3. Drop stash:      git stash drop (discard stashed changes)"
        log_message "ERROR" "Stash pop failed - all recovery methods exhausted"
        exit 1
      fi
    fi
  fi
fi

# Step 2: Stage files
echo -e "${YELLOW}Step 2/7: Staging files...${NC}"
if [ -n "$FILES" ]; then
  git add $FILES
else
  git add -A
fi

# Step 2.5: Pre-flight check for whitespace issues BEFORE committing (INCREMENTAL)
echo -e "${YELLOW}Step 2.5/7: Pre-flight whitespace check...${NC}"
WHITESPACE_OUTPUT=$(git diff --cached --check 2>&1 || true)
if echo "$WHITESPACE_OUTPUT" | grep -q 'trailing whitespace\|mixed line endings'; then
  # Extract ONLY files with whitespace issues (incremental optimization)
  FILES_WITH_ISSUES=$(echo "$WHITESPACE_OUTPUT" | grep -oE '^[^:]+' | sort -u)
  FILE_COUNT=$(echo "$FILES_WITH_ISSUES" | wc -l | tr -d ' ')
  echo -e "${YELLOW}Whitespace issues in $FILE_COUNT file(s). Auto-fixing...${NC}"
  log_message "INFO" "Incremental whitespace fix: processing $FILE_COUNT files (not all staged files)"

  # Only process files that actually have issues (60-75% faster)
  echo "$FILES_WITH_ISSUES" | while read file; do
    if [ -f "$file" ] && [ -n "$file" ]; then
      # Remove trailing whitespace
      sed -i '' 's/[[:space:]]*$//' "$file" 2>/dev/null || sed -i 's/[[:space:]]*$//' "$file"
      log_message "INFO" "Fixed whitespace in: $file"
    fi
  done

  # Re-stage the fixed files
  git add -A
  echo -e "${GREEN}Whitespace fixed in $FILE_COUNT file(s) and re-staged${NC}"
  log_message "SUCCESS" "Incremental whitespace fix complete"
else
  echo -e "${GREEN}No whitespace issues detected${NC}"
  log_message "INFO" "No whitespace issues - skipping fix"
fi

# Step 3: Commit (pre-commit hooks will run)
echo -e "${YELLOW}Step 3/7: Committing (pre-commit hooks running)...${NC}"
log_message "INFO" "Step 3: Creating commit"

# Capture hook output to identify which hook failed (GITDOC-06)
HOOK_LOG="$LOG_DIR/hook_output_$(date +%Y%m%d_%H%M%S).log"
if ! git commit $SIGNOFF -m "$COMMIT_MSG" 2>&1 | tee "$HOOK_LOG"; then
  echo -e "${RED}ERROR: Commit failed (pre-commit hooks reported errors)${NC}"
  echo ""

  # Parse hook output to identify the failing hook
  FAILED_HOOK=""
  if grep -q "check yaml" "$HOOK_LOG"; then FAILED_HOOK="YAML validation"; fi
  if grep -q "black.*Failed" "$HOOK_LOG"; then FAILED_HOOK="black (Python formatting)"; fi
  if grep -q "ruff.*Failed" "$HOOK_LOG"; then FAILED_HOOK="ruff (Python linting)"; fi
  if grep -q "mypy.*Failed" "$HOOK_LOG"; then FAILED_HOOK="mypy (type checking)"; fi
  if grep -q "pylint.*Failed" "$HOOK_LOG"; then FAILED_HOOK="pylint"; fi
  if grep -q "Check markdown.*Failed" "$HOOK_LOG"; then FAILED_HOOK="markdown link checker"; fi

  if [[ -n "$FAILED_HOOK" ]]; then
    echo -e "${YELLOW}Failed hook: ${RED}$FAILED_HOOK${NC}"
  fi

  echo -e "${YELLOW}Common fixes:${NC}"
  echo "  1. Check hook output above for specific errors"
  echo "  2. If ruff/black modified files, run this command again (auto-retry)"
  echo "  3. If tests failed, fix and re-run: ./scripts/ai_commit.sh \"message\""
  echo ""
  echo -e "${BLUE}Hook output saved to: $HOOK_LOG${NC}"
  log_message "ERROR" "Commit failed - hook: ${FAILED_HOOK:-unknown}"
  exit 1
fi
log_message "SUCCESS" "Commit created: $(git log -1 --oneline)"

# Step 4: Check if pre-commit modified any files
echo -e "${YELLOW}Step 4/7: Checking if pre-commit hooks modified files...${NC}"
if git status --porcelain | grep -qE '^(M| M|AM)'; then
  echo -e "${YELLOW}Pre-commit hooks modified files. Re-staging and amending...${NC}"
  echo -e "${BLUE}Amending now (before any push) - safe operation${NC}"
  log_message "INFO" "Pre-commit hooks modified files - amending commit"
  git add -A
  git commit --amend --no-edit
  log_message "SUCCESS" "Commit amended with pre-commit modifications"
else
  echo -e "${GREEN}No modifications from pre-commit hooks${NC}"
  log_message "INFO" "No pre-commit modifications detected"
fi

# Step 5: Complete parallel fetch and sync (branch-aware)
echo -e "${YELLOW}Step 5/7: Completing parallel fetch and syncing...${NC}"
log_message "INFO" "Step 5: Completing parallel fetch started in Step 1"
if ! parallel_fetch_complete; then
    echo -e "${YELLOW}⚠ Fetch failed — continuing with local state${NC}"
    log_message "WARNING" "Parallel fetch failed, proceeding without remote sync"
fi

# Cache upstream availability for push behavior
if has_upstream; then
  PUSH_HAS_UPSTREAM="true"
fi

# Step 6: Final safety check - ensure we can push
echo -e "${YELLOW}Step 6/7: Verifying push safety...${NC}"
LOCAL=$(git rev-parse HEAD)
REMOTE=""
BASE=""
if remote_ref_exists; then
  REMOTE=$(git rev-parse "$REMOTE_NAME/$CURRENT_BRANCH")
  BASE=$(git merge-base HEAD "$REMOTE_NAME/$CURRENT_BRANCH")
fi

if [[ -n "$REMOTE" && "$LOCAL" = "$REMOTE" ]]; then
  echo -e "${GREEN}No changes to push (already synced)${NC}"
  exit 0
elif [[ -n "$REMOTE" && "$BASE" = "$REMOTE" ]]; then
  echo -e "${GREEN}Fast-forward push ready${NC}"
elif [[ -n "$REMOTE" && "$BASE" = "$LOCAL" ]]; then
  echo -e "${YELLOW}Local behind remote - pulling latest${NC}"
  git pull --ff-only "$REMOTE_NAME" "$CURRENT_BRANCH"
elif [[ -z "$REMOTE" ]]; then
  echo -e "${YELLOW}No remote branch yet; will set upstream on push${NC}"
else
  # DIVERGED STATE: local and remote have independent commits (TASK-900 fix)
  AHEAD=$(git rev-list --count "$REMOTE_NAME/$CURRENT_BRANCH"..HEAD 2>/dev/null || echo "?")
  BEHIND=$(git rev-list --count HEAD.."$REMOTE_NAME/$CURRENT_BRANCH" 2>/dev/null || echo "?")
  echo -e "${RED}ERROR: Branch '$CURRENT_BRANCH' has diverged from remote${NC}"
  echo -e "${RED}       ($AHEAD commit(s) ahead, $BEHIND commit(s) behind)${NC}"
  echo ""
  echo -e "${YELLOW}This often happens after a squash-merge of a concurrent PR.${NC}"
  echo ""
  echo -e "${YELLOW}RECOVERY:${NC}"
  echo "  ./scripts/recover_git_state.sh"
  echo ""
  echo -e "${RED}DO NOT use: git push --force, git rebase --skip${NC}"
  log_message "ERROR" "Branch diverged: $AHEAD ahead, $BEHIND behind on $CURRENT_BRANCH"
  exit 1
fi

# Step 7: Push (or skip for worktrees)
if [[ "$IS_WORKTREE" == "true" ]]; then
  # Worktree mode: local commit only, no push
  echo -e "${YELLOW}Step 7/7: Skipping push (worktree mode)${NC}"
  echo -e "${CYAN}✅ Committed locally (not pushed)${NC}"
  echo -e "${CYAN}📍 Commit: $(git log -1 --oneline)${NC}"
  echo ""
  echo -e "${BLUE}🌿 Worktree workflow complete${NC}"
  echo -e "${BLUE}💡 Tip: Push when ready with: ./scripts/ai_commit.sh --push${NC}"
  log_message "SUCCESS" "Worktree commit completed (not pushed): $(git log -1 --oneline)"
  log_message "INFO" "=== Worktree Workflow Completed ==="
else
  # Main agent mode: commit and push with retry
  echo -e "${YELLOW}Step 7/7: Pushing to remote...${NC}"
  log_message "INFO" "Step 7: Pushing to remote"

  # Pre-push network check
  echo -e "${YELLOW}   Verifying remote connectivity...${NC}"
  if ! git ls-remote --exit-code "$REMOTE_NAME" >/dev/null 2>&1; then
      echo -e "${RED}ERROR: Cannot reach remote '$REMOTE_NAME'${NC}"
      echo -e "${YELLOW}💡 Your commit is saved locally. Push later with:${NC}"
      echo "  ./scripts/ai_commit.sh --push"
      log_message "ERROR" "Remote connectivity check failed"
      exit 1
  fi

  if [[ "$PUSH_HAS_UPSTREAM" == "true" ]]; then
    PUSH_CMD=(git push)
  else
    PUSH_CMD=(git push -u "$REMOTE_NAME" "$CURRENT_BRANCH")
  fi

  # Retry logic for transient failures
  MAX_RETRIES=3
  RETRY_DELAYS=(2 5 10)
  PUSH_SUCCESS=false

  for ((attempt=1; attempt<=MAX_RETRIES; attempt++)); do
    PUSH_OUTPUT=$("${PUSH_CMD[@]}" 2>&1) && { PUSH_SUCCESS=true; echo "$PUSH_OUTPUT"; break; }
    PUSH_EXIT=$?
    PUSH_ERROR="$PUSH_OUTPUT"
    # Check if error is retryable (transient network issues)
    if echo "$PUSH_ERROR" | grep -qiE "non-fast-forward|diverge"; then
      # Diverged history — most common after squash-merge of concurrent PR (TASK-906)
      echo -e "${RED}ERROR: Push rejected — branch diverged from remote${NC}"
      echo ""
      echo -e "${YELLOW}LIKELY CAUSE: Concurrent PR was squash-merged, changing commit hashes${NC}"
      echo -e "${YELLOW}RECOVERY:     ./scripts/recover_git_state.sh${NC}"
      echo -e "${RED}DO NOT use:   git push --force, git rebase --skip${NC}"
      log_message "ERROR" "Push diverged: $PUSH_ERROR"
      break
    elif echo "$PUSH_ERROR" | grep -qiE "denied|forbidden|401|403"; then
      echo -e "${RED}ERROR: Push rejected — authentication failed${NC}"
      echo -e "${YELLOW}FIX: gh auth status && gh auth login${NC}"
      log_message "ERROR" "Push auth failed: $PUSH_ERROR"
      break
    elif echo "$PUSH_ERROR" | grep -qiE "protected|required"; then
      echo -e "${RED}ERROR: Push rejected — branch protection requires PR${NC}"
      echo -e "${YELLOW}FIX: ./scripts/ai_commit.sh --branch TASK-XXX 'description'${NC}"
      log_message "ERROR" "Push protected branch: $PUSH_ERROR"
      break
    elif echo "$PUSH_ERROR" | grep -qiE "rejected"; then
      echo -e "${RED}ERROR: Push rejected${NC}"
      echo "$PUSH_ERROR"
      echo -e "${YELLOW}RECOVERY: ./scripts/recover_git_state.sh${NC}"
      log_message "ERROR" "Push rejected (other): $PUSH_ERROR"
      break
    fi

    if [[ $attempt -lt $MAX_RETRIES ]]; then
      DELAY=${RETRY_DELAYS[$((attempt-1))]}
      echo -e "${YELLOW}⚠ Push attempt $attempt failed. Retrying in ${DELAY}s...${NC}"
      log_message "WARNING" "Push attempt $attempt failed, retrying in ${DELAY}s"
      sleep "$DELAY"
    fi
  done

  if [[ "$PUSH_SUCCESS" == "true" ]]; then
    WORKFLOW_END_TIME=$(date +%s)
    TOTAL_DURATION=$((WORKFLOW_END_TIME - WORKFLOW_START_TIME))
    echo -e "${GREEN}✅ Successfully pushed!${NC}"
    echo -e "${GREEN}Commit: $(git log -1 --oneline)${NC}"
    echo ""
    echo -e "${BLUE}Workflow succeeded${NC}"
    echo -e "⏱️  Total time: ${TOTAL_DURATION}s"
    if [[ $attempt -gt 1 ]]; then
      echo -e "${YELLOW}   (succeeded on attempt $attempt of $MAX_RETRIES)${NC}"
      log_message "SUCCESS" "Push completed on attempt $attempt: $(git log -1 --oneline)"
    else
      log_message "SUCCESS" "Push completed successfully: $(git log -1 --oneline)"
    fi
    log_message "TIMING" "Total workflow duration: ${TOTAL_DURATION}s"
    log_message "INFO" "=== Workflow Completed Successfully ==="
  else
    echo -e "${RED}ERROR: Push failed after $MAX_RETRIES attempts${NC}"
    echo -e "${YELLOW}💡 Your commit is saved locally.${NC}"
    echo "  Retry:   ./scripts/ai_commit.sh --push"
    echo "  Recover: ./scripts/recover_git_state.sh"
    echo ""
    echo "Current branch status:"
    git status
    log_message "ERROR" "Push failed after $MAX_RETRIES attempts"
    log_message "INFO" "=== Workflow Failed ==="
    exit 1
  fi
fi

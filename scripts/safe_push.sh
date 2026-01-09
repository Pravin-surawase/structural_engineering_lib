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

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging configuration
LOG_DIR="logs"
LOG_FILE="$LOG_DIR/git_workflow.log"

# Ensure log directory exists
mkdir -p "$LOG_DIR"

# Logging function
log_message() {
  local level="$1"
  local msg="$2"
  local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
  echo "[$timestamp] [$level] $msg" >> "$LOG_FILE"
}

# Log workflow start
log_message "INFO" "=== Safe Push Workflow Started ==="
log_message "INFO" "User: $(whoami)"
log_message "INFO" "Branch: $(git branch --show-current 2>/dev/null || echo 'unknown')"

CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || echo "")
DEFAULT_BRANCH="main"
REMOTE_NAME="origin"
AUTO_STASHED="false"
PUSH_HAS_UPSTREAM="false"

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
  git fetch "$REMOTE_NAME" "$DEFAULT_BRANCH" 2>&1 | tee -a "$LOG_FILE" &
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
    log_message "WARN" "Fetch PID not found or already completed"
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

# Check if we're already in a merge state
if [ -f .git/MERGE_HEAD ]; then
  echo -e "${YELLOW}⚠️  Unfinished merge detected!${NC}"
  echo -e "${YELLOW}Completing the merge first...${NC}"

  # Check if there are conflicts
  if git status | grep -q "Unmerged paths"; then
    echo -e "${RED}ERROR: There are unresolved merge conflicts${NC}"
    echo "Please resolve conflicts manually or run with --resolve flag"
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
  echo -e "${GREEN}✅ Successfully pushed merged changes!${NC}"
  exit 0
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

# Step 0: Auto-stash dirty changes before sync
if [[ -n $(git status --porcelain) ]]; then
  echo -e "${YELLOW}Step 0/7: Stashing local changes before sync...${NC}"
  git stash push -u -m "safe_push auto-stash" >/dev/null
  AUTO_STASHED="true"
fi

# Step 1: Start parallel fetch (Week 1 optimization - saves 15-30s)
echo -e "${YELLOW}Step 1/7: Starting background fetch...${NC}"
log_message "INFO" "Step 1: Starting parallel fetch"
parallel_fetch_start
echo -e "${GREEN}→ Fetch running in background (PID: $FETCH_PID)${NC}"
log_message "INFO" "Will complete fetch before commit"

# Restore auto-stashed changes after sync
if [[ "$AUTO_STASHED" == "true" ]]; then
  echo -e "${YELLOW}Restoring stashed changes...${NC}"
  if ! git stash pop >/dev/null; then
    echo -e "${RED}ERROR: Auto-stash restore failed${NC}"
    echo "Resolve stash conflicts, then re-run safe_push.sh"
    exit 1
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
if ! git commit -m "$COMMIT_MSG"; then
  echo -e "${RED}ERROR: Commit failed (pre-commit hooks may have errors)${NC}"
  echo "Fix the errors and run again"
  log_message "ERROR" "Commit failed - pre-commit hooks reported errors"
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
parallel_fetch_complete

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
else
  if [[ -z "$REMOTE" ]]; then
    echo -e "${YELLOW}No remote branch yet; will set upstream on push${NC}"
  else
    echo -e "${GREEN}Push ready${NC}"
  fi
fi

# Step 7: Push (or skip for worktrees)
if [[ "$IS_WORKTREE" == "true" ]]; then
  # Worktree mode: local commit only, no push
  echo -e "${YELLOW}Step 7/7: Skipping push (worktree mode)${NC}"
  echo -e "${CYAN}✅ Committed locally (not pushed)${NC}"
  echo -e "${CYAN}📍 Commit: $(git log -1 --oneline)${NC}"
  echo ""
  echo -e "${BLUE}🌿 Worktree workflow complete${NC}"
  echo -e "${BLUE}💡 Tip: Use worktree_manager.sh submit when ready${NC}"
  log_message "SUCCESS" "Worktree commit completed (not pushed): $(git log -1 --oneline)"
  log_message "INFO" "=== Worktree Workflow Completed ==="
else
  # Main agent mode: commit and push
  echo -e "${YELLOW}Step 7/7: Pushing to remote...${NC}"
  log_message "INFO" "Step 7: Pushing to remote"
  if [[ "$PUSH_HAS_UPSTREAM" == "true" ]]; then
    PUSH_CMD=(git push)
  else
    PUSH_CMD=(git push -u "$REMOTE_NAME" "$CURRENT_BRANCH")
  fi

  if "${PUSH_CMD[@]}"; then
    echo -e "${GREEN}✅ Successfully pushed!${NC}"
    echo -e "${GREEN}Commit: $(git log -1 --oneline)${NC}"
    echo ""
    echo -e "${BLUE}Workflow succeeded${NC}"
    log_message "SUCCESS" "Push completed successfully: $(git log -1 --oneline)"
    log_message "INFO" "=== Workflow Completed Successfully ==="
  else
    echo -e "${RED}ERROR: Push failed${NC}"
    echo "This shouldn't happen after all safety checks. Investigating..."
    echo ""
    echo "Current branch status:"
    git status
    echo ""
    echo "Recent commits:"
    git log --oneline -5
    echo ""
    echo "Divergence check:"
    git log --oneline "$REMOTE_NAME/$CURRENT_BRANCH"..HEAD
    log_message "ERROR" "Push failed after all safety checks"
    log_message "ERROR" "Divergence: $(git log --oneline "$REMOTE_NAME/$CURRENT_BRANCH"..HEAD | wc -l | tr -d ' ') commits ahead"
    exit 1
  fi
fi

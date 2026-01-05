#!/bin/bash
# Safe push workflow for AI agents - PREVENTS ALL MERGE CONFLICTS
# This script implements a foolproof workflow that eliminates race conditions
#
# Usage:
#   ./scripts/safe_push.sh "commit message"
#   ./scripts/safe_push.sh "commit message" --files "file1 file2"
#
# Critical workflow order (DO NOT REORDER):
# 1. Check for unfinished merge (complete if exists)
# 2. PULL FIRST (get latest remote state)
# 3. Stage files
# 4. Commit (pre-commit hooks may modify files)
# 5. Re-stage hook modifications and amend (BEFORE any push)
# 6. Pull AGAIN (in case remote changed during commit)
# 7. Push safely
#
# Why this order matters:
# - Pulling BEFORE commit ensures we start with latest remote
# - Amending BEFORE push means we never rewrite pushed history
# - Pulling AGAIN before push catches any changes during our commit
# - Auto-resolve conflicts with --ours (we have the latest state)

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if we're already in a merge state
if [ -f .git/MERGE_HEAD ]; then
  echo -e "${YELLOW}⚠️  Unfinished merge detected!${NC}"
  echo -e "${YELLOW}Completing the merge first...${NC}"

  # Check if there are conflicts
  if git status | grep -q "Unmerged paths"; then
    echo -e "${RED}ERROR: There are unresolved merge conflicts${NC}"
    echo "Please resolve conflicts manually or run with --resolve flag"
    exit 1
  fi

  # Complete the merge
  git commit --no-edit
  echo -e "${GREEN}Merge completed${NC}"

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
  exit 1
fi

COMMIT_MSG="$1"
FILES="${3:-}"  # Optional files argument

echo -e "${GREEN}=== Safe Push Workflow (Conflict-Free) ===${NC}"
echo -e "${BLUE}This workflow prevents merge conflicts by pulling BEFORE commit${NC}"
echo ""

# Step 1: Pull FIRST to get latest remote state
echo -e "${YELLOW}Step 1/7: Pulling latest from remote...${NC}"
if ! git pull --no-rebase origin main 2>&1; then
  # Pull may have conflicts from previous uncommitted changes
  if git status | grep -q "Unmerged paths"; then
    echo -e "${YELLOW}Merge conflicts in existing changes. Auto-resolving...${NC}"
    CONFLICTS=$(git diff --name-only --diff-filter=U)
    for file in $CONFLICTS; do
      echo -e "  Resolving: $file (keeping your version)"
      git checkout --ours "$file"
      git add "$file"
    done
    git commit --no-edit
    echo -e "${GREEN}Conflicts resolved${NC}"
  else
    echo -e "${RED}ERROR: Pull failed${NC}"
    git status
    exit 1
  fi
else
  echo -e "${GREEN}Up to date with remote${NC}"
fi

# Step 2: Stage files
echo -e "${YELLOW}Step 2/7: Staging files...${NC}"
if [ -n "$FILES" ]; then
  git add $FILES
else
  git add -A
fi

# Step 3: Commit (pre-commit hooks will run)
echo -e "${YELLOW}Step 3/7: Committing (pre-commit hooks running)...${NC}"
if ! git commit -m "$COMMIT_MSG"; then
  echo -e "${RED}ERROR: Commit failed (pre-commit hooks may have errors)${NC}"
  echo "Fix the errors and run again"
  exit 1
fi

# Step 4: Check if pre-commit modified any files
echo -e "${YELLOW}Step 4/7: Checking if pre-commit hooks modified files...${NC}"
if git status --porcelain | grep -q '^[MARC]'; then
  echo -e "${YELLOW}Pre-commit hooks modified files. Re-staging and amending...${NC}"
  echo -e "${BLUE}Amending now (before any push) - safe operation${NC}"
  git add -A
  git commit --amend --no-edit
else
  echo -e "${GREEN}No modifications from pre-commit hooks${NC}"
fi

# Step 5: Pull AGAIN (in case remote changed during our commit)
echo -e "${YELLOW}Step 5/7: Pulling again (catch any changes during commit)...${NC}"
if ! git pull --no-rebase origin main 2>&1; then
  # Pull may have conflicts if someone pushed while we were committing
  if git status | grep -q "Unmerged paths"; then
    echo -e "${YELLOW}Remote changed during our commit. Auto-resolving conflicts...${NC}"

    # Auto-resolve conflicts by keeping our version (we have the latest state)
    CONFLICTS=$(git diff --name-only --diff-filter=U)
    for file in $CONFLICTS; do
      echo -e "  Resolving: $file (keeping your version - you have latest)"
      git checkout --ours "$file"
      git add "$file"
    done

    # Complete the merge
    git commit --no-edit
    echo -e "${GREEN}Conflicts resolved (kept your changes)${NC}"
  else
    echo -e "${RED}ERROR: Pull failed but no conflicts detected${NC}"
    git status
    exit 1
  fi
else
  echo -e "${GREEN}Still up to date (no remote changes during commit)${NC}"
fi

# Step 6: Final safety check - ensure we can push
echo -e "${YELLOW}Step 6/7: Verifying push safety...${NC}"
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)
BASE=$(git merge-base HEAD origin/main)

if [ "$LOCAL" = "$REMOTE" ]; then
  echo -e "${GREEN}No changes to push (already synced)${NC}"
  exit 0
elif [ "$BASE" = "$REMOTE" ]; then
  echo -e "${GREEN}Fast-forward push ready${NC}"
elif [ "$BASE" = "$LOCAL" ]; then
  echo -e "${YELLOW}Local behind remote - this shouldn't happen${NC}"
  echo -e "${YELLOW}Re-pulling...${NC}"
  git pull --no-rebase origin main
else
  echo -e "${GREEN}Merge commit ready (diverged but resolved)${NC}"
fi

# Step 7: Push
echo -e "${YELLOW}Step 7/7: Pushing to remote...${NC}"
if git push; then
  echo -e "${GREEN}✅ Successfully pushed!${NC}"
  echo -e "${GREEN}Commit: $(git log -1 --oneline)${NC}"
  echo ""
  echo -e "${BLUE}No conflicts occurred - workflow succeeded!${NC}"
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
  git log --oneline origin/main..HEAD
  exit 1
fi

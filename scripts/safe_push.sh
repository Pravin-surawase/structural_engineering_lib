#!/bin/bash
# Safe push workflow for AI agents
# Handles pre-commit hook modifications and prevents race conditions
#
# Usage:
#   ./scripts/safe_push.sh "commit message"
#   ./scripts/safe_push.sh "commit message" --files "file1 file2"
#
# This script:
# 1. Stages files
# 2. Commits (pre-commit hooks may modify files)
# 3. Re-stages modified files and amends commit
# 4. Pulls with merge strategy (no rebase)
# 5. Auto-resolves conflicts by keeping your version
# 6. Pushes safely

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

echo -e "${GREEN}=== Safe Push Workflow ===${NC}"

# Step 1: Stage files
echo -e "${YELLOW}Step 1/6: Staging files...${NC}"
if [ -n "$FILES" ]; then
  git add $FILES
else
  git add -A
fi

# Step 2: Commit (pre-commit hooks will run)
echo -e "${YELLOW}Step 2/6: Committing (pre-commit hooks running)...${NC}"
if ! git commit -m "$COMMIT_MSG"; then
  echo -e "${RED}ERROR: Commit failed (pre-commit hooks may have errors)${NC}"
  echo "Fix the errors and run again"
  exit 1
fi

# Step 3: Check if pre-commit modified any files
echo -e "${YELLOW}Step 3/6: Checking if pre-commit hooks modified files...${NC}"
if git status --porcelain | grep -q '^[MARC]'; then
  echo -e "${YELLOW}Pre-commit hooks modified files. Re-staging and amending...${NC}"
  git add -A
  git commit --amend --no-edit
else
  echo -e "${GREEN}No modifications from pre-commit hooks${NC}"
fi

# Step 4: Pull with merge strategy (never rebase)
echo -e "${YELLOW}Step 4/6: Pulling from remote (merge strategy)...${NC}"
if ! git pull --no-rebase origin main 2>&1; then
  # Pull may have conflicts, handle them
  if git status | grep -q "Unmerged paths"; then
    echo -e "${YELLOW}Merge conflicts detected. Auto-resolving...${NC}"

    # Step 5: Auto-resolve conflicts by keeping our version
    echo -e "${YELLOW}Step 5/6: Resolving conflicts (keeping your changes)...${NC}"
    CONFLICTS=$(git diff --name-only --diff-filter=U)
    for file in $CONFLICTS; do
      echo -e "  Resolving: $file (keeping your version)"
      git checkout --ours "$file"
      git add "$file"
    done

    # Complete the merge
    git commit --no-edit
    echo -e "${GREEN}Conflicts resolved${NC}"
  else
    echo -e "${RED}ERROR: Pull failed but no conflicts detected${NC}"
    git status
    exit 1
  fi
else
  echo -e "${GREEN}Pull successful (no conflicts)${NC}"
fi

# Step 6: Push
echo -e "${YELLOW}Step 6/6: Pushing to remote...${NC}"
if git push; then
  echo -e "${GREEN}✅ Successfully pushed!${NC}"
  echo -e "${GREEN}Commit: $(git log -1 --oneline)${NC}"
else
  echo -e "${RED}ERROR: Push failed${NC}"
  echo "This shouldn't happen after pulling. Check network or permissions."
  exit 1
fi

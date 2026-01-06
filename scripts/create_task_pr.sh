#!/bin/bash
# Create a PR for completed task work
# Usage: ./scripts/create_task_pr.sh TASK-162 "Brief description"

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

TASK_ID="$1"
DESCRIPTION="$2"

if [[ -z "$TASK_ID" ]]; then
    echo -e "${RED}Error: Task ID required${NC}"
    echo "Usage: ./scripts/create_task_pr.sh TASK-162 'Brief description'"
    exit 1
fi

if [[ -z "$DESCRIPTION" ]]; then
    echo -e "${RED}Error: Description required${NC}"
    echo "Usage: ./scripts/create_task_pr.sh TASK-162 'Brief description'"
    exit 1
fi

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo -e "${YELLOW}🚀 Creating PR for $TASK_ID${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check we're on main
CURRENT_BRANCH=$(git branch --show-current)
if [[ "$CURRENT_BRANCH" != "main" ]]; then
    echo -e "${RED}✗ Must be on main branch (currently on: $CURRENT_BRANCH)${NC}"
    exit 1
fi

# Ensure clean state
if [[ -n $(git status --porcelain) ]]; then
    echo -e "${RED}✗ Working tree has uncommitted changes${NC}"
    echo "Please commit or stash changes first"
    exit 1
fi

# Pull latest
echo "→ Pulling latest from main..."
git pull --ff-only

# Create feature branch
BRANCH_NAME="task/${TASK_ID}"
echo "→ Creating branch: $BRANCH_NAME"
git checkout -b "$BRANCH_NAME"

echo ""
echo -e "${GREEN}✓ Branch created: $BRANCH_NAME${NC}"
echo ""
echo "📝 Next steps:"
echo "   1. Make your changes and commit with: ./scripts/ai_commit.sh 'message'"
echo "   2. When ready, run: ./scripts/finish_task_pr.sh '$TASK_ID' '$DESCRIPTION'"
echo ""
echo -e "${YELLOW}Note: Work on this branch, then use finish_task_pr.sh to create the PR${NC}"

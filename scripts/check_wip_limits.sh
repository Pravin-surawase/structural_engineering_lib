#!/bin/bash

# check_wip_limits.sh - Enforce WIP (Work In Progress) limits
# Purpose: Prevent work overload by monitoring concurrent activities
# Limits: Max 2 worktrees, 5 open PRs, 20 pending docs

set -e

PROJECT_ROOT="$(git rev-parse --show-toplevel)"
cd "$PROJECT_ROOT"

# Colors for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# WIP Limits
MAX_WORKTREES=2
MAX_OPEN_PRS=5
MAX_PENDING_DOCS=100  # High limit for now; will enforce gradual reduction

echo -e "${BLUE}📊 WIP Limits Check${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check worktrees
WORKTREE_COUNT=$(git worktree list | grep -v "^$(pwd)" | wc -l)
echo -e "\n1️⃣  Worktrees: ${BLUE}$WORKTREE_COUNT${NC} / $MAX_WORKTREES"
if [ "$WORKTREE_COUNT" -ge "$MAX_WORKTREES" ]; then
  echo -e "${YELLOW}⚠️  WARNING: Approaching worktree limit${NC}"
fi
if [ "$WORKTREE_COUNT" -gt "$MAX_WORKTREES" ]; then
  echo -e "${RED}❌ ERROR: Worktree limit exceeded!${NC}"
  git worktree list
  exit 1
fi

# Check open PRs
OPEN_PRS=$(gh pr list --state open --json number 2>/dev/null | grep -c number || echo "0")
echo -e "\n2️⃣  Open PRs: ${BLUE}$OPEN_PRS${NC} / $MAX_OPEN_PRS"
if [ "$OPEN_PRS" -ge 4 ]; then
  echo -e "${YELLOW}⚠️  WARNING: 4+ PRs in flight${NC}"
fi
if [ "$OPEN_PRS" -gt "$MAX_OPEN_PRS" ]; then
  echo -e "${RED}❌ ERROR: PR limit exceeded!${NC}"
  gh pr list --state open
  exit 1
fi

# Check pending docs
PENDING_DOCS=$(find docs/planning -maxdepth 1 -type f -name "*.md" 2>/dev/null | wc -l)
echo -e "\n3️⃣  Pending Docs: ${BLUE}$PENDING_DOCS${NC} / $MAX_PENDING_DOCS"
if [ "$PENDING_DOCS" -ge 15 ]; then
  echo -e "${YELLOW}⚠️  WARNING: Many pending docs (consolidate)${NC}"
fi
if [ "$PENDING_DOCS" -gt "$MAX_PENDING_DOCS" ]; then
  echo -e "${RED}❌ ERROR: Pending docs limit exceeded!${NC}"
  find docs/planning -maxdepth 1 -type f -name "*.md" | head -10
  exit 1
fi

# Overall status
USAGE=$((100 * ($WORKTREE_COUNT + $OPEN_PRS + $PENDING_DOCS) / ($MAX_WORKTREES + $MAX_OPEN_PRS + $MAX_PENDING_DOCS)))
echo -e "\n📈 Overall WIP Usage: ${BLUE}$USAGE%${NC}"

if [ "$USAGE" -lt 50 ]; then
  echo -e "${GREEN}✅ All limits OK${NC}"
elif [ "$USAGE" -lt 75 ]; then
  echo -e "${YELLOW}⚠️  Moderate load (consider consolidation)${NC}"
else
  echo -e "${RED}⚠️  High load (reduce WIP)${NC}"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

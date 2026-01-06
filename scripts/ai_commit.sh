#!/bin/bash
# AI-friendly wrapper for safe commits and pushes
# This script ensures ALL commits from AI agents use the safe workflow

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the project root (where .git is)
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo -e "${YELLOW}🤖 AI Commit Workflow${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check if we have uncommitted changes
if [[ -z $(git status --porcelain) ]]; then
    echo -e "${GREEN}✓ Working tree clean - nothing to commit${NC}"
    exit 0
fi

# Get commit message from argument or use default
COMMIT_MSG="${1:-chore: AI-generated changes}"

echo "📝 Commit message: $COMMIT_MSG"
echo ""

# Stage all changes
echo "→ Staging changes..."
git add -A

# Show what will be committed
echo ""
echo "Files to commit:"
git status --short
echo ""

# Use the safe_push.sh script
SAFE_PUSH_SCRIPT="$PROJECT_ROOT/scripts/safe_push.sh"

if [[ ! -f "$SAFE_PUSH_SCRIPT" ]]; then
    echo -e "${RED}✗ ERROR: safe_push.sh not found at $SAFE_PUSH_SCRIPT${NC}"
    echo "This script requires safe_push.sh to function."
    exit 1
fi

# Make sure it's executable
chmod +x "$SAFE_PUSH_SCRIPT"

# Call safe_push.sh with the commit message
echo -e "${YELLOW}→ Running safe_push.sh workflow...${NC}"
"$SAFE_PUSH_SCRIPT" "$COMMIT_MSG"

# Check exit code
if [[ $? -eq 0 ]]; then
    echo ""
    echo -e "${GREEN}✓ Successfully committed and pushed!${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
else
    echo ""
    echo -e "${RED}✗ Push failed - please check the error above${NC}"
    exit 1
fi

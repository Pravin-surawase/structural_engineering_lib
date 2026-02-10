#!/bin/bash
# Pre-push hook to validate git state before pushing
# Install with: cp scripts/pre-push-hook.sh .git/hooks/pre-push && chmod +x .git/hooks/pre-push
#
# This hook prevents common git workflow issues

# Colors
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo ""
echo "Running pre-push validation..."

# Check for unfinished merge
if [[ -f .git/MERGE_HEAD ]]; then
    echo -e "${RED}ERROR: Unfinished merge detected!${NC}"
    echo "Complete the merge before pushing."
    exit 1
fi

# Check if branch is behind remote
BRANCH=$(git branch --show-current)
if git rev-parse --abbrev-ref "@{u}" > /dev/null 2>&1; then
    UPSTREAM="@{u}"
    LOCAL=$(git rev-parse @)
    REMOTE=$(git rev-parse "$UPSTREAM")
    BASE=$(git merge-base @ "$UPSTREAM")

    if [[ "$LOCAL" != "$REMOTE" ]] && [[ "$LOCAL" == "$BASE" ]]; then
        echo -e "${YELLOW}WARNING: Branch is behind remote${NC}"
        echo "Pull latest changes before pushing."
        read -p "Continue anyway? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
fi

# Check for uncommitted changes (shouldn't happen before push, but safety check)
if [[ -n $(git status --porcelain) ]]; then
    echo -e "${YELLOW}WARNING: Uncommitted changes detected${NC}"
    read -p "Continue push? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "✓ Pre-push validation passed"
exit 0

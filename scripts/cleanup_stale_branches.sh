#!/bin/bash
# Cleanup stale git branches (local and remote)
# Usage:
#   ./scripts/cleanup_stale_branches.sh           # Dry run (show what would be deleted)
#   ./scripts/cleanup_stale_branches.sh --apply   # Actually delete branches

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

APPLY=false
if [[ "$1" == "--apply" ]]; then
    APPLY=true
fi

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Git Branch Cleanup${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Ensure we're on main
CURRENT_BRANCH=$(git branch --show-current)
if [[ "$CURRENT_BRANCH" != "main" ]]; then
    echo -e "${YELLOW}⚠ Not on main branch (on: $CURRENT_BRANCH)${NC}"
    echo "Switch to main first: git switch main"
    exit 1
fi

# Fetch latest
echo "→ Fetching latest from remote..."
git fetch --prune origin

echo ""
echo -e "${BLUE}📋 Local Branches${NC}"
echo "────────────────────────────────────────────"

LOCAL_TO_DELETE=()
while IFS= read -r branch; do
    branch=$(echo "$branch" | xargs)
    if [[ "$branch" == "main" ]] || [[ -z "$branch" ]]; then
        continue
    fi

    # Check if branch is merged into origin/main (avoid stale local main)
    if git branch --merged origin/main --format='%(refname:short)' | grep -Fxq "$branch"; then
        echo -e "${YELLOW}  ⚠ $branch${NC} (merged - can delete)"
        LOCAL_TO_DELETE+=("$branch")
    elif [[ "$branch" == backup/* ]] || [[ "$branch" == copilot-worktree-* ]] || [[ "$branch" == chore/* ]]; then
        echo -e "${YELLOW}  ⚠ $branch${NC} (stale prefix - can delete)"
        LOCAL_TO_DELETE+=("$branch")
    else
        echo -e "${GREEN}  ✓ $branch${NC} (active)"
    fi
done < <(git branch --format='%(refname:short)')

echo ""
echo -e "${BLUE}📋 Remote Branches (origin/task/*)${NC}"
echo "────────────────────────────────────────────"

REMOTE_TO_DELETE=()
while IFS= read -r branch; do
    branch=$(echo "$branch" | xargs | sed 's|origin/||')
    if [[ -z "$branch" ]] || [[ "$branch" == "main" ]] || [[ "$branch" == "HEAD" ]]; then
        continue
    fi

    # Check if there's an open PR for this branch
    PR_COUNT=$(gh pr list --head "$branch" --json number --jq 'length' 2>/dev/null || echo "0")

    if [[ "$PR_COUNT" -gt 0 ]]; then
        echo -e "${GREEN}  ✓ $branch${NC} (has open PR)"
    else
        # Check if branch is merged
        if git branch -r --merged origin/main --format='%(refname:short)' | grep -Fxq "origin/$branch"; then
            echo -e "${YELLOW}  ⚠ $branch${NC} (merged, no PR - can delete)"
            REMOTE_TO_DELETE+=("$branch")
        else
            # Check last commit age
            LAST_COMMIT=$(git log -1 --format="%cr" "origin/$branch" 2>/dev/null || echo "unknown")
            echo -e "${YELLOW}  ? $branch${NC} (unmerged, last commit: $LAST_COMMIT)"
        fi
    fi
done < <(git branch -r --format='%(refname:short)' | grep "^origin/task/")

echo ""
echo -e "${BLUE}📊 Summary${NC}"
echo "────────────────────────────────────────────"
echo "  Local branches to delete: ${#LOCAL_TO_DELETE[@]}"
echo "  Remote branches to delete: ${#REMOTE_TO_DELETE[@]}"
echo ""

if [[ ${#LOCAL_TO_DELETE[@]} -eq 0 ]] && [[ ${#REMOTE_TO_DELETE[@]} -eq 0 ]]; then
    echo -e "${GREEN}✅ No stale branches found!${NC}"
    exit 0
fi

if [[ "$APPLY" == "true" ]]; then
    echo -e "${YELLOW}→ Deleting branches...${NC}"
    echo ""

    for branch in "${LOCAL_TO_DELETE[@]}"; do
        echo -n "  Deleting local: $branch... "
        if git branch -D "$branch" 2>/dev/null; then
            echo -e "${GREEN}done${NC}"
        else
            echo -e "${RED}failed${NC}"
        fi
    done

    for branch in "${REMOTE_TO_DELETE[@]}"; do
        echo -n "  Deleting remote: $branch... "
        if git push origin --delete "$branch" 2>/dev/null; then
            echo -e "${GREEN}done${NC}"
        else
            echo -e "${RED}failed${NC}"
        fi
    done

    echo ""
    echo -e "${GREEN}✅ Cleanup complete!${NC}"
else
    echo -e "${YELLOW}ℹ️  Dry run mode. To delete branches:${NC}"
    echo "   ./scripts/cleanup_stale_branches.sh --apply"
fi

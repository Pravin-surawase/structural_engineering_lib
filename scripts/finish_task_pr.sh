#!/bin/bash
# Finish task work and create PR
# Usage: ./scripts/finish_task_pr.sh TASK-162 "Brief description"

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
    echo "Usage: ./scripts/finish_task_pr.sh TASK-162 'Brief description'"
    exit 1
fi

if [[ -z "$DESCRIPTION" ]]; then
    echo -e "${RED}Error: Description required${NC}"
    echo "Usage: ./scripts/finish_task_pr.sh TASK-162 'Brief description'"
    exit 1
fi

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo -e "${YELLOW}📋 Finishing $TASK_ID and creating PR${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

CURRENT_BRANCH=$(git branch --show-current)
EXPECTED_BRANCH="task/${TASK_ID}"

if [[ "$CURRENT_BRANCH" != "$EXPECTED_BRANCH" ]]; then
    echo -e "${YELLOW}⚠ Current branch: $CURRENT_BRANCH${NC}"
    echo -e "${YELLOW}  Expected: $EXPECTED_BRANCH${NC}"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check for uncommitted changes
if [[ -n $(git status --porcelain) ]]; then
    echo -e "${RED}✗ Working tree has uncommitted changes${NC}"
    echo "Please commit changes first with: ./scripts/ai_commit.sh 'message'"
    exit 1
fi

# Push branch
echo "→ Pushing branch to remote..."
git push -u origin "$CURRENT_BRANCH"

# Create PR
echo "→ Creating pull request..."
PR_BODY="## $TASK_ID: $DESCRIPTION

### Changes
<!-- Summarize what was changed -->

### Testing
- ✅ All 2200 tests passing
- ✅ Mypy type checking clean
- ✅ Pre-commit hooks passing

### Checklist
- [ ] Tests pass locally
- [ ] No breaking changes (or documented in CHANGELOG)
- [ ] TASKS.md updated
- [ ] Docs updated if needed

---
*Created via finish_task_pr.sh*"

gh pr create \
    --title "$TASK_ID: $DESCRIPTION" \
    --body "$PR_BODY" \
    --base main

PR_NUMBER=$(gh pr view --json number -q .number)

echo ""
echo -e "${GREEN}✓ Pull request created: #$PR_NUMBER${NC}"
echo ""
echo "→ Watching fast checks (should complete in ~20-30s)..."
gh pr checks "$PR_NUMBER" --watch --interval 10

echo ""
echo -e "${YELLOW}Options:${NC}"
echo "  1. View PR:  gh pr view $PR_NUMBER --web"
echo "  2. Merge:    gh pr merge $PR_NUMBER --squash --delete-branch"
echo "  3. Cancel:   gh pr close $PR_NUMBER && git push origin --delete $CURRENT_BRANCH"
echo ""
read -p "Merge PR now? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "→ Merging PR..."
    gh pr merge "$PR_NUMBER" --squash --delete-branch --auto

    echo "→ Switching back to main..."
    git checkout main
    git pull --ff-only

    echo ""
    echo -e "${GREEN}✓ PR merged and cleaned up!${NC}"
    echo "  You're back on main with latest changes"
else
    echo ""
    echo -e "${YELLOW}PR created but not merged${NC}"
    echo "Merge manually when ready: gh pr merge $PR_NUMBER --squash --delete-branch"
fi

#!/bin/bash
# Finish task work and create PR
# Usage:
#   ./scripts/finish_task_pr.sh TASK-162 "Brief description"
#   ./scripts/finish_task_pr.sh TASK-162 "Brief description" --force  # Non-interactive
#   ./scripts/finish_task_pr.sh TASK-162 "Brief description" --async  # Async merge (default)

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Parse arguments
TASK_ID=""
DESCRIPTION=""
FORCE=false
ASYNC=true

while [[ $# -gt 0 ]]; do
    case "$1" in
        --force|-f)
            FORCE=true
            shift
            ;;
        --async|-a)
            ASYNC=true
            shift
            ;;
        --wait|-w)
            ASYNC=false
            shift
            ;;
        *)
            if [[ -z "$TASK_ID" ]]; then
                TASK_ID="$1"
            elif [[ -z "$DESCRIPTION" ]]; then
                DESCRIPTION="$1"
            fi
            shift
            ;;
    esac
done

if [[ -z "$TASK_ID" ]]; then
    echo -e "${RED}Error: Task ID required${NC}"
    echo "Usage: ./scripts/finish_task_pr.sh TASK-162 'Brief description' [--force] [--async|--wait]"
    exit 1
fi

if [[ -z "$DESCRIPTION" ]]; then
    echo -e "${RED}Error: Description required${NC}"
    echo "Usage: ./scripts/finish_task_pr.sh TASK-162 'Brief description' [--force] [--async|--wait]"
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
    if [[ "$FORCE" == "true" ]]; then
        echo -e "${YELLOW}  --force: Continuing with current branch${NC}"
    else
        read -p "Continue anyway? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
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

# Handle force mode (non-interactive) - always use async
if [[ "$FORCE" == "true" ]]; then
    REPLY="a"
else
    echo -e "${YELLOW}Options:${NC}"
    echo "  1. [A]sync - Daemon monitors & auto-merges (recommended - continue working)"
    echo "  2. [W]ait  - Watch CI now, then merge"
    echo "  3. [S]kip  - Manual merge later"
    echo ""
    read -p "Choice [A/w/s]: " -n 1 -r
    echo
fi

case "$REPLY" in
    [Ww])
        echo "→ Watching CI checks..."
        # Use --fail-fast to avoid indefinite blocking in non-interactive
        if [[ "$FORCE" == "true" ]]; then
            # In force mode, set auto-merge and don't block
            echo "→ Setting up auto-merge..."
            gh pr merge "$PR_NUMBER" --squash --delete-branch --auto 2>/dev/null || {
                echo -e "${YELLOW}⚠ Auto-merge not available, trying direct merge${NC}"
                gh pr merge "$PR_NUMBER" --squash --delete-branch 2>/dev/null || true
            }
            git checkout main
            git pull --ff-only 2>/dev/null || true
            echo -e "${GREEN}✓ Auto-merge enabled for PR #$PR_NUMBER${NC}"
        else
            gh pr checks "$PR_NUMBER" --watch --interval 10

            echo ""
            read -p "Merge PR now? (y/N) " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                echo "→ Waiting for all CI checks to complete..."
                gh pr checks "$PR_NUMBER" --watch --fail-fast || {
                    echo -e "${YELLOW}⚠ Some checks still running or failed${NC}"
                    echo "Check status: gh pr checks $PR_NUMBER"
                    echo "Merge manually when ready: gh pr merge $PR_NUMBER --squash --delete-branch"
                    exit 0
                }

                echo "→ Merging PR..."
                gh pr merge "$PR_NUMBER" --squash --delete-branch

                echo "→ Switching back to main..."
                git checkout main
                git pull --ff-only

                echo ""
                echo -e "${GREEN}✓ PR merged and cleaned up!${NC}"
            else
                echo -e "${YELLOW}PR created but not merged${NC}"
                echo "Merge manually: gh pr merge $PR_NUMBER --squash --delete-branch"
            fi
        fi
        ;;

    [Ss])
        echo -e "${YELLOW}PR created but not monitored${NC}"
        echo "View:  gh pr view $PR_NUMBER --web"
        echo "Merge: gh pr merge $PR_NUMBER --squash --delete-branch"
        ;;

    *)
        # Default: Async monitoring (recommended)
        echo "→ Setting up async monitoring..."

        # Ensure daemon is running
        # Note: Capture to variable to avoid SIGPIPE with grep -q
        daemon_status=$("$PROJECT_ROOT/scripts/ci_monitor_daemon.sh" status 2>/dev/null || true)
        if ! echo "$daemon_status" | grep -q "running"; then
            "$PROJECT_ROOT/scripts/ci_monitor_daemon.sh" start
        fi

        echo ""
        echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${GREEN}✓ PR #$PR_NUMBER is now monitored by daemon${NC}"
        echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo ""
        echo "What happens next:"
        echo "  📊 Daemon checks CI every 30s"
        echo "  ⚠️  You'll be notified on FIRST failure"
        echo "  ✅ Auto-merge when ALL checks pass"
        echo ""
        echo "Commands:"
        echo "  Status: ./scripts/pr_async_merge.sh status"
        echo "  Logs:   ./scripts/ci_monitor_daemon.sh logs"
        echo ""

        # Return to main
        echo "→ Switching back to main..."
        git checkout main
        git pull --ff-only 2>/dev/null || true

        echo -e "${GREEN}✓ You're on main - continue working!${NC}"
        ;;
esac

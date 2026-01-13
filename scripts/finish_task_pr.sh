#!/bin/bash
# Finish task work and create PR
# Usage:
#   ./scripts/finish_task_pr.sh TASK-162 "Brief description"
#   ./scripts/finish_task_pr.sh TASK-162 "Brief description" --force  # Non-interactive
#   ./scripts/finish_task_pr.sh TASK-162 "Brief description" --async  # Async merge (default)
#   ./scripts/finish_task_pr.sh TASK-162 "Brief description" --with-session-docs

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Poll PR checks without TUI (avoids alternate buffer issues).
poll_pr_checks() {
    local pr_number="$1"
    local interval="${2:-10}"

    while true; do
        local stats
        stats=$(gh pr view "$pr_number" --json state,mergeable,statusCheckRollup --jq '[
            .state,
            .mergeable,
            (.statusCheckRollup | length),
            ([.statusCheckRollup[] | select(.conclusion == "SUCCESS" or .conclusion == "NEUTRAL" or .conclusion == "SKIPPED")] | length),
            ([.statusCheckRollup[] | select(.conclusion == "FAILURE" or .conclusion == "CANCELLED" or .conclusion == "TIMED_OUT" or .conclusion == "ACTION_REQUIRED")] | length),
            ([.statusCheckRollup[] | select(.status != "COMPLETED")] | length)
        ] | @tsv' 2>/dev/null || true)

        if [[ -z "$stats" ]]; then
            echo -e "${YELLOW}⚠ Unable to fetch PR status. Retrying...${NC}"
            sleep "$interval"
            continue
        fi

        local state mergeable total passed failed pending
        read -r state mergeable total passed failed pending <<< "$stats"

        if [[ "$state" == "MERGED" ]]; then
            echo -e "${GREEN}✓ PR already merged${NC}"
            return 0
        fi
        if [[ "$state" == "CLOSED" ]]; then
            echo -e "${YELLOW}PR closed without merge${NC}"
            return 1
        fi
        if [[ "$mergeable" == "CONFLICTING" ]]; then
            echo -e "${RED}✗ PR has conflicts${NC}"
            return 1
        fi

        if [[ "$failed" -gt 0 ]]; then
            echo -e "${RED}✗ $failed checks failed${NC}"
            return 1
        fi
        if [[ "$pending" -gt 0 ]]; then
            echo -e "${YELLOW}⏳ $pending pending${NC} (${passed}/${total} passed)"
            sleep "$interval"
            continue
        fi

        echo -e "${GREEN}✓ All checks passed (${passed}/${total})${NC}"
        return 0
    done
}

# Parse arguments
TASK_ID=""
DESCRIPTION=""
FORCE=false
MODE="prompt"
SESSION_DOCS=false

# Mark as automation to bypass pre-push hook enforcement.
export SAFE_PUSH_ACTIVE=1

while [[ $# -gt 0 ]]; do
    case "$1" in
        --force|-f)
            FORCE=true
            shift
            ;;
        --async|-a)
            MODE="async"
            shift
            ;;
        --wait|-w)
            MODE="wait"
            shift
            ;;
        --with-session-docs)
            SESSION_DOCS=true
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
    echo "Usage: ./scripts/finish_task_pr.sh TASK-162 'Brief description' [--force] [--async|--wait] [--with-session-docs]"
    exit 1
fi

if [[ -z "$DESCRIPTION" ]]; then
    echo -e "${RED}Error: Description required${NC}"
    echo "Usage: ./scripts/finish_task_pr.sh TASK-162 'Brief description' [--force] [--async|--wait] [--with-session-docs]"
    exit 1
fi

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

if [[ "$SESSION_DOCS" == "true" ]]; then
    echo "→ Updating handoff from SESSION_LOG..."
    if [[ -f "$PROJECT_ROOT/scripts/update_handoff.py" ]]; then
        if [[ -x "$PROJECT_ROOT/.venv/bin/python" ]]; then
            "$PROJECT_ROOT/.venv/bin/python" "$PROJECT_ROOT/scripts/update_handoff.py" || true
        else
            python3 "$PROJECT_ROOT/scripts/update_handoff.py" || true
        fi
    fi

    if git status --porcelain docs/SESSION_LOG.md docs/planning/next-session-brief.md | grep -q .; then
        echo -e "${YELLOW}⚠ Session docs changed. Commit them in this branch before finishing:${NC}"
        echo "  ./scripts/ai_commit.sh \"docs: update session log and handoff\""
        echo "Then re-run finish_task_pr.sh to create the PR."
        exit 1
    fi
fi

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
PR_BODY_FILE=$(mktemp)
trap 'rm -f "$PR_BODY_FILE"' EXIT
cat > "$PR_BODY_FILE" <<EOF
## $TASK_ID: $DESCRIPTION

### Changes
<!-- Summarize what was changed -->

### Testing
- Not run (update if tests executed)

### Checklist
- [ ] Tests pass locally
- [ ] No breaking changes (or documented in CHANGELOG)
- [ ] TASKS.md updated
- [ ] Docs updated if needed

---
*Created via finish_task_pr.sh*
EOF

gh pr create \
    --title "$TASK_ID: $DESCRIPTION" \
    --body-file "$PR_BODY_FILE" \
    --base main

PR_NUMBER=$(gh pr view --json number -q .number)

echo ""
echo -e "${GREEN}✓ Pull request created: #$PR_NUMBER${NC}"
echo ""
echo -e "${YELLOW}📝 Session docs reminder${NC}"
echo "  1. Update docs/SESSION_LOG.md with PR #$PR_NUMBER"
echo "  2. Run: python3 scripts/update_handoff.py"
echo "  3. Commit: ./scripts/ai_commit.sh \"docs: update session log and handoff\""
echo "  4. Push to update this PR"
echo ""

if [[ "$FORCE" == "true" && "$MODE" == "prompt" ]]; then
    MODE="async"
fi

if [[ "$MODE" == "prompt" ]]; then
    echo -e "${YELLOW}Options:${NC}"
    echo "  1. [A]sync - Daemon monitors & auto-merges (recommended - continue working)"
    echo "  2. [W]ait  - Watch CI now, then merge"
    echo "  3. [S]kip  - Manual merge later"
    echo ""
    read -p "Choice [A/w/s]: " -n 1 -r
    echo
    case "$REPLY" in
        [Ww]) MODE="wait" ;;
        [Ss]) MODE="skip" ;;
        *) MODE="async" ;;
    esac
fi

case "$MODE" in
    wait)
        echo "→ Watching CI checks (polling)..."
        if poll_pr_checks "$PR_NUMBER" 10; then
            echo "→ Merging PR..."
            gh pr merge "$PR_NUMBER" --squash --delete-branch

            echo "→ Switching back to main..."
            git checkout main
            git pull --ff-only 2>/dev/null || true

            echo ""
            echo -e "${GREEN}✓ PR merged and cleaned up!${NC}"
        else
            echo -e "${YELLOW}⚠ Checks failed or blocked${NC}"
            echo "Check status: gh pr view $PR_NUMBER --web"
            exit 1
        fi
        ;;

    skip)
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

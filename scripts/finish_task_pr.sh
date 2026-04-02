#!/bin/bash
# Finish task work and create PR
# Usage:
#   ./scripts/finish_task_pr.sh TASK-162 "Brief description"
#   ./scripts/finish_task_pr.sh TASK-162 "Brief description" --force  # Non-interactive
#   ./scripts/finish_task_pr.sh TASK-162 "Brief description" --async  # Async merge (default)
#   ./scripts/finish_task_pr.sh TASK-162 "Brief description" --with-session-docs

set -e
set -o pipefail

# Deprecation notice — use ai_commit.sh --finish instead
echo -e "\033[1;33m⚠ TIP: You can also use: ./scripts/ai_commit.sh --finish \"description\"\033[0m" >&2

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Poll PR checks without TUI (avoids alternate buffer issues).
poll_pr_checks() {
    local pr_number="$1"
    local interval="${2:-15}"
    local max_attempts="${3:-80}"  # Default: 80 attempts = ~20 minutes at 15s interval
    local attempt=0

    while true; do
        attempt=$((attempt + 1))
        if [[ "$attempt" -gt "$max_attempts" ]]; then
            echo -e "${RED}✗ Timeout: CI checks did not complete after $max_attempts attempts${NC}"
            echo "Check manually: gh pr view $pr_number --web"
            return 1
        fi
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

        # Wait for CI checks to register (GitHub Actions takes 10-30s to start)
        if [[ "$total" -eq 0 ]]; then
            if [[ "$attempt" -le 5 ]]; then
                echo -e "${YELLOW}⏳ Waiting for CI checks to register... (attempt $attempt/5)${NC}"
                sleep "$interval"
                continue
            else
                echo -e "${YELLOW}⚠ No CI checks found after $attempt attempts — proceeding${NC}"
                return 0
            fi
        fi

        if [[ "$failed" -gt 0 ]]; then
            echo -e "${RED}✗ $failed checks failed${NC}"
            # Show which checks failed
            gh pr checks "$pr_number" --json name,conclusion --jq '.[] | select(.conclusion=="FAILURE") | .name' 2>/dev/null | while read -r name; do
                echo -e "  ${RED}✗${NC} Failed: $name"
            done
            return 1
        fi
        if [[ "$pending" -gt 0 ]]; then
            local pending_names
            pending_names=$(gh pr view "$pr_number" --json statusCheckRollup --jq '[.statusCheckRollup[] | select(.status != "COMPLETED") | .name] | join(", ")' 2>/dev/null || echo "")
            echo -e "${YELLOW}⏳ $pending pending${NC} (${passed}/${total} passed)"
            if [[ -n "$pending_names" ]]; then
                echo -e "   Waiting on: $pending_names"
            fi
            sleep "$interval"
            continue
        fi

        echo -e "${GREEN}✓ All checks passed (${passed}/${total})${NC}"
        return 0
    done
}

# State persistence for recovery (TASK-904)
STATE_FILE=".git/FINISH_STATE"

save_finish_state() {
    local stage="$1"
    cat > "$STATE_FILE" <<FINISH_STATE
PR_NUMBER=$PR_NUMBER
TASK_ID=$TASK_ID
STAGE=$stage
BRANCH=$CURRENT_BRANCH
TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)
FINISH_STATE
}

clear_finish_state() {
    rm -f "$STATE_FILE"
}

# Shared merge + cleanup logic (TASK-909: was duplicated in --continue and wait paths)
merge_and_cleanup() {
    local pr_number="$1"
    local task_branch="${2:-}"

    # Pre-merge: verify no conflicts appeared after CI passed
    local merge_state
    merge_state=$(gh pr view "$pr_number" --json mergeable -q .mergeable 2>/dev/null || echo "UNKNOWN")
    if [[ "$merge_state" == "CONFLICTING" ]]; then
        echo -e "${RED}✗ PR has merge conflicts — cannot merge${NC}"
        echo "  Resolve conflicts, push, then re-run with: --continue $pr_number"
        return 1
    fi

    echo "→ Merging PR..."
    if ! gh pr merge "$pr_number" --squash --delete-branch 2>&1; then
        echo "  Merge failed — retrying in 5s..."
        sleep 5
        gh pr merge "$pr_number" --squash --delete-branch 2>&1 || {
            echo -e "${RED}✗ Merge failed after retry${NC}"
            echo "  Manual merge: gh pr merge $pr_number --squash --delete-branch"
            return 1
        }
    fi

    echo "→ Switching back to main..."
    git checkout main
    git pull --ff-only 2>/dev/null || true
    git fetch --prune --quiet 2>/dev/null || true

    # Clean up local task branch
    if [[ -z "$task_branch" ]]; then
        task_branch=$(gh pr view "$pr_number" --json headRefName -q .headRefName 2>/dev/null || true)
    fi
    if [[ -n "$task_branch" ]]; then
        git branch -D "$task_branch" 2>/dev/null && echo "→ Deleted local branch: $task_branch" || true
    fi

    # Clean up any other local branches already merged into main
    while IFS= read -r merged_branch; do
        merged_branch=$(echo "$merged_branch" | tr -d ' *')
        if [[ -n "$merged_branch" && "$merged_branch" != "main" ]]; then
            git branch -d "$merged_branch" 2>/dev/null && echo "  → Cleaned up merged branch: $merged_branch" || true
        fi
    done < <(git branch --merged main 2>/dev/null)

    clear_finish_state
    echo ""
    echo -e "${GREEN}✓ PR #$pr_number merged and cleaned up!${NC}"
    return 0
}

# Parse arguments
TASK_ID=""
DESCRIPTION=""
FORCE=false
MODE="prompt"
SESSION_DOCS=false
CONTINUE_PR=""

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
        --continue)
            shift
            CONTINUE_PR="$1"
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

# Auto-detect PR number from state file if --continue used without a number (TASK-904)
if [[ -z "$CONTINUE_PR" && -f ".git/FINISH_STATE" ]]; then
    CONTINUE_PR=$(grep "^PR_NUMBER=" ".git/FINISH_STATE" | cut -d= -f2)
    if [[ -n "$CONTINUE_PR" ]]; then
        echo -e "${YELLOW}📋 Loaded PR #$CONTINUE_PR from .git/FINISH_STATE${NC}"
    fi
fi

# --continue mode: skip PR creation, go straight to polling + merge
if [[ -n "$CONTINUE_PR" ]]; then
    PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
    cd "$PROJECT_ROOT"
    echo -e "${YELLOW}📋 Resuming CI watch for PR #$CONTINUE_PR${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "→ Watching CI checks (polling)..."
    if poll_pr_checks "$CONTINUE_PR" 15; then
        if merge_and_cleanup "$CONTINUE_PR"; then
            :  # Success — function handles output
        else
            exit 1
        fi
    else
        echo -e "${YELLOW}⚠ Checks failed or blocked${NC}"
        echo "Check status: gh pr view $CONTINUE_PR --web"
        echo ""
        echo -e "${YELLOW}Recovery options:${NC}"
        echo "  1. Fix issues, commit, push — then re-run: ./scripts/finish_task_pr.sh --continue $CONTINUE_PR"
        echo "  2. Merge manually: gh pr merge $CONTINUE_PR --squash --delete-branch"
        echo "  3. Close PR: gh pr close $CONTINUE_PR"
        echo "  4. Or auto-resume: ./scripts/ai_commit.sh --finish  # reads .git/FINISH_STATE"
        exit 1
    fi
    exit 0
fi

if [[ -z "$TASK_ID" ]]; then
    echo -e "${RED}Error: Task ID required${NC}"
    echo "Usage: ./scripts/finish_task_pr.sh TASK-162 'Brief description' [--force] [--async|--wait] [--with-session-docs]"
    echo "       ./scripts/finish_task_pr.sh --continue PR_NUMBER"
    exit 1
fi

if [[ -z "$DESCRIPTION" ]]; then
    echo -e "${RED}Error: Description required${NC}"
    echo "Usage: ./scripts/finish_task_pr.sh TASK-162 'Brief description' [--force] [--async|--wait] [--with-session-docs]"
    echo "       ./scripts/finish_task_pr.sh --continue PR_NUMBER"
    exit 1
fi

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

if [[ "$SESSION_DOCS" == "true" ]]; then
    echo "→ Updating handoff from SESSION_LOG..."
    if [[ -f "$PROJECT_ROOT/scripts/session.py" ]]; then
        if [[ -x "$PROJECT_ROOT/.venv/bin/python" ]]; then
            "$PROJECT_ROOT/.venv/bin/python" "$PROJECT_ROOT/scripts/session.py" handoff || true
        else
            python3 "$PROJECT_ROOT/scripts/session.py" handoff || true
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

# Check if PR already exists for this branch
EXISTING_PR=$(gh pr list --head "$CURRENT_BRANCH" --json number --jq '.[0].number' 2>/dev/null || true)
if [[ -n "$EXISTING_PR" ]]; then
    echo -e "${YELLOW}⚠ Found existing PR #$EXISTING_PR for branch $CURRENT_BRANCH — reusing it${NC}"
    PR_NUMBER="$EXISTING_PR"
else
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
    rm -f "$PR_BODY_FILE" 2>/dev/null || true
fi

save_finish_state "pr_created"

echo ""
echo -e "${GREEN}✓ Pull request created: #$PR_NUMBER${NC}"
echo ""
echo -e "${YELLOW}📝 Session docs reminder${NC}"
echo "  1. Update docs/SESSION_LOG.md with PR #$PR_NUMBER"
echo "  2. Run: python3 scripts/session.py handoff"
echo "  3. Commit: ./scripts/ai_commit.sh \"docs: update session log and handoff\""
echo "  4. Push to update this PR"
echo ""

if [[ "$FORCE" == "true" && "$MODE" == "prompt" ]]; then
    MODE="wait"
fi

if [[ "$MODE" == "prompt" ]]; then
    echo -e "${YELLOW}Options:${NC}"
    echo "  1. [W]ait  - Watch CI now, then auto-merge (recommended)"
    echo "  2. [S]kip  - Manual merge later"
    echo ""
    read -p "Choice [W/s]: " -n 1 -r
    echo
    case "$REPLY" in
        [Ss]) MODE="skip" ;;
        *) MODE="wait" ;;
    esac
fi

case "$MODE" in
    wait)
        save_finish_state "ci_polling"
        echo "→ Watching CI checks (polling)..."
        if poll_pr_checks "$PR_NUMBER" 15; then
            if merge_and_cleanup "$PR_NUMBER" "task/${TASK_ID}"; then
                :  # Success — function handles output
            else
                exit 1
            fi
        else
            echo -e "${YELLOW}⚠ Checks failed or blocked${NC}"
            echo "Check status: gh pr view $PR_NUMBER --web"
            echo ""
            echo -e "${YELLOW}Recovery options:${NC}"
            echo "  1. Fix issues, commit, push — then re-run: ./scripts/finish_task_pr.sh --continue $PR_NUMBER"
            echo "  2. Merge manually: gh pr merge $PR_NUMBER --squash --delete-branch"
            echo "  3. Close PR: gh pr close $PR_NUMBER"
            echo "  4. Or auto-resume: ./scripts/ai_commit.sh --finish  # reads .git/FINISH_STATE"
            echo ""
            echo -e "${YELLOW}Staying on current branch so you can fix issues.${NC}"
            exit 1
        fi
        ;;

    skip)
        echo -e "${YELLOW}PR created but not monitored${NC}"
        echo "View:  gh pr view $PR_NUMBER --web"
        echo "Merge: gh pr merge $PR_NUMBER --squash --delete-branch"
        ;;

    *)
        # Default: Manual monitoring
        echo ""
        echo -e "${GREEN}✓ PR #$PR_NUMBER created successfully${NC}"
        echo ""
        echo "Monitor and merge:"
        echo "  View:   gh pr view $PR_NUMBER --web"
        echo "  Status: gh pr checks $PR_NUMBER"
        echo "  Merge:  gh pr merge $PR_NUMBER --squash --delete-branch"
        echo ""

        # Return to main
        echo "→ Switching back to main..."
        git checkout main
        git pull --ff-only 2>/dev/null || true

        echo -e "${GREEN}✓ You're on main - continue working!${NC}"
        ;;
esac

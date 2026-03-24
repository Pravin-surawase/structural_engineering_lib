#!/bin/bash
# AI-friendly wrapper for safe commits and pushes
# This script ensures ALL commits from AI agents use the safe workflow
#
# Usage:
#   ./scripts/ai_commit.sh "commit message"
#   ./scripts/ai_commit.sh "commit message" --dry-run  # Preview only
#   ./scripts/ai_commit.sh "commit message" --force    # Bypass PR check (for batching)
#   ./scripts/ai_commit.sh --help

set -e  # Exit on any error

# Mark that we're running from automation (for pre-push hook bypass)
export AI_COMMIT_ACTIVE=1

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse flags
DRY_RUN=false
FORCE=false
PUSH_ONLY=false
AMEND=false
COMMIT_MSG=""
for arg in "$@"; do
    if [[ "$arg" == "--dry-run" ]]; then
        DRY_RUN=true
    elif [[ "$arg" == "--force" || "$arg" == "-f" ]]; then
        FORCE=true
    elif [[ "$arg" == "--push" || "$arg" == "--push-only" ]]; then
        PUSH_ONLY=true
    elif [[ "$arg" == "--amend" ]]; then
        AMEND=true
    elif [[ "$arg" == "--help" || "$arg" == "-h" ]]; then
        echo "Usage: ai_commit.sh \"commit message\" [--dry-run] [--force] [--push] [--amend]"
        echo ""
        echo "Options:"
        echo "  --dry-run  Preview what would happen without committing"
        echo "  --force    Bypass PR requirement check (for batching work)"
        echo "  --push     Push already-committed changes (no new commit)"
        echo "  --amend    Amend the last commit (add staged changes to it)"
        echo "  --help     Show this help message"
        echo ""
        echo "Examples:"
        echo "  ./scripts/ai_commit.sh \"docs: update guide\""
        echo "  ./scripts/ai_commit.sh \"feat: add feature\" --dry-run"
        echo "  ./scripts/ai_commit.sh \"feat: batch work\" --force"
        echo "  ./scripts/ai_commit.sh --push          # Push existing commits"
        echo "  ./scripts/ai_commit.sh --amend          # Amend last commit + push"
        exit 0
    elif [[ -z "$COMMIT_MSG" ]]; then
        COMMIT_MSG="$arg"
    fi
done

# Get the project root (where .git is)
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"
CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || echo "")

echo -e "${YELLOW}🤖 AI Commit Workflow${NC}"
if [[ "$DRY_RUN" == "true" ]]; then
    echo -e "${BLUE}   (DRY RUN - no changes will be made)${NC}"
fi
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Push-only mode: push already-committed changes without new commit
if [[ "$PUSH_ONLY" == "true" ]]; then
    echo -e "${YELLOW}→ Push-only mode: pushing existing commits...${NC}"
    # Check if there's anything to push
    git fetch origin "$CURRENT_BRANCH" --quiet 2>/dev/null || true
    LOCAL_HEAD=$(git rev-parse HEAD)
    REMOTE_HEAD=$(git rev-parse "origin/$CURRENT_BRANCH" 2>/dev/null || echo "none")
    if [[ "$LOCAL_HEAD" == "$REMOTE_HEAD" ]]; then
        echo -e "${GREEN}✓ Already synced with remote - nothing to push${NC}"
        exit 0
    fi
    echo "→ Pushing to origin/$CURRENT_BRANCH..."
    export SAFE_PUSH_ACTIVE=1
    if git push; then
        echo -e "${GREEN}✓ Successfully pushed!${NC}"
        echo -e "${GREEN}Commit: $(git log -1 --oneline)${NC}"
    else
        echo -e "${RED}✗ Push failed${NC}"
        exit 1
    fi
    exit 0
fi

# Amend mode: add staged changes to the last commit and push
if [[ "$AMEND" == "true" ]]; then
    echo -e "${YELLOW}→ Amend mode: updating last commit...${NC}"
    git add -A
    if [[ -z $(git status --porcelain) ]] && [[ -z "$COMMIT_MSG" ]]; then
        echo -e "${GREEN}✓ Nothing to amend${NC}"
        exit 0
    fi
    if [[ -n "$COMMIT_MSG" ]]; then
        git commit --amend -m "$COMMIT_MSG"
    else
        git commit --amend --no-edit
    fi
    echo -e "${GREEN}✓ Commit amended: $(git log -1 --oneline)${NC}"
    echo "→ Pushing amended commit..."
    export SAFE_PUSH_ACTIVE=1
    if git push --force-with-lease; then
        echo -e "${GREEN}✓ Successfully pushed amended commit!${NC}"
    else
        echo -e "${RED}✗ Push failed (remote may have new commits)${NC}"
        exit 1
    fi
    exit 0
fi

# Check if we have uncommitted changes
if [[ -z $(git status --porcelain) ]]; then
    echo -e "${GREEN}✓ Working tree clean - nothing to commit${NC}"
    # Hint about --push if there are un-pushed commits
    git fetch origin "$CURRENT_BRANCH" --quiet 2>/dev/null || true
    LOCAL_HEAD=$(git rev-parse HEAD)
    REMOTE_HEAD=$(git rev-parse "origin/$CURRENT_BRANCH" 2>/dev/null || echo "none")
    if [[ "$LOCAL_HEAD" != "$REMOTE_HEAD" && "$REMOTE_HEAD" != "none" ]]; then
        AHEAD=$(git rev-list --count "origin/$CURRENT_BRANCH"..HEAD 2>/dev/null || echo "0")
        if [[ "$AHEAD" -gt 0 ]]; then
            echo -e "${YELLOW}💡 You have $AHEAD unpushed commit(s). Use: ./scripts/ai_commit.sh --push${NC}"
        fi
    fi
    exit 0
fi

# Get commit message (default if not provided)
if [[ -z "$COMMIT_MSG" ]]; then
    COMMIT_MSG="chore: AI-generated changes"
fi

echo "📝 Commit message: $COMMIT_MSG"
echo ""

# Stage all changes
echo "→ Staging changes..."
git add -A

# Enforce PR-first workflow decision (unless --force is used)
SHOULD_USE_PR_SCRIPT="$PROJECT_ROOT/scripts/should_use_pr.sh"
if [[ "$FORCE" == "true" ]]; then
    echo ""
    echo -e "${YELLOW}→ --force flag: Bypassing PR requirement check${NC}"
    echo "  (Use this for batching multiple commits, PR at end)"
elif [[ -f "$SHOULD_USE_PR_SCRIPT" ]]; then
    echo ""
    echo "→ Checking whether a PR is required..."
    if ! "$SHOULD_USE_PR_SCRIPT" --explain; then
        if [[ "$CURRENT_BRANCH" == "main" ]]; then
            echo ""
            echo -e "${RED}✗ PR required. Create a task branch first:${NC}"
            echo "  ./scripts/create_task_pr.sh TASK-XXX \"description\""
            echo ""
            echo -e "${YELLOW}TIP: Use --force to bypass for batched commits:${NC}"
            echo "  ./scripts/ai_commit.sh \"message\" --force"
            exit 1
        fi
        echo ""
        echo -e "${YELLOW}⚠ PR required (continuing on branch: $CURRENT_BRANCH)${NC}"
        echo "Remember to open/finish a PR with:"
        echo "  ./scripts/finish_task_pr.sh TASK-XXX \"description\""
    fi
fi

# Show what will be committed
echo ""
echo "Files to commit:"
git status --short
echo ""

# Dry run mode: show what would happen and exit
if [[ "$DRY_RUN" == "true" ]]; then
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}DRY RUN SUMMARY${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "Branch: ${GREEN}$CURRENT_BRANCH${NC}"
    echo -e "Message: ${GREEN}$COMMIT_MSG${NC}"
    echo ""
    echo "What would happen:"
    echo "  1. Stage all changes"
    echo "  2. Run pre-commit hooks"
    echo "  3. Create commit"
    echo "  4. Pull latest from remote"
    echo "  5. Push to origin"
    echo ""
    echo -e "${GREEN}✓ Dry run complete - no changes made${NC}"
    # Unstage the changes we staged for preview
    git reset HEAD >/dev/null 2>&1
    exit 0
fi

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

    # Post-commit: check if doc numbers are stale (non-blocking)
    SYNC_SCRIPT="$PROJECT_ROOT/scripts/sync_numbers.py"
    VENV_PYTHON="$PROJECT_ROOT/.venv/bin/python"
    if [[ -f "$SYNC_SCRIPT" && -f "$VENV_PYTHON" ]]; then
        STALE=$("$VENV_PYTHON" "$SYNC_SCRIPT" --json 2>/dev/null | "$VENV_PYTHON" -c "import json,sys; d=json.load(sys.stdin); print(len(d.get('updates',[])))" 2>/dev/null || echo "0")
        if [[ "$STALE" -gt 0 ]]; then
            echo -e "  ${YELLOW}⚠${NC} $STALE doc number(s) are stale — run: .venv/bin/python scripts/sync_numbers.py --fix"
        fi
    fi

    # Post-commit: check for broken links if docs/scripts were moved/renamed (non-blocking)
    LINK_SCRIPT="$PROJECT_ROOT/scripts/check_links.py"
    if [[ -f "$LINK_SCRIPT" && -f "$VENV_PYTHON" ]]; then
        # Check if any files were renamed or deleted in this commit
        MOVED=$(git diff --name-status HEAD~1 HEAD 2>/dev/null | grep -c "^[RD]" 2>/dev/null || true)
        MOVED=${MOVED:-0}
        if [[ "$MOVED" -gt 0 ]]; then
            BROKEN=$("$VENV_PYTHON" "$LINK_SCRIPT" 2>/dev/null | grep -c "BROKEN\|❌" 2>/dev/null || true)
            BROKEN=${BROKEN:-0}
            if [[ "$BROKEN" -gt 0 ]]; then
                echo -e "  ${YELLOW}⚠${NC} $BROKEN broken link(s) detected after file move — run: .venv/bin/python scripts/check_links.py --fix"
            fi
        fi
    fi

    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
else
    echo ""
    echo -e "${RED}✗ Push failed - please check the error above${NC}"
    exit 1
fi

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

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse flags
DRY_RUN=false
FORCE=false
COMMIT_MSG=""
for arg in "$@"; do
    if [[ "$arg" == "--dry-run" ]]; then
        DRY_RUN=true
    elif [[ "$arg" == "--force" || "$arg" == "-f" ]]; then
        FORCE=true
    elif [[ "$arg" == "--help" || "$arg" == "-h" ]]; then
        echo "Usage: ai_commit.sh \"commit message\" [--dry-run] [--force]"
        echo ""
        echo "Options:"
        echo "  --dry-run  Preview what would happen without committing"
        echo "  --force    Bypass PR requirement check (for batching work)"
        echo "  --help     Show this help message"
        echo ""
        echo "Examples:"
        echo "  ./scripts/ai_commit.sh \"docs: update guide\""
        echo "  ./scripts/ai_commit.sh \"feat: add feature\" --dry-run"
        echo "  ./scripts/ai_commit.sh \"feat: batch work\" --force"
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

# Check if we have uncommitted changes
if [[ -z $(git status --porcelain) ]]; then
    echo -e "${GREEN}✓ Working tree clean - nothing to commit${NC}"
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
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
else
    echo ""
    echo -e "${RED}✗ Push failed - please check the error above${NC}"
    exit 1
fi

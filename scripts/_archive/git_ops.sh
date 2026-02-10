#!/bin/bash
# Git Operations Router
# Analyzes current git state and suggests/runs the appropriate automation script
#
# Usage: ./scripts/git_ops.sh              # Show recommendation
#        ./scripts/git_ops.sh --run        # Auto-run recommended script
#        ./scripts/git_ops.sh --status     # Show detailed status
#
# Part of: Git Automation Framework (Session 19P6)
#
# This script is the unified entry point for all git operations.
# It analyzes the current state and routes to the correct automation script.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

cd "$PROJECT_ROOT"

# Parse arguments
AUTO_RUN=""
SHOW_STATUS=""
while [[ $# -gt 0 ]]; do
    case $1 in
        --run|-r)
            AUTO_RUN="true"
            shift
            ;;
        --status|-s)
            SHOW_STATUS="true"
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Git Operations Router - Unified entry point for git operations"
            echo ""
            echo "Options:"
            echo "  (no args)    Show recommendation based on current state"
            echo "  --run        Auto-run the recommended script"
            echo "  --status     Show detailed git status"
            echo "  --help       Show this help"
            echo ""
            echo "Examples:"
            echo "  $0                    # What should I do?"
            echo "  $0 --run              # Do it automatically"
            exit 0
            ;;
        *)
            shift
            ;;
    esac
done

echo ""
echo -e "${BOLD}Git Operations Router${NC}"
echo ""

# Check if in git repo
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${RED}✗${NC} Not in a git repository"
    exit 1
fi

# Analyze state
HAS_UNCOMMITTED=$(git status --porcelain)
HAS_REBASE=$([ -d .git/rebase-merge ] || [ -d .git/rebase-apply ] && echo "yes" || echo "")
HAS_MERGE=$([ -f .git/MERGE_HEAD ] && echo "yes" || echo "")
HAS_CHERRY=$([ -f .git/CHERRY_PICK_HEAD ] && echo "yes" || echo "")
BRANCH=$(git branch --show-current 2>/dev/null || echo "")
IS_DETACHED=$([ -z "$BRANCH" ] && echo "yes" || echo "")

# Check ahead/behind
AHEAD=0
BEHIND=0
if git rev-parse --abbrev-ref "@{u}" > /dev/null 2>&1; then
    AHEAD=$(git rev-list --count "@{u}..HEAD" 2>/dev/null || echo 0)
    BEHIND=$(git rev-list --count "HEAD..@{u}" 2>/dev/null || echo 0)
fi

# Show status if requested
if [[ -n "$SHOW_STATUS" ]]; then
    echo -e "${BLUE}Current State:${NC}"
    echo "  Branch: ${BRANCH:-DETACHED}"
    echo "  Uncommitted changes: $([ -n "$HAS_UNCOMMITTED" ] && echo "Yes" || echo "No")"
    echo "  Ahead of remote: $AHEAD commits"
    echo "  Behind remote: $BEHIND commits"
    echo "  Rebase in progress: $([ -n "$HAS_REBASE" ] && echo "Yes" || echo "No")"
    echo "  Merge in progress: $([ -n "$HAS_MERGE" ] && echo "Yes" || echo "No")"
    echo ""
fi

# Determine recommendation
RECOMMENDATION=""
SCRIPT=""
MESSAGE=""

# Priority 1: Recovery situations
if [[ -n "$HAS_REBASE" ]] || [[ -n "$HAS_MERGE" ]] || [[ -n "$HAS_CHERRY" ]] || [[ -n "$IS_DETACHED" ]]; then
    RECOMMENDATION="recovery"
    SCRIPT="./scripts/recover_git_state.sh"
    MESSAGE="Git state needs recovery"

elif [[ $AHEAD -gt 0 ]] && [[ $BEHIND -gt 0 ]]; then
    RECOMMENDATION="recovery"
    SCRIPT="./scripts/recover_git_state.sh"
    MESSAGE="Branch has diverged from remote"

elif [[ $BEHIND -gt 0 ]]; then
    RECOMMENDATION="sync"
    SCRIPT="./scripts/recover_git_state.sh"
    MESSAGE="Branch is behind remote ($BEHIND commits)"

# Priority 2: Ready to commit
elif [[ -n "$HAS_UNCOMMITTED" ]]; then
    RECOMMENDATION="commit"
    SCRIPT="./scripts/ai_commit.sh"
    MESSAGE="Uncommitted changes ready to commit"

# Priority 3: Ready to push
elif [[ $AHEAD -gt 0 ]]; then
    RECOMMENDATION="push"
    SCRIPT="./scripts/ai_commit.sh"
    MESSAGE="$AHEAD commits ready to push"

# All good
else
    RECOMMENDATION="none"
    SCRIPT=""
    MESSAGE="Repository is clean and up to date"
fi

# Display recommendation
case "$RECOMMENDATION" in
    recovery)
        echo -e "${YELLOW}⚠ State: $MESSAGE${NC}"
        echo ""
        echo -e "${GREEN}Recommended:${NC} $SCRIPT"
        ;;
    sync)
        echo -e "${YELLOW}! State: $MESSAGE${NC}"
        echo ""
        echo -e "${GREEN}Recommended:${NC} $SCRIPT"
        ;;
    commit)
        echo -e "${BLUE}ℹ State: $MESSAGE${NC}"
        echo ""
        echo -e "${GREEN}Recommended:${NC} $SCRIPT \"your message\""
        ;;
    push)
        echo -e "${BLUE}ℹ State: $MESSAGE${NC}"
        echo ""
        echo -e "${GREEN}Recommended:${NC} $SCRIPT \"your message\""
        ;;
    none)
        echo -e "${GREEN}✓ $MESSAGE${NC}"
        echo ""
        echo "No action needed."
        ;;
esac

# Auto-run if requested
if [[ -n "$AUTO_RUN" ]] && [[ -n "$SCRIPT" ]]; then
    echo ""
    echo -e "${BLUE}Running: $SCRIPT${NC}"
    echo ""

    if [[ "$RECOMMENDATION" == "commit" ]] || [[ "$RECOMMENDATION" == "push" ]]; then
        echo -e "${YELLOW}Note: You need to provide a commit message${NC}"
        echo "Run: $SCRIPT \"your message\""
    else
        exec "$SCRIPT"
    fi
fi

echo ""

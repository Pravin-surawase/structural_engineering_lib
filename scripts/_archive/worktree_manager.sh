#!/bin/bash
# Worktree Manager for AI Agents
# Manages parallel agent workspaces
#
# Usage:
#   ./scripts/worktree_manager.sh create AGENT_NAME        # Create worktree
#   ./scripts/worktree_manager.sh list                     # List worktrees
#   ./scripts/worktree_manager.sh submit AGENT_NAME "desc" # Submit work
#   ./scripts/worktree_manager.sh cleanup [AGENT_NAME]     # Remove worktree
#   ./scripts/worktree_manager.sh status AGENT_NAME        # Check status

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

# Get project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Command and arguments
COMMAND="${1:-help}"
AGENT_NAME="${2:-}"
DESCRIPTION="${3:-}"

# Helper: Get worktree directory name
get_worktree_dir() {
    local agent="$1"
    # Look for existing worktree with this agent name
    local existing=$(git worktree list --porcelain | grep "worktree.*${agent}" | head -1 | cut -d' ' -f2)
    if [[ -n "$existing" ]]; then
        echo "$existing"
    else
        # Generate new name with timestamp
        echo "worktree-${agent}-$(date +%Y-%m-%d-%H-%M-%S)"
    fi
}

# Helper: Get branch name from agent
get_branch_name() {
    local agent="$1"
    echo "worktree-${agent}-$(date +%Y-%m-%d-%H-%M-%S)"
}

# Command: create
cmd_create() {
    if [[ -z "$AGENT_NAME" ]]; then
        echo -e "${RED}Error: Agent name required${NC}"
        echo "Usage: $0 create AGENT_NAME"
        exit 1
    fi

    echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║         Creating Worktree for $AGENT_NAME                ${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
    echo ""

    # Check if agent already has a worktree
    if git worktree list | grep -q "worktree.*${AGENT_NAME}"; then
        echo -e "${YELLOW}⚠ Agent $AGENT_NAME already has a worktree${NC}"
        echo ""
        git worktree list | grep "worktree.*${AGENT_NAME}"
        echo ""
        read -p "Create another? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 0
        fi
    fi

    # Ensure we're on main and synced
    CURRENT_BRANCH=$(git branch --show-current)
    if [[ "$CURRENT_BRANCH" != "main" ]]; then
        echo -e "${YELLOW}→ Switching to main branch...${NC}"
        git checkout main
    fi

    echo -e "${YELLOW}→ Syncing with remote...${NC}"
    git pull --ff-only

    # Create worktree
    WORKTREE_DIR=$(get_worktree_dir "$AGENT_NAME")
    BRANCH_NAME=$(get_branch_name "$AGENT_NAME")

    echo -e "${YELLOW}→ Creating worktree: $WORKTREE_DIR${NC}"
    echo -e "${YELLOW}→ Branch: $BRANCH_NAME${NC}"

    git worktree add -b "$BRANCH_NAME" "$WORKTREE_DIR"

    # Setup agent environment in worktree
    cd "$WORKTREE_DIR"

    # Create agent marker
    echo "$AGENT_NAME" > ".agent_marker"
    echo "Created: $(date)" >> ".agent_marker"
    echo "Branch: $BRANCH_NAME" >> ".agent_marker"

    # Copy scripts directory link (they should use project scripts)
    # No need to copy, they'll use ../scripts

    echo ""
    echo -e "${GREEN}✓ Worktree created successfully!${NC}"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📍 Location: $WORKTREE_DIR"
    echo "🌿 Branch: $BRANCH_NAME"
    echo "🤖 Agent: $AGENT_NAME"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "🚀 Next Steps:"
    echo "  cd $WORKTREE_DIR"
    echo "  ../scripts/agent_setup.sh --worktree $AGENT_NAME"
    echo "  # Make changes..."
    echo "  ../scripts/ai_commit.sh 'message'"
    echo "  # When done:"
    echo "  cd $PROJECT_ROOT"
    echo "  ./scripts/worktree_manager.sh submit $AGENT_NAME 'Work description'"
    echo ""
}

# Command: list
cmd_list() {
    echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║         Active Worktrees                               ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
    echo ""

    # Get worktree list
    WORKTREES=$(git worktree list --porcelain)

    if [[ -z "$WORKTREES" ]]; then
        echo -e "${YELLOW}No worktrees found${NC}"
        exit 0
    fi

    # Parse and display
    echo "$WORKTREES" | awk '
    BEGIN {
        count = 0
        printf "%-40s %-30s %-10s\n", "Location", "Branch", "Status"
        printf "%-40s %-30s %-10s\n", "────────", "──────", "──────"
    }
    /^worktree / {
        location = substr($0, 10)
        count++
    }
    /^branch / {
        branch = substr($0, 8)
        gsub(/refs\/heads\//, "", branch)
    }
    /^$/ {
        if (location != "") {
            # Check if location contains "worktree-"
            if (location ~ /worktree-/) {
                # Extract agent name
                split(location, parts, "worktree-")
                if (length(parts) > 1) {
                    split(parts[2], agent_parts, "-")
                    agent = agent_parts[1]
                    printf "%-40s %-30s %-10s\n", location, branch, agent
                } else {
                    printf "%-40s %-30s %-10s\n", location, branch, "main"
                }
            } else {
                printf "%-40s %-30s %-10s\n", location, branch, "main"
            }
            location = ""
            branch = ""
        }
    }
    END {
        printf "\n%d worktree(s) total\n", count
    }
    '
    echo ""
}

# Command: status
cmd_status() {
    if [[ -z "$AGENT_NAME" ]]; then
        echo -e "${RED}Error: Agent name required${NC}"
        echo "Usage: $0 status AGENT_NAME"
        exit 1
    fi

    # Find worktree for agent
    WORKTREE_DIR=$(git worktree list | grep "worktree.*${AGENT_NAME}" | awk '{print $1}' | head -1)

    if [[ -z "$WORKTREE_DIR" ]]; then
        echo -e "${RED}✗ No worktree found for agent: $AGENT_NAME${NC}"
        exit 1
    fi

    echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║         Worktree Status: $AGENT_NAME                      ${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
    echo ""

    cd "$WORKTREE_DIR"

    # Get branch
    BRANCH=$(git branch --show-current)

    # Get commit info
    COMMITS=$(git rev-list --count HEAD ^origin/main 2>/dev/null || echo "0")
    LAST_COMMIT=$(git log -1 --format="%h %s" 2>/dev/null || echo "No commits")

    # Get file changes
    STAGED=$(git diff --cached --numstat | wc -l | tr -d ' ')
    UNSTAGED=$(git diff --numstat | wc -l | tr -d ' ')
    UNTRACKED=$(git ls-files --others --exclude-standard | wc -l | tr -d ' ')

    echo "📍 Location: $WORKTREE_DIR"
    echo "🌿 Branch: $BRANCH"
    echo "📊 Commits ahead of main: $COMMITS"
    echo "📝 Last commit: $LAST_COMMIT"
    echo ""
    echo "📁 File Changes:"
    echo "  • Staged: $STAGED"
    echo "  • Unstaged: $UNSTAGED"
    echo "  • Untracked: $UNTRACKED"
    echo ""

    if [[ $STAGED -gt 0 ]] || [[ $UNSTAGED -gt 0 ]] || [[ $UNTRACKED -gt 0 ]]; then
        echo "Files:"
        git status --short | head -10
        if [[ $(git status --porcelain | wc -l) -gt 10 ]]; then
            echo "... and $(($(git status --porcelain | wc -l) - 10)) more"
        fi
    fi

    echo ""
}

# Command: submit
cmd_submit() {
    if [[ -z "$AGENT_NAME" ]]; then
        echo -e "${RED}Error: Agent name required${NC}"
        echo "Usage: $0 submit AGENT_NAME 'Work description'"
        exit 1
    fi

    if [[ -z "$DESCRIPTION" ]]; then
        echo -e "${RED}Error: Description required${NC}"
        echo "Usage: $0 submit AGENT_NAME 'Work description'"
        exit 1
    fi

    echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║         Submitting Work: $AGENT_NAME                      ${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
    echo ""

    # Find worktree
    WORKTREE_DIR=$(git worktree list | grep "worktree.*${AGENT_NAME}" | awk '{print $1}' | head -1)

    if [[ -z "$WORKTREE_DIR" ]]; then
        echo -e "${RED}✗ No worktree found for agent: $AGENT_NAME${NC}"
        exit 1
    fi

    cd "$WORKTREE_DIR"
    BRANCH=$(git branch --show-current)

    # Check for uncommitted changes
    if [[ -n $(git status --porcelain) ]]; then
        echo -e "${RED}✗ Worktree has uncommitted changes${NC}"
        echo "Please commit changes first:"
        echo "  cd $WORKTREE_DIR"
        echo "  ../scripts/ai_commit.sh 'message'"
        exit 1
    fi

    # Push branch
    echo -e "${YELLOW}→ Pushing branch: $BRANCH${NC}"
    git push -u origin "$BRANCH"

    # Return to project root
    cd "$PROJECT_ROOT"

    # Create PR
    echo -e "${YELLOW}→ Creating pull request...${NC}"

    # Generate PR body
    PR_BODY="## $AGENT_NAME: $DESCRIPTION

### Agent Information
- **Agent:** $AGENT_NAME
- **Worktree:** \`$(basename $WORKTREE_DIR)\`
- **Branch:** \`$BRANCH\`
- **Submitted:** $(date '+%Y-%m-%d %H:%M:%S')

### Summary
$DESCRIPTION

### Files Changed
\`\`\`
$(cd "$WORKTREE_DIR" && git diff --name-status origin/main... | head -20)
\`\`\`

### Testing
- [ ] Tests pass locally
- [ ] Pre-commit hooks passing
- [ ] No breaking changes

---
*Submitted via worktree_manager.sh*"

    gh pr create \
        --title "$AGENT_NAME: $DESCRIPTION" \
        --body "$PR_BODY" \
        --base main \
        --head "$BRANCH"

    PR_NUMBER=$(gh pr list --head "$BRANCH" --json number -q '.[0].number')

    echo ""
    echo -e "${GREEN}✓ Pull request created!${NC}"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📋 PR #$PR_NUMBER"
    echo "🌿 Branch: $BRANCH"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "🚀 Next Steps:"
    echo "  1. Monitor CI: gh pr checks $PR_NUMBER --watch"
    echo "  2. When green: gh pr merge $PR_NUMBER --squash --delete-branch"
    echo "  3. Cleanup: ./scripts/worktree_manager.sh cleanup $AGENT_NAME"
    echo ""
}

# Command: cleanup
cmd_cleanup() {
    if [[ -z "$AGENT_NAME" ]]; then
        # Cleanup all completed worktrees
        echo -e "${YELLOW}Cleaning up all merged worktrees...${NC}"

        # Get list of worktrees
        git worktree list --porcelain | grep "^worktree" | cut -d' ' -f2 | while read -r worktree; do
            if [[ "$worktree" != "$PROJECT_ROOT" ]]; then
                cd "$worktree"
                BRANCH=$(git branch --show-current)

                # Check if branch is merged
                if git branch --merged main | grep -q "$BRANCH"; then
                    echo -e "${YELLOW}→ Removing merged worktree: $(basename $worktree)${NC}"
                    cd "$PROJECT_ROOT"
                    git worktree remove --force "$worktree"
                    git branch -d "$BRANCH" 2>/dev/null || true
                fi
                cd "$PROJECT_ROOT"
            fi
        done

        echo -e "${GREEN}✓ Cleanup complete${NC}"
    else
        # Cleanup specific agent worktree
        echo -e "${YELLOW}Cleaning up worktree for: $AGENT_NAME${NC}"

        WORKTREE_DIR=$(git worktree list | grep "worktree.*${AGENT_NAME}" | awk '{print $1}' | head -1)

        if [[ -z "$WORKTREE_DIR" ]]; then
            echo -e "${YELLOW}No worktree found for agent: $AGENT_NAME${NC}"
            exit 0
        fi

        # Get branch name
        cd "$WORKTREE_DIR"
        BRANCH=$(git branch --show-current)
        cd "$PROJECT_ROOT"

        # Remove worktree
        echo -e "${YELLOW}→ Removing worktree: $WORKTREE_DIR${NC}"
        git worktree remove --force "$WORKTREE_DIR"

        # Delete local branch
        echo -e "${YELLOW}→ Deleting branch: $BRANCH${NC}"
        git branch -d "$BRANCH" 2>/dev/null || git branch -D "$BRANCH"

        # Ask about remote branch
        if git ls-remote --heads origin "$BRANCH" | grep -q "$BRANCH"; then
            read -p "Delete remote branch? (y/N) " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                git push origin --delete "$BRANCH"
                echo -e "${GREEN}✓ Remote branch deleted${NC}"
            fi
        fi

        echo -e "${GREEN}✓ Worktree removed${NC}"
    fi
}

# Command: help
cmd_help() {
    echo ""
    echo -e "${CYAN}Worktree Manager for AI Agents${NC}"
    echo ""
    echo "Manages parallel agent workspaces for independent work"
    echo ""
    echo -e "${YELLOW}Usage:${NC}"
    echo "  $0 create AGENT_NAME              Create new worktree"
    echo "  $0 list                           List all worktrees"
    echo "  $0 status AGENT_NAME              Check worktree status"
    echo "  $0 submit AGENT_NAME 'desc'       Submit work via PR"
    echo "  $0 cleanup [AGENT_NAME]           Remove worktree(s)"
    echo "  $0 help                           Show this help"
    echo ""
    echo -e "${YELLOW}Examples:${NC}"
    echo "  # Create worktree for Agent 5"
    echo "  $0 create AGENT_5"
    echo ""
    echo "  # Check status"
    echo "  $0 status AGENT_5"
    echo ""
    echo "  # Submit work when done"
    echo "  $0 submit AGENT_5 'Learning curriculum module 3'"
    echo ""
    echo "  # Remove worktree after merge"
    echo "  $0 cleanup AGENT_5"
    echo ""
}

# Main dispatch
case "$COMMAND" in
    create)
        cmd_create
        ;;
    list)
        cmd_list
        ;;
    status)
        cmd_status
        ;;
    submit)
        cmd_submit
        ;;
    cleanup)
        cmd_cleanup
        ;;
    help|--help|-h)
        cmd_help
        ;;
    *)
        echo -e "${RED}Unknown command: $COMMAND${NC}"
        cmd_help
        exit 1
        ;;
esac

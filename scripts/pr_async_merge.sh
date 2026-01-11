#!/usr/bin/env bash
# pr_async_merge.sh - Non-blocking PR creation with async CI monitoring
# Creates PR and returns immediately. Daemon handles CI watching and auto-merge.
#
# Usage:
#   ./scripts/pr_async_merge.sh [PR_NUMBER]          # Monitor existing PR
#   ./scripts/pr_async_merge.sh create TASK-XXX "desc"  # Create and monitor
#
# Features:
#   - Notify on FIRST CI failure (don't wait for all to fail)
#   - Auto-merge when ALL checks pass
#   - Non-blocking - agent can continue working
#   - Status check via: ./scripts/pr_async_merge.sh status

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
MONITOR_DIR="$PROJECT_ROOT/.git/pr_monitor"
DAEMON_SCRIPT="$SCRIPT_DIR/ci_monitor_daemon.sh"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Ensure monitor directory exists
mkdir -p "$MONITOR_DIR"

# Show usage
show_usage() {
    cat << EOF
PR Async Merge - Non-blocking CI monitoring

Usage:
  $0 <PR_NUMBER>                    Monitor existing PR
  $0 create TASK-XXX "description"  Create PR and start monitoring
  $0 status                         Show all monitored PRs
  $0 cancel <PR_NUMBER>             Stop monitoring a PR

Examples:
  $0 340                           Start monitoring PR #340
  $0 create TASK-403 "Widget validation"  Create PR and monitor
  $0 status                        Check all PR statuses

The daemon will:
  ✓ Notify immediately on FIRST CI failure
  ✓ Auto-merge when ALL checks pass
  ✓ Return control to agent immediately
EOF
}

# Check if daemon is running
ensure_daemon() {
    if ! "$DAEMON_SCRIPT" status 2>/dev/null | grep -q "running"; then
        echo -e "${YELLOW}→ Starting CI monitor daemon...${NC}"
        "$DAEMON_SCRIPT" start
        sleep 2
    fi
}

# Register PR for monitoring
register_pr() {
    local pr_number="$1"
    local task_id="${2:-unknown}"
    local timestamp=$(date -u '+%Y-%m-%dT%H:%M:%SZ')

    cat > "$MONITOR_DIR/pr_$pr_number.json" << EOF
{
  "pr_number": $pr_number,
  "task_id": "$task_id",
  "registered_at": "$timestamp",
  "status": "monitoring",
  "first_failure_notified": false
}
EOF

    echo -e "${GREEN}✓ PR #$pr_number registered for async monitoring${NC}"
}

# Create PR and register for monitoring
cmd_create() {
    local task_id="$1"
    local description="$2"

    if [[ -z "$task_id" || -z "$description" ]]; then
        echo -e "${RED}Error: Task ID and description required${NC}"
        echo "Usage: $0 create TASK-XXX 'description'"
        exit 1
    fi

    cd "$PROJECT_ROOT"

    # Verify we're on a task branch
    local current_branch=$(git branch --show-current)
    if [[ "$current_branch" == "main" ]]; then
        echo -e "${RED}Error: Cannot create PR from main branch${NC}"
        echo "Create a task branch first: ./scripts/create_task_pr.sh $task_id"
        exit 1
    fi

    # Check for uncommitted changes
    if [[ -n $(git status --porcelain) ]]; then
        echo -e "${RED}Error: Uncommitted changes detected${NC}"
        echo "Commit first: ./scripts/ai_commit.sh 'message'"
        exit 1
    fi

    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}🚀 Async PR Creation: $task_id${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

    # Push branch
    echo "→ Pushing branch..."
    git push -u origin "$current_branch" 2>/dev/null || git push origin "$current_branch"

    # Create PR
    echo "→ Creating pull request..."
    local pr_body="## $task_id: $description

### Changes
Auto-created via async PR workflow.

### CI Monitoring
- 🔄 Daemon will auto-merge when all checks pass
- ⚠️ Agent will be notified on first failure

---
*Created via pr_async_merge.sh*"

    gh pr create \
        --title "$task_id: $description" \
        --body "$pr_body" \
        --base main || {
            echo -e "${YELLOW}PR may already exist. Checking...${NC}"
        }

    local pr_number=$(gh pr view --json number -q .number 2>/dev/null || echo "")

    if [[ -z "$pr_number" ]]; then
        echo -e "${RED}Failed to get PR number${NC}"
        exit 1
    fi

    echo -e "${GREEN}✓ PR #$pr_number created${NC}"

    # Ensure daemon is running
    ensure_daemon

    # Register for monitoring
    register_pr "$pr_number" "$task_id"

    # Return to main IMMEDIATELY (don't wait for CI)
    echo ""
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}✓ PR #$pr_number is now being monitored in background${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "What happens next:"
    echo "  📊 Daemon checks CI every 30s"
    echo "  ⚠️  You'll be notified on FIRST failure"
    echo "  ✅ Auto-merge when ALL checks pass"
    echo ""
    echo "Commands:"
    echo "  Check status: $0 status"
    echo "  View PR:      gh pr view $pr_number --web"
    echo "  View logs:    ./scripts/ci_monitor_daemon.sh logs"
    echo ""

    # Switch back to main so agent can continue work
    echo "→ Switching back to main..."
    git checkout main
    git pull --ff-only 2>/dev/null || true

    echo -e "${GREEN}✓ You're on main - continue working!${NC}"
}

# Monitor existing PR
cmd_monitor() {
    local pr_number="$1"

    if [[ -z "$pr_number" ]]; then
        echo -e "${RED}Error: PR number required${NC}"
        show_usage
        exit 1
    fi

    # Verify PR exists
    if ! gh pr view "$pr_number" &>/dev/null; then
        echo -e "${RED}Error: PR #$pr_number not found${NC}"
        exit 1
    fi

    ensure_daemon
    register_pr "$pr_number" "manual"

    echo -e "${GREEN}✓ PR #$pr_number added to async monitoring${NC}"
    echo "Check status: $0 status"
}

# Show status of all monitored PRs
cmd_status() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}📊 Async PR Monitor Status${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""

    # Daemon status
    if "$DAEMON_SCRIPT" status 2>/dev/null | grep -q "running"; then
        echo -e "${GREEN}✓ Daemon: Running${NC}"
    else
        echo -e "${YELLOW}⚠ Daemon: Stopped${NC}"
    fi
    echo ""

    # Check registered PRs
    local pr_files=("$MONITOR_DIR"/pr_*.json)

    if [[ ! -f "${pr_files[0]}" ]]; then
        echo "No PRs currently monitored"
        echo ""
        echo "Open PRs:"
        gh pr list --json number,title,state -q '.[] | "  #\(.number): \(.title)"' || echo "  None"
        return
    fi

    echo "Monitored PRs:"
    for file in "${pr_files[@]}"; do
        if [[ -f "$file" ]]; then
            local pr_number=$(jq -r '.pr_number' "$file")
            local task_id=$(jq -r '.task_id' "$file")

            # Get current status from GitHub
            local pr_info=$(gh pr view "$pr_number" --json state,mergeable,statusCheckRollup 2>/dev/null || echo "")

            if [[ -z "$pr_info" ]]; then
                echo -e "  #$pr_number ($task_id): ${YELLOW}Cannot fetch status${NC}"
                continue
            fi

            local state=$(echo "$pr_info" | jq -r '.state')
            local mergeable=$(echo "$pr_info" | jq -r '.mergeable')

            if [[ "$state" == "MERGED" ]]; then
                echo -e "  #$pr_number ($task_id): ${GREEN}✓ MERGED${NC}"
                rm -f "$file"  # Cleanup
            elif [[ "$state" == "CLOSED" ]]; then
                echo -e "  #$pr_number ($task_id): ${YELLOW}CLOSED${NC}"
                rm -f "$file"  # Cleanup
            elif [[ "$mergeable" == "CONFLICTING" ]]; then
                echo -e "  #$pr_number ($task_id): ${RED}⚠ CONFLICT${NC}"
            else
                # Count check statuses
                local total=$(echo "$pr_info" | jq '.statusCheckRollup | length')
                local passed=$(echo "$pr_info" | jq '[.statusCheckRollup[] | select(.conclusion == "SUCCESS" or .conclusion == "NEUTRAL" or .conclusion == "SKIPPED")] | length')
                local failed=$(echo "$pr_info" | jq '[.statusCheckRollup[] | select(.conclusion == "FAILURE")] | length')
                local pending=$(echo "$pr_info" | jq '[.statusCheckRollup[] | select(.status != "COMPLETED")] | length')

                if [[ "$failed" -gt 0 ]]; then
                    echo -e "  #$pr_number ($task_id): ${RED}✗ $failed FAILED${NC} ($passed/$total passed)"
                elif [[ "$pending" -gt 0 ]]; then
                    echo -e "  #$pr_number ($task_id): ${YELLOW}⏳ $pending pending${NC} ($passed/$total passed)"
                else
                    echo -e "  #$pr_number ($task_id): ${GREEN}✓ All checks passed${NC} - will auto-merge"
                fi
            fi
        fi
    done

    echo ""
    echo "Daemon logs: ./scripts/ci_monitor_daemon.sh logs"
}

# Cancel monitoring
cmd_cancel() {
    local pr_number="$1"

    if [[ -z "$pr_number" ]]; then
        echo -e "${RED}Error: PR number required${NC}"
        exit 1
    fi

    local file="$MONITOR_DIR/pr_$pr_number.json"
    if [[ -f "$file" ]]; then
        rm -f "$file"
        echo -e "${GREEN}✓ Stopped monitoring PR #$pr_number${NC}"
    else
        echo -e "${YELLOW}PR #$pr_number was not being monitored${NC}"
    fi
}

# Main command router
main() {
    case "${1:-}" in
        create)
            cmd_create "${2:-}" "${3:-}"
            ;;
        status)
            cmd_status
            ;;
        cancel)
            cmd_cancel "${2:-}"
            ;;
        help|--help|-h)
            show_usage
            ;;
        [0-9]*)
            # PR number provided directly
            cmd_monitor "$1"
            ;;
        *)
            show_usage
            exit 1
            ;;
    esac
}

main "$@"

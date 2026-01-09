#!/usr/bin/env bash
# ci_monitor_daemon.sh - Background CI monitoring for Agent 8 Week 1 Optimization #3
# Monitors PRs in background and auto-merges when CI passes

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PID_FILE="$PROJECT_ROOT/.git/ci_monitor.pid"
LOG_FILE="$PROJECT_ROOT/logs/ci_monitor.log"
STATUS_FILE="$PROJECT_ROOT/.git/ci_monitor_status.json"
CHECK_INTERVAL=30  # seconds

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log_message() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" >> "$LOG_FILE"
}

# Update status JSON
update_status() {
    local daemon_status="$1"
    local prs_monitored="${2:-0}"
    local last_check="${3:-never}"

    cat > "$STATUS_FILE" << EOF
{
  "status": "$daemon_status",
  "pid": "${4:-null}",
  "prs_monitored": $prs_monitored,
  "last_check": "$last_check",
  "check_interval": $CHECK_INTERVAL,
  "log_file": "$LOG_FILE",
  "updated_at": "$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
}
EOF
}

# Check if daemon is running
is_running() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            return 0
        else
            # PID file exists but process is dead
            rm -f "$PID_FILE"
            return 1
        fi
    fi
    return 1
}

# Get daemon PID
get_pid() {
    if [ -f "$PID_FILE" ]; then
        cat "$PID_FILE"
    else
        echo "null"
    fi
}

# Monitor single PR
monitor_pr() {
    local pr_number="$1"

    log_message "INFO" "Checking PR #$pr_number"

    # Get PR status
    local pr_status=$(gh pr view "$pr_number" --json state,mergeable,statusCheckRollup -q '{state: .state, mergeable: .mergeable, checks: [.statusCheckRollup[] | {name: .name, status: .status, conclusion: .conclusion}]}' 2>/dev/null || echo "")

    if [ -z "$pr_status" ]; then
        log_message "WARN" "Could not fetch PR #$pr_number status"
        return 1
    fi

    # Parse status
    local state=$(echo "$pr_status" | jq -r '.state' 2>/dev/null || echo "UNKNOWN")
    local mergeable=$(echo "$pr_status" | jq -r '.mergeable' 2>/dev/null || echo "UNKNOWN")

    if [ "$state" != "OPEN" ]; then
        log_message "INFO" "PR #$pr_number is $state, skipping"
        return 0
    fi

    # Check CI status
    local checks_passing=true
    local checks_complete=true

    while IFS= read -r check; do
        local check_status=$(echo "$check" | jq -r '.status' 2>/dev/null || echo "UNKNOWN")
        local check_conclusion=$(echo "$check" | jq -r '.conclusion' 2>/dev/null || echo "")
        local check_name=$(echo "$check" | jq -r '.name' 2>/dev/null || echo "unknown")

        if [ "$check_status" = "IN_PROGRESS" ] || [ "$check_status" = "QUEUED" ] || [ "$check_status" = "PENDING" ]; then
            checks_complete=false
            log_message "INFO" "PR #$pr_number: $check_name is $check_status"
        elif [ "$check_status" = "COMPLETED" ]; then
            if [ "$check_conclusion" != "SUCCESS" ] && [ "$check_conclusion" != "NEUTRAL" ] && [ "$check_conclusion" != "SKIPPED" ]; then
                checks_passing=false
                log_message "WARN" "PR #$pr_number: $check_name failed ($check_conclusion)"
                # Send notification
                echo -e "\a"  # Terminal bell
            fi
        fi
    done < <(echo "$pr_status" | jq -c '.checks[]' 2>/dev/null || echo "")

    # Auto-merge if eligible
    if [ "$checks_complete" = true ] && [ "$checks_passing" = true ] && [ "$mergeable" = "MERGEABLE" ]; then
        log_message "SUCCESS" "PR #$pr_number is ready to merge! Attempting auto-merge..."

        if gh pr merge "$pr_number" --squash --delete-branch 2>&1 | tee -a "$LOG_FILE"; then
            log_message "SUCCESS" "✅ PR #$pr_number auto-merged successfully!"
            echo -e "${GREEN}✅ PR #$pr_number merged!${NC}"
            # Success notification
            echo -e "\a\a"  # Double bell
        else
            log_message "ERROR" "Failed to auto-merge PR #$pr_number"
            echo -e "${RED}❌ Failed to merge PR #$pr_number${NC}"
        fi
    elif [ "$checks_complete" = false ]; then
        log_message "INFO" "PR #$pr_number: CI still running..."
    elif [ "$checks_passing" = false ]; then
        log_message "WARN" "PR #$pr_number: CI checks failed"
        echo -e "${YELLOW}⚠️  PR #$pr_number has failed checks${NC}"
    fi

    return 0
}

# Main monitoring loop
monitor_loop() {
    log_message "INFO" "CI Monitor Daemon started (PID: $$)"
    update_status "running" 0 "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" "$$"

    while true; do
        # Get all open PRs
        local prs=$(gh pr list --json number -q '.[].number' 2>/dev/null || echo "")

        if [ -z "$prs" ]; then
            log_message "INFO" "No open PRs to monitor"
            update_status "running" 0 "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" "$$"
        else
            local pr_count=$(echo "$prs" | wc -l | tr -d ' ')
            log_message "INFO" "Monitoring $pr_count PR(s)"
            update_status "running" "$pr_count" "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" "$$"

            # Monitor each PR
            while IFS= read -r pr_number; do
                if [ -n "$pr_number" ]; then
                    monitor_pr "$pr_number" || true
                fi
            done <<< "$prs"
        fi

        # Wait before next check
        sleep $CHECK_INTERVAL
    done
}

# Start daemon
cmd_start() {
    if is_running; then
        local pid=$(cat "$PID_FILE")
        echo -e "${YELLOW}CI Monitor is already running (PID: $pid)${NC}"
        return 1
    fi

    # Ensure log directory exists
    mkdir -p "$(dirname "$LOG_FILE")"

    echo -e "${GREEN}Starting CI Monitor Daemon...${NC}"
    log_message "INFO" "Starting daemon from: $0"

    # Start daemon in background
    nohup bash "$0" _daemon >> "$LOG_FILE" 2>&1 &
    local daemon_pid=$!

    # Save PID
    echo "$daemon_pid" > "$PID_FILE"

    # Wait a moment to verify it started
    sleep 2

    if is_running; then
        echo -e "${GREEN}✅ CI Monitor started (PID: $daemon_pid)${NC}"
        echo -e "   Log: $LOG_FILE"
        echo -e "   Status: $STATUS_FILE"
        echo -e "   Check interval: ${CHECK_INTERVAL}s"
        log_message "SUCCESS" "Daemon started successfully (PID: $daemon_pid)"
        update_status "running" 0 "starting" "$daemon_pid"
    else
        echo -e "${RED}Failed to start daemon${NC}"
        echo -e "Check logs: $LOG_FILE"
        return 1
    fi
}

# Stop daemon
cmd_stop() {
    if ! is_running; then
        echo -e "${YELLOW}CI Monitor is not running${NC}"
        update_status "stopped" 0 "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" "null"
        return 0
    fi

    local pid=$(cat "$PID_FILE")
    echo -e "${YELLOW}Stopping CI Monitor (PID: $pid)...${NC}"
    log_message "INFO" "Stopping daemon (PID: $pid)"

    kill "$pid" 2>/dev/null || true

    # Wait for process to die
    local wait_count=0
    while ps -p "$pid" > /dev/null 2>&1 && [ $wait_count -lt 10 ]; do
        sleep 1
        ((wait_count++))
    done

    if ps -p "$pid" > /dev/null 2>&1; then
        echo -e "${RED}Force killing daemon...${NC}"
        kill -9 "$pid" 2>/dev/null || true
        log_message "WARN" "Daemon force killed"
    fi

    rm -f "$PID_FILE"
    update_status "stopped" 0 "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" "null"
    echo -e "${GREEN}✅ CI Monitor stopped${NC}"
    log_message "INFO" "Daemon stopped"
}

# Restart daemon
cmd_restart() {
    echo -e "${BLUE}Restarting CI Monitor...${NC}"
    cmd_stop
    sleep 2
    cmd_start
}

# Show status
cmd_status() {
    if is_running; then
        local pid=$(cat "$PID_FILE")
        echo -e "${GREEN}CI Monitor is running${NC}"
        echo -e "   PID: $pid"

        if [ -f "$STATUS_FILE" ]; then
            local prs_monitored=$(jq -r '.prs_monitored' "$STATUS_FILE" 2>/dev/null || echo "0")
            local last_check=$(jq -r '.last_check' "$STATUS_FILE" 2>/dev/null || echo "unknown")
            echo -e "   PRs monitored: $prs_monitored"
            echo -e "   Last check: $last_check"
        fi

        echo -e "   Log: $LOG_FILE"
        echo -e "   Status: $STATUS_FILE"
    else
        echo -e "${YELLOW}CI Monitor is not running${NC}"
        if [ -f "$STATUS_FILE" ]; then
            local last_check=$(jq -r '.last_check' "$STATUS_FILE" 2>/dev/null || echo "never")
            echo -e "   Last check: $last_check"
        fi
    fi
}

# Show recent logs
cmd_logs() {
    local lines="${1:-20}"

    if [ ! -f "$LOG_FILE" ]; then
        echo -e "${YELLOW}No log file found${NC}"
        return 1
    fi

    echo -e "${BLUE}CI Monitor Logs (last $lines lines):${NC}"
    tail -n "$lines" "$LOG_FILE"
}

# Internal daemon runner (called by nohup)
cmd_daemon() {
    monitor_loop
}

# Main command router
main() {
    case "${1:-}" in
        start)
            cmd_start
            ;;
        stop)
            cmd_stop
            ;;
        restart)
            cmd_restart
            ;;
        status)
            cmd_status
            ;;
        logs)
            cmd_logs "${2:-20}"
            ;;
        _daemon)
            # Internal command - run the actual daemon
            cmd_daemon
            ;;
        *)
            echo "CI Monitor Daemon - Week 1 Optimization #3"
            echo ""
            echo "Usage: $0 {start|stop|restart|status|logs}"
            echo ""
            echo "Commands:"
            echo "  start     Start the CI monitor daemon"
            echo "  stop      Stop the CI monitor daemon"
            echo "  restart   Restart the CI monitor daemon"
            echo "  status    Show daemon status"
            echo "  logs [N]  Show last N lines of logs (default: 20)"
            echo ""
            echo "The daemon monitors all open PRs every ${CHECK_INTERVAL}s and"
            echo "automatically merges them when CI checks pass."
            exit 1
            ;;
    esac
}

main "$@"

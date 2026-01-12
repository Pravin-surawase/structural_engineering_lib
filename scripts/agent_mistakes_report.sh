#!/bin/bash
# Agent Mistakes Report
# Short reminder of common agent mistakes and how to avoid them.
# Enhanced with hook output log parsing for deeper visibility.
#
# Usage: ./scripts/agent_mistakes_report.sh [--verbose]

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_GIT="$PROJECT_ROOT/logs/git_workflow.log"
LOG_CI="$PROJECT_ROOT/logs/ci_monitor.log"
LOG_DIR="$PROJECT_ROOT/logs"
VERBOSE="${1:-}"

count_matches() {
    local pattern="$1"
    local file="$2"
    if [[ -f "$file" ]]; then
        grep -c "$pattern" "$file" 2>/dev/null || true
    else
        echo "0"
    fi
}

# Parse hook output logs for detailed failure info
parse_hook_failures() {
    local total_files=0
    local failed_files=0

    # Check if any hook logs exist
    if ! ls "$LOG_DIR"/hook_output_*.log &>/dev/null; then
        echo "0|0"
        return
    fi

    total_files=$(ls -1 "$LOG_DIR"/hook_output_*.log 2>/dev/null | wc -l | tr -d ' ')

    # Count files with failures
    for log in "$LOG_DIR"/hook_output_*.log; do
        if grep -q "Failed" "$log" 2>/dev/null; then
            ((failed_files++)) || true
        fi
    done

    echo "${total_files}|${failed_files}"
}

# Get most common failing hooks
get_top_failing_hooks() {
    if ! ls "$LOG_DIR"/hook_output_*.log &>/dev/null; then
        return
    fi

    # Extract hook names from Failed lines and count
    grep -h -B1 "Failed" "$LOG_DIR"/hook_output_*.log 2>/dev/null | \
        grep -E "^[a-zA-Z].*\.\.\." | \
        sed 's/\.\.\..*$//' | \
        sort | uniq -c | sort -rn | head -5
}

COMMIT_FAILS=$(count_matches "Commit failed" "$LOG_GIT")
NO_MESSAGE=$(count_matches "No commit message provided" "$LOG_GIT")
CI_POLICY=$(count_matches "policy prohibits" "$LOG_CI")
CI_BEHIND=$(count_matches "head branch is behind" "$LOG_CI")

echo ""
echo "Common Mistakes (and fixes)"
echo "---------------------------"

if [[ "$COMMIT_FAILS" -gt 0 ]]; then
    echo "- Pre-commit failures (${COMMIT_FAILS} logged): use the hook output file and re-run ./scripts/ai_commit.sh"
else
    echo "- Pre-commit failures: none logged recently"
fi

if [[ "$NO_MESSAGE" -gt 0 ]]; then
    echo "- Missing commit message (${NO_MESSAGE} logged): always call ./scripts/ai_commit.sh \"message\""
else
    echo "- Missing commit message: none logged recently"
fi

if [[ "$CI_POLICY" -gt 0 ]]; then
    echo "- Merge blocked by policy (${CI_POLICY} logged): CI monitor now retries with --auto"
else
    echo "- Merge blocked by policy: none logged recently"
fi

if [[ "$CI_BEHIND" -gt 0 ]]; then
    echo "- PR behind main (${CI_BEHIND} logged): CI monitor auto-updates branch"
else
    echo "- PR behind main: none logged recently"
fi

# Hook output log analysis
echo ""
echo "Hook Output Log Analysis"
echo "------------------------"

HOOK_DATA=$(parse_hook_failures)
HOOK_TOTAL=$(echo "$HOOK_DATA" | cut -d'|' -f1)
HOOK_FAILED=$(echo "$HOOK_DATA" | cut -d'|' -f2)

if [[ "$HOOK_TOTAL" -gt 0 ]]; then
    echo "- Hook output logs: $HOOK_TOTAL total, $HOOK_FAILED with failures"

    if [[ "$HOOK_FAILED" -gt 0 ]]; then
        echo "- Top failing hooks:"
        get_top_failing_hooks | while read -r count hook; do
            echo "    $count x $hook"
        done

        # Show recent failure example if verbose
        if [[ "$VERBOSE" == "--verbose" ]]; then
            echo ""
            echo "- Recent failure example:"
            RECENT_FAIL=$(grep -l "Failed" "$LOG_DIR"/hook_output_*.log 2>/dev/null | tail -1)
            if [[ -n "$RECENT_FAIL" ]]; then
                grep -B2 -A3 "Failed" "$RECENT_FAIL" 2>/dev/null | head -10 | sed 's/^/    /'
            fi
        fi
    else
        echo "- All hooks passed ✓"
    fi
else
    echo "- No hook output logs found"
fi

echo ""
echo "Quick reminders"
echo "--------------"
echo "- Manual git is blocked by hooks; use ./scripts/ai_commit.sh or ./scripts/safe_push.sh"
echo "- When unsure, run: ./scripts/git_ops.sh --status"
echo "- If git feels broken, run: ./scripts/recover_git_state.sh"

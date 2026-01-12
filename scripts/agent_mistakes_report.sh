#!/bin/bash
# Agent Mistakes Report
# Short reminder of common agent mistakes and how to avoid them.
#
# Usage: ./scripts/agent_mistakes_report.sh

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_GIT="$PROJECT_ROOT/logs/git_workflow.log"
LOG_CI="$PROJECT_ROOT/logs/ci_monitor.log"

count_matches() {
    local pattern="$1"
    local file="$2"
    if [[ -f "$file" ]]; then
        grep -c "$pattern" "$file" 2>/dev/null || true
    else
        echo "0"
    fi
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

echo ""
echo "Quick reminders"
echo "--------------"
echo "- Manual git is blocked by hooks; use ./scripts/ai_commit.sh or ./scripts/safe_push.sh"
echo "- When unsure, run: ./scripts/git_ops.sh --status"
echo "- If git feels broken, run: ./scripts/recover_git_state.sh"

#!/usr/bin/env bash
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# agent_brief.sh — Fast 20-line actionable brief for AI agents
#
# PURPOSE: Give the agent ONLY what it needs NOW — not everything it
# could ever need. Replaces the 150+ line agent_context.py output
# for quick "what should I do" context. agent_context.py still exists
# for deep reference when needed.
#
# Usage:
#   ./scripts/agent_brief.sh                    # Auto-detect context
#   ./scripts/agent_brief.sh --agent backend    # Agent-specific brief
#   ./scripts/agent_brief.sh --handoff          # For next agent
#
# Output: ~20 lines of actionable context, runs in <100ms
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV="$REPO_ROOT/.venv/bin/python"
BRIEF="$REPO_ROOT/docs/planning/next-session-brief.md"
TASKS="$REPO_ROOT/docs/TASKS.md"
FEEDBACK_DIR="$REPO_ROOT/logs/feedback"

# ── Colors ─────────────────────────────────────────────────────────────
C='\033[0;36m' Y='\033[1;33m' G='\033[0;32m' R='\033[0;31m'
B='\033[1m' D='\033[2m' N='\033[0m'

# ── Current priorities (from next-session-brief.md) ────────────────────
_priorities() {
    if [[ -f "$BRIEF" ]]; then
        # Extract last session summary: "Completed:" line and known issues
        local completed known_issues focus
        focus=$(grep -m1 'Focus:' "$BRIEF" 2>/dev/null | sed 's/.*Focus:\*\*//' | sed 's/\*\*//' | head -c 120)
        completed=$(grep -A1 '^\*\*Completed:\*\*' "$BRIEF" 2>/dev/null | tail -1 | head -c 120)
        known_issues=$(grep -A3 '^\*\*Known Issues:\*\*' "$BRIEF" 2>/dev/null | grep '^-' | head -3 | sed 's/^/    /')

        [[ -n "$focus" ]] && echo "  Last focus: $focus"
        [[ -n "$completed" ]] && echo "  Done: $completed"
        if [[ -n "$known_issues" ]]; then
            echo "  Known issues:"
            echo "$known_issues"
        fi
    else
        echo "  (no next-session-brief.md found)"
    fi
}

# ── Active tasks ───────────────────────────────────────────────────────
_active_tasks() {
    if [[ -f "$TASKS" ]]; then
        # Get active release line (e.g., "v0.21 | React UX + Library Expansion")
        local active_line todo_items
        active_line=$(grep '🔄 ACTIVE' "$TASKS" 2>/dev/null | head -1 | awk -F'|' '{gsub(/^[ *]+|[ *]+$/, "", $2); gsub(/^[ *]+|[ *]+$/, "", $3); print $2 " — " $3}') || true
        [[ -n "$active_line" ]] && echo "  Release: $active_line"
        # Show pending feature tasks (📋 = not started)
        todo_items=$(grep '📋' "$TASKS" 2>/dev/null | grep 'TASK-' | head -3 | awk -F'|' '{gsub(/^[ ]+|[ ]+$/, "", $3); gsub(/^[ ]+|[ ]+$/, "", $4); print "  TODO: " $3 " — " $4}') || true
        [[ -n "$todo_items" ]] && echo "$todo_items"
    else
        echo "  (no TASKS.md)"
    fi
}

# ── Health score (fast — reads last saved report) ──────────────────────
_health_score() {
    local latest
    latest=$(ls -t "$REPO_ROOT/logs/evolution/health_"*.json 2>/dev/null | head -1)
    if [[ -n "$latest" ]]; then
        score=$(grep -o '"overall_score": [0-9]*' "$latest" | grep -o '[0-9]*')
        echo "${score}/100"
    else
        echo "?"
    fi
}

# ── Pending feedback count ─────────────────────────────────────────────
_pending_feedback() {
    local count=0
    if [[ -d "$FEEDBACK_DIR" ]]; then
        count=$(grep -l '"pending"' "$FEEDBACK_DIR"/*.json 2>/dev/null | wc -l | tr -d ' ')
    fi
    echo "$count"
}

# ── Recent git activity ───────────────────────────────────────────────
_recent_changes() {
    git -C "$REPO_ROOT" --no-pager log --oneline -5 2>/dev/null || echo "  (no git history)"
}

# ── Current branch & status ───────────────────────────────────────────
_git_status() {
    local branch dirty
    branch=$(git -C "$REPO_ROOT" branch --show-current 2>/dev/null)
    dirty=$(git -C "$REPO_ROOT" status --porcelain 2>/dev/null | wc -l | tr -d ' ')
    echo "${branch:-detached} (${dirty} uncommitted files)"
}

# ── Live counts (fast grep) ──────────────────────────────────────────
_live_counts() {
    local tests endpoints hooks
    tests=$(find "$REPO_ROOT/Python/tests" -name "test_*.py" -exec grep -c "def test_" {} + 2>/dev/null | awk -F: '{sum+=$NF} END{print sum}')
    endpoints=$(grep -r "@router\.\(get\|post\|put\|delete\|patch\|websocket\)" "$REPO_ROOT/fastapi_app/routers/" 2>/dev/null | wc -l | tr -d ' ')
    hooks=$(grep -r "^export.*function\|^export.*const.*use" "$REPO_ROOT/react_app/src/hooks/" 2>/dev/null | wc -l | tr -d ' ')
    echo "Tests: $tests | Endpoints: $endpoints | Hooks: $hooks"
}

# ── Handoff context (what the last agent left) ────────────────────────
_handoff_context() {
    local last_commit
    last_commit=$(git -C "$REPO_ROOT" --no-pager log -1 --format="%s" 2>/dev/null)
    echo "Last commit: $last_commit"

    # Check for handoff file
    local handoff="$REPO_ROOT/logs/handoff_latest.md"
    if [[ -f "$handoff" ]]; then
        echo ""
        echo -e "${B}Handoff from previous agent:${N}"
        head -10 "$handoff"
    fi
}

# ── Agent-specific one-liners ─────────────────────────────────────────
_agent_focus() {
    local agent="${1:-}"
    case "$agent" in
        backend)
            echo "Focus: Python/structural_lib/ | Run: .venv/bin/python scripts/discover_api_signatures.py <func>"
            ;;
        frontend)
            echo "Focus: react_app/src/ | Run: cd react_app && npm run build"
            ;;
        api-developer)
            echo "Focus: fastapi_app/routers/ | Check: grep -r '@router' fastapi_app/routers/"
            ;;
        structural-engineer)
            echo "Focus: Python/structural_lib/codes/is456/ | Run: .venv/bin/pytest Python/tests/ -k is456"
            ;;
        reviewer)
            echo "Focus: Review changes | Run: git diff --stat HEAD~3"
            ;;
        tester)
            echo "Focus: Python/tests/ | Run: .venv/bin/pytest Python/tests/ -v"
            ;;
        doc-master)
            echo "Focus: docs/ | Run: .venv/bin/python scripts/check_docs.py"
            ;;
        ops)
            echo "Focus: CI/CD, Docker | Run: colima status && docker compose config --quiet"
            ;;
        governance)
            echo "Focus: Project health | Run: ./run.sh health"
            ;;
        orchestrator)
            echo "Focus: Planning | Read: docs/TASKS.md + docs/planning/next-session-brief.md"
            ;;
        ui-designer)
            echo "Focus: Design review (read-only) | Check: react_app/src/components/"
            ;;
        *)
            echo "Run: .venv/bin/python scripts/agent_context.py <agent> for deep context"
            ;;
    esac
}

# ── Main ──────────────────────────────────────────────────────────────
main() {
    local agent="" handoff_mode=false

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --agent)  agent="$2"; shift 2 ;;
            --handoff) handoff_mode=true; shift ;;
            --help|-h)
                echo "Usage: ./scripts/agent_brief.sh [--agent <name>] [--handoff]"
                echo "  --agent <name>   Agent-specific brief"
                echo "  --handoff        Show handoff context from previous agent"
                exit 0
                ;;
            *) agent="$1"; shift ;;
        esac
    done

    if $handoff_mode; then
        _handoff_context
        exit 0
    fi

    echo -e "${B}${C}━━━ Agent Brief ━━━${N}"
    echo -e "  Git: $(_git_status)"
    echo -e "  Health: $(_health_score) | Feedback: $(_pending_feedback) pending"
    echo -e "  $(_live_counts)"
    echo ""

    if [[ -n "$agent" ]]; then
        echo -e "${B}Agent: ${agent}${N}"
        echo -e "  $(_agent_focus "$agent")"
        echo ""
    fi

    echo -e "${B}Priorities:${N}"
    _priorities | head -3
    echo ""

    echo -e "${B}Active Tasks:${N}"
    _active_tasks
    echo ""

    echo -e "${D}Recent:${N}"
    _recent_changes
    echo ""

    echo -e "${D}Session end: ./run.sh feedback log --agent ${agent:-<name>} --stale-doc '...'${N}"
    echo -e "${D}Deep context: .venv/bin/python scripts/agent_context.py ${agent:-<name>}${N}"
}

main "$@"

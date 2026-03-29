#!/usr/bin/env bash
# git_health_check.sh — Comprehensive git/PR/CI health check
#
# Single command to check everything about the project's git/PR/CI health.
# Used by humans AND agents before starting any work.
#
# Usage:
#   ./scripts/git_health_check.sh
#   ./scripts/git_health_check.sh --fix
#   ./scripts/git_health_check.sh --json
#   ./scripts/git_health_check.sh --verbose

set -euo pipefail

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ANSI Colors & Symbols
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

CHECK="✓"
CROSS="✗"
WARN="⚠"
INFO="ℹ"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Configuration
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

FIX_MODE=0
JSON_MODE=0
VERBOSE=0

PASSED=0
WARNED=0
FAILED=0

# JSON output accumulator
JSON_OUTPUT='{"checks": [], "summary": {}}'

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Helpers
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

log_check() {
    local status="$1" message="$2" detail="${3:-}"
    if [[ "$JSON_MODE" -eq 0 ]]; then
        case "$status" in
            pass) echo -e "${GREEN}${CHECK}${NC} $message" ;;
            warn) echo -e "${YELLOW}${WARN}${NC} $message" ;;
            fail) echo -e "${RED}${CROSS}${NC} $message" ;;
            info) echo -e "${CYAN}${INFO}${NC} $message" ;;
        esac
        [[ -n "$detail" && "$VERBOSE" -eq 1 ]] && echo -e "  ${CYAN}→${NC} $detail"
    fi

    # Add to JSON only if jq is available
    if command -v jq &>/dev/null; then
        local json_status
        case "$status" in
            pass) json_status="passed" ;;
            warn) json_status="warned" ;;
            fail) json_status="failed" ;;
            info) json_status="info" ;;
        esac
        JSON_OUTPUT=$(echo "$JSON_OUTPUT" | jq --arg msg "$message" --arg st "$json_status" --arg det "$detail" \
            '.checks += [{"message": $msg, "status": $st, "detail": $det}]' 2>/dev/null || echo "$JSON_OUTPUT")
    fi
}

track_result() {
    case "$1" in
        0) PASSED=$((PASSED + 1)) ;;
        1) WARNED=$((WARNED + 1)) ;;
        2) FAILED=$((FAILED + 1)) ;;
    esac
}

section_header() {
    [[ "$JSON_MODE" -eq 0 ]] && echo -e "\n${BOLD}${CYAN}$1${NC}"
}

show_help() {
    cat << 'HELP'
git_health_check.sh — Comprehensive git/PR/CI health check

Usage:
  ./scripts/git_health_check.sh [options]

Options:
  --fix          Auto-fix what can be fixed (stash changes, sync with remote)
  --json         Machine-readable JSON output for agents
  --verbose      Show extra details
  --help         Show this help

Examples:
  ./scripts/git_health_check.sh              # Quick health check
  ./scripts/git_health_check.sh --verbose    # Detailed output
  ./scripts/git_health_check.sh --json       # For automation
  ./scripts/git_health_check.sh --fix        # Auto-fix issues
HELP
    exit 0
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Section 1: Git Status
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

check_git_status() {
    section_header "Section 1: Git Status"

    # Check current branch
    local branch
    branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
    if [[ "$branch" == "HEAD" ]]; then
        log_check warn "Detached HEAD state" "Commit SHA: $(git rev-parse --short HEAD 2>/dev/null)"
        track_result 1
    else
        log_check pass "Branch: $branch"
        track_result 0
    fi

    # Check working tree
    if ! git rev-parse --verify HEAD &>/dev/null; then
        log_check info "Brand new repository (no commits yet)"
        track_result 0
    elif git diff-index --quiet HEAD -- 2>/dev/null; then
        log_check pass "Working tree clean (no uncommitted changes)"
        track_result 0
    else
        local changed_count
        changed_count=$(git diff --name-only | wc -l | tr -d ' ')
        log_check warn "Working tree has $changed_count uncommitted changes" "Run 'git status' to see details"
        track_result 1

        if [[ "$FIX_MODE" -eq 1 ]]; then
            echo -e "${YELLOW}${WARN}${NC} Stashing uncommitted changes..."
            git stash push -m "git_health_check auto-stash $(date +%Y%m%d_%H%M%S)"
        fi
    fi

    # Check untracked files
    local untracked
    untracked=$(git ls-files --others --exclude-standard 2>/dev/null || true)
    if [[ -z "$untracked" ]]; then
        log_check pass "No untracked files"
        track_result 0
    else
        local untracked_count
        untracked_count=$(echo "$untracked" | wc -l | tr -d ' ')
        log_check info "Untracked files: $untracked_count" "$(echo "$untracked" | head -3 | paste -sd ',' -)"
        track_result 0
    fi

    # Check merge/rebase in progress
    if [[ -d .git/rebase-merge ]] || [[ -d .git/rebase-apply ]] || [[ -f .git/MERGE_HEAD ]]; then
        log_check fail "Merge/rebase in progress" "Complete or abort the current operation"
        track_result 2
    else
        log_check pass "No merge/rebase in progress"
        track_result 0
    fi

    # Check ahead/behind
    if git remote get-url origin &>/dev/null; then
        local ahead behind
        ahead=$(git rev-list --count @{u}..HEAD 2>/dev/null || echo "0")
        behind=$(git rev-list --count HEAD..@{u} 2>/dev/null || echo "0")

        if [[ "$ahead" -eq 0 && "$behind" -eq 0 ]]; then
            log_check pass "Ahead/behind: 0/0 from remote"
            track_result 0
        elif [[ "$behind" -gt 0 ]]; then
            log_check warn "Ahead/behind: $ahead/$behind from remote" "Pull latest changes"
            track_result 1

            if [[ "$FIX_MODE" -eq 1 ]]; then
                echo -e "${YELLOW}${WARN}${NC} Pulling latest changes..."
                git pull --rebase
            fi
        else
            log_check info "Ahead/behind: $ahead/$behind from remote" "Push your commits"
            track_result 0
        fi
    fi
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Section 2: PR Status
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

check_pr_status() {
    section_header "Section 2: PR Status"

    if ! command -v gh &>/dev/null; then
        log_check info "GitHub CLI (gh) not installed" "Install to check PR status"
        return
    fi

    if ! command -v jq &>/dev/null; then
        log_check info "jq not installed" "Install jq to parse PR details"
        return
    fi

    local branch
    branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")

    if [[ "$branch" == "main" ]]; then
        log_check info "On main branch (no PR check needed)"
        track_result 0
        return
    fi

    # Check for open PR
    local pr_info
    pr_info=$(gh pr view --json number,title,state,mergeable,baseRefName 2>/dev/null || echo "")

    if [[ -z "$pr_info" ]]; then
        log_check info "No open PR for this branch"
        track_result 0
        return
    fi

    local pr_number pr_title pr_state pr_mergeable base_branch
    pr_number=$(echo "$pr_info" | jq -r '.number')
    pr_title=$(echo "$pr_info" | jq -r '.title')
    pr_state=$(echo "$pr_info" | jq -r '.state')
    pr_mergeable=$(echo "$pr_info" | jq -r '.mergeable')
    base_branch=$(echo "$pr_info" | jq -r '.baseRefName')

    log_check pass "Open PR: #$pr_number \"$pr_title\" → $base_branch"
    track_result 0

    # Check PR state
    if [[ "$pr_state" == "OPEN" && "$pr_mergeable" == "MERGEABLE" ]]; then
        log_check pass "PR state: OPEN, mergeable: MERGEABLE"
        track_result 0
    elif [[ "$pr_mergeable" == "CONFLICTING" ]]; then
        log_check fail "PR state: CONFLICTING" "Resolve merge conflicts"
        track_result 2
    else
        log_check warn "PR state: $pr_state, mergeable: $pr_mergeable"
        track_result 1
    fi

    # Check CI status
    local ci_stats
    ci_stats=$(gh pr view "$pr_number" --json statusCheckRollup --jq '
        [
            (.statusCheckRollup | length),
            ([.statusCheckRollup[] | select(.conclusion == "SUCCESS" or .conclusion == "NEUTRAL" or .conclusion == "SKIPPED")] | length),
            ([.statusCheckRollup[] | select(.conclusion == "FAILURE" or .conclusion == "CANCELLED" or .conclusion == "TIMED_OUT")] | length),
            ([.statusCheckRollup[] | select(.status != "COMPLETED")] | length)
        ] | @tsv' 2>/dev/null || echo "0 0 0 0")

    local total passed failed pending
    read -r total passed failed pending <<< "$ci_stats"

    if [[ "$total" -eq 0 ]]; then
        log_check info "No CI checks configured"
        track_result 0
    elif [[ "$failed" -gt 0 ]]; then
        log_check fail "CI checks: $passed/$total passed, $failed failed"
        track_result 2
    elif [[ "$pending" -gt 0 ]]; then
        log_check warn "CI checks: $passed/$total passed, $pending pending"
        track_result 1
    else
        log_check pass "CI checks: $passed/$total passed"
        track_result 0
    fi
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Section 3: Recent CI/Actions Status
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

check_ci_status() {
    section_header "Section 3: Recent CI/Actions Status"

    if ! command -v gh &>/dev/null; then
        log_check info "GitHub CLI (gh) not installed"
        return
    fi

    local run_info
    run_info=$(gh run list --limit 1 --json conclusion,displayTitle,createdAt,url 2>/dev/null || echo "")

    if [[ -z "$run_info" || "$run_info" == "[]" ]]; then
        log_check info "No recent workflow runs"
        track_result 0
        return
    fi

    local conclusion title created_at url time_ago
    conclusion=$(echo "$run_info" | jq -r '.[0].conclusion')
    title=$(echo "$run_info" | jq -r '.[0].displayTitle')
    created_at=$(echo "$run_info" | jq -r '.[0].createdAt')
    url=$(echo "$run_info" | jq -r '.[0].url')

    # Calculate time ago
    local created_epoch now_epoch diff_sec
    if date --version &>/dev/null 2>&1; then
        # GNU date (Linux)
        created_epoch=$(date -d "${created_at}" "+%s" 2>/dev/null || echo "0")
    else
        # BSD date (macOS)
        created_epoch=$(date -j -f "%Y-%m-%dT%H:%M:%SZ" "${created_at}" "+%s" 2>/dev/null || echo "0")
    fi
    now_epoch=$(date "+%s")
    diff_sec=$((now_epoch - created_epoch))

    if [[ "$diff_sec" -lt 60 ]]; then
        time_ago="${diff_sec}s ago"
    elif [[ "$diff_sec" -lt 3600 ]]; then
        time_ago="$((diff_sec / 60))m ago"
    else
        time_ago="$((diff_sec / 3600))h ago"
    fi

    if [[ "$conclusion" == "success" ]]; then
        log_check pass "Latest workflow run: success ($time_ago)"
        track_result 0
    elif [[ "$conclusion" == "failure" ]]; then
        log_check fail "Latest workflow run: failure ($time_ago)" "Run: $url"
        track_result 2
    else
        log_check warn "Latest workflow run: $conclusion ($time_ago)" "Run: $url"
        track_result 1
    fi
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Section 4: Repository Health
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

check_repo_health() {
    section_header "Section 4: Repository Health"

    # Fetch remote with timeout (portable for macOS and Linux)
    local fetch_result
    if command -v gtimeout &>/dev/null; then
        # Use gtimeout if available (brew install coreutils on macOS)
        fetch_result=$(gtimeout 10s git fetch origin &>/dev/null && echo "success" || echo "failed")
    elif command -v timeout &>/dev/null; then
        # Use timeout on Linux
        fetch_result=$(timeout 10s git fetch origin &>/dev/null && echo "success" || echo "failed")
    else
        # Fallback: try fetch without timeout
        fetch_result=$(git fetch origin &>/dev/null && echo "success" || echo "failed")
    fi

    if [[ "$fetch_result" == "success" ]]; then
        log_check pass "Remote is reachable"
        track_result 0
    else
        log_check warn "Remote fetch failed or timed out" "Check network connectivity"
        track_result 1
    fi

    # Check for stale local branches (merged to main but still exist locally)
    local stale_branches
    stale_branches=$(git branch --merged main | grep -v "^\*" | grep -v "main" | grep -v "master" || true)

    if [[ -z "$stale_branches" ]]; then
        log_check pass "No stale local branches"
        track_result 0
    else
        local stale_count
        stale_count=$(echo "$stale_branches" | wc -l | tr -d ' ')
        local branch_list
        branch_list=$(echo "$stale_branches" | tr '\n' ',' | sed 's/,$//')
        log_check warn "$stale_count stale branches: $branch_list" "Run 'git branch -d <branch>' to clean up"
        track_result 1

        if [[ "$FIX_MODE" -eq 1 ]]; then
            echo -e "${YELLOW}${WARN}${NC} Deleting stale branches..."
            while IFS= read -r b; do
                b=$(echo "$b" | xargs)  # trim whitespace
                [[ -n "$b" ]] && git branch -d "$b" 2>/dev/null || true
            done <<< "$stale_branches"
        fi
    fi

    # Check open issues assigned to you (if gh available)
    if command -v gh &>/dev/null; then
        local issue_count
        issue_count=$(gh issue list --assignee @me --state open --json number --jq 'length' 2>/dev/null || echo "0")

        if [[ "$issue_count" -eq 0 ]]; then
            log_check pass "No open issues assigned to you"
            track_result 0
        else
            log_check info "$issue_count open issues assigned to you"
            track_result 0
        fi
    fi
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Summary
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

show_summary() {
    local total=$((PASSED + WARNED + FAILED))

    if [[ "$JSON_MODE" -eq 1 ]]; then
        if command -v jq &>/dev/null; then
            JSON_OUTPUT=$(echo "$JSON_OUTPUT" | jq --argjson p "$PASSED" --argjson w "$WARNED" --argjson f "$FAILED" --argjson t "$total" \
                '.summary = {total: $t, passed: $p, warned: $w, failed: $f}' 2>/dev/null)
            echo "$JSON_OUTPUT"
        else
            echo "{\"error\": \"jq not installed\", \"summary\": {\"total\": $total, \"passed\": $PASSED, \"warned\": $WARNED, \"failed\": $FAILED}}"
        fi
        if [[ "$FAILED" -gt 0 ]]; then
            exit 2
        elif [[ "$WARNED" -gt 0 ]]; then
            exit 1
        else
            exit 0
        fi
    fi

    echo ""
    if [[ "$FAILED" -gt 0 ]]; then
        cat << 'SUMMARY'
╔════════════════════════════════════════╗
║  Git Health: ✗ FAILING                ║
║  Fix errors above before proceeding   ║
╚════════════════════════════════════════╝
SUMMARY
        exit 2
    elif [[ "$WARNED" -gt 0 ]]; then
        cat << 'SUMMARY'
╔════════════════════════════════════════╗
║  Git Health: ⚠ WARNINGS                ║
║  Fix warnings above before proceeding ║
╚════════════════════════════════════════╝
SUMMARY
        exit 1
    else
        cat << 'SUMMARY'
╔════════════════════════════════════════╗
║  Git Health: ✓ CLEAN                   ║
║  Ready to start work                  ║
╚════════════════════════════════════════╝
SUMMARY
        exit 0
    fi
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Main
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

main() {
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --fix) FIX_MODE=1; shift ;;
            --json) JSON_MODE=1; shift ;;
            --verbose) VERBOSE=1; shift ;;
            --help) show_help ;;
            *) echo "Unknown option: $1"; show_help ;;
        esac
    done

    if [[ "$JSON_MODE" -eq 0 ]]; then
        echo -e "${BOLD}${CYAN}Git/PR/CI Health Check${NC}"
        echo -e "${CYAN}════════════════════════${NC}"
    fi

    check_git_status
    check_pr_status
    check_ci_status
    check_repo_health
    show_summary
}

main "$@"

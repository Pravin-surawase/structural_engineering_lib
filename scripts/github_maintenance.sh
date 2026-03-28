#!/usr/bin/env bash
# GitHub Maintenance Automation
# When to use: Run periodically (weekly or per session) to keep GitHub clean.
# Handles stale branches, old issues, PR status, dependabot, and overall health.
#
# Usage:
#   ./scripts/github_maintenance.sh health               # Full health report
#   ./scripts/github_maintenance.sh stale-branches        # List stale branches
#   ./scripts/github_maintenance.sh clean-branches        # Delete stale branches
#   ./scripts/github_maintenance.sh stale-issues [N]      # Issues older than N days
#   ./scripts/github_maintenance.sh close-stale-issues [N] # Close stale issues
#   ./scripts/github_maintenance.sh pr-status             # Open PRs + CI status
#   ./scripts/github_maintenance.sh dependabot            # Dependabot PRs ready to merge
#   ./scripts/github_maintenance.sh full-cleanup          # Run all cleanup steps
#
# Flags:
#   --dry-run    Preview changes without applying (DEFAULT for destructive ops)
#   --execute    Actually apply destructive changes
#   --days N     Override staleness threshold (default: 30)
#
# Examples:
#   ./run.sh github health
#   ./run.sh github clean-branches --execute
#   ./run.sh github stale-issues --days 60
#   ./run.sh github full-cleanup --days 45 --execute

set -euo pipefail

# ── Colors ──────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
DIM='\033[2m'
NC='\033[0m'

# ── Globals ─────────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DRY_RUN=true
DAYS_THRESHOLD=30
SUBCOMMAND=""

# ── Helpers ─────────────────────────────────────────────────────────────────
_header() { echo -e "\n${BOLD}${CYAN}━━━ $1 ━━━${NC}"; }
_info()   { echo -e "  ${BLUE}ℹ${NC}  $1"; }
_ok()     { echo -e "  ${GREEN}✅${NC} $1"; }
_warn()   { echo -e "  ${YELLOW}⚠️${NC}  $1"; }
_err()    { echo -e "  ${RED}❌${NC} $1"; }
_dim()    { echo -e "  ${DIM}$1${NC}"; }
_line()   { echo -e "${DIM}────────────────────────────────────────────────────${NC}"; }

_require_gh() {
    if ! command -v gh &> /dev/null; then
        _err "gh CLI not found. Install: https://cli.github.com/"
        exit 1
    fi
    if ! gh auth status &> /dev/null 2>&1; then
        _err "gh not authenticated. Run: gh auth login"
        exit 1
    fi
}

_dry_run_banner() {
    if $DRY_RUN; then
        echo -e "\n  ${YELLOW}${BOLD}🔒 DRY RUN${NC} ${DIM}— no changes will be made. Use --execute to apply.${NC}"
        echo ""
    fi
}

# ── Parse Args ──────────────────────────────────────────────────────────────
_parse_args() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            health|stale-branches|clean-branches|stale-issues|close-stale-issues|pr-status|dependabot|full-cleanup)
                SUBCOMMAND="$1"
                shift
                ;;
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            --execute)
                DRY_RUN=false
                shift
                ;;
            --days)
                shift
                DAYS_THRESHOLD="${1:-30}"
                shift
                ;;
            --help|-h)
                _show_help
                exit 0
                ;;
            *)
                if [[ "$1" =~ ^[0-9]+$ ]]; then
                    DAYS_THRESHOLD="$1"
                else
                    _err "Unknown argument: $1"
                    _show_help
                    exit 1
                fi
                shift
                ;;
        esac
    done

    if [[ -z "$SUBCOMMAND" ]]; then
        _show_help
        exit 1
    fi
}

_show_help() {
    cat <<'EOF'
GitHub Maintenance Automation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Usage: ./scripts/github_maintenance.sh <subcommand> [options]
       ./run.sh github <subcommand> [options]

Subcommands:
  health                Full GitHub health report (read-only)
  stale-branches        List branches merged into main but not deleted
  clean-branches        Delete stale branches (--dry-run default)
  stale-issues [N]      List issues older than N days (default: 30)
  close-stale-issues [N]  Close stale issues (--dry-run default)
  pr-status             Show all open PRs with CI status
  dependabot            Show Dependabot PRs ready to merge
  full-cleanup          Run all cleanup steps (--dry-run default)

Flags:
  --dry-run             Preview changes (default for destructive ops)
  --execute             Actually apply destructive changes
  --days N              Override staleness threshold (default: 30)

Examples:
  ./run.sh github health
  ./run.sh github clean-branches --execute
  ./run.sh github stale-issues --days 60
  ./run.sh github full-cleanup --execute
EOF
}

# ── Subcommands ─────────────────────────────────────────────────────────────

_get_stale_branches() {
    local current_branch
    current_branch=$(git branch --show-current 2>/dev/null || echo "")
    git fetch --prune --quiet 2>/dev/null || true
    git branch -r --merged origin/main 2>/dev/null | \
        grep -v 'main$' | \
        grep -v 'HEAD' | \
        sed 's|^ *origin/||' | \
        grep -v "^${current_branch}$" | \
        sort || true
}

# ---- health ----------------------------------------------------------------
_cmd_health() {
    _header "GitHub Health Report"

    local issues prs stale_branches dependabot_count actions_needed=0

    issues=$(gh issue list --state open --json number --jq 'length' 2>/dev/null || echo "?")
    prs=$(gh pr list --state open --json number --jq 'length' 2>/dev/null || echo "?")
    stale_branches=$(_get_stale_branches | grep -c . 2>/dev/null || echo "0")
    dependabot_count=$(gh pr list --state open --json author --jq '[.[] | select(.author.login == "app/dependabot")] | length' 2>/dev/null || echo "0")

    [[ "$issues" != "0" && "$issues" != "?" ]] && actions_needed=$((actions_needed + 1))
    [[ "$stale_branches" != "0" ]] && actions_needed=$((actions_needed + 1))
    [[ "$dependabot_count" != "0" ]] && actions_needed=$((actions_needed + 1))

    echo ""
    echo -e "  ${BOLD}📋 Open Issues:${NC}     $issues"
    echo -e "  ${BOLD}🔀 Open PRs:${NC}        $prs"
    echo -e "  ${BOLD}🌿 Stale Branches:${NC}  $stale_branches"
    echo -e "  ${BOLD}🤖 Dependabot PRs:${NC}  $dependabot_count"
    echo -e "  ${BOLD}⚡ Actions Needed:${NC}  $actions_needed"
    _line

    if [[ "$actions_needed" -eq 0 ]]; then
        _ok "GitHub is healthy! No maintenance needed."
    else
        _warn "Maintenance recommended. Run: ./run.sh github full-cleanup"
    fi

    if [[ "$issues" != "0" && "$issues" != "?" ]]; then
        echo ""
        _info "Open issues:"
        gh issue list --state open --json number,title,createdAt --jq '.[] | "    #\(.number) \(.title) (\(.createdAt | split("T")[0]))"' 2>/dev/null || true
    fi

    if [[ "$prs" != "0" && "$prs" != "?" ]]; then
        echo ""
        _info "Open PRs:"
        gh pr list --state open --json number,title,headRefName --jq '.[] | "    #\(.number) \(.title) [\(.headRefName)]"' 2>/dev/null || true
    fi

    if [[ "$stale_branches" -gt 0 ]] 2>/dev/null; then
        echo ""
        _info "Stale branches (merged into main):"
        _get_stale_branches | while read -r b; do
            [[ -n "$b" ]] && echo "    $b"
        done
    fi

    echo ""
    _info "Recent failed CI runs (last 5):"
    local failed_runs
    failed_runs=$(gh run list --status failure --limit 5 --json name,createdAt,headBranch --jq '.[] | "    ❌ \(.name) on \(.headBranch) (\(.createdAt | split("T")[0]))"' 2>/dev/null || echo "")
    if [[ -z "$failed_runs" ]]; then
        _ok "No recent failures"
    else
        echo "$failed_runs"
    fi
    echo ""
}

# ---- stale-branches --------------------------------------------------------
_cmd_stale_branches() {
    _header "Stale Branches (merged into main)"

    local branches count
    branches=$(_get_stale_branches)
    count=$(echo "$branches" | grep -c . 2>/dev/null || echo "0")
    if [[ -z "$branches" ]]; then count=0; fi

    if [[ "$count" -eq 0 ]]; then
        _ok "No stale branches found"
        return
    fi

    echo -e "  Found ${BOLD}$count${NC} stale branches:"
    echo ""
    echo "$branches" | while read -r branch; do
        [[ -z "$branch" ]] && continue
        local last_commit
        last_commit=$(git log -1 --format='%ci' "origin/$branch" 2>/dev/null | cut -d' ' -f1 || echo "unknown")
        echo -e "    ${DIM}$last_commit${NC}  $branch"
    done
    echo ""
    _info "Delete with: ./run.sh github clean-branches --execute"
}

# ---- clean-branches --------------------------------------------------------
_cmd_clean_branches() {
    _header "Clean Stale Branches"
    _dry_run_banner

    local branches count
    branches=$(_get_stale_branches)
    count=$(echo "$branches" | grep -c . 2>/dev/null || echo "0")
    if [[ -z "$branches" ]]; then count=0; fi

    if [[ "$count" -eq 0 ]]; then
        _ok "No stale branches to clean"
        return
    fi

    echo -e "  ${BOLD}$count${NC} branches to delete:"
    echo ""

    echo "$branches" | while read -r branch; do
        [[ -z "$branch" ]] && continue
        if $DRY_RUN; then
            echo -e "    ${DIM}[dry-run]${NC} Would delete: $branch"
        else
            if git push origin --delete "$branch" 2>/dev/null; then
                _ok "Deleted: $branch"
            else
                _err "Failed to delete: $branch"
            fi
        fi
    done

    echo ""
    if $DRY_RUN; then
        _info "Use --execute to actually delete these branches"
    fi
}

# ---- stale-issues ----------------------------------------------------------
_cmd_stale_issues() {
    _header "Stale Issues (older than ${DAYS_THRESHOLD} days)"

    local cutoff_date
    if [[ "$(uname)" == "Darwin" ]]; then
        cutoff_date=$(date -v-"${DAYS_THRESHOLD}"d +%Y-%m-%dT00:00:00Z)
    else
        cutoff_date=$(date -d "-${DAYS_THRESHOLD} days" +%Y-%m-%dT00:00:00Z)
    fi

    local issues
    issues=$(gh issue list --state open --json number,title,createdAt --jq \
        ".[] | select(.createdAt < \"$cutoff_date\") | \"    #\(.number)  \(.createdAt | split(\"T\")[0])  \(.title)\"" 2>/dev/null || echo "")

    if [[ -z "$issues" ]]; then
        _ok "No issues older than ${DAYS_THRESHOLD} days"
        return
    fi

    local count
    count=$(echo "$issues" | grep -c . || echo "0")
    echo -e "  Found ${BOLD}$count${NC} stale issues:"
    echo ""
    echo "$issues"
    echo ""
    _info "Close with: ./run.sh github close-stale-issues --days ${DAYS_THRESHOLD} --execute"
}

# ---- close-stale-issues ----------------------------------------------------
_cmd_close_stale_issues() {
    _header "Close Stale Issues (older than ${DAYS_THRESHOLD} days)"
    _dry_run_banner

    local cutoff_date
    if [[ "$(uname)" == "Darwin" ]]; then
        cutoff_date=$(date -v-"${DAYS_THRESHOLD}"d +%Y-%m-%dT00:00:00Z)
    else
        cutoff_date=$(date -d "-${DAYS_THRESHOLD} days" +%Y-%m-%dT00:00:00Z)
    fi

    local issue_numbers
    issue_numbers=$(gh issue list --state open --json number,createdAt --jq \
        ".[] | select(.createdAt < \"$cutoff_date\") | .number" 2>/dev/null || echo "")

    if [[ -z "$issue_numbers" ]]; then
        _ok "No stale issues to close"
        return
    fi

    local count
    count=$(echo "$issue_numbers" | grep -c . || echo "0")
    echo -e "  ${BOLD}$count${NC} issues to close:"
    echo ""

    echo "$issue_numbers" | while read -r num; do
        [[ -z "$num" ]] && continue
        local title
        title=$(gh issue view "$num" --json title --jq '.title' 2>/dev/null || echo "?")
        if $DRY_RUN; then
            echo -e "    ${DIM}[dry-run]${NC} Would close #$num: $title"
        else
            if gh issue close "$num" --comment "Auto-closed by maintenance: older than ${DAYS_THRESHOLD} days." 2>/dev/null; then
                _ok "Closed #$num: $title"
            else
                _err "Failed to close #$num"
            fi
        fi
    done

    echo ""
    if $DRY_RUN; then
        _info "Use --execute to actually close these issues"
    fi
}

# ---- pr-status --------------------------------------------------------------
_cmd_pr_status() {
    _header "Open Pull Requests"

    local pr_count
    pr_count=$(gh pr list --state open --json number --jq 'length' 2>/dev/null || echo "0")

    if [[ "$pr_count" -eq 0 ]]; then
        _ok "No open pull requests"
        return
    fi

    echo -e "  ${BOLD}$pr_count${NC} open PRs:"
    echo ""

    gh pr list --state open --json number,title,headRefName,createdAt,author,mergeable --jq '.[] |
        "    #\(.number)  \(if .mergeable == "MERGEABLE" then "✅" elif .mergeable == "CONFLICTING" then "⚠️" else "❓" end)  \(.title)\n         Branch: \(.headRefName) | Author: \(.author.login) | Created: \(.createdAt | split("T")[0])"' 2>/dev/null || true

    echo ""
    _info "CI Status:"
    for num in $(gh pr list --state open --json number --jq '.[].number' 2>/dev/null); do
        local checks_json
        checks_json=$(gh pr checks "$num" --json name,state 2>/dev/null || echo "[]")
        local passed failed pending
        passed=$(echo "$checks_json" | python3 -c "import json,sys; d=json.load(sys.stdin); print(sum(1 for c in d if c['state']=='SUCCESS'))" 2>/dev/null || echo "0")
        failed=$(echo "$checks_json" | python3 -c "import json,sys; d=json.load(sys.stdin); print(sum(1 for c in d if c['state']=='FAILURE'))" 2>/dev/null || echo "0")
        pending=$(echo "$checks_json" | python3 -c "import json,sys; d=json.load(sys.stdin); print(sum(1 for c in d if c['state'] not in ('SUCCESS','FAILURE','SKIPPED')))" 2>/dev/null || echo "0")
        local total
        total=$(echo "$checks_json" | python3 -c "import json,sys; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")

        local icon="✅"
        [[ "$failed" -gt 0 ]] && icon="❌"
        [[ "$pending" -gt 0 && "$failed" -eq 0 ]] && icon="⏳"

        echo -e "    #$num: $icon $passed/$total passed"
        if [[ "$failed" -gt 0 ]]; then
            echo "$checks_json" | python3 -c "
import json,sys
for c in json.load(sys.stdin):
    if c['state']=='FAILURE': print(f'         ❌ {c[\"name\"]}')
" 2>/dev/null || true
        fi
    done
    echo ""
}

# ---- dependabot -------------------------------------------------------------
_cmd_dependabot() {
    _header "Dependabot Pull Requests"

    local count
    count=$(gh pr list --state open --json author --jq '[.[] | select(.author.login == "app/dependabot")] | length' 2>/dev/null || echo "0")

    if [[ "$count" -eq 0 ]]; then
        _ok "No Dependabot PRs"
        return
    fi

    echo -e "  ${BOLD}$count${NC} Dependabot PRs:"
    echo ""

    gh pr list --state open --json number,title,createdAt,author,mergeable --jq '
        .[] | select(.author.login == "app/dependabot") |
        "    #\(.number)  \(if .mergeable == "MERGEABLE" then "✅ Ready" elif .mergeable == "CONFLICTING" then "⚠️ Conflict" else "❓ Unknown" end)  \(.title) (created \(.createdAt | split("T")[0]))"' 2>/dev/null || true

    echo ""
    _info "To merge: gh pr merge <number> --merge"
}

# ---- full-cleanup -----------------------------------------------------------
_cmd_full_cleanup() {
    _header "Full GitHub Cleanup"
    _dry_run_banner

    local total_actions=0

    # 1. Stale branches
    local branches branch_count
    branches=$(_get_stale_branches)
    branch_count=$(echo "$branches" | grep -c . 2>/dev/null || echo "0")
    [[ -z "$branches" ]] && branch_count=0

    if [[ "$branch_count" -gt 0 ]]; then
        echo -e "\n  ${BOLD}🌿 Stale Branches: $branch_count${NC}"
        echo "$branches" | while read -r branch; do
            [[ -z "$branch" ]] && continue
            if $DRY_RUN; then
                echo -e "    ${DIM}[dry-run]${NC} Would delete: $branch"
            else
                if git push origin --delete "$branch" 2>/dev/null; then
                    _ok "Deleted: $branch"
                else
                    _err "Failed: $branch"
                fi
            fi
        done
        total_actions=$((total_actions + branch_count))
    else
        _ok "No stale branches"
    fi

    # 2. Stale issues
    local cutoff_date
    if [[ "$(uname)" == "Darwin" ]]; then
        cutoff_date=$(date -v-"${DAYS_THRESHOLD}"d +%Y-%m-%dT00:00:00Z)
    else
        cutoff_date=$(date -d "-${DAYS_THRESHOLD} days" +%Y-%m-%dT00:00:00Z)
    fi

    local issue_numbers issue_count
    issue_numbers=$(gh issue list --state open --json number,createdAt --jq \
        ".[] | select(.createdAt < \"$cutoff_date\") | .number" 2>/dev/null || echo "")
    issue_count=$(echo "$issue_numbers" | grep -c . 2>/dev/null || echo "0")
    [[ -z "$issue_numbers" ]] && issue_count=0

    if [[ "$issue_count" -gt 0 ]]; then
        echo -e "\n  ${BOLD}📋 Stale Issues: $issue_count${NC} (older than ${DAYS_THRESHOLD} days)"
        echo "$issue_numbers" | while read -r num; do
            [[ -z "$num" ]] && continue
            local title
            title=$(gh issue view "$num" --json title --jq '.title' 2>/dev/null || echo "?")
            if $DRY_RUN; then
                echo -e "    ${DIM}[dry-run]${NC} Would close #$num: $title"
            else
                if gh issue close "$num" --comment "Auto-closed by maintenance: older than ${DAYS_THRESHOLD} days." 2>/dev/null; then
                    _ok "Closed #$num: $title"
                else
                    _err "Failed: #$num"
                fi
            fi
        done
        total_actions=$((total_actions + issue_count))
    else
        _ok "No stale issues (threshold: ${DAYS_THRESHOLD} days)"
    fi

    # 3. Dependabot PRs
    local dependabot_count
    dependabot_count=$(gh pr list --state open --json author --jq '[.[] | select(.author.login == "app/dependabot")] | length' 2>/dev/null || echo "0")
    if [[ "$dependabot_count" -gt 0 ]]; then
        echo -e "\n  ${BOLD}🤖 Dependabot PRs: $dependabot_count${NC}"
        _info "Review manually: ./run.sh github dependabot"
        total_actions=$((total_actions + dependabot_count))
    else
        _ok "No Dependabot PRs pending"
    fi

    # Summary
    _line
    echo ""
    if [[ "$total_actions" -eq 0 ]]; then
        _ok "GitHub is clean — no maintenance needed!"
    elif $DRY_RUN; then
        _warn "$total_actions action(s) available. Run with --execute to apply."
    else
        _ok "Cleanup complete!"
    fi
    echo ""
}

# ── Main ────────────────────────────────────────────────────────────────────
main() {
    cd "$REPO_ROOT"
    _require_gh
    _parse_args "$@"

    case "$SUBCOMMAND" in
        health)             _cmd_health ;;
        stale-branches)     _cmd_stale_branches ;;
        clean-branches)     _cmd_clean_branches ;;
        stale-issues)       _cmd_stale_issues ;;
        close-stale-issues) _cmd_close_stale_issues ;;
        pr-status)          _cmd_pr_status ;;
        dependabot)         _cmd_dependabot ;;
        full-cleanup)       _cmd_full_cleanup ;;
        *)
            _err "Unknown subcommand: $SUBCOMMAND"
            _show_help
            exit 1
            ;;
    esac
}

main "$@"

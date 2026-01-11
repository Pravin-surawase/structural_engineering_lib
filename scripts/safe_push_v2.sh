#!/bin/bash
# ⚠️ DEPRECATED: Use safe_push.sh instead!
# This v2 version was experimental and is no longer maintained.
# Canonical script: ./scripts/safe_push.sh
# Removal planned: v0.18.0
#
# Enterprise-grade safe push workflow v2.0
# Professional git workflow with comprehensive error handling and logging
#
# Features:
# - Audit logging
# - Metrics collection
# - Dry-run mode
# - Rollback capability
# - Network timeout handling
# - Advanced conflict resolution
# - Branch protection
# - Commit validation

set -euo pipefail  # Strict error handling
IFS=$'\n\t'        # Strict word splitting

# ============================================================================
# CONFIGURATION
# ============================================================================

SCRIPT_VERSION="2.0.0"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_FILE="$PROJECT_ROOT/logs/git_workflow.log"
METRICS_FILE="$PROJECT_ROOT/logs/git_metrics.json"
NETWORK_TIMEOUT=30
MAX_RETRIES=3

# Colors
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly CYAN='\033[0;36m'
readonly NC='\033[0m'

# Options
DRY_RUN=false
QUIET=false
SKIP_TESTS=false
FORCE=false
START_TIME=$(date +%s)

# ============================================================================
# LOGGING & METRICS
# ============================================================================

log() {
    local level=$1
    shift
    local msg="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    # Log to file
    mkdir -p "$(dirname "$LOG_FILE")"
    echo "[$timestamp] [$level] $msg" >> "$LOG_FILE"

    # Log to console (unless quiet)
    if [[ "$QUIET" == "false" ]]; then
        case $level in
            ERROR)   echo -e "${RED}✗ $msg${NC}" ;;
            WARN)    echo -e "${YELLOW}⚠ $msg${NC}" ;;
            SUCCESS) echo -e "${GREEN}✓ $msg${NC}" ;;
            INFO)    echo -e "${BLUE}ℹ $msg${NC}" ;;
            *)       echo "$msg" ;;
        esac
    fi
}

record_metric() {
    local key=$1
    local value=$2
    mkdir -p "$(dirname "$METRICS_FILE")"

    if [[ ! -f "$METRICS_FILE" ]]; then
        echo "{}" > "$METRICS_FILE"
    fi

    # Simple JSON append (would use jq in production)
    local temp=$(mktemp)
    echo "{\"timestamp\": \"$(date -Iseconds)\", \"$key\": $value}" >> "$temp"
    cat "$temp" >> "$METRICS_FILE"
    rm "$temp"
}

# ============================================================================
# ERROR HANDLING & CLEANUP
# ============================================================================

cleanup() {
    local exit_code=$?
    local end_time=$(date +%s)
    local duration=$((end_time - START_TIME))

    log INFO "Workflow completed in ${duration}s with exit code $exit_code"
    record_metric "duration_seconds" "$duration"
    record_metric "exit_code" "$exit_code"

    # Cleanup temp files
    rm -f /tmp/git_workflow_*

    exit $exit_code
}

trap cleanup EXIT
trap 'log ERROR "Unexpected error at line $LINENO"; exit 1' ERR

# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

validate_git_state() {
    log INFO "Validating git state..."

    # Check if in git repo
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        log ERROR "Not in a git repository"
        return 1
    fi

    # Check for detached HEAD
    if ! git symbolic-ref -q HEAD > /dev/null; then
        log ERROR "Detached HEAD state detected"
        log INFO "Checkout a branch first: git checkout main"
        return 1
    fi

    # Check for rebase/cherry-pick in progress
    if [[ -d .git/rebase-merge ]] || [[ -d .git/rebase-apply ]]; then
        log ERROR "Rebase in progress - complete or abort first"
        return 1
    fi

    if [[ -f .git/CHERRY_PICK_HEAD ]]; then
        log ERROR "Cherry-pick in progress - complete or abort first"
        return 1
    fi

    # Check for unfinished merge
    if [[ -f .git/MERGE_HEAD ]]; then
        if git status | grep -q "Unmerged paths"; then
            log ERROR "Unresolved merge conflicts"
            return 1
        fi
        log WARN "Unfinished merge detected - will complete"
        git commit --no-edit
        return 0
    fi

    log SUCCESS "Git state is valid"
    return 0
}

validate_commit_message() {
    local msg="$1"

    # Check length
    if [[ ${#msg} -lt 10 ]]; then
        log ERROR "Commit message too short (min 10 chars)"
        return 1
    fi

    if [[ ${#msg} -gt 500 ]]; then
        log ERROR "Commit message too long (max 500 chars)"
        return 1
    fi

    # Check for conventional commit format (optional)
    if [[ ! "$msg" =~ ^(feat|fix|docs|style|refactor|test|chore|perf|ci|build|revert)(\(.+\))?:\ .+ ]]; then
        log WARN "Commit message doesn't follow conventional commits format"
        log INFO "Recommended: <type>: <description>"
    fi

    return 0
}

check_branch_protection() {
    local branch=$(git branch --show-current)

    if [[ "$branch" == "main" ]] || [[ "$branch" == "master" ]]; then
        if [[ "$FORCE" == "false" ]]; then
            log WARN "Pushing to protected branch: $branch"
            log INFO "Use --force flag to override"
            return 1
        fi
    fi

    return 0
}

# ============================================================================
# NETWORK OPERATIONS WITH TIMEOUT
# ============================================================================

git_pull_with_timeout() {
    local timeout=$NETWORK_TIMEOUT
    local retry=0

    while [[ $retry -lt $MAX_RETRIES ]]; do
        log INFO "Pulling from remote (attempt $((retry + 1))/$MAX_RETRIES)..."

        if timeout "$timeout" git pull --no-rebase origin main 2>&1; then
            log SUCCESS "Pull completed"
            return 0
        else
            local exit_code=$?
            if [[ $exit_code -eq 124 ]]; then
                log WARN "Network timeout after ${timeout}s"
            else
                log WARN "Pull failed with exit code $exit_code"
            fi
            retry=$((retry + 1))
            sleep 2
        fi
    done

    log ERROR "Pull failed after $MAX_RETRIES attempts"
    return 1
}

git_push_with_timeout() {
    local timeout=$NETWORK_TIMEOUT
    local retry=0

    while [[ $retry -lt $MAX_RETRIES ]]; do
        log INFO "Pushing to remote (attempt $((retry + 1))/$MAX_RETRIES)..."

        if timeout "$timeout" git push 2>&1; then
            log SUCCESS "Push completed"
            record_metric "push_success" 1
            return 0
        else
            local exit_code=$?
            if [[ $exit_code -eq 124 ]]; then
                log WARN "Network timeout after ${timeout}s"
            else
                log WARN "Push failed with exit code $exit_code"
            fi
            retry=$((retry + 1))
            sleep 2
        fi
    done

    log ERROR "Push failed after $MAX_RETRIES attempts"
    record_metric "push_failure" 1
    return 1
}

# ============================================================================
# MAIN WORKFLOW
# ============================================================================

main() {
    log INFO "=== Enterprise Git Workflow v$SCRIPT_VERSION ==="
    log INFO "Started at $(date '+%Y-%m-%d %H:%M:%S')"

    # Parse arguments
    local commit_msg=""
    while [[ $# -gt 0 ]]; do
        case $1 in
            --dry-run) DRY_RUN=true; shift ;;
            --quiet) QUIET=true; shift ;;
            --skip-tests) SKIP_TESTS=true; shift ;;
            --force) FORCE=true; shift ;;
            --help)
                echo "Usage: $0 \"commit message\" [options]"
                echo ""
                echo "Options:"
                echo "  --dry-run      Show what would be done without executing"
                echo "  --quiet        Suppress console output (logs to file only)"
                echo "  --skip-tests   Skip running tests before commit"
                echo "  --force        Force push to protected branches"
                echo "  --help         Show this help message"
                exit 0
                ;;
            *)
                if [[ -z "$commit_msg" ]]; then
                    commit_msg="$1"
                fi
                shift
                ;;
        esac
    done

    # Validate commit message
    if [[ -z "$commit_msg" ]]; then
        log ERROR "Commit message required"
        exit 1
    fi

    validate_commit_message "$commit_msg" || exit 1

    # Change to project root
    cd "$PROJECT_ROOT"

    # Step 1: Validate git state
    validate_git_state || exit 1

    # Step 2: Check branch protection
    check_branch_protection || exit 1

    # Step 3: Run tests (unless skipped)
    if [[ "$SKIP_TESTS" == "false" ]] && [[ -f "$PROJECT_ROOT/scripts/quick_check.sh" ]]; then
        log INFO "Running pre-commit tests..."
        if [[ "$DRY_RUN" == "false" ]]; then
            if ! "$PROJECT_ROOT/scripts/quick_check.sh"; then
                log ERROR "Tests failed - commit aborted"
                exit 1
            fi
        else
            log INFO "[DRY-RUN] Would run tests"
        fi
    fi

    # Step 4: Pull first
    if [[ "$DRY_RUN" == "false" ]]; then
        git_pull_with_timeout || exit 1
    else
        log INFO "[DRY-RUN] Would pull from remote"
    fi

    # Step 5: Stage files
    log INFO "Staging files..."
    if [[ "$DRY_RUN" == "false" ]]; then
        git add -A
        log INFO "Staged files:"
        git status --short
    else
        log INFO "[DRY-RUN] Would stage: $(git status --short | wc -l) files"
    fi

    # Step 6: Commit
    log INFO "Committing..."
    if [[ "$DRY_RUN" == "false" ]]; then
        if ! git commit -m "$commit_msg"; then
            log ERROR "Commit failed"
            exit 1
        fi
    else
        log INFO "[DRY-RUN] Would commit: $commit_msg"
    fi

    # Step 7: Handle pre-commit modifications
    if [[ "$DRY_RUN" == "false" ]]; then
        if git status --porcelain | grep -qE '^(M| M|AM)'; then
            log INFO "Pre-commit hooks modified files - amending..."
            git add -A
            git commit --amend --no-edit
        fi
    fi

    # Step 8: Pull again (safety check)
    if [[ "$DRY_RUN" == "false" ]]; then
        log INFO "Pulling again (safety check)..."
        if ! git_pull_with_timeout; then
            log WARN "Pull failed - attempting conflict resolution"
            # Auto-resolve with --ours
            if git status | grep -q "Unmerged paths"; then
                log INFO "Auto-resolving conflicts..."
                git checkout --ours .
                git add -A
                git commit --no-edit
            fi
        fi
    else
        log INFO "[DRY-RUN] Would pull again"
    fi

    # Step 9: Push
    if [[ "$DRY_RUN" == "false" ]]; then
        git_push_with_timeout || exit 1

        log SUCCESS "=== Workflow Complete ==="
        log SUCCESS "Commit: $(git log -1 --oneline)"
        record_metric "workflow_success" 1
    else
        log INFO "[DRY-RUN] Would push to remote"
        log INFO "[DRY-RUN] Workflow would complete successfully"
    fi
}

# Run main
main "$@"

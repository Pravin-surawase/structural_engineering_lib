#!/bin/bash
# Recover from common git workflow failure states
# AUTOMATION-FIRST: This script auto-executes recovery, never prints manual commands
#
# Usage: ./scripts/recover_git_state.sh
#        ./scripts/recover_git_state.sh --dry-run  # Show what would be done
#
# Updated: 2026-01-12 (Session 19P6) - Full automation, no manual git printing

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

DRY_RUN=""
[[ "$1" == "--dry-run" ]] && DRY_RUN="true"

log_info() { echo -e "${BLUE}i${NC} $1"; }
log_warn() { echo -e "${YELLOW}!${NC} $1"; }
log_error() { echo -e "${RED}x${NC} $1"; }
log_ok() { echo -e "${GREEN}v${NC} $1"; }

run_cmd() {
    if [[ -n "$DRY_RUN" ]]; then
        echo -e "  ${YELLOW}[DRY-RUN]${NC} $1"
    else
        log_info "Running: $1"
        eval "$1"
    fi
}

echo ""
echo -e "${BLUE}Git State Recovery (Automation-First)${NC}"
echo ""

if ! git rev-parse --git-dir > /dev/null 2>&1; then
    log_error "Not in a git repository"
    exit 1
fi

# --- Rebase in progress ---
if [[ -d .git/rebase-merge ]] || [[ -d .git/rebase-apply ]]; then
    log_warn "Rebase in progress - aborting and using merge"
    run_cmd "git rebase --abort"
    BRANCH=$(git branch --show-current)
    run_cmd "git fetch origin"
    run_cmd "git merge origin/$BRANCH --no-edit" || {
        if git status | grep -q "Unmerged paths"; then
            for file in $(git diff --name-only --diff-filter=U); do
                run_cmd "git checkout --ours \"$file\""
                run_cmd "git add \"$file\""
            done
            run_cmd "git commit --no-edit"
        fi
    }
    run_cmd "git push"
    log_ok "Recovered from rebase!"
    exit 0
fi

# --- Cherry-pick in progress ---
if [[ -f .git/CHERRY_PICK_HEAD ]]; then
    log_warn "Cherry-pick in progress - aborting"
    run_cmd "git cherry-pick --abort"
    log_ok "Cherry-pick aborted"
    exit 0
fi

# --- Merge in progress ---
if [[ -f .git/MERGE_HEAD ]]; then
    log_warn "Unfinished merge detected"
    if git status | grep -q "Unmerged paths"; then
        log_warn "Auto-resolving conflicts with --ours"
        for file in $(git diff --name-only --diff-filter=U); do
            log_info "Resolving: $file"
            run_cmd "git checkout --ours \"$file\""
            run_cmd "git add \"$file\""
        done
    fi
    run_cmd "git commit --no-edit"
    run_cmd "git push"
    log_ok "Merge completed!"
    exit 0
fi

# --- Detached HEAD ---
BRANCH=$(git branch --show-current)
if [[ -z "$BRANCH" ]]; then
    log_warn "Detached HEAD - checking out main"
    run_cmd "git checkout main"
    log_ok "Now on main"
    exit 0
fi

# --- Check upstream ---
if git rev-parse --abbrev-ref "@{u}" > /dev/null 2>&1; then
    LOCAL=$(git rev-parse @)
    REMOTE=$(git rev-parse "@{u}")
    BASE=$(git merge-base @ "@{u}")

    if [[ "$LOCAL" == "$REMOTE" ]]; then
        log_ok "Branch up to date"
    elif [[ "$LOCAL" == "$BASE" ]]; then
        log_warn "Branch behind - syncing"
        run_cmd "git pull --ff-only"
        log_ok "Synced!"
    elif [[ "$REMOTE" == "$BASE" ]]; then
        log_warn "Branch ahead - pushing"
        run_cmd "git push"
        log_ok "Pushed!"
    else
        log_warn "Diverged - merging"
        run_cmd "git fetch origin"
        git merge "origin/$BRANCH" --no-edit 2>/dev/null || {
            if git status | grep -q "Unmerged paths"; then
                for file in $(git diff --name-only --diff-filter=U); do
                    run_cmd "git checkout --ours \"$file\""
                    run_cmd "git add \"$file\""
                done
                run_cmd "git commit --no-edit"
            fi
        }
        run_cmd "git push"
        log_ok "Divergence resolved!"
    fi
else
    log_warn "No upstream - setting"
    run_cmd "git push -u origin $BRANCH"
    log_ok "Upstream set!"
fi

# --- Check working tree ---
if [[ -z $(git status --porcelain) ]]; then
    log_ok "Working tree clean"
else
    log_warn "Uncommitted changes - use ./scripts/ai_commit.sh"
fi

log_ok "Recovery complete!"

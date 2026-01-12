#!/bin/bash
# Recover from common git workflow failure states
# Usage: ./scripts/recover_git_state.sh

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
}

log_ok() {
    echo -e "${GREEN}✓${NC} $1"
}

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Git State Recovery${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if ! git rev-parse --git-dir > /dev/null 2>&1; then
    log_error "Not in a git repository"
    exit 1
fi

if [[ -d .git/rebase-merge ]] || [[ -d .git/rebase-apply ]]; then
    log_error "Rebase in progress"
    log_info "Resolve rebase or abort:"
    echo "  git rebase --continue"
    echo "  git rebase --abort"
    exit 1
fi

if [[ -f .git/CHERRY_PICK_HEAD ]]; then
    log_error "Cherry-pick in progress"
    log_info "Resolve cherry-pick or abort:"
    echo "  git cherry-pick --continue"
    echo "  git cherry-pick --abort"
    exit 1
fi

if [[ -f .git/MERGE_HEAD ]]; then
    log_warn "Unfinished merge detected"
    if git status | grep -q "Unmerged paths"; then
        log_error "Merge conflicts still present"
        log_info "Auto-recovery steps:"
        echo ""
        echo "  # Step 1: Keep your version of conflicted files"
        echo "  git checkout --ours docs/TASKS.md  # (adjust filename as needed)"
        echo ""
        echo "  # Step 2: Complete with automation"
        echo "  ./scripts/safe_push.sh \"merge: resolve conflicts\""
        echo ""
        log_info "The automation script handles staging, committing, and pushing."
        exit 1
    fi

    log_info "Conflicts resolved. Completing merge automatically..."
    git commit --no-edit
    git push
    log_ok "Merge completed and pushed!"
    exit 0
fi

BRANCH=$(git branch --show-current)
if [[ -z "$BRANCH" ]]; then
    log_warn "Detached HEAD"
    log_info "Checkout a branch before committing:"
    echo "  git checkout main"
    exit 1
fi

if git rev-parse --abbrev-ref "@{u}" > /dev/null 2>&1; then
    UPSTREAM="@{u}"
    LOCAL=$(git rev-parse @)
    REMOTE=$(git rev-parse "$UPSTREAM")
    BASE=$(git merge-base @ "$UPSTREAM")

    if [[ "$LOCAL" == "$REMOTE" ]]; then
        log_ok "Branch up to date with remote"
    elif [[ "$LOCAL" == "$BASE" ]]; then
        log_warn "Branch behind remote"
        log_info "Auto-syncing with remote..."
        git pull --ff-only
        log_ok "Synced with remote!"
        exit 0
    elif [[ "$REMOTE" == "$BASE" ]]; then
        log_warn "Branch ahead of remote"
        log_info "Use automation to push:"
        echo "  ./scripts/ai_commit.sh \"your message\""
        exit 0
    else
        log_error "Branch has diverged from remote"
        log_info "Auto-recovery steps:"
        echo ""
        echo "  # Option 1: Rebase (preferred if no conflicts expected)"
        echo "  git fetch origin && git rebase origin/$BRANCH"
        echo "  ./scripts/ai_commit.sh \"merge: sync with remote\""
        echo ""
        echo "  # Option 2: Merge (if rebase fails)"
        echo "  git fetch origin && git merge origin/$BRANCH"
        echo "  ./scripts/safe_push.sh \"merge: sync with remote\""
        exit 1
    fi
else
    log_warn "No upstream configured"
    log_info "Setting upstream automatically..."
    git push -u origin $BRANCH
    log_ok "Upstream set and pushed!"
    exit 0
fi

if [[ -z $(git status --porcelain) ]]; then
    log_ok "Working tree clean"
    log_info "Use safe_push.sh for commits:"
    echo "  ./scripts/safe_push.sh \"message\""
else
    log_warn "Working tree has uncommitted changes"
    log_info "Commit with:"
    echo "  ./scripts/ai_commit.sh \"message\""
fi

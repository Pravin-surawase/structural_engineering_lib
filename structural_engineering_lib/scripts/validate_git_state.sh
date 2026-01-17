#!/bin/bash
# Git workflow validator - run before any git operation
# Validates git state and prevents common issues
#
# Usage:
#   ./scripts/validate_git_state.sh           # Run all checks
#   ./scripts/validate_git_state.sh --fix     # Auto-fix issues
#   ./scripts/validate_git_state.sh --strict  # Fail on any warning

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Get options
FIX_MODE=false
STRICT_MODE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --fix) FIX_MODE=true; shift ;;
        --strict) STRICT_MODE=true; shift ;;
        *) shift ;;
    esac
done

ISSUES_FOUND=0
WARNINGS_FOUND=0

log_ok() {
    echo -e "${GREEN}✓${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
    WARNINGS_FOUND=$((WARNINGS_FOUND + 1))
}

log_error() {
    echo -e "${RED}✗${NC} $1"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
}

log_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Git Workflow Validator${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# ============================================================================
# CHECK: Git Repository
# ============================================================================

if ! git rev-parse --git-dir > /dev/null 2>&1; then
    log_error "Not in a git repository"
    exit 1
else
    log_ok "Valid git repository"
fi

# ============================================================================
# CHECK: Unfinished Merge
# ============================================================================

if [[ -f .git/MERGE_HEAD ]]; then
    log_error "Unfinished merge detected!"
    log_info "Complete the merge with: git commit --no-edit"
    log_info "Or abort with: git merge --abort"

    if [[ "$FIX_MODE" == "true" ]]; then
        if ! git status | grep -q "Unmerged paths"; then
            log_info "Auto-completing merge..."
            git commit --no-edit
            log_ok "Merge completed"
        else
            log_error "Cannot auto-fix: merge has conflicts"
        fi
    fi
else
    log_ok "No unfinished merge"
fi

# ============================================================================
# CHECK: Diverged Branches
# ============================================================================

BRANCH=$(git branch --show-current)
if [[ -z "$BRANCH" ]]; then
    log_warn "Detached HEAD state"
else
    log_ok "On branch: $BRANCH"

    # Check if branch has remote tracking
    if git rev-parse --abbrev-ref "@{u}" > /dev/null 2>&1; then
        UPSTREAM="@{u}"
        LOCAL=$(git rev-parse @)
        REMOTE=$(git rev-parse "$UPSTREAM")
        BASE=$(git merge-base @ "$UPSTREAM")

        if [[ "$LOCAL" == "$REMOTE" ]]; then
            log_ok "Branch up to date with remote"
        elif [[ "$LOCAL" == "$BASE" ]]; then
            log_warn "Branch behind remote (need to pull)"
            if [[ "$FIX_MODE" == "true" ]]; then
                log_info "Pulling latest changes..."
                git pull --ff-only
                log_ok "Pulled successfully"
            fi
        elif [[ "$REMOTE" == "$BASE" ]]; then
            log_ok "Branch ahead of remote (unpushed commits)"
        else
            log_error "Branch has diverged from remote!"
            log_info "Local commits:  $(git rev-list --count HEAD..$UPSTREAM)"
            log_info "Remote commits: $(git rev-list --count $UPSTREAM..HEAD)"
            log_info "Fix: Pull and resolve, or reset to remote"
        fi
    else
        log_warn "No remote tracking branch"
    fi
fi

# ============================================================================
# CHECK: Working Tree Status
# ============================================================================

if [[ -z $(git status --porcelain) ]]; then
    log_ok "Working tree clean"
else
    STATUS=$(git status --short)
    UNTRACKED=$(echo "$STATUS" | grep "^??" | wc -l | tr -d ' ')
    MODIFIED=$(echo "$STATUS" | grep "^ M" | wc -l | tr -d ' ')
    STAGED=$(echo "$STATUS" | grep "^M" | wc -l | tr -d ' ')

    log_warn "Working tree has changes"
    log_info "  Staged:    $STAGED files"
    log_info "  Modified:  $MODIFIED files"
    log_info "  Untracked: $UNTRACKED files"
fi

# ============================================================================
# CHECK: Stashed Changes
# ============================================================================

STASH_COUNT=$(git stash list | wc -l | tr -d ' ')
if [[ "$STASH_COUNT" -gt 0 ]]; then
    log_warn "Stashed changes: $STASH_COUNT"
    log_info "Review with: git stash list"
else
    log_ok "No stashed changes"
fi

# ============================================================================
# CHECK: Recent Commits
# ============================================================================

RECENT_COMMITS=$(git log --oneline -5 2>/dev/null | wc -l | tr -d ' ')
if [[ "$RECENT_COMMITS" -gt 0 ]]; then
    log_ok "Repository has commit history"
else
    log_warn "No commit history (new repository?)"
fi

# ============================================================================
# CHECK: Git Configuration
# ============================================================================

if git config user.name >/dev/null 2>&1 && git config user.email >/dev/null 2>&1; then
    log_ok "Git user configured ($(git config user.name))"
else
    log_error "Git user not configured"
    log_info "Set with: git config user.name 'Your Name'"
    log_info "         git config user.email 'you@example.com'"
fi

# ============================================================================
# CHECK: Remote Access
# ============================================================================

if git ls-remote --quiet --exit-code origin HEAD >/dev/null 2>&1; then
    log_ok "Can access remote origin"
else
    log_warn "Cannot access remote origin (check network/auth)"
fi

# ============================================================================
# CHECK: Branch Protection
# ============================================================================

if [[ "$BRANCH" == "main" ]] || [[ "$BRANCH" == "master" ]]; then
    log_warn "On protected branch: $BRANCH"
    log_info "Consider using feature branches"
fi

# ============================================================================
# CHECK: Large Files
# ============================================================================

LARGE_FILES=$(find . -type f -size +10M 2>/dev/null | grep -v ".git" | head -5)
if [[ -n "$LARGE_FILES" ]]; then
    log_warn "Large files detected (>10MB):"
    echo "$LARGE_FILES" | while read -r file; do
        SIZE=$(du -h "$file" | cut -f1)
        log_info "  $SIZE  $file"
    done
    log_info "Consider using Git LFS for large files"
fi

# ============================================================================
# CHECK: .gitignore
# ============================================================================

if [[ -f .gitignore ]]; then
    log_ok ".gitignore exists"
else
    log_warn ".gitignore not found"
fi

# ============================================================================
# SUMMARY
# ============================================================================

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Validation Summary${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "Errors:   ${RED}$ISSUES_FOUND${NC}"
echo -e "Warnings: ${YELLOW}$WARNINGS_FOUND${NC}"
echo ""

if [[ $ISSUES_FOUND -gt 0 ]]; then
    echo -e "${RED}✗ Validation failed with $ISSUES_FOUND error(s)${NC}"
    exit 1
elif [[ $WARNINGS_FOUND -gt 0 ]]; then
    if [[ "$STRICT_MODE" == "true" ]]; then
        echo -e "${RED}✗ Strict mode: $WARNINGS_FOUND warning(s) treated as errors${NC}"
        exit 1
    else
        echo -e "${YELLOW}⚠ Validation passed with $WARNINGS_FOUND warning(s)${NC}"
        exit 0
    fi
else
    echo -e "${GREEN}✓ Validation passed - git state is clean${NC}"
    exit 0
fi

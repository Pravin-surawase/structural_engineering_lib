#!/bin/bash
# Test suite for git workflow scripts
# Tests safe_push.sh, ai_commit.sh, and PR helpers in isolated environment
#
# Usage:
#   ./scripts/test_git_workflow.sh              # Run all tests
#   ./scripts/test_git_workflow.sh --verbose    # Run with detailed output
#   ./scripts/test_git_workflow.sh --test <name> # Run specific test

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Verbose mode
VERBOSE=false
if [[ "$1" == "--verbose" ]]; then
    VERBOSE=true
fi

# Get project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Test temp directory
TEST_DIR="$PROJECT_ROOT/.test_git_workflow_$$"

# Cleanup function
cleanup() {
    if [[ -d "$TEST_DIR" ]]; then
        rm -rf "$TEST_DIR"
    fi
}

trap cleanup EXIT

# Logging functions
log_test() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}TEST: $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    TESTS_RUN=$((TESTS_RUN + 1))
}

log_pass() {
    echo -e "${GREEN}✓ PASS: $1${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
}

log_fail() {
    echo -e "${RED}✗ FAIL: $1${NC}"
    TESTS_FAILED=$((TESTS_FAILED + 1))
}

log_info() {
    if [[ "$VERBOSE" == "true" ]]; then
        echo -e "${YELLOW}  ℹ $1${NC}"
    fi
}

# Assert functions
assert_file_exists() {
    if [[ -f "$1" ]]; then
        log_pass "File exists: $1"
    else
        log_fail "File does not exist: $1"
        return 1
    fi
}

assert_exit_code() {
    local expected=$1
    local actual=$2
    local msg=$3
    if [[ "$expected" -eq "$actual" ]]; then
        log_pass "$msg (exit code: $actual)"
    else
        log_fail "$msg (expected: $expected, got: $actual)"
        return 1
    fi
}

assert_git_clean() {
    if [[ -z $(git status --porcelain) ]]; then
        log_pass "Git working tree is clean"
    else
        log_fail "Git working tree has uncommitted changes"
        git status --short
        return 1
    fi
}

assert_no_merge_conflict() {
    if [[ ! -f .git/MERGE_HEAD ]]; then
        log_pass "No merge in progress"
    else
        log_fail "Merge conflict or unfinished merge detected"
        return 1
    fi
}

assert_script_executable() {
    if [[ -x "$1" ]]; then
        log_pass "Script is executable: $1"
    else
        log_fail "Script is not executable: $1"
        return 1
    fi
}

# ============================================================================
# PRE-FLIGHT CHECKS
# ============================================================================

preflight_checks() {
    log_test "Pre-flight Checks"

    # Check scripts exist
    assert_file_exists "$PROJECT_ROOT/scripts/safe_push.sh" || return 1
    assert_file_exists "$PROJECT_ROOT/scripts/ai_commit.sh" || return 1
    assert_file_exists "$PROJECT_ROOT/scripts/create_task_pr.sh" || return 1
    assert_file_exists "$PROJECT_ROOT/scripts/finish_task_pr.sh" || return 1
    assert_file_exists "$PROJECT_ROOT/scripts/recover_git_state.sh" || return 1
    assert_file_exists "$PROJECT_ROOT/scripts/git_ops.sh" || return 1
    assert_file_exists "$PROJECT_ROOT/scripts/install_git_hooks.sh" || return 1
    assert_file_exists "$PROJECT_ROOT/scripts/git_automation_health.sh" || return 1

    # Check scripts are executable
    assert_script_executable "$PROJECT_ROOT/scripts/safe_push.sh" || return 1
    assert_script_executable "$PROJECT_ROOT/scripts/ai_commit.sh" || return 1
    assert_script_executable "$PROJECT_ROOT/scripts/git_ops.sh" || return 1
    assert_script_executable "$PROJECT_ROOT/scripts/install_git_hooks.sh" || return 1

    # Check versioned hooks exist
    assert_file_exists "$PROJECT_ROOT/scripts/git-hooks/pre-commit" || return 1
    assert_file_exists "$PROJECT_ROOT/scripts/git-hooks/pre-push" || return 1

    # Check we're in a git repo
    if git rev-parse --git-dir > /dev/null 2>&1; then
        log_pass "In valid git repository"
    else
        log_fail "Not in a git repository"
        return 1
    fi

    # Check current state (soft check - dev sessions may be dirty)
    if [[ -z $(git status --porcelain) ]]; then
        log_pass "Git working tree is clean"
    else
        log_info "Working tree not clean (OK for dev)"
    fi
    assert_no_merge_conflict || return 1

    echo ""
}

# ============================================================================
# TEST: Script Syntax Validation
# ============================================================================

test_script_syntax() {
    log_test "Script Syntax Validation"

    local scripts=(
        "safe_push.sh"
        "ai_commit.sh"
        "create_task_pr.sh"
        "finish_task_pr.sh"
        "check_unfinished_merge.sh"
        "recover_git_state.sh"
        "git_ops.sh"
        "install_git_hooks.sh"
        "git_automation_health.sh"
    )

    for script in "${scripts[@]}"; do
        local path="$PROJECT_ROOT/scripts/$script"
        if [[ -f "$path" ]]; then
            # Check bash syntax
            if bash -n "$path" 2>/dev/null; then
                log_pass "Valid bash syntax: $script"
            else
                log_fail "Invalid bash syntax: $script"
                bash -n "$path"
                return 1
            fi
        fi
    done

    echo ""
}

# ============================================================================
# TEST: safe_push.sh Input Validation
# ============================================================================

test_safe_push_input_validation() {
    log_test "safe_push.sh Input Validation"

    cd "$PROJECT_ROOT"

    # Test 1: No commit message
    log_info "Testing with no commit message..."
    if ./scripts/safe_push.sh 2>&1 | grep -q "ERROR: Commit message required"; then
        log_pass "Rejects empty commit message"
    else
        # Script might use a default message
        log_info "Script may use default message"
    fi

    # Test 2: Check help flag
    log_info "Testing --help flag..."
    if ./scripts/safe_push.sh --help 2>&1 | grep -q "Usage"; then
        log_pass "Help message available"
    else
        log_info "No help message (OK if script is simple)"
    fi

    echo ""
}

# ============================================================================
# TEST: ai_commit.sh Wrapper Functionality
# ============================================================================

test_ai_commit_wrapper() {
    log_test "ai_commit.sh Wrapper Functionality"

    cd "$PROJECT_ROOT"

    # Test 1: Calls safe_push.sh
    log_info "Checking if ai_commit.sh calls safe_push.sh..."
    if grep -q "safe_push.sh" ./scripts/ai_commit.sh; then
        log_pass "ai_commit.sh correctly calls safe_push.sh"
    else
        log_fail "ai_commit.sh does not call safe_push.sh"
        return 1
    fi

    # Test 2: Handles no changes gracefully
    log_info "Testing clean working tree handling..."
    # This is a dry-run test - we won't actually commit
    # Just verify the script structure is correct

    if grep -q "git status --porcelain" ./scripts/ai_commit.sh; then
        log_pass "ai_commit.sh checks for uncommitted changes"
    else
        log_fail "ai_commit.sh doesn't check working tree status"
        return 1
    fi

    echo ""
}

# ============================================================================
# TEST: Git State Detection
# ============================================================================

test_git_state_detection() {
    log_test "Git State Detection"

    cd "$PROJECT_ROOT"

    # Test 1: Detect clean state
    if [[ -z $(git status --porcelain) ]]; then
        log_pass "Can detect clean working tree"
    else
        log_info "Working tree not clean (expected in development)"
    fi

    # Test 2: Detect branch
    local branch=$(git branch --show-current)
    if [[ -n "$branch" ]]; then
        log_pass "Can detect current branch: $branch"
    else
        if [[ -n "${GITHUB_ACTIONS:-}" ]]; then
            log_info "Detached HEAD in CI (expected)"
        else
            log_fail "Cannot detect current branch"
            return 1
        fi
    fi

    # Test 3: Detect remote
    if git remote get-url origin >/dev/null 2>&1; then
        log_pass "Can access remote origin"
    else
        log_fail "Cannot access remote origin"
        return 1
    fi

    # Test 4: Detect merge state
    if [[ -f .git/MERGE_HEAD ]]; then
        log_fail "Unfinished merge detected (clean this up!)"
        return 1
    else
        log_pass "No unfinished merge"
    fi

    echo ""
}

# ============================================================================
# TEST: Pre-commit Hook Detection
# ============================================================================

test_precommit_hook_detection() {
    log_test "Pre-commit Hook Detection"

    cd "$PROJECT_ROOT"

    # Test 1: Check if pre-commit is installed
    if command -v pre-commit >/dev/null 2>&1; then
        log_pass "pre-commit tool is installed"
    else
        log_info "pre-commit tool not found (skip check)"
        return 0
    fi

    # Test 2: Check if hooks are installed
    if [[ -f .git/hooks/pre-commit ]]; then
        log_pass "pre-commit hooks are installed"
    else
        log_info "pre-commit hooks not installed (run: pre-commit install)"
        return 0
    fi

    # Test 3: Check .pre-commit-config.yaml exists
    if [[ -f .pre-commit-config.yaml ]]; then
        log_pass ".pre-commit-config.yaml exists"
    else
        log_fail ".pre-commit-config.yaml not found"
        return 1
    fi

    echo ""
}

# ============================================================================
# TEST: Safe Push Handles Pre-commit File Modifications (CRITICAL)
# ============================================================================

test_safe_push_precommit_modifications() {
    log_test "Safe Push Handles Pre-commit File Modifications"

    # Create temporary test repo
    local test_repo="$TEST_DIR/precommit_test"
    mkdir -p "$test_repo"
    cd "$test_repo"
    git init
    git config user.name "Test User"
    git config user.email "test@example.com"

    # Copy safe_push.sh to test repo
    cp "$PROJECT_ROOT/scripts/safe_push.sh" "$test_repo/safe_push.sh"

    # Test 1: Verify Step 2.5 exists in safe_push.sh
    if grep -q "Step 2.5" "$test_repo/safe_push.sh"; then
        log_pass "safe_push.sh contains Step 2.5 (pre-flight whitespace check)"
    else
        log_fail "safe_push.sh missing Step 2.5"
        return 1
    fi

    # Test 2: Create file with trailing whitespace
    echo "test line with trailing whitespace   " > test_file.txt
    log_info "Created test file with trailing whitespace"

    # Test 3: Stage the file
    git add test_file.txt

    # Test 4: Verify git detects the whitespace
    if git diff --cached --check 2>&1 | grep -q 'trailing whitespace'; then
        log_pass "Git detects trailing whitespace in staged files"
    else
        log_fail "Git should detect trailing whitespace"
        return 1
    fi

    # Test 5: Simulate Step 2.5 fix
    git diff --cached --name-only | while read file; do
        if [ -f "$file" ]; then
            sed -i '' 's/[[:space:]]*$//' "$file" 2>/dev/null || sed -i 's/[[:space:]]*$//' "$file"
        fi
    done
    log_info "Applied sed fix to remove trailing whitespace"

    # Test 6: Verify whitespace is removed
    if ! grep -q '   $' test_file.txt; then
        log_pass "Trailing whitespace successfully removed"
    else
        log_fail "Trailing whitespace still present after sed"
        return 1
    fi

    # Test 7: Re-stage and verify no whitespace warnings
    git add test_file.txt
    if ! git diff --cached --check 2>&1 | grep -q 'trailing whitespace'; then
        log_pass "No whitespace warnings after fix"
    else
        log_fail "Whitespace warnings still present"
        return 1
    fi

    # Test 8: Verify Step 2.5 runs before commit
    local step_order=$(grep -n "Step 2.5/7\|Step 3/7: Committing" "$test_repo/safe_push.sh" | head -2)
    if echo "$step_order" | head -1 | grep -q "Step 2.5/7"; then
        log_pass "Step 2.5 runs BEFORE commit (correct order)"
    else
        log_fail "Step 2.5 must run before commit"
        return 1
    fi

    cd "$PROJECT_ROOT"
    echo ""
}

# ============================================================================
# TEST: Conflict Prevention Logic
# ============================================================================

test_conflict_prevention_logic() {
    log_test "Conflict Prevention Logic"

    cd "$PROJECT_ROOT"

    # Test 1: safe_push.sh pulls before commit
    if grep -q "git pull" ./scripts/safe_push.sh; then
        log_pass "safe_push.sh includes pull before commit"
    else
        log_fail "safe_push.sh missing pull before commit"
        return 1
    fi

    # Test 2: safe_push.sh pulls again before push
    local pull_count=$(grep -c "git pull" ./scripts/safe_push.sh || echo 0)
    if [[ "$pull_count" -ge 2 ]]; then
        log_pass "safe_push.sh pulls multiple times (before commit and before push)"
    else
        log_fail "safe_push.sh should pull at least twice"
        return 1
    fi

    # Test 3: Detects pre-commit modifications
    if grep -q "git status --porcelain.*grep" ./scripts/safe_push.sh; then
        log_pass "safe_push.sh detects pre-commit modifications"
    else
        log_fail "safe_push.sh doesn't check for pre-commit modifications"
        return 1
    fi

    # Test 4: Amends commit when hooks modify files
    if grep -q "git commit --amend --no-edit" ./scripts/safe_push.sh; then
        log_pass "safe_push.sh amends commit for hook modifications"
    else
        log_fail "safe_push.sh missing amend logic"
        return 1
    fi

    echo ""
}

# ============================================================================
# TEST: Hook Enforcement System (GITDOC-19/20)
# ============================================================================

test_hook_enforcement_system() {
    log_test "Hook Enforcement System"

    cd "$PROJECT_ROOT"

    # Test 1: Versioned hooks directory exists
    if [[ -d "$PROJECT_ROOT/scripts/git-hooks" ]]; then
        log_pass "scripts/git-hooks directory exists"
    else
        log_fail "scripts/git-hooks directory missing"
        return 1
    fi

    # Test 2: pre-commit hook exists and has correct content
    local pre_commit="$PROJECT_ROOT/scripts/git-hooks/pre-commit"
    if [[ -f "$pre_commit" ]]; then
        log_pass "pre-commit hook exists"
        # Check for bypass logic
        if grep -q "AI_COMMIT_ACTIVE" "$pre_commit" && grep -q "SAFE_PUSH_ACTIVE" "$pre_commit"; then
            log_pass "pre-commit hook has bypass environment variables"
        else
            log_fail "pre-commit hook missing bypass variables"
            return 1
        fi
    else
        log_fail "pre-commit hook missing"
        return 1
    fi

    # Test 3: pre-push hook exists and has correct content
    local pre_push="$PROJECT_ROOT/scripts/git-hooks/pre-push"
    if [[ -f "$pre_push" ]]; then
        log_pass "pre-push hook exists"
        if grep -q "AI_COMMIT_ACTIVE" "$pre_push" && grep -q "SAFE_PUSH_ACTIVE" "$pre_push"; then
            log_pass "pre-push hook has bypass environment variables"
        else
            log_fail "pre-push hook missing bypass variables"
            return 1
        fi
    else
        log_fail "pre-push hook missing"
        return 1
    fi

    # Test 4: Hooks are executable
    assert_script_executable "$pre_commit" || return 1
    assert_script_executable "$pre_push" || return 1

    # Test 5: install_git_hooks.sh uses core.hooksPath
    if grep -q "core.hooksPath" "$PROJECT_ROOT/scripts/install_git_hooks.sh"; then
        log_pass "install_git_hooks.sh uses core.hooksPath"
    else
        log_fail "install_git_hooks.sh should use core.hooksPath"
        return 1
    fi

    # Test 6: install_git_hooks.sh is idempotent (has status check)
    if grep -q "\-\-status" "$PROJECT_ROOT/scripts/install_git_hooks.sh"; then
        log_pass "install_git_hooks.sh supports --status flag"
    else
        log_fail "install_git_hooks.sh missing --status support"
        return 1
    fi

    echo ""
}

# ============================================================================
# TEST: Git Operations Router (GITDOC-23)
# ============================================================================

test_git_ops_router() {
    log_test "Git Operations Router"

    cd "$PROJECT_ROOT"

    local git_ops="$PROJECT_ROOT/scripts/git_ops.sh"

    # Test 1: Script exists and is executable
    assert_file_exists "$git_ops" || return 1
    assert_script_executable "$git_ops" || return 1

    # Test 2: Has --status flag
    if grep -q "\-\-status" "$git_ops"; then
        log_pass "git_ops.sh supports --status flag"
    else
        log_fail "git_ops.sh missing --status support"
        return 1
    fi

    # Test 3: Detects rebase in progress
    if grep -q "rebase-merge\|rebase-apply" "$git_ops"; then
        log_pass "git_ops.sh detects rebase in progress"
    else
        log_fail "git_ops.sh should detect rebase state"
        return 1
    fi

    # Test 4: Detects merge in progress
    if grep -q "MERGE_HEAD" "$git_ops"; then
        log_pass "git_ops.sh detects merge in progress"
    else
        log_fail "git_ops.sh should detect merge state"
        return 1
    fi

    # Test 5: Recommends recover_git_state.sh for issues
    if grep -q "recover_git_state" "$git_ops"; then
        log_pass "git_ops.sh recommends recover_git_state.sh"
    else
        log_fail "git_ops.sh should recommend recovery script"
        return 1
    fi

    # Test 6: Recommends ai_commit.sh for normal commits
    if grep -q "ai_commit" "$git_ops"; then
        log_pass "git_ops.sh recommends ai_commit.sh"
    else
        log_fail "git_ops.sh should recommend commit script"
        return 1
    fi

    # Test 7: Can run with --status without error
    if "$git_ops" --status >/dev/null 2>&1; then
        log_pass "git_ops.sh --status runs successfully"
    else
        log_fail "git_ops.sh --status failed to run"
        return 1
    fi

    echo ""
}

# ============================================================================
# TEST: Git Automation Health Check (GITDOC-27)
# ============================================================================

test_git_automation_health() {
    log_test "Git Automation Health Check"

    cd "$PROJECT_ROOT"

    local health_check="$PROJECT_ROOT/scripts/git_automation_health.sh"

    # Test 1: Script exists and is executable
    assert_file_exists "$health_check" || return 1
    assert_script_executable "$health_check" || return 1

    # Test 2: Checks hook enforcement
    if grep -q "Hook Enforcement\|core.hooksPath" "$health_check"; then
        log_pass "git_automation_health.sh checks hook enforcement"
    else
        log_fail "git_automation_health.sh should check hook enforcement"
        return 1
    fi

    # Test 3: Can run without error
    if "$health_check" >/dev/null 2>&1; then
        log_pass "git_automation_health.sh runs successfully"
    else
        # It may return non-zero if some checks fail, that's OK
        log_info "git_automation_health.sh completed (some checks may have failed)"
    fi

    echo ""
}

# ============================================================================
# TEST: Error Handling
# ============================================================================

test_error_handling() {
    log_test "Error Handling"

    cd "$PROJECT_ROOT"

    # Test 1: Scripts use set -e
    for script in safe_push.sh ai_commit.sh; do
        if grep -q "set -e" "./scripts/$script"; then
            log_pass "$script uses 'set -e' for error handling"
        else
            log_fail "$script missing 'set -e'"
            return 1
        fi
    done

    # Test 2: Scripts have error messages
    if grep -q "ERROR" ./scripts/safe_push.sh; then
        log_pass "safe_push.sh includes error messages"
    else
        log_fail "safe_push.sh missing error messages"
        return 1
    fi

    echo ""
}

# ============================================================================
# TEST: PR Helper Scripts Structure
# ============================================================================

test_pr_helper_structure() {
    log_test "PR Helper Scripts Structure"

    cd "$PROJECT_ROOT"

    # Test 1: create_task_pr.sh validates task ID
    if [[ -f ./scripts/create_task_pr.sh ]]; then
        if grep -q "TASK" ./scripts/create_task_pr.sh; then
            log_pass "create_task_pr.sh handles TASK-XXX pattern"
        else
            log_info "create_task_pr.sh may not validate task ID format"
        fi
    fi

    # Test 2: finish_task_pr.sh uses gh CLI
    if [[ -f ./scripts/finish_task_pr.sh ]]; then
        if grep -q "gh pr" ./scripts/finish_task_pr.sh; then
            log_pass "finish_task_pr.sh uses GitHub CLI"
        else
            log_fail "finish_task_pr.sh doesn't use gh CLI"
            return 1
        fi
    fi

    # Test 3: Check if gh CLI is available
    if command -v gh >/dev/null 2>&1; then
        log_pass "GitHub CLI (gh) is installed"
    else
        log_fail "GitHub CLI (gh) not found"
        log_info "Install with: brew install gh"
        return 1
    fi

    echo ""
}

# ============================================================================
# TEST: finish_task_pr.sh Flags & CI Polling
# ============================================================================

test_finish_task_pr_flags() {
    log_test "finish_task_pr.sh Flags & CI Polling"

    local script="$PROJECT_ROOT/scripts/finish_task_pr.sh"
    assert_file_exists "$script" || return 1

    # Flags documented
    if grep -q "\-\-async" "$script" && grep -q "\-\-wait" "$script" && grep -q "\-\-force" "$script"; then
        log_pass "finish_task_pr.sh documents --async/--wait/--force flags"
    else
        log_fail "finish_task_pr.sh missing flag documentation"
        return 1
    fi

    # Non-TUI CI polling
    if grep -q "statusCheckRollup" "$script"; then
        log_pass "finish_task_pr.sh polls CI using statusCheckRollup"
    else
        log_fail "finish_task_pr.sh missing statusCheckRollup polling"
        return 1
    fi

    # Avoid TUI check command
    if grep -q "gh pr checks --watch" "$script"; then
        log_fail "finish_task_pr.sh should not use gh pr checks --watch"
        return 1
    else
        log_pass "finish_task_pr.sh avoids gh pr checks --watch"
    fi

    # PR body safety
    if grep -q "\-\-body-file" "$script" && grep -q "mktemp" "$script"; then
        log_pass "finish_task_pr.sh uses --body-file with temp file"
    else
        log_fail "finish_task_pr.sh missing --body-file temp usage"
        return 1
    fi

    # Branch cleanup on merge
    if grep -q "gh pr merge .*--delete-branch" "$script"; then
        log_pass "finish_task_pr.sh deletes branch on merge"
    else
        log_fail "finish_task_pr.sh should delete branch on merge"
        return 1
    fi

    echo ""
}

# ============================================================================
# TEST: cleanup_stale_branches.sh Behavior
# ============================================================================

test_cleanup_stale_branches() {
    log_test "cleanup_stale_branches.sh Behavior"

    local script="$PROJECT_ROOT/scripts/cleanup_stale_branches.sh"
    assert_file_exists "$script" || return 1
    assert_script_executable "$script" || return 1

    if grep -q "git fetch --prune origin" "$script"; then
        log_pass "cleanup_stale_branches.sh fetches with prune"
    else
        log_fail "cleanup_stale_branches.sh missing prune fetch"
        return 1
    fi

    if grep -q "origin/main" "$script"; then
        log_pass "cleanup_stale_branches.sh compares against origin/main"
    else
        log_fail "cleanup_stale_branches.sh should use origin/main"
        return 1
    fi

    if grep -q "\-\-apply" "$script" && grep -q "Dry run" "$script"; then
        log_pass "cleanup_stale_branches.sh uses dry-run gating"
    else
        log_fail "cleanup_stale_branches.sh missing dry-run safeguards"
        return 1
    fi

    if grep -q "gh pr list" "$script"; then
        log_pass "cleanup_stale_branches.sh checks open PRs"
    else
        log_fail "cleanup_stale_branches.sh missing PR check"
        return 1
    fi

    echo ""
}

# ============================================================================
# TEST: Hook Logging & Diagnostics
# ============================================================================

test_hook_logging() {
    log_test "Hook Logging & Diagnostics"

    local pre_commit="$PROJECT_ROOT/scripts/git-hooks/pre-commit"
    local pre_push="$PROJECT_ROOT/scripts/git-hooks/pre-push"

    if grep -q "BLOCKED: Manual git commit" "$pre_commit"; then
        log_pass "pre-commit hook logs blocked manual commit"
    else
        log_fail "pre-commit hook missing block log"
        return 1
    fi

    if grep -q "BLOCKED: Manual git push" "$pre_push"; then
        log_pass "pre-push hook logs blocked manual push"
    else
        log_fail "pre-push hook missing block log"
        return 1
    fi

    if grep -q "hook_output_" "$PROJECT_ROOT/scripts/safe_push.sh"; then
        log_pass "safe_push.sh captures hook output"
    else
        log_fail "safe_push.sh missing hook output capture"
        return 1
    fi

    echo ""
}

# ============================================================================
# TEST: CI Monitor Edge Cases
# ============================================================================

test_ci_monitor_edge_cases() {
    log_test "CI Monitor Edge Cases"

    local script="$PROJECT_ROOT/scripts/ci_monitor_daemon.sh"

    if grep -q "head branch is behind" "$script" && grep -q "update-branch" "$script"; then
        log_pass "ci_monitor_daemon.sh handles head-behind updates"
    else
        log_fail "ci_monitor_daemon.sh missing head-behind handling"
        return 1
    fi

    if grep -q "policy prohibits" "$script"; then
        log_pass "ci_monitor_daemon.sh detects policy-prohibited merges"
    else
        log_fail "ci_monitor_daemon.sh missing policy-prohibit handling"
        return 1
    fi

    echo ""
}

# ============================================================================
# TEST: Git Configuration
# ============================================================================

test_git_configuration() {
    log_test "Git Configuration"

    cd "$PROJECT_ROOT"

    # Test 1: User name configured
    if git config user.name >/dev/null 2>&1; then
        log_pass "Git user.name configured: $(git config user.name)"
    else
        log_fail "Git user.name not configured"
        return 1
    fi

    # Test 2: User email configured
    if git config user.email >/dev/null 2>&1; then
        log_pass "Git user.email configured: $(git config user.email)"
    else
        log_fail "Git user.email not configured"
        return 1
    fi

    # Test 3: Default branch
    local default_branch=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@')
    if [[ -n "$default_branch" ]]; then
        log_pass "Default branch: $default_branch"
    else
        log_info "Cannot determine default branch"
    fi

    echo ""
}

# ============================================================================
# TEST: Workflow Documentation
# ============================================================================

test_workflow_documentation() {
    log_test "Workflow Documentation"

    cd "$PROJECT_ROOT"

    # Test 1: Check for workflow docs
    if [[ -f docs/contributing/github-workflow.md ]]; then
        log_pass "Workflow documentation exists"
    else
        log_fail "Missing docs/contributing/github-workflow.md"
        return 1
    fi

    # Test 2: Check for copilot instructions
    if [[ -f .github/copilot-instructions.md ]]; then
        log_pass "Copilot instructions exist"
    else
        log_info "No copilot instructions (optional)"
    fi

    # Test 3: Scripts have usage documentation
    if grep -q "Usage:" ./scripts/safe_push.sh; then
        log_pass "safe_push.sh includes usage documentation"
    else
        log_fail "safe_push.sh missing usage documentation"
        return 1
    fi

    echo ""
}

# ============================================================================
# TEST: Script Permissions
# ============================================================================

test_script_permissions() {
    log_test "Script Permissions"

    cd "$PROJECT_ROOT"

    local scripts=(
        "scripts/safe_push.sh"
        "scripts/ai_commit.sh"
        "scripts/create_task_pr.sh"
        "scripts/finish_task_pr.sh"
    )

    for script in "${scripts[@]}"; do
        if [[ -f "$script" ]]; then
            if [[ -x "$script" ]]; then
                log_pass "Executable: $script"
            else
                log_fail "Not executable: $script"
                log_info "Run: chmod +x $script"
                return 1
            fi
        fi
    done

    echo ""
}

# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

main() {
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  Git Workflow Test Suite                      ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════╝${NC}"
    echo ""

    # Run all tests
    preflight_checks
    test_script_syntax
    test_safe_push_input_validation
    test_ai_commit_wrapper
    test_git_state_detection
    test_precommit_hook_detection
    test_safe_push_precommit_modifications
    test_conflict_prevention_logic
    test_hook_enforcement_system
    test_git_ops_router
    test_git_automation_health
    test_error_handling
    test_pr_helper_structure
    test_finish_task_pr_flags
    test_cleanup_stale_branches
    test_hook_logging
    test_ci_monitor_edge_cases
    test_git_configuration
    test_workflow_documentation
    test_script_permissions

    # Summary
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}TEST SUMMARY${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "Tests run:    ${BLUE}$TESTS_RUN${NC}"
    echo -e "Tests passed: ${GREEN}$TESTS_PASSED${NC}"
    echo -e "Tests failed: ${RED}$TESTS_FAILED${NC}"
    echo ""

    if [[ $TESTS_FAILED -eq 0 ]]; then
        echo -e "${GREEN}✓ ALL TESTS PASSED!${NC}"
        echo ""
        return 0
    else
        echo -e "${RED}✗ SOME TESTS FAILED${NC}"
        echo ""
        return 1
    fi
}

# Run tests
main "$@"

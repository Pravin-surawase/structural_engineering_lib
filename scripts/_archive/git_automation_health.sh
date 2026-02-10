#!/bin/bash
# Git Automation Health Check
# Validates all automation scripts and their dependencies
#
# Usage:
#   ./scripts/git_automation_health.sh
#   ./scripts/git_automation_health.sh --verbose

# Don't use set -e because arithmetic operations can return 1

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

VERBOSE=false
if [[ "$1" == "--verbose" || "$1" == "-v" ]]; then
    VERBOSE=true
fi

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Git Automation Health Check${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

PASSED=0
FAILED=0
WARNINGS=0

check_script() {
    local name="$1"
    local path="$2"
    local critical="$3"

    printf "%-30s" "$name"

    if [[ -f "$path" ]]; then
        if [[ -x "$path" ]]; then
            echo -e "${GREEN}✓${NC}"
            ((PASSED++))
        else
            echo -e "${YELLOW}⚠ not executable${NC}"
            ((WARNINGS++))
        fi
    else
        if [[ "$critical" == "true" ]]; then
            echo -e "${RED}✗ missing (CRITICAL)${NC}"
            ((FAILED++))
        else
            echo -e "${YELLOW}⚠ missing${NC}"
            ((WARNINGS++))
        fi
    fi
}

check_git() {
    printf "%-30s" "Git available"
    if command -v git &>/dev/null; then
        VERSION=$(git --version | cut -d' ' -f3)
        echo -e "${GREEN}✓${NC} (v$VERSION)"
        ((PASSED++))
    else
        echo -e "${RED}✗ not found${NC}"
        ((FAILED++))
    fi
}

check_python() {
    printf "%-30s" "Python venv"
    if [[ -f ".venv/bin/python" ]]; then
        VERSION=$(.venv/bin/python --version 2>&1 | cut -d' ' -f2)
        echo -e "${GREEN}✓${NC} (v$VERSION)"
        ((PASSED++))
    else
        echo -e "${YELLOW}⚠ not found${NC}"
        ((WARNINGS++))
    fi
}

check_gh() {
    printf "%-30s" "GitHub CLI"
    if command -v gh &>/dev/null; then
        VERSION=$(gh --version | head -1 | cut -d' ' -f3)
        echo -e "${GREEN}✓${NC} (v$VERSION)"
        ((PASSED++))
    else
        echo -e "${YELLOW}⚠ not found (PR features limited)${NC}"
        ((WARNINGS++))
    fi
}

check_git_state() {
    printf "%-30s" "Git state clean"
    if [[ -f ".git/MERGE_HEAD" ]]; then
        echo -e "${RED}✗ unfinished merge${NC}"
        ((FAILED++))
    elif [[ -d ".git/rebase-merge" ]] || [[ -d ".git/rebase-apply" ]]; then
        echo -e "${RED}✗ rebase in progress${NC}"
        ((FAILED++))
    else
        echo -e "${GREEN}✓${NC}"
        ((PASSED++))
    fi
}

check_branch() {
    printf "%-30s" "Current branch"
    BRANCH=$(git branch --show-current 2>/dev/null || echo "")
    if [[ -z "$BRANCH" ]]; then
        echo -e "${RED}✗ detached HEAD${NC}"
        ((FAILED++))
    else
        echo -e "${GREEN}✓${NC} ($BRANCH)"
        ((PASSED++))
    fi
}

check_remote() {
    printf "%-30s" "Remote connection"
    if git ls-remote origin HEAD &>/dev/null; then
        echo -e "${GREEN}✓${NC}"
        ((PASSED++))
    else
        echo -e "${RED}✗ cannot reach origin${NC}"
        ((FAILED++))
    fi
}

check_log_dir() {
    printf "%-30s" "Log directory"
    if [[ -d "logs" ]]; then
        echo -e "${GREEN}✓${NC}"
        ((PASSED++))
    else
        echo -e "${YELLOW}⚠ missing (will be created)${NC}"
        mkdir -p logs
        ((WARNINGS++))
    fi
}

echo -e "${BLUE}📋 Core Scripts${NC}"
echo "────────────────────────────────────────────"
check_script "ai_commit.sh" "scripts/ai_commit.sh" "true"
check_script "safe_push.sh" "scripts/safe_push.sh" "true"
check_script "should_use_pr.sh" "scripts/should_use_pr.sh" "true"
check_script "recover_git_state.sh" "scripts/recover_git_state.sh" "true"
check_script "git_ops.sh" "scripts/git_ops.sh" "false"
echo ""

echo -e "${BLUE}🔒 Git Hook Enforcement${NC}"
echo "────────────────────────────────────────────"
printf "%-30s" "core.hooksPath configured"
HOOKS_PATH=$(git config --get core.hooksPath 2>/dev/null || echo "")
if [[ -z "$HOOKS_PATH" ]]; then
    echo -e "${YELLOW}⚠ not set (manual git allowed)${NC}"
    ((WARNINGS++))
elif [[ "$HOOKS_PATH" == *"scripts/git-hooks"* ]]; then
    echo -e "${GREEN}✓${NC}"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠ set to: $HOOKS_PATH${NC}"
    ((WARNINGS++))
fi

check_script "pre-commit hook" "scripts/git-hooks/pre-commit" "false"
check_script "pre-push hook" "scripts/git-hooks/pre-push" "false"
check_script "install_git_hooks.sh" "scripts/install_git_hooks.sh" "false"
echo ""

echo -e "${BLUE}🔧 Session Scripts${NC}"
echo "────────────────────────────────────────────"
check_script "agent_start.sh" "scripts/agent_start.sh" "false"
check_script "agent_setup.sh" "scripts/agent_setup.sh" "false"
check_script "agent_preflight.sh" "scripts/agent_preflight.sh" "false"
check_script "agent_mistakes_report.sh" "scripts/agent_mistakes_report.sh" "false"
echo ""

echo -e "${BLUE}🔀 PR Management${NC}"
echo "────────────────────────────────────────────"
check_script "create_task_pr.sh" "scripts/create_task_pr.sh" "false"
check_script "finish_task_pr.sh" "scripts/finish_task_pr.sh" "false"
check_script "worktree_manager.sh" "scripts/worktree_manager.sh" "false"
echo ""

echo -e "${BLUE}🔍 Dependencies${NC}"
echo "────────────────────────────────────────────"
check_git
check_python
check_gh
echo ""

echo -e "${BLUE}📊 Git State${NC}"
echo "────────────────────────────────────────────"
check_git_state
check_branch
check_remote
check_log_dir
echo ""

# QA-02: Check for deprecated/duplicate scripts
echo -e "${BLUE}🧹 Deprecated Script Check${NC}"
echo "────────────────────────────────────────────"

# Check for old enforcement script
printf "%-30s" "Old enforcement hook"
if [[ -f "scripts/install_enforcement_hook.sh" ]]; then
    # Check if it's deprecated (has deprecation banner)
    if grep -q "DEPRECATED" "scripts/install_enforcement_hook.sh" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} (deprecated with banner)"
        ((PASSED++))
    else
        echo -e "${YELLOW}⚠ exists (should be deprecated)${NC}"
        ((WARNINGS++))
    fi
else
    echo -e "${GREEN}✓${NC} (removed)"
    ((PASSED++))
fi

# Check for duplicate hook installers
printf "%-30s" "Duplicate hook scripts"
HOOK_INSTALLERS=$(find scripts -name "*hook*.sh" -type f 2>/dev/null | wc -l | tr -d ' ')
if [[ "$HOOK_INSTALLERS" -gt 2 ]]; then
    echo -e "${YELLOW}⚠ $HOOK_INSTALLERS found (check for duplicates)${NC}"
    ((WARNINGS++))
else
    echo -e "${GREEN}✓${NC} ($HOOK_INSTALLERS scripts)"
    ((PASSED++))
fi

# Check for multiple entrypoint scripts advertising themselves
printf "%-30s" "Entrypoint consistency"
# Should only advertise agent_start.sh, ai_commit.sh, git_ops.sh
ADVERTISED=$(grep -l "Start session\|Session start\|start here" scripts/*.sh 2>/dev/null | wc -l | tr -d ' ')
if [[ "$ADVERTISED" -gt 3 ]]; then
    echo -e "${YELLOW}⚠ too many ($ADVERTISED) - consolidate docs${NC}"
    ((WARNINGS++))
else
    echo -e "${GREEN}✓${NC}"
    ((PASSED++))
fi

# Check for undocumented scripts (not in automation-scripts.md)
printf "%-30s" "Undocumented git scripts"
UNDOCUMENTED=0
DOC_FILE="docs/git-automation/automation-scripts.md"
if [[ -f "$DOC_FILE" ]]; then
    for script in scripts/ai_commit.sh scripts/safe_push.sh scripts/git_ops.sh scripts/should_use_pr.sh scripts/recover_git_state.sh; do
        basename_script=$(basename "$script")
        if ! grep -q "$basename_script" "$DOC_FILE" 2>/dev/null; then
            ((UNDOCUMENTED++))
            if [[ "$VERBOSE" == "true" ]]; then
                echo ""
                echo -e "  ${YELLOW}Missing: $basename_script${NC}"
            fi
        fi
    done
    if [[ "$UNDOCUMENTED" -gt 0 ]]; then
        echo -e "${YELLOW}⚠ $UNDOCUMENTED core scripts not in docs${NC}"
        ((WARNINGS++))
    else
        echo -e "${GREEN}✓${NC}"
        ((PASSED++))
    fi
else
    echo -e "${YELLOW}⚠ automation-scripts.md not found${NC}"
    ((WARNINGS++))
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "Results: ${GREEN}$PASSED passed${NC} | ${YELLOW}$WARNINGS warnings${NC} | ${RED}$FAILED failed${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [[ $FAILED -gt 0 ]]; then
    echo ""
    echo -e "${RED}❌ Health check FAILED${NC}"
    echo "Fix critical issues before using git automation."
    exit 1
elif [[ $WARNINGS -gt 0 ]]; then
    echo ""
    echo -e "${YELLOW}⚠️ Health check passed with warnings${NC}"
    echo "Git automation will work but some features may be limited."
    exit 0
else
    echo ""
    echo -e "${GREEN}✅ All checks passed!${NC}"
    echo "Git automation is fully operational."
    exit 0
fi

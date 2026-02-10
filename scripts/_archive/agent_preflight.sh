#!/bin/bash
# Agent Pre-Flight Checklist
# Validates environment before starting work
#
# Usage:
#   ./scripts/agent_preflight.sh              # Full check
#   ./scripts/agent_preflight.sh --quick      # Skip expensive checks
#   ./scripts/agent_preflight.sh --fix        # Auto-fix issues

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# Parse arguments
QUICK_MODE=false
FIX_MODE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --quick)
            QUICK_MODE=true
            shift
            ;;
        --fix)
            FIX_MODE=true
            shift
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Usage: $0 [--quick] [--fix]"
            exit 1
            ;;
    esac
done

# Get project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         Agent Pre-Flight Checklist v1.0.0             ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

# Track issues
ISSUES_FOUND=0
WARNINGS_FOUND=0

# Check 1: Git state
echo -e "${BLUE}[1/10]${NC} Git State"
if [[ ! -d .git ]]; then
    echo -e "${RED}  ✗ Not a git repository${NC}"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
else
    echo -e "${GREEN}  ✓ Git repository${NC}"
fi

# Check 2: Branch
CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || echo "")
if [[ -z "$CURRENT_BRANCH" ]]; then
    echo -e "${RED}  ✗ Detached HEAD state${NC}"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
else
    echo -e "${GREEN}  ✓ Branch: $CURRENT_BRANCH${NC}"
fi

# Check 3: Unfinished merge
if [[ -f .git/MERGE_HEAD ]]; then
    echo -e "${RED}  ✗ Unfinished merge detected${NC}"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
    if [[ "$FIX_MODE" == true ]]; then
        echo -e "${YELLOW}  → Attempting to complete merge...${NC}"
        git commit --no-edit 2>/dev/null && echo -e "${GREEN}  ✓ Merge completed${NC}" || echo -e "${RED}  ✗ Auto-fix failed${NC}"
    else
        echo -e "${YELLOW}  → Run with --fix to auto-complete${NC}"
    fi
else
    echo -e "${GREEN}  ✓ No unfinished merge${NC}"
fi

# Check 4: Remote sync status
echo -e "${BLUE}[2/10]${NC} Remote Sync"
git fetch origin "$CURRENT_BRANCH" 2>/dev/null || git fetch origin main 2>/dev/null || true
LOCAL_COMMIT=$(git rev-parse @ 2>/dev/null || echo "")
REMOTE_COMMIT=$(git rev-parse @{u} 2>/dev/null || echo "")

if [[ "$LOCAL_COMMIT" != "$REMOTE_COMMIT" ]]; then
    if [[ -z "$REMOTE_COMMIT" ]]; then
        echo -e "${YELLOW}  ⚠ No upstream branch set${NC}"
        WARNINGS_FOUND=$((WARNINGS_FOUND + 1))
    else
        echo -e "${YELLOW}  ⚠ Branch out of sync with remote${NC}"
        WARNINGS_FOUND=$((WARNINGS_FOUND + 1))
        if [[ "$FIX_MODE" == true ]]; then
            echo -e "${YELLOW}  → Pulling latest changes...${NC}"
            git pull --ff-only 2>/dev/null && echo -e "${GREEN}  ✓ Synced${NC}" || echo -e "${RED}  ✗ Auto-sync failed${NC}"
        fi
    fi
else
    echo -e "${GREEN}  ✓ Synced with remote${NC}"
fi

# Check 5: Uncommitted changes
echo -e "${BLUE}[3/10]${NC} Working Tree"
UNCOMMITTED=$(git status --porcelain | wc -l | tr -d ' ')
if [[ "$UNCOMMITTED" -gt 0 ]]; then
    echo -e "${YELLOW}  ⚠ $UNCOMMITTED uncommitted change(s)${NC}"
    git status --short | head -5
    if [[ "$UNCOMMITTED" -gt 5 ]]; then
        echo "  ... and $((UNCOMMITTED - 5)) more"
    fi
    WARNINGS_FOUND=$((WARNINGS_FOUND + 1))
else
    echo -e "${GREEN}  ✓ Working tree clean${NC}"
fi

# Check 6: Python environment
echo -e "${BLUE}[4/10]${NC} Python Environment"
if [[ ! -d .venv ]]; then
    echo -e "${RED}  ✗ Virtual environment missing${NC}"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
    if [[ "$FIX_MODE" == true ]]; then
        echo -e "${YELLOW}  → Creating .venv...${NC}"
        python3 -m venv .venv
        echo -e "${GREEN}  ✓ Created${NC}"
    fi
else
    echo -e "${GREEN}  ✓ Virtual environment exists${NC}"

    # Check activation
    if [[ -z "$VIRTUAL_ENV" ]]; then
        echo -e "${YELLOW}  ⚠ Environment not activated${NC}"
        WARNINGS_FOUND=$((WARNINGS_FOUND + 1))
        echo -e "${YELLOW}  → Run: source .venv/bin/activate${NC}"
    else
        echo -e "${GREEN}  ✓ Environment activated${NC}"
    fi
fi

# Check 7: Required scripts
echo -e "${BLUE}[5/10]${NC} Workflow Scripts"
REQUIRED_SCRIPTS=(
    "scripts/ai_commit.sh"
    "scripts/safe_push.sh"
    "scripts/should_use_pr.sh"
    "scripts/recover_git_state.sh"
)

MISSING=0
for script in "${REQUIRED_SCRIPTS[@]}"; do
    if [[ ! -f "$script" ]]; then
        echo -e "${RED}  ✗ Missing: $script${NC}"
        MISSING=$((MISSING + 1))
    fi
done

if [[ $MISSING -eq 0 ]]; then
    echo -e "${GREEN}  ✓ All required scripts present${NC}"
else
    echo -e "${RED}  ✗ $MISSING script(s) missing${NC}"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
fi

# Check 8: Script permissions
echo -e "${BLUE}[6/10]${NC} Script Permissions"
NON_EXECUTABLE=0
for script in scripts/*.sh; do
    if [[ ! -x "$script" ]]; then
        NON_EXECUTABLE=$((NON_EXECUTABLE + 1))
    fi
done

if [[ $NON_EXECUTABLE -gt 0 ]]; then
    echo -e "${YELLOW}  ⚠ $NON_EXECUTABLE script(s) not executable${NC}"
    WARNINGS_FOUND=$((WARNINGS_FOUND + 1))
    if [[ "$FIX_MODE" == true ]]; then
        echo -e "${YELLOW}  → Fixing permissions...${NC}"
        chmod +x scripts/*.sh 2>/dev/null || true
        echo -e "${GREEN}  ✓ Fixed${NC}"
    fi
else
    echo -e "${GREEN}  ✓ All scripts executable${NC}"
fi

# Check 9: Recent test status (expensive, skip in quick mode)
if [[ "$QUICK_MODE" == false ]]; then
    echo -e "${BLUE}[7/10]${NC} Test Status"
    if [[ -f "Python/test_stats.json" ]]; then
        # Parse test stats
        TOTAL_TESTS=$(grep -o '"total_tests":[^,]*' Python/test_stats.json | cut -d':' -f2 | tr -d ' ' || echo "0")
        PASSED_TESTS=$(grep -o '"passed_tests":[^,]*' Python/test_stats.json | cut -d':' -f2 | tr -d ' ' || echo "0")

        if [[ "$TOTAL_TESTS" -gt 0 ]]; then
            echo -e "${GREEN}  ✓ Last run: $PASSED_TESTS/$TOTAL_TESTS tests passed${NC}"
        else
            echo -e "${YELLOW}  ⚠ No test stats available${NC}"
            WARNINGS_FOUND=$((WARNINGS_FOUND + 1))
        fi
    else
        echo -e "${YELLOW}  ⚠ Test stats file missing${NC}"
        WARNINGS_FOUND=$((WARNINGS_FOUND + 1))
    fi
else
    echo -e "${BLUE}[7/10]${NC} Test Status"
    echo -e "${YELLOW}  ⊘ Skipped (quick mode)${NC}"
fi

# Check 10: Documentation state
echo -e "${BLUE}[8/10]${NC} Documentation"
DOCS_UNCOMMITTED=$(git status --porcelain docs/ 2>/dev/null | wc -l | tr -d ' ')
if [[ "$DOCS_UNCOMMITTED" -gt 0 ]]; then
    echo -e "${YELLOW}  ⚠ $DOCS_UNCOMMITTED uncommitted doc change(s)${NC}"
    WARNINGS_FOUND=$((WARNINGS_FOUND + 1))
else
    echo -e "${GREEN}  ✓ Documentation in sync${NC}"
fi

# Check 11: Version consistency (expensive, skip in quick mode)
if [[ "$QUICK_MODE" == false ]]; then
    echo -e "${BLUE}[9/10]${NC} Version Consistency"
    if [[ -f "scripts/check_doc_versions.py" ]]; then
        # Run version check
        .venv/bin/python scripts/check_doc_versions.py --quiet 2>&1 | grep -q "All versions consistent" && {
            echo -e "${GREEN}  ✓ Version references consistent${NC}"
        } || {
            echo -e "${YELLOW}  ⚠ Version drift detected${NC}"
            WARNINGS_FOUND=$((WARNINGS_FOUND + 1))
            if [[ "$FIX_MODE" == true ]]; then
                echo -e "${YELLOW}  → Auto-fixing versions...${NC}"
                .venv/bin/python scripts/check_doc_versions.py --fix >/dev/null 2>&1
                echo -e "${GREEN}  ✓ Fixed${NC}"
            else
                echo -e "${YELLOW}  → Run with --fix to auto-correct${NC}"
            fi
        }
    else
        echo -e "${YELLOW}  ⊘ Version check script missing${NC}"
    fi
else
    echo -e "${BLUE}[9/10]${NC} Version Consistency"
    echo -e "${YELLOW}  ⊘ Skipped (quick mode)${NC}"
fi

# Check 12: Disk space
echo -e "${BLUE}[10/10]${NC} Disk Space"
AVAILABLE_GB=$(df -h . | tail -1 | awk '{print $4}' | sed 's/Gi*//')
if [[ ${AVAILABLE_GB%.*} -lt 5 ]]; then
    echo -e "${RED}  ✗ Low disk space: ${AVAILABLE_GB}GB${NC}"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
else
    echo -e "${GREEN}  ✓ Disk space: ${AVAILABLE_GB}GB available${NC}"
fi

# Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [[ $ISSUES_FOUND -eq 0 ]] && [[ $WARNINGS_FOUND -eq 0 ]]; then
    echo -e "${GREEN}✓ ALL CHECKS PASSED${NC}"
    echo -e "${GREEN}You're ready to start working!${NC}"
    EXIT_CODE=0
elif [[ $ISSUES_FOUND -eq 0 ]]; then
    echo -e "${YELLOW}⚠ $WARNINGS_FOUND WARNING(S) FOUND${NC}"
    echo -e "${YELLOW}You can proceed, but review warnings above${NC}"
    EXIT_CODE=0
else
    echo -e "${RED}✗ $ISSUES_FOUND ISSUE(S) FOUND${NC}"
    if [[ $WARNINGS_FOUND -gt 0 ]]; then
        echo -e "${YELLOW}  + $WARNINGS_FOUND warning(s)${NC}"
    fi
    echo -e "${RED}Fix issues before continuing${NC}"
    if [[ "$FIX_MODE" == false ]]; then
        echo -e "${YELLOW}Run with --fix to auto-fix common issues${NC}"
    fi
    EXIT_CODE=1
fi
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Show recommended next actions
if [[ $EXIT_CODE -eq 0 ]]; then
    echo "📋 Recommended Actions:"
    echo ""

    # Check what kind of work is pending
    if [[ $DOCS_UNCOMMITTED -gt 0 ]]; then
        echo "  1. Review doc changes: git status docs/"
        echo "  2. Commit docs: ./scripts/ai_commit.sh 'docs: ...'"
    elif [[ $UNCOMMITTED -gt 0 ]]; then
        echo "  1. Review changes: git status"
        echo "  2. Decide: ./scripts/should_use_pr.sh --explain"
        echo "  3. Commit: ./scripts/ai_commit.sh 'message'"
    else
        echo "  1. Review TASKS.md for current work"
        echo "  2. Start new task: ./scripts/create_task_pr.sh TASK-XXX '...'"
        echo "  3. Or make direct changes and commit"
    fi
    echo ""
fi

exit $EXIT_CODE

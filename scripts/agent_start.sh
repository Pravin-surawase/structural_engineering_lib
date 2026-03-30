#!/bin/bash
# Unified Agent Start Script
# One command to onboard any agent and start a session
#
# Usage:
#   ./scripts/agent_start.sh                         # Default (full checks)
#   ./scripts/agent_start.sh --quick                 # Skip detailed checks
#   ./scripts/agent_start.sh --agent backend         # Agent-specific context
#   ./scripts/agent_start.sh --agent frontend        # Agent-specific context
#   ./scripts/agent_start.sh --worktree AGENT_5      # Background agent worktree
#   ./scripts/agent_start.sh --skip-preflight        # Skip preflight (for recovery)
#
# Available agents (11):
#   orchestrator, backend, frontend, api-developer, structural-engineer,
#   reviewer, tester, doc-master, ops, governance, ui-designer
#
# This script handles (all-in-one):
#   1. Git hooks + pager config (prevents terminal lock)
#   2. Environment setup (venv, dependencies)
#   3. Pre-flight checks (git state, imports)
#   4. Session start via session.py
#   5. Agent-specific context via agent_context.py
#
# Created: 2026-01-11 (Session 13 Part 5)
# Updated: 2026-03-28 — v3.0: Named agents via agent_context.py, removed legacy numbered agents

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'
BOLD='\033[1m'
DIM='\033[2m'

# Parse arguments
AGENT=""
QUICK=""
WORKTREE=""
SKIP_PREFLIGHT=""
while [[ $# -gt 0 ]]; do
    case $1 in
        --agent)
            AGENT="$2"
            shift 2
            ;;
        --quick|-q)
            QUICK="--quick"
            shift
            ;;
        --worktree)
            WORKTREE="$2"
            shift 2
            ;;
        --skip-preflight)
            SKIP_PREFLIGHT="true"
            shift
            ;;
        --help|-h)
            echo "Usage: ./scripts/agent_start.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --agent NAME      Load agent-specific context (see agents below)"
            echo "  --quick           Skip detailed checks, faster startup"
            echo "  --worktree NAME   Create/use a worktree for background agent"
            echo "  --skip-preflight  Skip pre-flight checks (for recovery)"
            echo ""
            echo "Agents: orchestrator, backend, frontend, api-developer,"
            echo "  structural-engineer, reviewer, tester, doc-master, ops, governance, ui-designer"
            echo ""
            echo "Examples:"
            echo "  ./scripts/agent_start.sh                      # Full checks"
            echo "  ./scripts/agent_start.sh --quick              # Fast mode"
            echo "  ./scripts/agent_start.sh --agent backend      # Backend agent context"
            echo "  ./scripts/agent_start.sh --agent frontend     # Frontend agent context"
            echo "  ./scripts/agent_start.sh --worktree AGENT_5   # Background agent"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

cd "$PROJECT_ROOT"

# Ensure all scripts are executable
chmod +x "$SCRIPT_DIR"/*.sh 2>/dev/null || true

echo ""
echo -e "${BOLD}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}║           🤖 Agent Start - Unified Onboarding v3.0         ║${NC}"
echo -e "${BOLD}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Step 0: Install Git Hooks (ensures enforcement is active)
echo -e "${BLUE}[0/6]${NC} Installing git hooks (enforcement)..."
if [ -f "$SCRIPT_DIR/install_git_hooks.sh" ]; then
    "$SCRIPT_DIR/install_git_hooks.sh" > /dev/null 2>&1 && {
        echo -e "  ${GREEN}✓${NC} Git hooks installed (manual git blocked)"
    } || {
        echo -e "  ${YELLOW}⚠${NC} Git hooks installation had warnings"
    }
else
    echo -e "  ${YELLOW}⚠${NC} install_git_hooks.sh not found"
fi

# Step 1: Git Pager Configuration (inline — copilot_setup.sh was consolidated here)
echo -e "${BLUE}[1/6]${NC} Configuring git pager (prevents terminal lock)..."
git config --global core.pager cat 2>/dev/null || true
git config --global pager.status false 2>/dev/null || true
git config --global pager.branch false 2>/dev/null || true
git config --global pager.diff false 2>/dev/null || true
export GIT_EDITOR=":"
export PAGER=cat
echo -e "  ${GREEN}✓${NC} Git pager disabled"

# Step 2: Environment Setup (inline — agent_setup.sh was consolidated here)
echo -e "${BLUE}[2/6]${NC} Running environment setup..."
if [ -f "$PROJECT_ROOT/.venv/bin/activate" ]; then
    source "$PROJECT_ROOT/.venv/bin/activate"
    echo -e "  ${GREEN}✓${NC} Virtual environment activated"
else
    echo -e "  ${RED}✗${NC} Virtual environment not found!"
    echo -e "  ${YELLOW}→${NC} Recovery steps:"
    echo -e "     1. Run: python3 -m venv .venv"
    echo -e "     2. Run: source .venv/bin/activate"
    echo -e "     3. Run: cd Python && pip install -e '.[dev]' && cd .."
    echo -e "     4. Then re-run: ./scripts/agent_start.sh"
    exit 1
fi

# Step 3: Pre-flight Check (skip in quick mode or if explicitly skipped)
echo -e "${BLUE}[3/6]${NC} Running pre-flight checks..."

# Dependency verification (skip in quick mode)
if [ -z "$QUICK" ]; then
    MISSING_DEPS=""

    # Check critical dependencies (fail fast if missing)
    "$PROJECT_ROOT/.venv/bin/python" -c "import pydantic" 2>/dev/null || MISSING_DEPS="$MISSING_DEPS pydantic"
    "$PROJECT_ROOT/.venv/bin/python" -c "import pandas" 2>/dev/null || MISSING_DEPS="$MISSING_DEPS pandas"
    "$PROJECT_ROOT/.venv/bin/python" -c "import numpy" 2>/dev/null || MISSING_DEPS="$MISSING_DEPS numpy"

    if [ -n "$MISSING_DEPS" ]; then
        echo -e "  ${YELLOW}⚠${NC} Missing dependencies:$MISSING_DEPS"
        echo -e "  ${YELLOW}→${NC} Run: .venv/bin/pip install -r requirements.txt"
        echo -e "  ${YELLOW}→${NC} Or:  .venv/bin/pip install -e \"Python[dev,dxf,render,report,pdf,validation,cad]\""
    else
        echo -e "  ${GREEN}✓${NC} Critical dependencies verified"
    fi
else
    echo -e "  ${YELLOW}⊘${NC} Dependency check skipped (quick mode)"
fi
if [ -n "$SKIP_PREFLIGHT" ]; then
    echo -e "  ${YELLOW}⊘${NC} Skipped (--skip-preflight)"
elif [ -n "$QUICK" ]; then
    # Quick mode: basic git state check only
    if git status --porcelain | grep -q '^UU\|^AA'; then
        echo -e "  ${YELLOW}⚠${NC} Unresolved merge conflicts detected"
    else
        echo -e "  ${GREEN}✓${NC} Quick pre-flight passed"
    fi
else
    # Full mode: inline pre-flight checks (agent_preflight.sh was consolidated here)
    PREFLIGHT_OK=true
    # Check for merge conflicts
    if git status --porcelain | grep -q '^UU\|^AA'; then
        echo -e "  ${RED}✗${NC} Unresolved merge conflicts!"
        PREFLIGHT_OK=false
    fi
    # Check for broken imports
    if [ -f "$PROJECT_ROOT/.venv/bin/python" ]; then
        "$PROJECT_ROOT/.venv/bin/python" -c "import structural_lib" 2>/dev/null || {
            echo -e "  ${YELLOW}⚠${NC} structural_lib import failed (check Python/)"
        }
    fi
    if [ "$PREFLIGHT_OK" = false ]; then
        echo -e "  ${RED}✗${NC} Pre-flight failed! Fix issues before continuing."
        echo -e "  ${YELLOW}→${NC} Run with --skip-preflight to bypass (not recommended)"
        exit 1
    else
        echo -e "  ${GREEN}✓${NC} Pre-flight checks passed"
    fi
fi

# Step 3b: Git hygiene (non-blocking)
if [ -z "$QUICK" ] && [ -z "$SKIP_PREFLIGHT" ]; then
    echo -e "${BLUE}[3b/6]${NC} Git hygiene..."

    # Prune stale remote tracking refs (silent network call)
    BEFORE_PRUNE=$(git branch -r 2>/dev/null | wc -l | tr -d ' ')
    git fetch --prune --quiet 2>/dev/null || true
    AFTER_PRUNE=$(git branch -r 2>/dev/null | wc -l | tr -d ' ')
    PRUNED=$((BEFORE_PRUNE - AFTER_PRUNE))
    [ "$PRUNED" -gt 0 ] && echo -e "  ${GREEN}✓${NC} Pruned $PRUNED stale remote tracking ref(s)"

    # Check for stale local branches (merged into main)
    STALE_MERGED=$(git branch --merged main 2>/dev/null | grep -v '^\*\|main$' | wc -l | tr -d ' ')
    if [ "$STALE_MERGED" -gt 0 ]; then
        echo -e "  ${YELLOW}⚠${NC} $STALE_MERGED local branch(es) already merged into main"
        git branch --merged main 2>/dev/null | grep -v '^\*\|main$' | head -5
        echo -e "  ${DIM}Cleanup: .venv/bin/python scripts/cleanup_stale_branches.py --delete${NC}"
    fi

    # Check for unmerged branches
    STALE_UNMERGED=$(git branch --no-merged main 2>/dev/null | grep -v '^\*' | wc -l | tr -d ' ')
    if [ "$STALE_UNMERGED" -gt 0 ]; then
        echo -e "  ${YELLOW}⚠${NC} $STALE_UNMERGED local branch(es) NOT merged into main"
        git branch --no-merged main 2>/dev/null | grep -v '^\*' | head -5
    fi

    # Check stale auto-stashes (warn only, no auto-drop)
    STASH_COUNT=$(git stash list 2>/dev/null | grep -c "auto-stash" || echo "0")
    if [ "$STASH_COUNT" -gt 2 ]; then
        echo -e "  ${YELLOW}⚠${NC} $STASH_COUNT auto-stash entries — review: git stash list"
    fi

    # Check for open PRs
    OPEN_PRS=$(gh pr list --state open --limit 5 --json number,title 2>/dev/null || echo "")
    if [ -n "$OPEN_PRS" ] && [ "$OPEN_PRS" != "[]" ]; then
        PR_COUNT=$(echo "$OPEN_PRS" | grep -c '"number"' || echo "0")
        echo -e "  ${YELLOW}⚠${NC} $PR_COUNT open PR(s):"
        echo "$OPEN_PRS" | grep '"title"' | sed 's/.*"title": *"//;s/".*/  /' | head -3
    fi

    if [ "$PRUNED" -eq 0 ] && [ "$STALE_MERGED" -eq 0 ] && [ "$STALE_UNMERGED" -eq 0 ] && [ "$STASH_COUNT" -le 2 ]; then
        echo -e "  ${GREEN}✓${NC} Git state clean"
    fi
fi

# Step 4: Start Session
echo -e "${BLUE}[4/6]${NC} Starting session..."
if [ -f "$PROJECT_ROOT/.venv/bin/python" ]; then
    "$PROJECT_ROOT/.venv/bin/python" scripts/session.py start $QUICK
else
    echo -e "  ${RED}✗${NC} Python interpreter not found in .venv"
    echo ""
    echo -e "  ${YELLOW}💡 Tip: Collect diagnostics for troubleshooting:${NC}"
    echo "     .venv/bin/python scripts/collect_diagnostics.py > diagnostics.txt"
    exit 1
fi

# Step 5: Agent-specific guidance
echo -e "${BLUE}[5/6]${NC} Ready!"
echo ""
echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Agent-specific guidance via agent_context.py
if [ -n "$AGENT" ]; then
    echo ""
    if [ -f "$SCRIPT_DIR/agent_context.py" ]; then
        "$PROJECT_ROOT/.venv/bin/python" "$SCRIPT_DIR/agent_context.py" "$AGENT" 2>&1 || {
            echo -e "  ${RED}Unknown agent '$AGENT'${NC}"
            echo -e "  Run: .venv/bin/python scripts/agent_context.py --list"
        }
    else
        echo -e "  ${RED}✗${NC} agent_context.py not found at $SCRIPT_DIR/agent_context.py"
    fi
    echo ""
fi

# Worktree-specific guidance
if [ -n "$WORKTREE" ]; then
    echo ""
    echo -e "${BOLD}🌳 Worktree Mode: $WORKTREE${NC}"
    echo ""
    echo "  Your changes are isolated in this worktree."
    echo "  When done, submit work:"
    echo "    cd $PROJECT_ROOT"
    echo "    ./scripts/ai_commit.sh \"feat: description\""
    echo ""
fi

# Essential guidance (concise — agent_context.py provides per-agent details)
echo -e "${BOLD}📚 Essential Docs${NC}"
echo "  • docs/TASKS.md (current work)"
echo "  • docs/planning/next-session-brief.md (last session handoff)"
echo "  • .github/copilot-instructions.md (all rules)"
echo ""

echo -e "${BOLD}⚡ THE ONE RULE${NC}"
echo -e "  ${RED}NEVER use manual git commands!${NC}"
echo "  ALWAYS use: ./scripts/ai_commit.sh \"message\""
echo ""

echo -e "${BOLD}🔍 Key Commands${NC}"
echo "  ./scripts/ai_commit.sh \"message\"                        # Commit (THE ONE RULE)"
echo "  .venv/bin/python scripts/agent_context.py <agent>       # Agent-specific context"
echo "  .venv/bin/python scripts/find_automation.py \"task\"      # Find the right script"
echo "  .venv/bin/python scripts/discover_api_signatures.py fn  # API param names"
echo ""

# Docker status check
echo -e "${BOLD}🐳 Docker (Colima on Mac)${NC}"
if command -v colima &> /dev/null; then
    if colima status &> /dev/null; then
        echo -e "  ${GREEN}✓${NC} Colima running"
    else
        echo -e "  ${YELLOW}⊘${NC} Colima not running → colima start --cpu 4 --memory 4"
    fi
elif command -v docker &> /dev/null && docker info &> /dev/null; then
    echo -e "  ${GREEN}✓${NC} Docker available"
else
    echo -e "  ${YELLOW}⊘${NC} Docker not running (optional for local dev)"
fi
echo ""

# Mistake review (quick refresher)
if [ -f "$SCRIPT_DIR/agent_mistakes_report.sh" ]; then
    echo -e "${BOLD}Mistake Review${NC}"
    "$SCRIPT_DIR/agent_mistakes_report.sh"
    echo ""
fi

echo -e "${GREEN}Ready to work!${NC}"

#!/bin/bash
# Unified Agent Start Script
# One command to onboard any agent and start a session
#
# Usage:
#   ./scripts/agent_start.sh              # Default (full checks)
#   ./scripts/agent_start.sh --quick      # Skip detailed checks
#   ./scripts/agent_start.sh --agent 6    # Agent 6 (UI focus)
#   ./scripts/agent_start.sh --agent 8    # Agent 8 (Git/Automation)
#   ./scripts/agent_start.sh --agent 9    # Agent 9 (Governance)
#   ./scripts/agent_start.sh --worktree AGENT_5  # Background agent worktree
#   ./scripts/agent_start.sh --skip-preflight    # Skip preflight (for recovery)
#
# This script handles (all-in-one):
#   1. Git pager config (prevents terminal lock)
#   2. Environment setup (venv, dependencies)
#   3. Pre-flight checks (git state, imports)
#   4. Session start via session.py
#
# Created: 2026-01-11 (Session 13 Part 5)
# Updated: 2026-01-11 (Session 13 Part 7) - v2.1: Fixed full mode, worktree passthrough

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
            echo "  --agent N         Agent-specific configuration (6, 8, or 9)"
            echo "  --quick           Skip detailed checks, faster startup"
            echo "  --worktree NAME   Create/use a worktree for background agent"
            echo "  --skip-preflight  Skip pre-flight checks (for recovery)"
            echo ""
            echo "Examples:"
            echo "  ./scripts/agent_start.sh              # Full checks"
            echo "  ./scripts/agent_start.sh --quick      # Fast mode"
            echo "  ./scripts/agent_start.sh --agent 8    # Agent 8 focus"
            echo "  ./scripts/agent_start.sh --worktree AGENT_5  # Background agent"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

cd "$PROJECT_ROOT"

echo ""
echo -e "${BOLD}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}║           🤖 Agent Start - Unified Onboarding v2.2         ║${NC}"
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

# Step 2.5: Dependency Verification (quick check for critical packages)
if [ -z "$QUICK" ]; then
    echo -e "${BLUE}[2.5/6]${NC} Verifying critical dependencies..."
    MISSING_DEPS=""

    # Check critical dependencies (fail fast if missing)
    "$PROJECT_ROOT/.venv/bin/python" -c "import pydantic" 2>/dev/null || MISSING_DEPS="$MISSING_DEPS pydantic"
    "$PROJECT_ROOT/.venv/bin/python" -c "import streamlit" 2>/dev/null || MISSING_DEPS="$MISSING_DEPS streamlit"
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

# Agent-specific guidance
if [ -n "$AGENT" ]; then
    echo ""
    echo -e "${BOLD}🎯 Agent $AGENT Quick Start${NC}"
    echo ""
    case $AGENT in
        6)
            echo -e "  ${YELLOW}Focus:${NC} UI/UX, Streamlit app improvements"
            echo -e "  ${YELLOW}Hub:${NC}   docs/agents/guides/agent-6-quick-start.md"
            echo -e "  ${YELLOW}Tasks:${NC} Look for UI-* or STREAMLIT-* in TASKS.md"
            echo ""
            echo -e "  ${BOLD}Key Commands:${NC}"
            echo "    .venv/bin/python scripts/check_streamlit.py --all-pages"
            echo "    .venv/bin/python -m streamlit run streamlit_app/Home.py"
            ;;
        8)
            echo -e "  ${YELLOW}Focus:${NC} Git workflow, automation, CI/CD"
            echo -e "  ${YELLOW}Hub:${NC}   docs/agents/guides/agent-8-automation.md"
            echo -e "  ${YELLOW}Tasks:${NC} Look for AUTOMATION-* or GIT-* in TASKS.md"
            echo ""
            echo -e "  ${BOLD}Key Commands:${NC}"
            echo "    ./scripts/ai_commit.sh \"message\"   # All commits"
            echo "    ./scripts/safe_push.sh \"message\"   # Direct push"
            echo "    git worktree list                  # Check worktrees"
            ;;
        9)
            echo -e "  ${YELLOW}Focus:${NC} Governance, folder structure, documentation"
            echo -e "  ${YELLOW}Hub:${NC}   docs/agents/guides/agent-9-governance-hub.md"
            echo -e "  ${YELLOW}Tasks:${NC} Look for GOV-* or DOC-* in TASKS.md"
            echo ""
            echo -e "  ${BOLD}Key Commands:${NC}"
            echo "    .venv/bin/python scripts/check_governance.py --structure"
            echo "    .venv/bin/python scripts/check_governance.py --compliance"
            echo "    .venv/bin/python scripts/check_links.py"
            ;;
        *)
            echo -e "  ${YELLOW}Unknown agent $AGENT${NC}"
            echo -e "  Available agents: 6, 8, 9"
            ;;
    esac
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

# Common guidance
echo -e "${BOLD}📚 Essential Docs${NC}"
echo "  • docs/getting-started/agent-essentials.md (V3 stack reference)"
echo "  • docs/getting-started/agent-bootstrap.md (quick start)"
echo "  • docs/TASKS.md (current work)"
echo "  • .github/copilot-instructions.md (all rules)"
echo ""

# V3 Stack Overview - CRITICAL TO PREVENT DUPLICATE CODE
echo -e "${BOLD}🏗️ V3 Stack — DON'T REINVENT!${NC}"
echo ""
echo -e "  ${YELLOW}Before writing code, check what exists:${NC}"
echo ""
echo "  React Hooks (react_app/src/hooks/):"
echo "    useBeamGeometry     → 3D rebar/stirrup positions from API"
echo "    useCSVFileImport    → CSV import via library adapters (40+ columns)"
echo "    useBatchDesign      → Batch design all imported beams"
echo ""
echo "  FastAPI Endpoints (http://localhost:8000/docs):"
echo "    POST /api/v1/import/csv        → CSV file import"
echo "    POST /api/v1/geometry/beam/full → Full 3D geometry"
echo "    POST /api/v1/design/beam       → Beam design"
echo ""
echo "  Library (Python/structural_lib/):"
echo "    api.py              → 43 public functions"
echo "    adapters.py         → GenericCSVAdapter, ETABSAdapter"
echo "    geometry_3d.py      → beam_to_3d_geometry()"
echo ""

echo -e "${BOLD}⚡ THE ONE RULE${NC}"
echo -e "  ${RED}NEVER use manual git commands!${NC}"
echo "  ALWAYS use: ./scripts/ai_commit.sh \"message\""
echo ""
echo -e "${BOLD}🧭 Git Workflow Quick Reference${NC}"
echo "  1) ./scripts/ai_commit.sh \"message\""
echo "  2) ./scripts/finish_task_pr.sh TASK-XXX \"description\" [--with-session-docs]"
echo "  3) git status && git log --oneline -3"
echo "  Docs: docs/git-automation/README.md"
echo ""

# Docker status check
echo -e "${BOLD}🐳 Docker (FastAPI Backend)${NC}"
if command -v docker &> /dev/null && docker info &> /dev/null; then
    echo -e "  ${GREEN}✓${NC} Docker available"
    echo "  docker compose up --build          # Production"
    echo "  docker compose -f docker-compose.dev.yml up  # Dev (hot reload)"
    echo "  API: http://localhost:8000/docs"
else
    echo -e "  ${YELLOW}⊘${NC} Docker not running (optional for local dev)"
    echo "  Start Docker Desktop or: brew install --cask docker"
fi
echo ""

# Mistake review (quick refresher)
if [ -f "$SCRIPT_DIR/agent_mistakes_report.sh" ]; then
    echo -e "${BOLD}Mistake Review${NC}"
    "$SCRIPT_DIR/agent_mistakes_report.sh"
    echo ""
fi

echo -e "${GREEN}Ready to work!${NC}"

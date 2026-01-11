#!/bin/bash
# Unified Agent Start Script
# One command to onboard any agent and start a session
#
# Usage:
#   ./scripts/agent_start.sh              # Default (no agent-specific config)
#   ./scripts/agent_start.sh --agent 6    # Agent 6 (UI focus)
#   ./scripts/agent_start.sh --agent 8    # Agent 8 (Git/Automation)
#   ./scripts/agent_start.sh --agent 9    # Agent 9 (Governance)
#   ./scripts/agent_start.sh --quick      # Skip detailed checks
#
# This script replaces the need to run:
#   1. source scripts/copilot_setup.sh (git pager config)
#   2. ./scripts/agent_setup.sh (environment setup)
#   3. ./scripts/agent_preflight.sh (pre-flight checks)
#   4. .venv/bin/python scripts/start_session.py (session start)
#
# Created: 2026-01-11 (Session 13 Part 5)

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
        --help|-h)
            echo "Usage: ./scripts/agent_start.sh [--agent 6|8|9] [--quick]"
            echo ""
            echo "Options:"
            echo "  --agent N   Agent-specific configuration (6, 8, or 9)"
            echo "  --quick     Skip detailed checks, faster startup"
            echo ""
            echo "Examples:"
            echo "  ./scripts/agent_start.sh              # Default start"
            echo "  ./scripts/agent_start.sh --agent 8    # Agent 8 focus"
            echo "  ./scripts/agent_start.sh --quick      # Fast mode"
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
echo -e "${BOLD}║           🤖 Agent Start - Unified Onboarding              ║${NC}"
echo -e "${BOLD}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Step 1: Git Pager Configuration
echo -e "${BLUE}[1/4]${NC} Configuring git pager (prevents terminal lock)..."
git config --global core.pager cat 2>/dev/null || true
git config --global pager.status false 2>/dev/null || true
git config --global pager.branch false 2>/dev/null || true
git config --global pager.diff false 2>/dev/null || true
export GIT_EDITOR=":"
export PAGER=cat
echo -e "  ${GREEN}✓${NC} Git pager disabled"

# Step 2: Environment Setup
echo -e "${BLUE}[2/4]${NC} Setting up environment..."
if [ -f "$PROJECT_ROOT/.venv/bin/activate" ]; then
    source "$PROJECT_ROOT/.venv/bin/activate"
    echo -e "  ${GREEN}✓${NC} Virtual environment activated"
else
    echo -e "  ${RED}✗${NC} Virtual environment not found! Run: python -m venv .venv"
    exit 1
fi

# Step 3: Pre-flight Check (optional in quick mode)
if [ -z "$QUICK" ]; then
    echo -e "${BLUE}[3/4]${NC} Running pre-flight checks..."
    if [ -f "$SCRIPT_DIR/agent_preflight.sh" ]; then
        "$SCRIPT_DIR/agent_preflight.sh" --quick 2>/dev/null || true
    fi
else
    echo -e "${BLUE}[3/4]${NC} Skipping pre-flight (quick mode)"
fi

# Step 4: Start Session
echo -e "${BLUE}[4/4]${NC} Starting session..."
.venv/bin/python scripts/start_session.py $QUICK

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
            echo "    .venv/bin/python scripts/check_streamlit_issues.py --all-pages"
            echo "    .venv/bin/python -m streamlit run streamlit_app/Home.py"
            ;;
        8)
            echo -e "  ${YELLOW}Focus:${NC} Git workflow, automation, CI/CD"
            echo -e "  ${YELLOW}Hub:${NC}   docs/agents/guides/agent-8-quick-start.md"
            echo -e "  ${YELLOW}Tasks:${NC} Look for AUTOMATION-* or GIT-* in TASKS.md"
            echo ""
            echo -e "  ${BOLD}Key Commands:${NC}"
            echo "    ./scripts/ai_commit.sh \"message\"   # All commits"
            echo "    ./scripts/safe_push.sh \"message\"   # Direct push"
            echo "    ./scripts/worktree_manager.sh list  # Manage worktrees"
            ;;
        9)
            echo -e "  ${YELLOW}Focus:${NC} Governance, folder structure, documentation"
            echo -e "  ${YELLOW}Hub:${NC}   docs/agents/guides/agent-9-quick-start.md"
            echo -e "  ${YELLOW}Tasks:${NC} Look for GOV-* or DOC-* in TASKS.md"
            echo ""
            echo -e "  ${BOLD}Key Commands:${NC}"
            echo "    .venv/bin/python scripts/validate_folder_structure.py"
            echo "    .venv/bin/python scripts/check_governance_compliance.py"
            echo "    .venv/bin/python scripts/check_links.py"
            ;;
        *)
            echo -e "  ${YELLOW}Unknown agent $AGENT${NC}"
            echo -e "  Available agents: 6, 8, 9"
            ;;
    esac
    echo ""
fi

# Common guidance
echo -e "${BOLD}📚 Essential Docs${NC}"
echo "  • docs/getting-started/agent-bootstrap.md (quick start)"
echo "  • docs/TASKS.md (current work)"
echo "  • .github/copilot-instructions.md (all rules)"
echo ""
echo -e "${BOLD}⚡ THE ONE RULE${NC}"
echo -e "  ${RED}NEVER use manual git commands!${NC}"
echo "  ALWAYS use: ./scripts/ai_commit.sh \"message\""
echo ""
echo -e "${GREEN}Ready to work!${NC}"

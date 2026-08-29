#!/bin/bash
# Unified Agent Start Script
# One command to onboard any agent and start a session
#
# Usage:
#   ./scripts/agent_start.sh                         # Default (full checks)
#   ./scripts/agent_start.sh --quick                 # Skip detailed checks
#   ./scripts/agent_start.sh --agent backend         # Agent-specific context
#   ./scripts/agent_start.sh --agent frontend        # Agent-specific context
#   ./scripts/agent_start.sh --worktree AGENT_5      # Worktree-specific guidance
#   ./scripts/agent_start.sh --skip-preflight        # Skip preflight (for recovery)
#   ./scripts/agent_start.sh --preflight-only        # Environment proof without context
#
# Available agents come from agents/agent_registry.json.
#
# This script handles (all-in-one):
#   1. Codex-native Git boundary + process-local pager config
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
PYTHON_RUNTIME="$SCRIPT_DIR/python_runtime.sh"

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
PREFLIGHT_ONLY=""
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
        --preflight-only)
            PREFLIGHT_ONLY="true"
            shift
            ;;
        --help|-h)
            echo "Usage: ./scripts/agent_start.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --agent NAME      Load agent-specific context (see agents below)"
            echo "  --quick           Skip detailed checks, faster startup"
            echo "  --worktree NAME   Display worktree-specific guidance"
            echo "  --skip-preflight  Skip pre-flight checks (for recovery)"
            echo "  --preflight-only  Stop after environment preflight; no session/context output"
            echo ""
            echo "Agents: ./scripts/python_runtime.sh scripts/agent_context.py --list"
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

echo ""
echo -e "${BOLD}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}║           🤖 Agent Start - Unified Onboarding v3.0         ║${NC}"
echo -e "${BOLD}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Step 0: Confirm the retired wrapper-enforcement hook path is not active.
echo -e "${BLUE}[0/6]${NC} Checking Codex-native Git mode..."
HOOKS_PATH=$(git config --get core.hooksPath 2>/dev/null || true)
if [[ "$HOOKS_PATH" == "scripts/git-hooks" || "$HOOKS_PATH" == */scripts/git-hooks ]]; then
    echo -e "  ${RED}✗${NC} Retired wrapper hooks are still configured."
    echo -e "  ${YELLOW}→${NC} Remove the local override: git config --unset core.hooksPath"
    exit 1
else
    echo -e "  ${GREEN}✓${NC} Repository Git wrapper enforcement is disabled"
fi

# Step 1: Process-local pager configuration (no global Git mutation).
echo -e "${BLUE}[1/6]${NC} Configuring process-local Git pager..."
export GIT_PAGER=cat
export GIT_EDITOR=":"
export PAGER=cat
echo -e "  ${GREEN}✓${NC} Git pager disabled"

# Step 2: Resolve the approved Python runtime for this or the primary worktree.
echo -e "${BLUE}[2/6]${NC} Resolving Python runtime..."
if [ ! -x "$PYTHON_RUNTIME" ]; then
    echo -e "  ${RED}✗${NC} Python runtime launcher not found: $PYTHON_RUNTIME"
    exit 1
fi
PYTHON_PATH=$("$PYTHON_RUNTIME" -c 'import sys; print(sys.executable)' 2>/dev/null) || {
    echo -e "  ${RED}✗${NC} No approved Python interpreter could be resolved"
    echo -e "  ${YELLOW}→${NC} Create .venv in the primary checkout or set STRUCTURAL_LIB_PYTHON"
    exit 1
}
echo -e "  ${GREEN}✓${NC} Python runtime: $PYTHON_PATH"
PYTHON_SOURCE=$("$PYTHON_RUNTIME" -c 'from pathlib import Path; import structural_lib; print(Path(structural_lib.__file__).resolve())' 2>/dev/null) || {
    echo -e "  ${RED}✗${NC} structural_lib could not be imported through the approved runtime"
    exit 1
}
EXPECTED_SOURCE="$PROJECT_ROOT/Python/structural_lib"
case "$(uname -s)" in
    MINGW*|MSYS*|CYGWIN*)
        NORMALIZED_PYTHON_SOURCE="$(cygpath -m "$PYTHON_SOURCE")"
        NORMALIZED_EXPECTED_SOURCE="$(cygpath -m "$EXPECTED_SOURCE")"
        ;;
    *)
        NORMALIZED_PYTHON_SOURCE="${PYTHON_SOURCE//\\//}"
        NORMALIZED_EXPECTED_SOURCE="${EXPECTED_SOURCE//\\//}"
        ;;
esac
case "$NORMALIZED_PYTHON_SOURCE" in
    "$NORMALIZED_EXPECTED_SOURCE"/*)
        echo -e "  ${GREEN}✓${NC} Python source binding: current worktree"
        ;;
    *)
        echo -e "  ${RED}✗${NC} Python source shadowing detected: $PYTHON_SOURCE"
        echo -e "  ${YELLOW}→${NC} Diagnose with: ./scripts/python_runtime.sh --diagnose"
        exit 1
        ;;
esac

# Step 3: Pre-flight Check (skip in quick mode or if explicitly skipped)
echo -e "${BLUE}[3/6]${NC} Running pre-flight checks..."

# Dependency verification (skip in quick mode)
if [ -z "$QUICK" ]; then
    MISSING_DEPS=""

    # Check critical dependencies (fail fast if missing)
    "$PYTHON_RUNTIME" -c "import pydantic" 2>/dev/null || MISSING_DEPS="$MISSING_DEPS pydantic"
    "$PYTHON_RUNTIME" -c "import pandas" 2>/dev/null || MISSING_DEPS="$MISSING_DEPS pandas"
    "$PYTHON_RUNTIME" -c "import numpy" 2>/dev/null || MISSING_DEPS="$MISSING_DEPS numpy"

    if [ -n "$MISSING_DEPS" ]; then
        echo -e "  ${YELLOW}⚠${NC} Missing dependencies:$MISSING_DEPS"
        echo -e "  ${YELLOW}→${NC} Install dependencies in the resolved environment before continuing"
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
    "$PYTHON_RUNTIME" -c "import structural_lib" 2>/dev/null || {
        echo -e "  ${YELLOW}⚠${NC} structural_lib import failed (check Python/)"
    }
    if [ "$PREFLIGHT_OK" = false ]; then
        echo -e "  ${RED}✗${NC} Pre-flight failed! Fix issues before continuing."
        echo -e "  ${YELLOW}→${NC} Run with --skip-preflight to bypass (not recommended)"
        exit 1
    else
        echo -e "  ${GREEN}✓${NC} Pre-flight checks passed"
    fi
fi

if [ -n "$PREFLIGHT_ONLY" ]; then
    echo -e "  ${GREEN}✓${NC} Environment preflight complete"
    exit 0
fi

# Step 4: Start Session
echo -e "${BLUE}[4/6]${NC} Starting session..."
"$PYTHON_RUNTIME" scripts/session.py start $QUICK

# Step 5: Agent-specific guidance
echo -e "${BLUE}[5/6]${NC} Ready!"
echo ""
echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Agent-specific guidance via agent_context.py
if [ -n "$AGENT" ]; then
    echo ""
    if [ -f "$SCRIPT_DIR/agent_context.py" ]; then
        "$PYTHON_RUNTIME" "$SCRIPT_DIR/agent_context.py" "$AGENT" 2>&1 || {
            echo -e "  ${RED}Unknown agent '$AGENT'${NC}"
            echo -e "  Run: ./scripts/python_runtime.sh scripts/agent_context.py --list"
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
    echo "  When done, return to the main Codex task for diff review and integration."
    echo ""
fi

# Essential guidance (concise — agent_context.py provides per-agent details)
echo -e "${BOLD}📚 Essential Docs${NC}"
echo "  • docs/TASKS.md (current work)"
echo "  • docs/planning/next-session-brief.md (last session handoff)"
echo "  • .github/copilot-instructions.md (all rules)"
echo ""

echo -e "${BOLD}Git and GitHub${NC}"
echo "  Codex reviews the diff, commits and pushes intended files, and manages the PR."
echo "  Canonical workflow: docs/git-automation/git-workflow-single-source.md"
echo ""

echo -e "${BOLD}🔍 Key Commands${NC}"
echo "  ./scripts/python_runtime.sh scripts/agent_context.py <agent>       # Agent-specific context"
echo "  ./scripts/python_runtime.sh scripts/find_automation.py \"task\"      # Find the right script"
echo "  ./scripts/python_runtime.sh scripts/discover_api_signatures.py fn  # API param names"
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

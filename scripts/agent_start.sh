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
ALLOW_CLEAN_MAIN_INTAKE=""
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
        --allow-clean-main-intake)
            ALLOW_CLEAN_MAIN_INTAKE="true"
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
            echo "  --allow-clean-main-intake  Admit clean synchronized main for read-only intake"
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

# Process-local display settings only; repository configuration is untouched.
export GIT_PAGER=cat
export GIT_EDITOR=":"
export PAGER=cat

# One maintained authority for Git state, Python source and effective hook proof.
# --skip-preflight skips optional app/dependency probes, never these safety facts.
PREFLIGHT_ARGS=(--expected-root "$PROJECT_ROOT")
if [ -n "$QUICK" ] || [ -n "$SKIP_PREFLIGHT" ]; then
    PREFLIGHT_ARGS+=(--environment-only)
fi
if [ -n "$ALLOW_CLEAN_MAIN_INTAKE" ]; then
    PREFLIGHT_ARGS+=(--allow-clean-main-intake)
fi
"$PYTHON_RUNTIME" "$SCRIPT_DIR/preflight.py" "${PREFLIGHT_ARGS[@]}"

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

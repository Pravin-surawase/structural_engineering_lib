#!/bin/bash
# Agent Environment Setup Script
# Prepares the environment for AI agent work
#
# Usage:
#   ./scripts/agent_setup.sh                    # Main agent setup
#   ./scripts/agent_setup.sh --worktree AGENT_5 # Background agent setup
#   ./scripts/agent_setup.sh --quick            # Skip slow checks

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# Parse arguments
WORKTREE_MODE=false
AGENT_NAME=""
QUICK_MODE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --worktree)
            WORKTREE_MODE=true
            AGENT_NAME="$2"
            shift 2
            ;;
        --quick)
            QUICK_MODE=true
            shift
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Usage: $0 [--worktree AGENT_NAME] [--quick]"
            exit 1
            ;;
    esac
done

# Get project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         Agent Environment Setup v1.0.0                ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

if [[ "$WORKTREE_MODE" == true ]]; then
    echo -e "${YELLOW}🤖 Mode: Background Agent (Worktree)${NC}"
    echo -e "${YELLOW}Agent Name: $AGENT_NAME${NC}"
else
    echo -e "${YELLOW}🤖 Mode: Main Agent${NC}"
fi
echo ""

# Step 1: Check Git repository
echo -e "${BLUE}[1/8]${NC} Checking Git repository..."
if [[ ! -d .git ]]; then
    echo -e "${RED}✗ Not a git repository${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Git repository OK${NC}"

# Step 2: Check branch
echo -e "${BLUE}[2/8]${NC} Checking branch..."
CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || echo "")
if [[ -z "$CURRENT_BRANCH" ]]; then
    echo -e "${RED}✗ Detached HEAD state${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Branch: $CURRENT_BRANCH${NC}"

# Step 3: Check for uncommitted changes
echo -e "${BLUE}[3/8]${NC} Checking working tree..."
if [[ -n $(git status --porcelain) ]]; then
    echo -e "${YELLOW}⚠ Working tree has uncommitted changes${NC}"
    git status --short | head -10
    if [[ $(git status --porcelain | wc -l) -gt 10 ]]; then
        echo "... and $(($(git status --porcelain | wc -l) - 10)) more files"
    fi
else
    echo -e "${GREEN}✓ Working tree clean${NC}"
fi

# Step 4: Check Python virtual environment
echo -e "${BLUE}[4/8]${NC} Checking Python environment..."
if [[ ! -d .venv ]]; then
    echo -e "${YELLOW}⚠ Virtual environment not found${NC}"
    echo "Creating .venv..."
    python3 -m venv .venv
fi

# Activate venv and check
source .venv/bin/activate
PYTHON_PATH=$(which python)
echo -e "${GREEN}✓ Python: $PYTHON_PATH${NC}"
PYTHON_VERSION=$(python --version)
echo -e "${GREEN}✓ Version: $PYTHON_VERSION${NC}"

# Step 5: Install/update dependencies
echo -e "${BLUE}[5/8]${NC} Checking dependencies..."
if [[ "$QUICK_MODE" == false ]]; then
    cd Python
    pip install -q -e ".[dev]" 2>&1 | grep -v "already satisfied" || true
    cd ..
    echo -e "${GREEN}✓ Dependencies installed${NC}"
else
    echo -e "${YELLOW}⊘ Skipped (quick mode)${NC}"
fi

# Step 6: Make scripts executable
echo -e "${BLUE}[6/8]${NC} Setting script permissions..."
chmod +x scripts/*.sh 2>/dev/null || true
chmod +x scripts/*.py 2>/dev/null || true
echo -e "${GREEN}✓ Script permissions set${NC}"

# Step 7: Check key scripts exist
echo -e "${BLUE}[7/8]${NC} Validating workflow scripts..."
REQUIRED_SCRIPTS=(
    "scripts/ai_commit.sh"
    "scripts/safe_push.sh"
    "scripts/should_use_pr.sh"
    "scripts/create_task_pr.sh"
    "scripts/finish_task_pr.sh"
    "scripts/recover_git_state.sh"
    "scripts/end_session.py"
)

MISSING_SCRIPTS=()
for script in "${REQUIRED_SCRIPTS[@]}"; do
    if [[ ! -f "$script" ]]; then
        MISSING_SCRIPTS+=("$script")
    fi
done

if [[ ${#MISSING_SCRIPTS[@]} -gt 0 ]]; then
    echo -e "${RED}✗ Missing scripts:${NC}"
    for script in "${MISSING_SCRIPTS[@]}"; do
        echo "  - $script"
    done
    exit 1
fi
echo -e "${GREEN}✓ All workflow scripts present${NC}"

# Step 8: Display environment info
echo -e "${BLUE}[8/8]${NC} Environment summary..."
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✓ Environment ready!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 Configuration:"
echo "  • Project: structural_engineering_lib"
echo "  • Branch: $CURRENT_BRANCH"
echo "  • Python: $(python --version | cut -d' ' -f2)"
echo "  • Git: $(git --version | cut -d' ' -f3)"
if [[ "$WORKTREE_MODE" == true ]]; then
    echo "  • Mode: Background Agent ($AGENT_NAME)"
    echo "  • Worktree: $(pwd)"
else
    echo "  • Mode: Main Agent"
fi
echo ""

# Show recent activity
echo "📝 Recent Activity:"
git log --oneline --max-count=3 --decorate=short
echo ""

# Show next steps
echo "🚀 Next Steps:"
echo ""
if [[ "$WORKTREE_MODE" == true ]]; then
    echo "  1. Review your task in docs/TASKS.md"
    echo "  2. Make changes in this worktree"
    echo "  3. Commit: ./scripts/ai_commit.sh 'message'"
    echo "  4. Submit: cd $PROJECT_ROOT && ./scripts/worktree_manager.sh submit $AGENT_NAME 'description'"
else
    echo "  1. Run pre-flight check: ./scripts/agent_preflight.sh"
    echo "  2. Review TASKS.md for current work"
    echo "  3. Make changes and commit: ./scripts/ai_commit.sh 'message'"
    echo "  4. End session: ./scripts/end_session.py"
fi
echo ""

# Worktree-specific setup
if [[ "$WORKTREE_MODE" == true ]]; then
    # Create agent-specific marker file
    AGENT_MARKER=".agent_${AGENT_NAME}"
    echo "$AGENT_NAME" > "$AGENT_MARKER"
    echo "Worktree created: $(date)" >> "$AGENT_MARKER"
    echo -e "${GREEN}✓ Agent marker created: $AGENT_MARKER${NC}"
    echo ""
fi

# Optional: Run start_session.py if available and not in worktree
if [[ "$WORKTREE_MODE" == false ]] && [[ "$QUICK_MODE" == false ]]; then
    if [[ -f "scripts/start_session.py" ]]; then
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo -e "${BLUE}Running session startup checks...${NC}"
        echo ""
        python scripts/start_session.py --quick || true
    fi
fi

echo ""
echo -e "${GREEN}✓ Setup complete! You're ready to start working.${NC}"
echo ""

#!/bin/bash
# =============================================================================
# Streamlit Launch Automation Script
# =============================================================================
#
# Automates all steps needed to launch the Streamlit app:
#   1. Environment verification (Python, venv, dependencies)
#   2. Port availability check
#   3. Streamlit configuration validation
#   4. App startup with proper working directory
#   5. Browser auto-open (optional)
#   6. Graceful shutdown handling
#
# Usage:
#   ./scripts/launch_streamlit.sh              # Default launch
#   ./scripts/launch_streamlit.sh --port 8502  # Custom port
#   ./scripts/launch_streamlit.sh --no-browser # Don't auto-open browser
#   ./scripts/launch_streamlit.sh --check      # Check only, don't launch
#   ./scripts/launch_streamlit.sh --bg         # Run in background
#
# Created: 2026-01-16 (Session 35)
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
STREAMLIT_DIR="$PROJECT_ROOT/streamlit_app"
VENV_DIR="$PROJECT_ROOT/.venv"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# Default settings
PORT="${STREAMLIT_PORT:-8501}"
BROWSER="true"
CHECK_ONLY="false"
BACKGROUND="false"

# =============================================================================
# Argument Parsing
# =============================================================================
while [[ $# -gt 0 ]]; do
    case $1 in
        --port|-p)
            PORT="$2"
            shift 2
            ;;
        --no-browser|-n)
            BROWSER="false"
            shift
            ;;
        --check|-c)
            CHECK_ONLY="true"
            shift
            ;;
        --bg|--background)
            BACKGROUND="true"
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --port, -p PORT    Use custom port (default: 8501)"
            echo "  --no-browser, -n   Don't auto-open browser"
            echo "  --check, -c        Check environment only, don't launch"
            echo "  --bg, --background Run Streamlit in background"
            echo "  --help, -h         Show this help message"
            echo ""
            echo "Environment Variables:"
            echo "  STREAMLIT_PORT     Default port (overridden by --port)"
            echo ""
            echo "Examples:"
            echo "  $0                       # Launch on default port 8501"
            echo "  $0 --port 8502           # Launch on custom port"
            echo "  $0 --check               # Verify environment only"
            echo "  $0 --bg --no-browser     # Background mode for CI/testing"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# =============================================================================
# Helper Functions
# =============================================================================
log_step() {
    echo -e "${BLUE}→${NC} $1"
}

log_success() {
    echo -e "${GREEN}✓${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
}

check_command() {
    if command -v "$1" &> /dev/null; then
        return 0
    else
        return 1
    fi
}

# =============================================================================
# Environment Checks
# =============================================================================
echo -e "${BOLD}${CYAN}🚀 Streamlit Launch Automation${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

CHECKS_PASSED=true

# Check 1: Python
log_step "Checking Python..."
if check_command python3; then
    PYTHON_VERSION=$(python3 --version 2>&1)
    log_success "Python found: $PYTHON_VERSION"
else
    log_error "Python3 not found!"
    CHECKS_PASSED=false
fi

# Check 2: Virtual environment
log_step "Checking virtual environment..."
if [ -d "$VENV_DIR" ]; then
    log_success "Virtual environment found: $VENV_DIR"
    PYTHON_CMD="$VENV_DIR/bin/python"
    STREAMLIT_CMD="$VENV_DIR/bin/streamlit"
else
    log_warn "Virtual environment not found at $VENV_DIR"
    log_step "Attempting to use system Python..."
    PYTHON_CMD="python3"
    STREAMLIT_CMD="streamlit"
fi

# Check 3: Streamlit installed
log_step "Checking Streamlit installation..."
if [ -f "$STREAMLIT_CMD" ] || check_command streamlit; then
    if [ -f "$STREAMLIT_CMD" ]; then
        STREAMLIT_VERSION=$("$STREAMLIT_CMD" version 2>&1 | head -1)
    else
        STREAMLIT_VERSION=$(streamlit version 2>&1 | head -1)
    fi
    log_success "Streamlit found: $STREAMLIT_VERSION"
else
    log_error "Streamlit not installed!"
    log_step "To install: pip install streamlit"
    CHECKS_PASSED=false
fi

# Check 4: App directory and entry point
log_step "Checking Streamlit app..."
if [ -d "$STREAMLIT_DIR" ]; then
    if [ -f "$STREAMLIT_DIR/app.py" ]; then
        log_success "App found: streamlit_app/app.py"
        APP_FILE="$STREAMLIT_DIR/app.py"
    elif [ -f "$STREAMLIT_DIR/Home.py" ]; then
        log_success "App found: streamlit_app/Home.py"
        APP_FILE="$STREAMLIT_DIR/Home.py"
    else
        log_error "No app.py or Home.py found in streamlit_app/"
        CHECKS_PASSED=false
    fi
else
    log_error "streamlit_app/ directory not found!"
    CHECKS_PASSED=false
fi

# Check 5: Port availability
log_step "Checking port $PORT availability..."
if lsof -i ":$PORT" &> /dev/null; then
    log_warn "Port $PORT is in use!"
    # Find the process using the port
    PROCESS=$(lsof -i ":$PORT" | tail -1 | awk '{print $1, $2}')
    log_step "Process using port: $PROCESS"

    # Check if it's already streamlit
    if lsof -i ":$PORT" | grep -q streamlit; then
        log_warn "Streamlit appears to be already running on port $PORT"
        echo -e "   Open: ${CYAN}http://localhost:$PORT${NC}"
        if [ "$CHECK_ONLY" = "true" ]; then
            exit 0
        fi
        read -p "Kill existing process and restart? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            PID=$(lsof -i ":$PORT" | grep streamlit | awk '{print $2}' | head -1)
            kill "$PID" 2>/dev/null || true
            sleep 1
            log_success "Killed previous Streamlit process"
        else
            log_step "Keeping existing process. Exiting."
            exit 0
        fi
    else
        log_error "Port $PORT is in use by another process: $PROCESS"
        log_step "Try: ./scripts/launch_streamlit.sh --port 8502"
        CHECKS_PASSED=false
    fi
else
    log_success "Port $PORT is available"
fi

# Check 6: Streamlit configuration
log_step "Checking Streamlit config..."
CONFIG_DIR="$STREAMLIT_DIR/.streamlit"
CONFIG_FILE="$CONFIG_DIR/config.toml"
if [ -f "$CONFIG_FILE" ]; then
    log_success "Config found: .streamlit/config.toml"
else
    log_warn "No .streamlit/config.toml found (using defaults)"
fi

# Check 7: Required Python packages
log_step "Checking critical dependencies..."
MISSING_DEPS=""
for pkg in pandas numpy plotly; do
    if ! "$PYTHON_CMD" -c "import $pkg" 2>/dev/null; then
        MISSING_DEPS="$MISSING_DEPS $pkg"
    fi
done

if [ -n "$MISSING_DEPS" ]; then
    log_warn "Missing packages:$MISSING_DEPS"
    log_step "Install with: pip install$MISSING_DEPS"
else
    log_success "All critical dependencies installed"
fi

# Check 8: Run code scanner for runtime issues
log_step "Running code scanner on Streamlit pages..."
SCANNER_SCRIPT="$PROJECT_ROOT/scripts/check_streamlit_issues.py"
if [ -f "$SCANNER_SCRIPT" ]; then
    SCAN_OUTPUT=$("$PYTHON_CMD" "$SCANNER_SCRIPT" --all-pages 2>&1 || true)
    # Parse only the summary line counts
    CRITICAL_COUNT=$(echo "$SCAN_OUTPUT" | grep -E "^\s*- Critical:" | grep -oE "[0-9]+" | head -1 || echo "0")
    HIGH_COUNT=$(echo "$SCAN_OUTPUT" | grep -E "^\s*- High:" | grep -oE "[0-9]+" | head -1 || echo "0")
    CRITICAL_COUNT="${CRITICAL_COUNT:-0}"
    HIGH_COUNT="${HIGH_COUNT:-0}"

    if [ "$CRITICAL_COUNT" -gt 0 ] 2>/dev/null || [ "$HIGH_COUNT" -gt 0 ] 2>/dev/null; then
        log_error "Code scanner found $CRITICAL_COUNT critical, $HIGH_COUNT high issues!"
        echo "$SCAN_OUTPUT" | tail -20
        CHECKS_PASSED=false
    else
        log_success "Code scanner: 0 critical/high issues"
    fi
else
    log_warn "Code scanner not found (skipping)"
fi

# =============================================================================
# Summary and Launch
# =============================================================================
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ "$CHECKS_PASSED" = "false" ]; then
    echo -e "${RED}${BOLD}Pre-flight checks failed!${NC}"
    echo "Fix the issues above and try again."
    exit 1
fi

if [ "$CHECK_ONLY" = "true" ]; then
    echo -e "${GREEN}${BOLD}All checks passed! ✓${NC}"
    echo "Ready to launch: $0 (without --check)"
    exit 0
fi

# =============================================================================
# Launch Streamlit
# =============================================================================
echo -e "${GREEN}${BOLD}All checks passed! Launching Streamlit...${NC}"
echo ""

# Build command
STREAMLIT_ARGS="run $APP_FILE --server.port $PORT"

if [ "$BROWSER" = "false" ]; then
    STREAMLIT_ARGS="$STREAMLIT_ARGS --server.headless true"
fi

# Add theme and other defaults
STREAMLIT_ARGS="$STREAMLIT_ARGS --server.runOnSave true"

echo -e "Command: ${CYAN}$STREAMLIT_CMD $STREAMLIT_ARGS${NC}"
echo -e "URL:     ${CYAN}http://localhost:$PORT${NC}"
echo ""

# Trap for graceful shutdown
cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down Streamlit...${NC}"
    exit 0
}
trap cleanup SIGINT SIGTERM

# Change to streamlit_app directory for proper imports
cd "$STREAMLIT_DIR"

if [ "$BACKGROUND" = "true" ]; then
    # Background mode
    nohup "$STREAMLIT_CMD" $STREAMLIT_ARGS > /tmp/streamlit.log 2>&1 &
    PID=$!
    echo -e "${GREEN}Streamlit started in background (PID: $PID)${NC}"
    echo "Log: /tmp/streamlit.log"
    echo "Stop: kill $PID"

    # Wait a moment and check if it's running
    sleep 2
    if ps -p $PID > /dev/null 2>&1; then
        log_success "Streamlit is running!"
        if [ "$BROWSER" = "true" ]; then
            # Open browser on macOS
            if [[ "$OSTYPE" == "darwin"* ]]; then
                open "http://localhost:$PORT"
            elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
                xdg-open "http://localhost:$PORT" 2>/dev/null || true
            fi
        fi
    else
        log_error "Streamlit failed to start! Check /tmp/streamlit.log"
        exit 1
    fi
else
    # Foreground mode
    exec "$STREAMLIT_CMD" $STREAMLIT_ARGS
fi

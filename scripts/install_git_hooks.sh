#!/bin/bash
# Install versioned git hooks via core.hooksPath
# This script configures git to use hooks from scripts/git-hooks/
#
# Usage: ./scripts/install_git_hooks.sh
#        ./scripts/install_git_hooks.sh --uninstall  # Remove hook configuration
#        ./scripts/install_git_hooks.sh --status     # Check installation status
#
# Part of: Git Automation Framework (Session 19P6)
#
# Features:
# - Idempotent: safe to run multiple times
# - Non-interactive: works in automated environments (no TTY required)
# - Preserves pre-commit hooks (only adds enforcement layer)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
HOOKS_DIR="$SCRIPT_DIR/git-hooks"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}ℹ${NC} $1"; }
log_ok() { echo -e "${GREEN}✓${NC} $1"; }
log_warn() { echo -e "${YELLOW}⚠${NC} $1"; }
log_error() { echo -e "${RED}✗${NC} $1"; }

show_status() {
    echo ""
    echo -e "${BLUE}Git Hooks Status${NC}"
    echo ""

    CURRENT_PATH=$(git config --get core.hooksPath 2>/dev/null || echo "")

    if [[ -z "$CURRENT_PATH" ]]; then
        log_warn "core.hooksPath not set (using default .git/hooks)"
    else
        if [[ "$CURRENT_PATH" == *"scripts/git-hooks"* ]]; then
            log_ok "core.hooksPath: $CURRENT_PATH (enforcement active)"
        else
            log_warn "core.hooksPath: $CURRENT_PATH (not our hooks)"
        fi
    fi

    # Check if hooks are executable
    if [[ -x "$HOOKS_DIR/pre-commit" ]]; then
        log_ok "pre-commit hook: executable"
    else
        log_warn "pre-commit hook: missing or not executable"
    fi

    if [[ -x "$HOOKS_DIR/pre-push" ]]; then
        log_ok "pre-push hook: executable"
    else
        log_warn "pre-push hook: missing or not executable"
    fi

    echo ""
}

install_hooks() {
    echo ""
    echo -e "${BLUE}Installing Git Hooks${NC}"
    echo ""

    cd "$PROJECT_ROOT"

    # Check if already installed
    CURRENT_PATH=$(git config --get core.hooksPath 2>/dev/null || echo "")
    if [[ "$CURRENT_PATH" == "$HOOKS_DIR" ]]; then
        log_ok "Already installed (idempotent)"
        return 0
    fi

    # Make hooks executable
    chmod +x "$HOOKS_DIR/pre-commit" 2>/dev/null || true
    chmod +x "$HOOKS_DIR/pre-push" 2>/dev/null || true

    # Set core.hooksPath (local to this repo)
    git config core.hooksPath "$HOOKS_DIR"
    log_ok "Set core.hooksPath to $HOOKS_DIR"

    # Verify
    VERIFY=$(git config --get core.hooksPath)
    if [[ "$VERIFY" == "$HOOKS_DIR" ]]; then
        log_ok "Installation verified"
    else
        log_error "Installation failed!"
        exit 1
    fi

    echo ""
    log_ok "Git hooks installed successfully!"
    echo ""
    echo "Manual git commands are now blocked."
    echo "Use ./scripts/ai_commit.sh for all commits."
    echo ""
}

uninstall_hooks() {
    echo ""
    echo -e "${BLUE}Uninstalling Git Hooks${NC}"
    echo ""

    cd "$PROJECT_ROOT"

    # Check if installed
    CURRENT_PATH=$(git config --get core.hooksPath 2>/dev/null || echo "")
    if [[ -z "$CURRENT_PATH" ]]; then
        log_ok "Not installed (nothing to uninstall)"
        return 0
    fi

    # Remove core.hooksPath
    git config --unset core.hooksPath
    log_ok "Removed core.hooksPath configuration"

    echo ""
    log_ok "Git hooks uninstalled!"
    echo "Manual git commands are now allowed."
    echo ""
}

# Parse arguments
case "${1:-}" in
    --status)
        show_status
        ;;
    --uninstall)
        uninstall_hooks
        ;;
    --help|-h)
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  (no args)    Install hooks"
        echo "  --status     Show installation status"
        echo "  --uninstall  Remove hook configuration"
        echo "  --help       Show this help"
        ;;
    *)
        install_hooks
        ;;
esac

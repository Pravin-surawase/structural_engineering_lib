#!/bin/bash
# =============================================================================
# Install Git Hooks Script
# =============================================================================
#
# Installs all custom git hooks from scripts/hooks/ to .git/hooks/
#
# Usage:
#   ./scripts/install_hooks.sh
#
# Created: 2026-01-16 (Session 35)
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
HOOKS_SOURCE="$SCRIPT_DIR/hooks"
HOOKS_TARGET="$PROJECT_ROOT/.git/hooks"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Installing Git Hooks${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check if hooks source directory exists
if [ ! -d "$HOOKS_SOURCE" ]; then
    echo -e "${YELLOW}No hooks directory found at $HOOKS_SOURCE${NC}"
    exit 0
fi

# Install each hook
INSTALLED=0
for hook in "$HOOKS_SOURCE"/*; do
    if [ -f "$hook" ]; then
        HOOK_NAME=$(basename "$hook")
        echo -e "→ Installing ${HOOK_NAME}..."

        # Backup existing hook if it exists and isn't a symlink
        if [ -f "$HOOKS_TARGET/$HOOK_NAME" ] && [ ! -L "$HOOKS_TARGET/$HOOK_NAME" ]; then
            mv "$HOOKS_TARGET/$HOOK_NAME" "$HOOKS_TARGET/$HOOK_NAME.bak"
            echo "  (backed up existing hook)"
        fi

        # Copy hook
        cp "$hook" "$HOOKS_TARGET/$HOOK_NAME"
        chmod +x "$HOOKS_TARGET/$HOOK_NAME"

        echo -e "  ${GREEN}✓${NC} Installed"
        ((INSTALLED++))
    fi
done

echo ""
if [ "$INSTALLED" -gt 0 ]; then
    echo -e "${GREEN}✓ Installed $INSTALLED hook(s)${NC}"
else
    echo -e "${YELLOW}No hooks to install${NC}"
fi

# Reminder about pre-commit
echo ""
echo -e "${BLUE}Note:${NC} Pre-commit hooks are managed separately via:"
echo "  pre-commit install"

#!/bin/bash
# ⚠️ DEPRECATED: This script is superseded by install_git_hooks.sh
#
# This script only warned on manual git. The new script BLOCKS manual git.
# Use install_git_hooks.sh instead (or just run agent_start.sh which calls it).
#
# This script will be removed in a future version.
# ═══════════════════════════════════════════════════════════════════════════════

echo ""
echo "⚠️  DEPRECATED: install_enforcement_hook.sh is superseded!"
echo ""
echo "This script only WARNED on manual git commands."
echo "The new script BLOCKS them entirely (which is what we want)."
echo ""
echo "Use instead:"
echo "  ./scripts/install_git_hooks.sh"
echo ""
echo "Or just run:"
echo "  ./scripts/agent_start.sh --quick"
echo ""
echo "The new hooks are already active if you've run agent_start.sh."
echo ""
exit 1

# ═══════════════════════════════════════════════════════════════════════════════
# ORIGINAL CODE BELOW (kept for reference, no longer executed)
# ═══════════════════════════════════════════════════════════════════════════════
#
# Install a pre-push hook that warns on manual git push to main
# Usage: ./scripts/install_enforcement_hook.sh

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOOK_FILE="$PROJECT_ROOT/.git/hooks/pre-push"

# Create the pre-push hook
cat > "$HOOK_FILE" << 'HOOK'
#!/bin/bash
# Pre-push hook: Warn on manual pushes to main
# Installed by: ./scripts/install_enforcement_hook.sh

# Skip if we're being called by our automation scripts
if [[ "$AI_COMMIT_ACTIVE" == "1" ]] || [[ "$SAFE_PUSH_ACTIVE" == "1" ]]; then
    exit 0
fi

# Check if pushing to main
while read local_ref local_sha remote_ref remote_sha; do
    if [[ "$remote_ref" == *"/main" ]]; then
        echo ""
        echo -e "\033[1;33m⚠️  WARNING: Direct push to main detected!\033[0m"
        echo ""
        echo "For consistent workflow, please use:"
        echo "  ./scripts/ai_commit.sh \"your message\""
        echo ""
        echo "This ensures pre-commit hooks and conflict prevention."
        echo ""
        read -p "Continue with manual push anyway? [y/N] " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "Push cancelled. Use ./scripts/ai_commit.sh instead."
            exit 1
        fi
    fi
done

exit 0
HOOK

chmod +x "$HOOK_FILE"

echo "✅ Pre-push enforcement hook installed at $HOOK_FILE"
echo ""
echo "What it does:"
echo "  - Warns when pushing directly to main without automation scripts"
echo "  - Allows bypass with 'y' confirmation"
echo "  - Skipped automatically when using ai_commit.sh or safe_push.sh"
echo ""
echo "To uninstall: rm $HOOK_FILE"

#!/bin/bash
# Copilot Agent Environment Setup
# Source this at the start of Copilot sessions to prevent common issues

# Exit on error
set -e

echo "🤖 Setting up Copilot Agent environment..."

# 1. Disable git pager (CRITICAL)
echo "Configuring git pager..."
git config --global core.pager cat
git config --global pager.status false
git config --global pager.branch false
git config --global pager.diff false
echo "✅ Git pager disabled"

# 2. Set non-interactive git editor
echo "Configuring git editor..."
git config --global core.editor ":"
export GIT_EDITOR=":"
echo "✅ Git editor set to non-interactive"

# 3. Disable pagers for other commands
export PAGER=cat
export MANPAGER=cat
echo "✅ System pagers disabled"

# 4. Verify git config
echo ""
echo "Current git config:"
echo "  core.pager: $(git config core.pager)"
echo "  pager.status: $(git config pager.status)"
echo "  core.editor: $(git config core.editor)"

# 5. Create safe git aliases
echo ""
echo "Creating safe git aliases..."
git config --global alias.st 'status --short'
git config --global alias.lg 'log --oneline -n 20'
git config --global alias.df 'diff --stat'
git config --global alias.br 'branch --list'
echo "✅ Safe aliases created (git st, git lg, git df, git br)"

# 6. Test git commands
echo ""
echo "Testing git commands..."
git status --short > /dev/null 2>&1 && echo "✅ git status works" || echo "❌ git status failed"
git log --oneline -n 1 > /dev/null 2>&1 && echo "✅ git log works" || echo "❌ git log failed"

echo ""
echo "🎉 Copilot environment setup complete!"
echo ""
echo "Safe git commands to use:"
echo "  git status --short    (or: git st)"
echo "  git log --oneline -n 20   (or: git lg)"
echo "  git diff --stat       (or: git df)"
echo "  git --no-pager [command]  (for any git command)"

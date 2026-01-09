#!/bin/bash
# Complete Agent 6 session closure workflow

set -e

WORKTREE_PATH="/Users/Pravin/Library/Mobile Documents/com~apple~CloudDocs/pravin/projects/project_21_dec_25/structural_engineering_lib.worktrees/worktree-2026-01-09T08-59-17"

echo "🤖 Agent 6 Session Closure"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Step 1: Commit all work
echo ""
echo "Step 1: Committing work..."
cd "$WORKTREE_PATH"

# Read commit message
COMMIT_MSG=$(cat COMMIT_MESSAGE.txt)

# Use ai_commit.sh
./scripts/ai_commit.sh "$COMMIT_MSG"

if [ $? -eq 0 ]; then
    echo "✅ Commit successful"
else
    echo "❌ Commit failed"
    exit 1
fi

# Step 2: Get branch name
BRANCH=$(git branch --show-current)
echo ""
echo "Step 2: Current branch: $BRANCH"

# Step 3: Switch to main and merge
echo ""
echo "Step 3: Merging to main..."
cd ..
git switch main
git merge "$BRANCH" --no-ff -m "Merge Agent 6 session: IMPL-007 Phase 1 + Autonomous Workflow Research"

if [ $? -eq 0 ]; then
    echo "✅ Merge successful"
else
    echo "❌ Merge failed"
    exit 1
fi

# Step 4: Push to remote
echo ""
echo "Step 4: Pushing to remote..."
git push origin main

if [ $? -eq 0 ]; then
    echo "✅ Push successful"
else
    echo "❌ Push failed"
    exit 1
fi

# Step 5: Close worktree
echo ""
echo "Step 5: Closing worktree..."
git worktree remove "$WORKTREE_PATH"

if [ $? -eq 0 ]; then
    echo "✅ Worktree removed"
else
    echo "⚠️  Worktree removal failed (may need manual cleanup)"
fi

# Step 6: Delete branch
echo ""
echo "Step 6: Deleting branch..."
git branch -d "$BRANCH"

if [ $? -eq 0 ]; then
    echo "✅ Branch deleted"
else
    echo "⚠️  Branch deletion failed"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 Agent 6 session closed successfully!"
echo ""
echo "Summary:"
echo "  • Work committed"
echo "  • Merged to main"
echo "  • Pushed to remote"
echo "  • Worktree removed"
echo "  • Branch cleaned up"
echo ""
echo "Next session: Agent 6 continues from main branch"

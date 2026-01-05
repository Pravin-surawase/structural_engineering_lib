#!/bin/bash
# Check for unfinished merge before allowing new commits
# This prevents creating new commits when there's a merge in progress

if [ -f .git/MERGE_HEAD ]; then
    echo ""
    echo "❌ ERROR: Cannot create new commit - there's an unfinished merge!"
    echo ""
    echo "You must complete the current merge first:"
    echo "  1. Check for conflicts: git status"
    echo "  2. If conflicts exist, resolve them"
    echo "  3. Complete the merge: git commit --no-edit"
    echo "  4. Push: git push"
    echo ""
    echo "Or use the safe push script:"
    echo "  ./scripts/safe_push.sh (it will complete the merge automatically)"
    echo ""
    exit 1
fi

exit 0

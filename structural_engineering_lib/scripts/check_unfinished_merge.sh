#!/bin/bash
# Check for unfinished merge before allowing new commits
# This prevents creating new commits when there's a merge in progress
# BUT allows completing the merge itself

# Check if this is a merge commit (MERGE_MSG exists means we're completing a merge)
if [ -f .git/MERGE_MSG ] && [ -f .git/MERGE_HEAD ]; then
    # This is completing a merge - allow it
    exit 0
fi

# Check if there's an unfinished merge AND we're trying to create a new commit
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

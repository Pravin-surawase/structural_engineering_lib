#!/usr/bin/env bash
# Pre-flight checks before committing
# Run this BEFORE staging files to catch issues early

set -euo pipefail

echo "=== Pre-Commit Flight Check ==="

# Check for trailing whitespace in staged files
if git diff --cached --check 2>&1 | grep -q 'trailing whitespace'; then
    echo "❌ ERROR: Trailing whitespace detected!"
    echo ""
    echo "Files with trailing whitespace:"
    git diff --cached --check | grep 'trailing whitespace'
    echo ""
    echo "Fix with: git diff --cached | sed 's/[[:space:]]*$//' | git apply"
    echo "Or: Remove manually and re-stage"
    exit 1
fi

# Check for mixed line endings
if git diff --cached --check 2>&1 | grep -q 'mixed line endings'; then
    echo "❌ ERROR: Mixed line endings detected!"
    git diff --cached --check | grep 'mixed line endings'
    exit 1
fi

# Check for merge conflict markers
if git diff --cached | grep -q '^+.*<<<<<<<\|^+.*=======\|^+.*>>>>>>>'; then
    echo "❌ ERROR: Merge conflict markers found in staged changes!"
    exit 1
fi

echo "✅ Pre-commit checks passed"
exit 0

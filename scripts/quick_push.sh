#!/bin/bash
# Quick push script for solo development
# Usage:
#   ./scripts/quick_push.sh "commit message"          # runs ./scripts/quick_check.sh
#   ./scripts/quick_push.sh "commit message" docs     # runs ./scripts/quick_check.sh docs
#   ./scripts/quick_push.sh "commit message" --cov    # runs ./scripts/quick_check.sh --cov

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

COMMIT_MESSAGE="${1-}"
CHECK_MODE="${2-}"

if [[ -z "$COMMIT_MESSAGE" ]]; then
    echo "Usage: ./scripts/quick_push.sh 'commit message' [docs|--cov]"
    exit 1
fi

# Ensure on main
git switch main

# Pull latest
git pull --rebase

# Run quick checks
echo "Running quick checks..."
if [[ -n "$CHECK_MODE" ]]; then
    ./scripts/quick_check.sh "$CHECK_MODE"
else
    ./scripts/quick_check.sh
fi

# Commit and push
git add .

echo "Staged changes:"
git status -sb

if git diff --cached --quiet; then
    echo "No staged changes. Nothing to commit."
    exit 0
fi

git commit -m "$COMMIT_MESSAGE"
git push

echo "✅ Pushed to main. CI running at:"
echo "https://github.com/Pravin-surawase/structural_engineering_lib/actions"

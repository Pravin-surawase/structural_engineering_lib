#!/bin/bash
# Quick push script for solo development
# Usage: ./scripts/quick_push.sh "commit message"

set -e

if [ -z "$1" ]; then
    echo "Usage: ./scripts/quick_push.sh 'commit message'"
    exit 1
fi

# Ensure on main
git checkout main

# Pull latest
git pull --rebase

# Run quick checks
echo "Running quick checks..."
./scripts/quick_check.sh

# Commit and push
git add .
git commit -m "$1"
git push

echo "✅ Pushed to main. CI running at:"
echo "https://github.com/Pravin-surawase/structural_engineering_lib/actions"

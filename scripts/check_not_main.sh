#!/usr/bin/env bash
set -euo pipefail

branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || true)

if [[ "$branch" == "main" ]]; then
  echo "ERROR: commits to main are blocked. Create a branch first:"
  echo "  git switch -c feat/<task>-short-desc"
  exit 1
fi

if [[ "$branch" == "HEAD" || -z "$branch" ]]; then
  echo "WARNING: detached HEAD. Commit on a branch to avoid losing work."
fi

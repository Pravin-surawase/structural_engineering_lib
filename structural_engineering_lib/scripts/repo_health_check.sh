#!/usr/bin/env bash
set -euo pipefail

echo "=== Repository Health Report ==="
echo "Date: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo ""

echo "Repository Size:"
du -sh .git/ | awk '{print "  .git/: " $1}'
du -sh . | awk '{print "  Total: " $1}'
echo ""

echo "Large Files (>1MB, excluding .venv and .git):"
find . -type f -size +1M \
  -not -path "./.venv/*" \
  -not -path "./.git/*" \
  -print0 \
  | xargs -0 du -h \
  | sort -rh

echo ""

echo "File Counts:"
echo "  Markdown: $(find . -name '*.md' -not -path './.venv/*' | wc -l | tr -d ' ')"
echo "  Python: $(find . -name '*.py' -not -path './.venv/*' | wc -l | tr -d ' ')"
echo "  Total tracked files: $(git ls-files | wc -l | tr -d ' ')"
echo ""

echo "Git Objects:"
git count-objects -vH

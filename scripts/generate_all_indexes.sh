#!/usr/bin/env bash
# Generate index.json + index.md for all research-relevant folders

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"
PYTHON_RUNNER="$PROJECT_ROOT/scripts/python_runtime.sh"

echo "🔍 Generating hierarchical indexes for navigation study..."

# Folders to index (expanded list)
FOLDERS=(
    "docs"
    "docs/getting-started"
    "docs/reference"
    "docs/contributing"
    "docs/architecture"
    "docs/agents/guides"
    "docs/guidelines"
    "docs/planning"
    "docs/verification"
    "docs/developers"
    "docs/research"
    "agents"
    "agents/agent-9"
    "agents/roles"
    "Python"
    "scripts"
)

for folder in "${FOLDERS[@]}"; do
    if [ -d "$folder" ]; then
        echo ""
        echo "📂 Processing: $folder"
        if [ "$folder" == "docs" ]; then
            "$PYTHON_RUNNER" scripts/generate_enhanced_index.py --json-only "$folder"
        else
            "$PYTHON_RUNNER" scripts/generate_enhanced_index.py "$folder"
        fi
    else
        echo "⚠️  Skipping (not found): $folder"
    fi
done

echo ""
echo "✅ All indexes generated successfully!"
echo ""
echo "📊 Summary:"
find . -name "index.json" -type f | wc -l | xargs echo "   JSON indexes:"
find . -name "index.md" -type f | wc -l | xargs echo "   Markdown indexes:"

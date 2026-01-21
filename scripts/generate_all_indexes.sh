#!/usr/bin/env bash
# Generate index.json + index.md for all research-relevant folders

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "🔍 Generating hierarchical indexes for navigation study..."

# Folders to index (13 total)
FOLDERS=(
    "docs"
    "docs/getting-started"
    "docs/reference"
    "docs/contributing"
    "docs/architecture"
    "docs/agents/guides"
    "agents"
    "agents/agent-9"
    "agents/roles"
    "Python"
)

for folder in "${FOLDERS[@]}"; do
    if [ -d "$folder" ]; then
        echo ""
        echo "📂 Processing: $folder"
        if [ "$folder" == "docs" ]; then
            .venv/bin/python scripts/generate_folder_index.py --json-only "$folder"
        else
            .venv/bin/python scripts/generate_folder_index.py "$folder"
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

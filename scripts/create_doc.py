#!/usr/bin/env python3
"""
Create a new documentation file with proper metadata header.

USAGE:
    python scripts/create_doc.py docs/research/my-topic.md "My Topic Research"
    python scripts/create_doc.py docs/planning/task-plan.md "Task Planning" --type=Plan

This script:
1. Creates a new markdown file with proper metadata
2. Adds the required header fields
3. Ensures consistent file structure
"""

import argparse
import json
import subprocess
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent

# Type-to-folder mapping for validation
TYPE_FOLDER_MAP = {
    "research": ["docs/research"],
    "guide": ["docs/agents/guides", "docs/contributing", "docs/getting-started"],
    "reference": ["docs/reference"],
    "architecture": ["docs/architecture"],
    "decision": ["docs/adr"],
    "plan": ["docs/planning"],
    "index": ["docs", "agents", "Python"],
}

TEMPLATE = """# {title}

**Type:** {doc_type}
**Audience:** {audience}
**Status:** {status}
**Importance:** {importance}
**Created:** {created}
**Last Updated:** {created}
**Related Tasks:** {tasks}
**Abstract:** {abstract}

---

## Summary

[Brief summary of this document]

## Details

[Main content goes here]

## Next Steps

[Action items if applicable]

---

*This document follows the metadata standard defined in copilot-instructions.md.*
"""


def get_type_from_path(file_path: Path) -> str:
    """Infer document type from file path."""
    path_str = str(file_path)

    if "research" in path_str:
        return "Research"
    elif "planning" in path_str:
        return "Plan"
    elif "agents/guides" in path_str:
        return "Guide"
    elif "reference" in path_str:
        return "Reference"
    elif "architecture" in path_str:
        return "Architecture"
    elif "adr" in path_str:
        return "Decision"
    elif "contributing" in path_str:
        return "Guide"
    elif "getting-started" in path_str:
        return "Guide"
    else:
        return "Guide"


def get_audience_from_type(doc_type: str) -> str:
    """Infer audience from document type."""
    type_audience = {
        "Research": "All Agents",
        "Guide": "All Agents",
        "Reference": "Developers",
        "Architecture": "Architects",
        "Decision": "All Agents",
        "Plan": "All Agents",
        "Index": "All Agents",
    }
    return type_audience.get(doc_type, "All Agents")


def check_for_similar_docs(title: str) -> dict:
    """Run similarity checks to prevent duplicate docs."""
    script_path = REPO_ROOT / "scripts" / "check_doc_similarity.py"
    if not script_path.exists():
        return {}

    result = subprocess.run(
        [sys.executable, str(script_path), title, "--json"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0 or not result.stdout.strip():
        return {}

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {}


def main():
    parser = argparse.ArgumentParser(description="Create a new doc with metadata")
    parser.add_argument(
        "filepath", help="Path for new document (e.g., docs/research/topic.md)"
    )
    parser.add_argument("title", help="Document title")
    parser.add_argument(
        "--type", dest="doc_type", help="Document type (Research, Guide, etc.)"
    )
    parser.add_argument("--status", default="In Progress", help="Initial status")
    parser.add_argument("--importance", default="Medium", help="Importance level")
    parser.add_argument("--tasks", default="", help="Related task IDs")
    parser.add_argument(
        "--abstract",
        default="[Brief description of this document's purpose]",
        help="One-line abstract",
    )
    parser.add_argument("--force", action="store_true", help="Overwrite existing file")
    parser.add_argument(
        "--allow-duplicate",
        action="store_true",
        help="Allow creation even if similar docs exist",
    )
    parser.add_argument(
        "--skip-similarity-check",
        action="store_true",
        help="Skip duplicate/similarity check",
    )

    args = parser.parse_args()

    file_path = Path(args.filepath)
    if not file_path.is_absolute():
        file_path = REPO_ROOT / file_path

    # Check for similar or canonical docs (avoid duplication)
    if not args.skip_similarity_check and not args.allow_duplicate:
        results = check_for_similar_docs(args.title)
        canonical = results.get("canonical_matches", []) if results else []
        similar = results.get("similar_docs", []) if results else []
        high_similar = [d for d in similar if d.get("similarity", 0) >= 0.7]

        if canonical or high_similar:
            print("⚠️  Similar or canonical documents detected:")
            for match in canonical:
                print(f"  • Canonical: {match.get('path')} ({match.get('title')})")
            for doc in high_similar[:5]:
                print(
                    f"  • Similar: {doc.get('path')} "
                    f"({doc.get('reason', 'similar')})"
                )
            print()
            print("→ Update existing docs instead of creating a new one.")
            print("→ Use --allow-duplicate to proceed anyway.")
            return 1
        elif similar:
            print("⚠️  Possible related docs found (low similarity):")
            for doc in similar[:5]:
                print(f"  • {doc.get('path')} ({doc.get('reason', 'similar')})")
            print("→ Proceeding, but review existing docs if possible.")
            print()

    # Check if file exists
    if file_path.exists() and not args.force:
        print(f"❌ File already exists: {file_path}")
        print("   Use --force to overwrite")
        return 1

    # Ensure parent directory exists
    file_path.parent.mkdir(parents=True, exist_ok=True)

    # Determine type
    doc_type = args.doc_type or get_type_from_path(file_path)
    audience = get_audience_from_type(doc_type)

    # Generate content
    content = TEMPLATE.format(
        title=args.title,
        doc_type=doc_type,
        audience=audience,
        status=args.status,
        importance=args.importance,
        created=date.today().strftime("%Y-%m-%d"),
        tasks=args.tasks or "None",
        abstract=args.abstract,
    )

    # Write file
    file_path.write_text(content)

    print(f"✅ Created: {file_path}")
    print(f"   Type: {doc_type}")
    print(f"   Status: {args.status}")
    print()
    print("📝 Next steps:")
    print("   1. Edit the file to add content")
    print("   2. Update Abstract with actual summary")
    print("   3. Set Related Tasks if applicable")
    print("   4. Commit when ready")

    return 0


if __name__ == "__main__":
    sys.exit(main())

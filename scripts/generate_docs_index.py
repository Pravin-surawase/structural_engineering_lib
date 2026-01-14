#!/usr/bin/env python3
"""Generate machine-readable JSON index of documentation.

Purpose:
    Creates docs-index.json for AI agent efficiency.
    Enables programmatic navigation of documentation.

Usage:
    python scripts/generate_docs_index.py          # Preview
    python scripts/generate_docs_index.py --write  # Write to file

Output:
    docs/docs-index.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).parent.parent
DOCS_DIR = PROJECT_ROOT / "docs"
OUTPUT_FILE = DOCS_DIR / "docs-index.json"

# Directories to skip
SKIP_DIRS = {
    "_archive",
    "_internal",
    "node_modules",
    ".git",
    "__pycache__",
}

# Tags mapping based on folder
FOLDER_TAGS = {
    "reference": ["api", "technical"],
    "getting-started": ["beginner", "tutorial"],
    "research": ["investigation", "planning"],
    "architecture": ["design", "structure"],
    "agents": ["ai", "automation"],
    "contributing": ["development", "workflow"],
    "verification": ["testing", "validation"],
    "planning": ["roadmap", "tasks"],
    "troubleshooting": ["help", "issues"],
    "specs": ["requirements", "design"],
    "cookbook": ["examples", "recipes"],
    "learning": ["education", "training"],
}


# Complexity estimation based on file size
def estimate_complexity(file_size: int) -> str:
    """Estimate document complexity from file size."""
    if file_size < 2000:
        return "beginner"
    elif file_size < 8000:
        return "intermediate"
    else:
        return "advanced"


def extract_title(content: str, filepath: Path) -> str:
    """Extract title from markdown content."""
    # Try front-matter title
    fm_match = re.search(
        r'^---\s*\n.*?^title:\s*["\']?(.+?)["\']?\s*$.*?^---',
        content,
        re.MULTILINE | re.DOTALL,
    )
    if fm_match:
        return fm_match.group(1).strip()

    # Try first heading
    h1_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    if h1_match:
        return h1_match.group(1).strip()

    # Fall back to filename
    return filepath.stem.replace("-", " ").replace("_", " ").title()


def extract_sections(content: str) -> list[str]:
    """Extract H2 sections from markdown."""
    sections = re.findall(r"^##\s+(.+)$", content, re.MULTILINE)
    return [s.strip() for s in sections[:10]]  # Max 10 sections


def extract_tags(content: str, folder: str) -> list[str]:
    """Extract tags from front-matter and folder."""
    tags = set()

    # Add folder-based tags
    if folder in FOLDER_TAGS:
        tags.update(FOLDER_TAGS[folder])

    # Try front-matter tags
    fm_match = re.search(r"^tags:\s*\[([^\]]+)\]", content, re.MULTILINE)
    if fm_match:
        fm_tags = [t.strip().strip("\"'") for t in fm_match.group(1).split(",")]
        tags.update(fm_tags)

    return sorted(tags)


def get_doc_type(filepath: Path, content: str) -> str:
    """Determine document type."""
    name = filepath.stem.lower()
    parent = filepath.parent.name.lower()

    if "readme" in name:
        return "index"
    elif parent in ("reference", "api"):
        return "reference"
    elif parent in ("getting-started", "learning"):
        return "tutorial"
    elif "research" in parent or "research" in name:
        return "research"
    elif "guide" in name:
        return "guide"
    elif "spec" in parent or "spec" in name:
        return "specification"
    elif "troubleshoot" in name or "troubleshoot" in parent:
        return "troubleshooting"
    elif "changelog" in name or "task" in name:
        return "tracking"
    else:
        return "documentation"


def scan_docs() -> dict:
    """Scan docs directory and build index."""
    docs = {}
    navigation = {
        "by_role": {
            "ai_agent": [],
            "python_dev": [],
            "excel_user": [],
            "contributor": [],
        },
        "by_topic": {},
    }

    for md_file in DOCS_DIR.rglob("*.md"):
        # Skip excluded directories
        if any(skip in md_file.parts for skip in SKIP_DIRS):
            continue

        # Get relative path
        rel_path = md_file.relative_to(PROJECT_ROOT)
        rel_str = str(rel_path)

        try:
            content = md_file.read_text(encoding="utf-8")
        except Exception:
            continue

        file_size = md_file.stat().st_size
        folder = md_file.parent.name if md_file.parent != DOCS_DIR else "root"

        # Extract metadata
        title = extract_title(content, md_file)
        doc_type = get_doc_type(md_file, content)
        complexity = estimate_complexity(file_size)
        sections = extract_sections(content)
        tags = extract_tags(content, folder)

        # Build doc entry
        docs[rel_str] = {
            "title": title,
            "type": doc_type,
            "complexity": complexity,
            "folder": folder,
            "tags": tags,
            "sections": sections,
            "size_bytes": file_size,
        }

        # Add to navigation by role
        if "agent" in folder or "ai" in title.lower():
            navigation["by_role"]["ai_agent"].append(rel_str)
        if "python" in folder or "python" in title.lower():
            navigation["by_role"]["python_dev"].append(rel_str)
        if "excel" in folder or "excel" in title.lower():
            navigation["by_role"]["excel_user"].append(rel_str)
        if "contrib" in folder or "development" in title.lower():
            navigation["by_role"]["contributor"].append(rel_str)

        # Add to navigation by topic
        for tag in tags:
            if tag not in navigation["by_topic"]:
                navigation["by_topic"][tag] = []
            navigation["by_topic"][tag].append(rel_str)

    return {
        "version": "1.0.0",
        "generated": datetime.now().isoformat(),
        "total_docs": len(docs),
        "docs": docs,
        "navigation": navigation,
    }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Generate docs-index.json")
    parser.add_argument("--write", action="store_true", help="Write to file")
    args = parser.parse_args()

    print("📚 Scanning documentation...")
    index = scan_docs()

    print(f"   Found {index['total_docs']} documents")

    # Count by type
    type_counts: dict[str, int] = {}
    for doc in index["docs"].values():
        t = doc["type"]
        type_counts[t] = type_counts.get(t, 0) + 1

    print("\n   By type:")
    for t, count in sorted(type_counts.items(), key=lambda x: -x[1]):
        print(f"     {t}: {count}")

    if args.write:
        OUTPUT_FILE.write_text(json.dumps(index, indent=2))
        print(f"\n✅ Written to {OUTPUT_FILE}")
    else:
        print(f"\n💡 Run with --write to save to {OUTPUT_FILE}")
        # Preview first few entries
        print("\n   Preview (first 3 docs):")
        for path, meta in list(index["docs"].items())[:3]:
            print(f"     {path}: {meta['title']} ({meta['type']})")

    return 0


if __name__ == "__main__":
    sys.exit(main())

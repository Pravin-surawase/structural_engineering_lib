#!/usr/bin/env python3
"""
Validate documentation front-matter metadata.

Checks that docs have proper YAML front-matter with required fields.

Usage:
    python scripts/check_doc_frontmatter.py           # Report missing/invalid
    python scripts/check_doc_frontmatter.py --add     # Add template to files without front-matter
    python scripts/check_doc_frontmatter.py --json    # Output JSON report

Created: 2026-01-10
Author: AI Agent (Phase C.2)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Required fields in front-matter
REQUIRED_FIELDS = ["owner", "status", "last_updated", "doc_type"]

# Optional but recommended
OPTIONAL_FIELDS = ["complexity", "tags"]

# Valid values for each field
VALID_VALUES = {
    "status": ["active", "draft", "deprecated", "archived"],
    "doc_type": ["guide", "reference", "tutorial", "index", "spec", "log"],
    "complexity": ["beginner", "intermediate", "advanced"],
}

# Directories to skip
SKIP_DIRS = {"_archive", "node_modules", ".git", "__pycache__", ".venv"}

# Files to skip (these don't need front-matter)
SKIP_FILES = {
    "README.md",  # Index files have different structure
    "index.md",
    "TASKS.md",
    "SESSION_LOG.md",
    "CHANGELOG.md",
}


def parse_frontmatter(content: str) -> tuple[dict[str, Any] | None, str]:
    """Parse YAML front-matter from markdown content.

    Returns:
        (frontmatter_dict, remaining_content) or (None, content) if no front-matter
    """
    if not content.startswith("---"):
        return None, content

    # Find closing ---
    end_match = re.search(r"\n---\s*\n", content[3:])
    if not end_match:
        return None, content

    fm_text = content[4 : end_match.start() + 3]
    remaining = content[end_match.end() + 4 :]

    # Simple YAML parsing (key: value)
    fm_dict: dict[str, Any] = {}
    for line in fm_text.split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip().strip("'\"")
            # Handle arrays
            if value.startswith("[") and value.endswith("]"):
                value = [
                    v.strip().strip("'\"") for v in value[1:-1].split(",") if v.strip()
                ]
            fm_dict[key] = value

    return fm_dict, remaining


def validate_frontmatter(fm: dict[str, Any], filepath: Path) -> list[str]:
    """Validate front-matter fields.

    Returns:
        List of validation errors (empty if valid)
    """
    errors = []

    # Check required fields
    for field in REQUIRED_FIELDS:
        if field not in fm:
            errors.append(f"Missing required field: {field}")

    # Validate field values
    for field, valid_values in VALID_VALUES.items():
        if field in fm and fm[field] not in valid_values:
            errors.append(f"Invalid {field}: '{fm[field]}' (valid: {valid_values})")

    # Validate date format
    if "last_updated" in fm:
        try:
            datetime.strptime(str(fm["last_updated"]), "%Y-%m-%d")
        except ValueError:
            errors.append(
                f"Invalid last_updated format: '{fm['last_updated']}' (use YYYY-MM-DD)"
            )

    return errors


def generate_frontmatter(
    doc_type: str = "guide", complexity: str = "intermediate"
) -> str:
    """Generate a front-matter template."""
    today = datetime.now().strftime("%Y-%m-%d")
    return f"""---
owner: Main Agent
status: active
last_updated: {today}
doc_type: {doc_type}
complexity: {complexity}
tags: []
---

"""


def check_docs(docs_dir: Path, add_missing: bool = False) -> dict[str, Any]:
    """Check all docs for front-matter.

    Returns:
        Report dict with stats and issues
    """
    report = {
        "total": 0,
        "with_frontmatter": 0,
        "without_frontmatter": 0,
        "invalid_frontmatter": 0,
        "skipped": 0,
        "issues": [],
        "files_without": [],
        "files_invalid": [],
    }

    for md_file in docs_dir.rglob("*.md"):
        # Skip excluded directories
        if any(skip in md_file.parts for skip in SKIP_DIRS):
            report["skipped"] += 1
            continue

        # Skip known files
        if md_file.name in SKIP_FILES:
            report["skipped"] += 1
            continue

        report["total"] += 1
        rel_path = md_file.relative_to(docs_dir)

        try:
            content = md_file.read_text(encoding="utf-8")
        except Exception as e:
            report["issues"].append({"file": str(rel_path), "error": str(e)})
            continue

        fm, remaining = parse_frontmatter(content)

        if fm is None:
            report["without_frontmatter"] += 1
            report["files_without"].append(str(rel_path))

            if add_missing:
                # Infer doc_type from path
                doc_type = "guide"
                if "reference" in str(rel_path):
                    doc_type = "reference"
                elif "tutorial" in str(rel_path):
                    doc_type = "tutorial"
                elif "spec" in str(rel_path):
                    doc_type = "spec"

                new_content = generate_frontmatter(doc_type) + content
                md_file.write_text(new_content, encoding="utf-8")
                print(f"  ✅ Added front-matter: {rel_path}")
        else:
            report["with_frontmatter"] += 1
            errors = validate_frontmatter(fm, md_file)
            if errors:
                report["invalid_frontmatter"] += 1
                report["files_invalid"].append(
                    {
                        "file": str(rel_path),
                        "errors": errors,
                    }
                )

    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate doc front-matter")
    parser.add_argument(
        "--add",
        action="store_true",
        help="Add front-matter template to files without it",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output JSON report",
    )
    args = parser.parse_args()

    docs_dir = Path(__file__).parent.parent / "docs"

    if not docs_dir.exists():
        print(f"❌ docs directory not found: {docs_dir}")
        return 1

    print("🔍 Checking documentation front-matter...\n")

    report = check_docs(docs_dir, add_missing=args.add)

    if args.json:
        print(json.dumps(report, indent=2))
        return 0

    # Print summary
    print("\n📊 Front-Matter Report")
    print(f"{'=' * 40}")
    print(f"Total docs checked: {report['total']}")
    print(f"With front-matter: {report['with_frontmatter']}")
    print(f"Without front-matter: {report['without_frontmatter']}")
    print(f"Invalid front-matter: {report['invalid_frontmatter']}")
    print(f"Skipped (README, index, etc.): {report['skipped']}")

    if report["files_without"] and not args.add:
        print(f"\n⚠️  Files without front-matter ({len(report['files_without'])}):")
        for f in report["files_without"][:10]:
            print(f"   - {f}")
        if len(report["files_without"]) > 10:
            print(f"   ... and {len(report['files_without']) - 10} more")
        print("\n   Run with --add to add front-matter template")

    if report["files_invalid"]:
        print(f"\n❌ Files with invalid front-matter ({len(report['files_invalid'])}):")
        for item in report["files_invalid"][:5]:
            print(f"   - {item['file']}")
            for err in item["errors"]:
                print(f"     • {err}")

    return 1 if report["without_frontmatter"] or report["invalid_frontmatter"] else 0


if __name__ == "__main__":
    sys.exit(main())

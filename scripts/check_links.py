#!/usr/bin/env python3
"""Check for broken internal links in markdown files.

Usage:
    python scripts/check_links.py
"""
import re
from pathlib import Path


def find_markdown_links(content: str) -> list[tuple[str, str]]:
    """Find all markdown links [text](target)."""
    pattern = r'(?<!!)\[([^\]]+)\]\(([^)]+)\)'
    return re.findall(pattern, content)


def main() -> int:
    """Check all markdown files for broken internal links."""
    # Find project root (where this script lives in scripts/)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    docs_dir = project_root / "docs"
    python_dir = project_root / "Python"

    broken_links: list[dict] = []
    file_count = 0
    link_count = 0

    # Collect all markdown files to check
    md_files = list(docs_dir.rglob("*.md"))
    md_files.append(python_dir / "README.md")
    md_files.append(project_root / "README.md")

    for md_file in md_files:
        if not md_file.exists():
            continue

        file_count += 1
        content = md_file.read_text(encoding='utf-8')
        links = find_markdown_links(content)

        for text, target in links:
            # Skip external links
            if target.startswith(('http://', 'https://', 'mailto:')):
                continue
            # Skip pure anchors
            if target.startswith('#'):
                continue

            link_count += 1

            # Handle relative paths (remove anchor)
            target_path = target.split('#')[0]
            if not target_path:
                continue

            # Resolve relative to the file's directory
            full_path = (md_file.parent / target_path).resolve()

            # Check if exists
            if not full_path.exists():
                broken_links.append({
                    'file': str(md_file.relative_to(project_root)),
                    'link_text': text,
                    'target': target,
                })

    # Report
    print(f"Checked {file_count} markdown files")
    print(f"Found {link_count} internal links")
    print(f"Broken links: {len(broken_links)}\n")

    if broken_links:
        for bl in broken_links:
            print(f"❌ {bl['file']}")
            print(f"   [{bl['link_text']}]({bl['target']})")
            print()
        return 1
    else:
        print("✅ All internal links are valid!")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())

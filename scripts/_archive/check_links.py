#!/usr/bin/env python3
"""Check for broken internal links in markdown files.

Enhanced for migration with link mapping and auto-fix support.

Usage:
    python scripts/check_links.py                      # Check all links
    python scripts/check_links.py --map links.json     # Use migration mapping
    python scripts/check_links.py --fix --map links.json  # Auto-fix broken links
"""
import re
import json
import argparse
from pathlib import Path
from typing import Dict


# Skip these patterns - they are placeholders/examples, not real links
SKIP_LINK_PATTERNS = [
    r"^text$",  # [text](target) - example link
    r"^Link \d+$",  # [Link 1], [Link 2] - example links
    r"^\$\w+$",  # [$file] - variable placeholder
    r"^\.\*",  # [.*\] - regex pattern in docs
    r"^\'.*\'$",  # ['check_fn'] - code references
    r"^path/to/",  # path/to/doc.md - example paths
    r"^target\.md$",  # target.md - example
    r"^old-file\.md",  # old-file.md - example
    r"^Old_File\.md",  # Old_File.md - example
    r"^file\.md",  # file.md - example
]

# Skip files in these directories (planning/migration docs with target paths)
SKIP_DIRECTORIES = [
    "agents/agent-9",  # Agent-9 governance/planning docs
    "docs/_archive",  # Archived docs with historical links
    "docs/research",  # Research docs with example content
]


def is_placeholder_link(text: str, target: str) -> bool:
    """Check if a link is a placeholder/example that should be skipped."""
    for pattern in SKIP_LINK_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return True
        if re.search(pattern, target, re.IGNORECASE):
            return True
    return False


def should_skip_file(file_path: Path, project_root: Path) -> bool:
    """Check if a file should be skipped based on its directory."""
    try:
        rel_path = str(file_path.relative_to(project_root))
        for skip_dir in SKIP_DIRECTORIES:
            if rel_path.startswith(skip_dir):
                return True
    except ValueError:
        pass
    return False


def find_markdown_links(content: str) -> list[tuple[str, str]]:
    """Find all markdown links [text](target)."""
    pattern = r"(?<!!)\[([^\]]+)\]\(([^)]+)\)"
    return re.findall(pattern, content)


def main() -> int:
    """Check all markdown files for broken internal links."""
    parser = argparse.ArgumentParser(description="Check markdown links")
    parser.add_argument("--map", help="Path to link mapping JSON (old -> new paths)")
    parser.add_argument(
        "--fix", action="store_true", help="Auto-fix broken links using map"
    )
    args = parser.parse_args()

    # Load link map if provided
    link_map: Dict[str, str] = {}
    if args.map and Path(args.map).exists():
        with open(args.map, "r") as f:
            link_map = json.load(f)
        print(f"📋 Loaded {len(link_map)} mappings from {args.map}")

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
    md_files.extend(list((project_root / "agents").rglob("*.md")))  # Added agents/
    md_files.append(python_dir / "README.md")
    md_files.append(project_root / "README.md")

    for md_file in md_files:
        if not md_file.exists():
            continue

        # Skip files in excluded directories
        if should_skip_file(md_file, project_root):
            continue

        file_count += 1
        content = md_file.read_text(encoding="utf-8")
        links = find_markdown_links(content)

        for text, target in links:
            # Skip external links
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            # Skip pure anchors
            if target.startswith("#"):
                continue
            # Skip placeholder/example links
            if is_placeholder_link(text, target):
                continue

            link_count += 1

            # Handle relative paths (remove anchor)
            target_path = target.split("#")[0]
            anchor = "#" + target.split("#")[1] if "#" in target else ""
            if not target_path:
                continue

            # Resolve relative to the file's directory
            full_path = (md_file.parent / target_path).resolve()

            # Check if exists
            if not full_path.exists():
                # Check if we have a fix suggestion
                suggestion = link_map.get(target_path, None)

                broken_links.append(
                    {
                        "file": str(md_file.relative_to(project_root)),
                        "file_path": md_file,
                        "link_text": text,
                        "target": target,
                        "target_path": target_path,
                        "anchor": anchor,
                        "suggestion": suggestion,
                    }
                )

    # Report
    print(f"\n🔍 Checked {file_count} markdown files")
    print(f"   Found {link_count} internal links")
    print(f"   Broken links: {len(broken_links)}\n")

    if broken_links:
        # Show broken links
        for bl in broken_links:
            print(f"❌ {bl['file']}")
            print(f"   [{bl['link_text']}]({bl['target']})")
            if bl["suggestion"]:
                print(f"   💡 Suggestion: {bl['suggestion']}")
            print()

        # Auto-fix if requested
        if args.fix and link_map:
            fixed_count = 0
            files_to_update: Dict[Path, str] = {}

            for bl in broken_links:
                if bl["suggestion"]:
                    file_path = bl["file_path"]

                    # Load content if not already loaded
                    if file_path not in files_to_update:
                        files_to_update[file_path] = file_path.read_text(
                            encoding="utf-8"
                        )

                    # Replace old link with new link
                    old_link = f"]({bl['target']})"
                    new_link = f"]({bl['suggestion']}{bl['anchor']})"
                    files_to_update[file_path] = files_to_update[file_path].replace(
                        old_link, new_link
                    )
                    fixed_count += 1

            # Write updated files
            for file_path, content in files_to_update.items():
                file_path.write_text(content, encoding="utf-8")

            print(f"✅ Fixed {fixed_count} links in {len(files_to_update)} files")

            # Re-check
            print("\n🔄 Re-checking after fixes...")
            return main()  # Recursively check again
        elif args.fix and not link_map:
            print("⚠️  --fix requires --map with link mapping JSON")

        return 1
    else:
        print("✅ All internal links are valid!")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())

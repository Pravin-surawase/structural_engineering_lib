#!/usr/bin/env python3
"""
Enhance README files with comprehensive content.

This script analyzes folder contents and generates structured README content
including file tables, descriptions, and navigation links.

Usage:
    python scripts/enhance_readme.py docs/reference --dry-run
    python scripts/enhance_readme.py docs/reference --apply
    python scripts/enhance_readme.py --check-all  # Find sparse READMEs
"""

from __future__ import annotations

import argparse
from pathlib import Path


def get_project_root() -> Path:
    """Get the project root directory."""
    script_dir = Path(__file__).parent
    return script_dir.parent


def count_lines(file_path: Path) -> int:
    """Count lines in a file."""
    try:
        return len(file_path.read_text().splitlines())
    except Exception:
        return 0


def get_file_description(file_path: Path) -> str:
    """Extract a brief description from a markdown file's first heading or content."""
    try:
        content = file_path.read_text()
        lines = content.splitlines()

        # Look for first heading
        for line in lines[:10]:
            if line.startswith("# "):
                title = line[2:].strip()
                # Don't return if it's just the filename
                if title.lower().replace("-", " ").replace(
                    "_", " "
                ) != file_path.stem.lower().replace("-", " ").replace("_", " "):
                    return title
                break

        # Look for first paragraph
        for line in lines[:20]:
            line = line.strip()
            if (
                line
                and not line.startswith("#")
                and not line.startswith("|")
                and not line.startswith("-")
                and not line.startswith("*")
            ):
                if len(line) > 20:
                    return line[:80] + "..." if len(line) > 80 else line
                break

        # Fallback: format filename
        return file_path.stem.replace("-", " ").replace("_", " ").title()

    except Exception:
        return file_path.stem.replace("-", " ").replace("_", " ").title()


def analyze_folder(folder_path: Path) -> dict:
    """Analyze folder contents and structure."""
    result = {
        "readme_path": folder_path / "README.md",
        "readme_exists": (folder_path / "README.md").exists(),
        "readme_lines": 0,
        "markdown_files": [],
        "subfolders": [],
        "other_files": [],
    }

    if result["readme_exists"]:
        result["readme_lines"] = count_lines(result["readme_path"])

    for item in sorted(folder_path.iterdir()):
        if item.name.startswith("."):
            continue

        if item.is_dir():
            result["subfolders"].append(
                {
                    "name": item.name,
                    "has_readme": (item / "README.md").exists(),
                }
            )
        elif item.suffix == ".md" and item.name != "README.md":
            result["markdown_files"].append(
                {
                    "name": item.name,
                    "path": item,
                    "description": get_file_description(item),
                }
            )
        else:
            result["other_files"].append(item.name)

    return result


def generate_readme_content(folder_path: Path, analysis: dict) -> str:
    """Generate enhanced README content."""
    folder_name = folder_path.name
    title = folder_name.replace("-", " ").replace("_", " ").title()

    # Count total files
    total_files = len(analysis["markdown_files"])

    lines = [
        f"# {title}",
        "",
        "[Add description of what this folder contains]",
        "",
        f"**Files:** {total_files} | **Updated:** 2026-01-11",
        "",
        "---",
        "",
    ]

    # Add subfolders section if any
    if analysis["subfolders"]:
        lines.extend(
            [
                "## Subfolders",
                "",
                "| Folder | Description |",
                "|--------|-------------|",
            ]
        )
        for sf in analysis["subfolders"]:
            readme_link = (
                f"[{sf['name']}/]({sf['name']}/README.md)"
                if sf["has_readme"]
                else f"`{sf['name']}/`"
            )
            lines.append(f"| {readme_link} | [Add description] |")
        lines.append("")

    # Add files section
    if analysis["markdown_files"]:
        lines.extend(
            [
                "## Contents",
                "",
                "| File | Description |",
                "|------|-------------|",
            ]
        )
        for f in analysis["markdown_files"]:
            lines.append(f"| [{f['name']}]({f['name']}) | {f['description']} |")
        lines.append("")

    # Add navigation footer
    parent = folder_path.parent
    if parent.name != folder_path.name:
        lines.extend(
            [
                "---",
                "",
                "**Parent:** [../README.md](../README.md)",
            ]
        )

    return "\n".join(lines)


def check_all_readmes(min_lines: int = 50) -> list[dict]:
    """Find all sparse READMEs."""
    root = get_project_root()
    docs_path = root / "docs"

    sparse_readmes = []

    for readme in docs_path.rglob("README.md"):
        lines = count_lines(readme)
        if lines < min_lines:
            sparse_readmes.append(
                {
                    "path": readme.relative_to(root),
                    "lines": lines,
                    "folder": readme.parent.relative_to(root),
                }
            )

    return sorted(sparse_readmes, key=lambda x: x["lines"])


def main():
    parser = argparse.ArgumentParser(description="Enhance README files")
    parser.add_argument("folder", nargs="?", help="Folder to enhance")
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be generated"
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply changes (preserves existing content)",
    )
    parser.add_argument(
        "--check-all", action="store_true", help="Find all sparse READMEs"
    )
    parser.add_argument(
        "--min-lines", type=int, default=50, help="Minimum lines for --check-all"
    )

    args = parser.parse_args()

    if args.check_all:
        sparse = check_all_readmes(args.min_lines)
        print(f"\n{'='*60}")
        print(f"📁 Sparse READMEs (<{args.min_lines} lines)")
        print(f"{'='*60}\n")

        if not sparse:
            print("✅ All READMEs have sufficient content!")
            return

        print(f"{'Lines':<8} {'Path'}")
        print(f"{'-'*8} {'-'*50}")
        for r in sparse:
            print(f"{r['lines']:<8} {r['path']}")

        print(f"\nTotal: {len(sparse)} sparse READMEs")
        return

    if not args.folder:
        parser.print_help()
        return

    root = get_project_root()
    folder_path = Path(args.folder)

    if not folder_path.is_absolute():
        folder_path = root / folder_path

    if not folder_path.exists():
        print(f"❌ Folder not found: {folder_path}")
        return

    analysis = analyze_folder(folder_path)
    content = generate_readme_content(folder_path, analysis)

    print(f"\n{'='*60}")
    print(f"📁 README Enhancement: {folder_path.relative_to(root)}")
    print(f"{'='*60}\n")

    print(f"Current README: {analysis['readme_lines']} lines")
    print(f"Markdown files: {len(analysis['markdown_files'])}")
    print(f"Subfolders: {len(analysis['subfolders'])}")
    print()

    if args.dry_run:
        print("Generated content:\n")
        print("-" * 40)
        print(content)
        print("-" * 40)
        print("\nUse --apply to write this content")
        return

    if args.apply:
        readme_path = analysis["readme_path"]

        if readme_path.exists():
            # Preserve existing content after our generated header
            existing = readme_path.read_text()
            print("⚠️  README exists. Generated content shown above.")
            print("    Manual merge recommended to preserve existing content.")
            print("\nGenerated content:\n")
            print("-" * 40)
            print(content)
            print("-" * 40)
        else:
            readme_path.write_text(content)
            print(f"✅ Created: {readme_path.relative_to(root)}")

        return

    # Default: show analysis
    print("Generated content:\n")
    print("-" * 40)
    print(content)
    print("-" * 40)
    print("\nOptions:")
    print("  --dry-run  Show what would be generated")
    print("  --apply    Create/update the README")


if __name__ == "__main__":
    main()

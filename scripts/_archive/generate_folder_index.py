#!/usr/bin/env python3
"""Generate index.json + index.md for a folder.

This script scans a folder and generates two index files:
1. index.json - Machine-readable (for AI agents using jq)
2. index.md - Human-readable (for GitHub rendering)

Both contain:
- File listings with descriptions
- Subfolder listings
- Metadata (last_updated, file_count, doc_type)

Usage:
    python scripts/generate_folder_index.py <folder_path>

Example:
    python scripts/generate_folder_index.py docs/getting-started/
"""

import json
import sys
import re
from pathlib import Path
from datetime import datetime
from typing import Dict


def extract_title(content: str) -> str:
    """Extract title from markdown content."""
    lines = content.split("\n")
    for line in lines[:5]:  # Check first 5 lines
        if line.startswith("# "):
            return line[2:].strip()
    return ""


def extract_description(content: str) -> str:
    """Extract description from first paragraph after title."""
    lines = content.split("\n")
    skip_title = False
    description_lines = []

    for line in lines:
        line = line.strip()

        # Skip title
        if line.startswith("# "):
            skip_title = True
            continue

        # Skip metadata block
        if line.startswith("**") and ":" in line:
            continue

        # Skip horizontal rules
        if line.startswith("---") or line.startswith("==="):
            continue

        # Found non-empty line after title
        if skip_title and line and not line.startswith("#"):
            description_lines.append(line)
            if len(description_lines) >= 2:  # Get up to 2 lines
                break

    description = " ".join(description_lines[:2]).strip()
    description = _strip_markdown(description)
    return description[:200]  # Max 200 chars


def _strip_markdown(text: str) -> str:
    """Strip links/code from descriptions to keep index entries safe."""
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
    text = text.replace("`", "")
    return text


def extract_metadata(content: str) -> Dict[str, any]:
    """Extract metadata from markdown content."""
    metadata = {}
    lines = content.split("\n")

    # Look for metadata in first 20 lines
    for line in lines[:20]:
        line = line.strip()

        # Pattern: **Key:** Value
        if line.startswith("**") and ":**" in line:
            parts = line.split(":**", 1)
            if len(parts) == 2:
                key = parts[0].replace("**", "").strip().lower().replace(" ", "_")
                value = parts[1].strip()
                metadata[key] = value

    return metadata


def scan_folder(folder_path: Path) -> Dict:
    """Scan folder and generate index data."""

    # Get markdown files (exclude index files and READMEs at this level)
    md_files = sorted(
        [f for f in folder_path.glob("*.md") if f.name not in ["index.md", "README.md"]]
    )

    # Get subfolders (exclude hidden and special folders)
    subfolders = sorted(
        [
            d
            for d in folder_path.iterdir()
            if d.is_dir() and not d.name.startswith((".", "_"))
        ]
    )

    # Read README if exists for folder description
    readme_path = folder_path / "README.md"
    folder_description = ""
    if readme_path.exists():
        readme_content = readme_path.read_text(encoding="utf-8")
        folder_description = extract_description(readme_content)

    # Build index
    index = {
        "folder": str(folder_path).replace(str(Path.cwd()) + "/", ""),
        "description": folder_description,
        "last_updated": datetime.now().strftime("%Y-%m-%d"),
        "file_count": len(md_files),
        "files": [],
        "subfolders": [],
    }

    # Scan files
    for md_file in md_files:
        try:
            content = md_file.read_text(encoding="utf-8")
            title = extract_title(content)
            description = extract_description(content)
            metadata = extract_metadata(content)

            file_info = {
                "name": md_file.name,
                "title": title,
                "description": description,
                "last_updated": datetime.fromtimestamp(
                    md_file.stat().st_mtime
                ).strftime("%Y-%m-%d"),
                "size_lines": len(content.split("\n")),
            }

            # Add optional metadata if present
            if "doc_type" in metadata:
                file_info["doc_type"] = metadata["doc_type"]
            if "complexity" in metadata:
                file_info["complexity"] = metadata["complexity"]
            if "audience" in metadata:
                file_info["audience"] = metadata["audience"]
            if "status" in metadata:
                file_info["status"] = metadata["status"]

            index["files"].append(file_info)

        except Exception as e:
            print(f"Warning: Could not process {md_file}: {e}")
            continue

    # Scan subfolders
    for subfolder in subfolders:
        subfolder_readme = subfolder / "README.md"
        subfolder_description = ""

        if subfolder_readme.exists():
            try:
                readme_content = subfolder_readme.read_text(encoding="utf-8")
                subfolder_description = extract_description(readme_content)
            except (OSError, UnicodeDecodeError):
                pass

        index["subfolders"].append(
            {
                "name": subfolder.name,
                "path": f"{subfolder.name}/",
                "description": subfolder_description,
            }
        )

    return index


def generate_json(index: Dict, output_path: Path):
    """Generate index.json."""
    json_path = output_path / "index.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
    print(f"✅ Generated: {json_path}")


def generate_markdown(index: Dict, output_path: Path):
    """Generate index.md."""

    folder_name = Path(index["folder"]).name or "Root"

    lines = [
        f"# {folder_name.replace('-', ' ').title()} Index",
        "",
    ]

    if index["description"]:
        lines.extend([index["description"], ""])

    lines.extend(
        [
            f"**Last Updated:** {index['last_updated']}  ",
            f"**File Count:** {index['file_count']}",
            "",
        ]
    )

    if index["files"]:
        lines.extend(
            [
                "## Files",
                "",
                "| File | Description | Updated | Lines |",
                "|------|-------------|---------|-------|",
            ]
        )

        for file in index["files"]:
            desc = file.get("description", "")[:80]  # Truncate long descriptions
            lines.append(
                f"| [{file['name']}]({file['name']}) | "
                f"{desc} | "
                f"{file['last_updated']} | "
                f"{file['size_lines']} |"
            )

        lines.append("")

    if index["subfolders"]:
        lines.extend(["## Subfolders", ""])

        for subfolder in index["subfolders"]:
            desc = f" - {subfolder['description']}" if subfolder["description"] else ""
            lines.append(f"- [{subfolder['name']}/]({subfolder['path']}){desc}")

        lines.append("")

    md_path = output_path / "index.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"✅ Generated: {md_path}")


def main():
    args = sys.argv[1:]
    json_only = False
    md_only = False

    if "--json-only" in args:
        json_only = True
        args.remove("--json-only")
    if "--md-only" in args:
        md_only = True
        args.remove("--md-only")

    if json_only and md_only:
        print("❌ Choose only one of --json-only or --md-only")
        sys.exit(1)

    if len(args) < 1:
        print("Usage: generate_folder_index.py [--json-only|--md-only] <folder>")
        print("\nExample:")
        print("  python scripts/generate_folder_index.py docs/getting-started/")
        print("  python scripts/generate_folder_index.py --json-only docs/")
        sys.exit(1)

    folder = Path(args[0])
    if not folder.exists():
        print(f"❌ Folder not found: {folder}")
        sys.exit(1)

    if not folder.is_dir():
        print(f"❌ Not a directory: {folder}")
        sys.exit(1)

    print(f"📂 Scanning folder: {folder}")
    index = scan_folder(folder)

    print(
        f"   Found {len(index['files'])} files, {len(index['subfolders'])} subfolders"
    )

    if not md_only:
        generate_json(index, folder)
    if not json_only:
        generate_markdown(index, folder)

    print(f"✅ Index generation complete for: {folder}")


if __name__ == "__main__":
    main()

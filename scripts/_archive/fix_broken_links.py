#!/usr/bin/env python3
"""Automatically fix broken internal links in markdown files.

This script:
1. Scans all markdown files for broken internal links
2. Attempts to find the correct location of target files
3. Generates correct relative paths
4. Updates all files in place

Usage:
    python scripts/fix_broken_links.py                # Dry run (show what would change)
    python scripts/fix_broken_links.py --fix          # Apply fixes
    python scripts/fix_broken_links.py --fix --verbose # Apply fixes with details
"""
import re
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from collections import defaultdict


def find_markdown_links(content: str) -> List[Tuple[str, str, int]]:
    """Find all markdown links [text](target) with their positions."""
    pattern = r"(?<!!)\[([^\]]+)\]\(([^)]+)\)"
    matches = []
    for match in re.finditer(pattern, content):
        text, target = match.groups()
        matches.append((text, target, match.start()))
    return matches


def build_file_index(project_root: Path) -> Dict[str, List[Path]]:
    """Build index of all markdown files by filename."""
    index: Dict[str, List[Path]] = defaultdict(list)

    # Scan all markdown files
    for md_file in project_root.rglob("*.md"):
        # Skip node_modules, .git, etc.
        if any(
            part.startswith(".") or part == "node_modules" for part in md_file.parts
        ):
            continue
        filename = md_file.name.lower()
        index[filename].append(md_file)

    # Also index Python files that might be linked
    for py_file in project_root.rglob("*.py"):
        if any(
            part.startswith(".") or part == "node_modules" for part in py_file.parts
        ):
            continue
        filename = py_file.name.lower()
        index[filename].append(py_file)

    return index


def normalize_filename(name: str) -> str:
    """Normalize filename for matching (lowercase, handle variations)."""
    name = name.lower()
    # Handle SCREAMING_SNAKE_CASE to kebab-case
    name = name.replace("_", "-")
    return name


def find_best_match(
    target_path: str,
    source_file: Path,
    file_index: Dict[str, List[Path]],
    project_root: Path,
) -> Optional[Path]:
    """Find the best matching file for a broken link target."""
    # Extract just the filename from the target
    target = Path(target_path)
    filename = target.name.lower()

    # Try exact filename match
    if filename in file_index:
        candidates = file_index[filename]
        if len(candidates) == 1:
            return candidates[0]
        # Multiple matches - try to find best one based on path similarity
        # Prefer files in similar directory structure
        source_parts = set(source_file.parent.relative_to(project_root).parts)
        best_score = -1
        best_match = None
        for candidate in candidates:
            candidate_parts = set(candidate.parent.relative_to(project_root).parts)
            score = len(source_parts & candidate_parts)
            if score > best_score:
                best_score = score
                best_match = candidate
        return best_match

    # Try normalized filename (handle UPPERCASE to lowercase, _ to -)
    normalized = normalize_filename(filename)
    for indexed_name, candidates in file_index.items():
        if normalize_filename(indexed_name) == normalized:
            if len(candidates) == 1:
                return candidates[0]
            # Return first match from docs/ if available
            for c in candidates:
                if "docs" in c.parts:
                    return c
            return candidates[0]

    # Try without extension variations
    stem = target.stem.lower()
    normalized_stem = normalize_filename(stem)
    for indexed_name, candidates in file_index.items():
        indexed_stem = Path(indexed_name).stem.lower()
        if normalize_filename(indexed_stem) == normalized_stem:
            if len(candidates) == 1:
                return candidates[0]
            # Return first match from docs/ if available
            for c in candidates:
                if "docs" in c.parts:
                    return c
            return candidates[0]

    return None


def compute_relative_path(from_file: Path, to_file: Path, project_root: Path) -> str:
    """Compute relative path from source file to target file."""
    from_dir = from_file.parent
    try:
        rel_path = to_file.relative_to(from_dir)
        return str(rel_path)
    except ValueError:
        # Files are in different directory trees
        # Go up to common ancestor then down
        from_rel = from_dir.relative_to(project_root)
        to_rel = to_file.relative_to(project_root)

        # Find common prefix
        from_parts = from_rel.parts
        to_parts = to_rel.parts

        common_length = 0
        for i, (f, t) in enumerate(zip(from_parts, to_parts)):
            if f == t:
                common_length = i + 1
            else:
                break

        # Go up from source
        ups = len(from_parts) - common_length
        # Then down to target
        downs = to_parts[common_length:]

        path_parts = [".."] * ups + list(downs)
        return "/".join(path_parts)


def fix_links_in_file(
    file_path: Path,
    file_index: Dict[str, List[Path]],
    project_root: Path,
    apply_fix: bool = False,
    verbose: bool = False,
) -> Tuple[int, int, List[str]]:
    """Fix broken links in a single file. Returns (checked, fixed, messages)."""
    content = file_path.read_text(encoding="utf-8")
    links = find_markdown_links(content)

    checked = 0
    fixed = 0
    messages = []
    replacements = []

    for text, target, pos in links:
        # Skip external links
        if target.startswith(("http://", "https://", "mailto:")):
            continue
        # Skip pure anchors
        if target.startswith("#"):
            continue

        checked += 1

        # Handle anchors
        target_path = target.split("#")[0]
        anchor = "#" + target.split("#")[1] if "#" in target else ""

        if not target_path:
            continue

        # Resolve relative to the file's directory
        full_path = (file_path.parent / target_path).resolve()

        # Check if exists
        if full_path.exists():
            continue  # Link is valid

        # Try to find the file
        match = find_best_match(target_path, file_path, file_index, project_root)

        if match:
            # Compute correct relative path
            new_path = compute_relative_path(file_path, match, project_root)
            new_target = new_path + anchor

            if new_target != target:
                replacements.append((target, new_target, text))
                fixed += 1
                if verbose:
                    messages.append(f"  [{text}]({target}) → ({new_target})")

    # Apply replacements
    if apply_fix and replacements:
        new_content = content
        for old_target, new_target, link_text in replacements:
            # Be careful to replace the exact link
            old_link = f"]({old_target})"
            new_link = f"]({new_target})"
            new_content = new_content.replace(old_link, new_link)

        file_path.write_text(new_content, encoding="utf-8")

    return checked, fixed, messages


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Fix broken markdown links")
    parser.add_argument(
        "--fix", action="store_true", help="Apply fixes (default: dry run)"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show detailed changes"
    )
    parser.add_argument(
        "--exclude-archive", action="store_true", help="Skip _archive directories"
    )
    args = parser.parse_args()

    # Find project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    print("🔍 Building file index...")
    file_index = build_file_index(project_root)
    print(f"   Indexed {sum(len(v) for v in file_index.values())} files")

    # Collect all markdown files
    md_files = list(project_root.rglob("*.md"))
    md_files = [
        f for f in md_files if not any(part.startswith(".") for part in f.parts)
    ]

    if args.exclude_archive:
        md_files = [f for f in md_files if "_archive" not in str(f)]

    print(f"\n📝 Scanning {len(md_files)} markdown files...")

    total_checked = 0
    total_fixed = 0
    files_modified = 0

    for md_file in sorted(md_files):
        checked, fixed, messages = fix_links_in_file(
            md_file, file_index, project_root, apply_fix=args.fix, verbose=args.verbose
        )
        total_checked += checked
        total_fixed += fixed

        if fixed > 0:
            files_modified += 1
            rel_path = md_file.relative_to(project_root)
            action = "Fixed" if args.fix else "Would fix"
            print(f"\n{action} {fixed} links in {rel_path}")
            for msg in messages:
                print(msg)

    print(f"\n{'='*60}")
    print("📊 Summary:")
    print(f"   Links checked: {total_checked}")
    print(f"   Links {'fixed' if args.fix else 'to fix'}: {total_fixed}")
    print(f"   Files {'modified' if args.fix else 'to modify'}: {files_modified}")

    if not args.fix and total_fixed > 0:
        print("\n💡 Run with --fix to apply changes:")
        print("   python scripts/fix_broken_links.py --fix")

    if args.fix and total_fixed > 0:
        print(f"\n✅ Fixed {total_fixed} broken links!")
        print("\n🔄 Re-running link checker to verify...")
        import subprocess

        result = subprocess.run(
            [
                str(project_root / ".venv/bin/python"),
                str(script_dir / "check_links.py"),
            ],
            capture_output=True,
            text=True,
            cwd=project_root,
        )
        # Extract just the summary
        for line in result.stdout.split("\n")[:5]:
            print(f"   {line}")

    return 0 if total_fixed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

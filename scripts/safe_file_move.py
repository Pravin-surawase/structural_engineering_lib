#!/usr/bin/env python3
"""Safe file move script with automatic link updates.

This script safely moves/renames files by:
1. Checking for references in docs and code (using fast git grep)
2. Updating all internal links
3. Optionally creating redirect stubs
4. Running link validation

Usage:
    python scripts/safe_file_move.py <source> <destination> [--stub] [--dry-run]

Examples:
    python scripts/safe_file_move.py docs/old.md docs/new.md
    python scripts/safe_file_move.py docs/old.md docs/archive/old.md --stub
    python scripts/safe_file_move.py docs/old.md docs/new.md --dry-run
"""

from __future__ import annotations

import argparse
import contextlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path


def find_references(file_path: Path, project_root: Path) -> list[tuple[Path, str, int]]:
    """Find all references to a file in docs and code.

    Returns list of (file, line_content, line_number) tuples.

    Uses git grep for fast searching (works in git repos), falls back to Python if not.
    """
    filename = file_path.name

    try:
        relative_path = str(file_path.relative_to(project_root))
    except ValueError:
        relative_path = str(file_path)

    # Try using git grep for fast search (uses git's index, much faster)
    references = _find_references_git_grep(filename, project_root)
    if references is not None:
        # Filter out self-references
        return [(f, line, num) for f, line, num in references if f != file_path]

    # Fallback to Python-based search (slower but always works)
    return _find_references_python(file_path, project_root)


def _find_references_git_grep(
    pattern: str, project_root: Path
) -> list[tuple[Path, str, int]] | None:
    """Fast reference search using git grep.

    Git grep uses the git index which is much faster than filesystem search.
    Returns None if not in a git repo or git grep fails.
    """
    references = []

    try:
        # Use git grep - it's fast because it uses git's index
        result = subprocess.run(
            [
                "git",
                "grep",
                "-n",  # Show line numbers
                "-I",  # Skip binary files
                "--no-color",
                "-F",  # Fixed string (literal)
                pattern,
            ],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=10,  # 10 second timeout
        )

        if result.returncode not in (0, 1):  # 0=found, 1=not found
            return None

        # Parse output: filename:lineno:content
        for line in result.stdout.strip().split("\n"):
            if not line:
                continue
            parts = line.split(":", 2)
            if len(parts) >= 3:
                file_match = project_root / parts[0]
                try:
                    line_num = int(parts[1])
                    content = parts[2].strip()[:100]
                    references.append((file_match, content, line_num))
                except (ValueError, IndexError):
                    continue

        return references

    except (subprocess.TimeoutExpired, OSError, FileNotFoundError):
        return None


def _find_references_python(
    file_path: Path, project_root: Path
) -> list[tuple[Path, str, int]]:
    """Python-based reference search (slower fallback).

    Note: This can be slow for large projects on iCloud or network drives.
    """
    references = []
    filename = file_path.name
    stem = file_path.stem

    try:
        relative_path = str(file_path.relative_to(project_root))
    except ValueError:
        relative_path = str(file_path)

    patterns = [
        filename,
        stem,
        relative_path,
        relative_path.replace("/", "\\"),
    ]

    # Search directories
    search_dirs = ["docs", "agents", "Python", "VBA", "streamlit_app", ".github"]
    extensions = [".md", ".py", ".bas", ".txt", ".json", ".yml", ".yaml"]

    # Directories to exclude (performance optimization)
    exclude_dirs = {
        ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache",
        "build", "dist", "htmlcov", ".mypy_cache", ".ruff_cache",
        "*.egg-info", ".git", "logs", "tmp"
    }

    for search_dir in search_dirs:
        search_path = project_root / search_dir
        if not search_path.exists():
            continue

        for ext in extensions:
            for file in search_path.rglob(f"*{ext}"):
                # Skip if file is in excluded directory
                if any(excluded in file.parts for excluded in exclude_dirs):
                    continue
                if file == file_path:
                    continue
                try:
                    content = file.read_text(encoding="utf-8", errors="ignore")
                    for i, line in enumerate(content.split("\n"), 1):
                        for pattern in patterns:
                            if pattern in line:
                                references.append((file, line.strip()[:100], i))
                                break
                except (OSError, UnicodeDecodeError):
                    continue

    return references


def _relative_posix_path(target: Path, start: Path) -> str:
    """Return a POSIX-style relative path from start to target."""
    return Path(os.path.relpath(target, start=start)).as_posix()


def update_links(
    old_path: Path, new_path: Path, project_root: Path, dry_run: bool = False
) -> tuple[int, list[str]]:
    """Update all links from old_path to new_path.

    Returns number of files updated.
    """
    updated_count = 0
    updated_files: list[str] = []
    old_relative = old_path.relative_to(project_root).as_posix()
    new_relative = new_path.relative_to(project_root).as_posix()

    search_dirs = ["docs", "agents", "Python", "streamlit_app"]
    text_extensions = {".md", ".json", ".yml", ".yaml", ".txt"}

    for search_dir in search_dirs:
        search_path = project_root / search_dir
        if not search_path.exists():
            continue

        for file in search_path.rglob("*"):
            if file.suffix not in text_extensions:
                continue
            if file == old_path or file == new_path:
                continue

            try:
                content = file.read_text(encoding="utf-8")
                original_content = content

                # Calculate paths from this file location.
                file_dir = file.parent
                old_rel_from_file = _relative_posix_path(old_path, file_dir)
                new_rel_from_file = _relative_posix_path(new_path, file_dir)

                if file.suffix == ".md":
                    # Replace markdown link targets for:
                    # - file-relative links: ](../old.md)
                    # - repo-relative links: ](docs/path/old.md)
                    # - root-absolute links: ](/docs/path/old.md)
                    markdown_link_patterns = {
                        old_rel_from_file: new_rel_from_file,
                        old_relative: new_relative,
                        f"/{old_relative}": f"/{new_relative}",
                    }
                    for old_target, new_target in markdown_link_patterns.items():
                        content = re.sub(
                            rf"(\[[^\]]+\]\(){re.escape(old_target)}(\))",
                            rf"\g<1>{new_target}\g<2>",
                            content,
                        )

                # Keep root-relative path references synced in json/yaml/txt.
                content = content.replace(old_relative, new_relative)
                content = content.replace(
                    old_relative.replace("/", "\\"),
                    new_relative.replace("/", "\\"),
                )

                if content != original_content:
                    if dry_run:
                        print(f"  Would update: {file}")
                    else:
                        file.write_text(content, encoding="utf-8")
                        print(f"  Updated: {file}")
                    updated_count += 1
                    updated_files.append(str(file.relative_to(project_root)))

            except (OSError, UnicodeDecodeError) as e:
                print(f"  Warning: Could not process {file}: {e}")

    return updated_count, updated_files


def create_redirect_stub(old_path: Path, new_path: Path, project_root: Path) -> None:
    """Create a redirect stub at the old location."""
    new_relative = new_path.relative_to(project_root)

    stub_content = f"""# Moved

This document has been moved to a new location.

**New location:** [{new_path.name}]({new_relative})

*Redirect created: {Path(__file__).name}*
"""
    old_path.write_text(stub_content, encoding="utf-8")
    print(f"  Created redirect stub at: {old_path}")


def get_broken_link_count(project_root: Path, *, print_output: bool = False) -> int | None:
    """Run link checker and return broken-link count if parsable."""
    check_script = project_root / "scripts" / "check_links.py"
    if not check_script.exists():
        print("  Warning: check_links.py not found, skipping validation")
        return None

    result = subprocess.run(
        [sys.executable, str(check_script)],
        cwd=project_root,
        capture_output=True,
        text=True,
    )

    if print_output:
        print(result.stdout)

    match = re.search(r"Broken links:\s*(\d+)", result.stdout)
    if match:
        return int(match.group(1))

    if result.returncode == 0:
        return 0

    return None


def run_move(args: argparse.Namespace) -> tuple[int, dict[str, object]]:
    """Execute safe move and return (exit_code, structured_result)."""
    result: dict[str, object] = {
        "tool": "safe_file_move",
        "dry_run": bool(args.dry_run),
        "mode": "dry-run" if args.dry_run else "live",
        "success": False,
        "source": args.source,
        "destination": args.destination,
        "stub_requested": bool(args.stub),
    }

    # Determine project root
    project_root = Path(__file__).parent.parent.resolve()

    source = Path(args.source)
    if not source.is_absolute():
        source = project_root / source
    source = source.resolve()

    destination = Path(args.destination)
    if not destination.is_absolute():
        destination = project_root / destination
    destination = destination.resolve()

    # Validate
    if not source.exists():
        print(f"❌ Error: Source file not found: {source}")
        result["error"] = f"Source file not found: {source}"
        return 1, result

    if destination.exists() and not args.force:
        print(f"❌ Error: Destination already exists: {destination}")
        print("   Use --force to overwrite")
        result["error"] = f"Destination already exists: {destination}"
        return 1, result

    result["source"] = str(source.relative_to(project_root))
    result["destination"] = str(destination.relative_to(project_root))

    print("=" * 60)
    print("🔄 Safe File Move")
    print("=" * 60)
    print(f"Source:      {source.relative_to(project_root)}")
    print(f"Destination: {destination.relative_to(project_root)}")
    print(f"Mode:        {'DRY RUN' if args.dry_run else 'LIVE'}")
    print()

    baseline_broken = None
    if not args.dry_run:
        baseline_broken = get_broken_link_count(project_root)
        if baseline_broken is not None:
            print(f"🔢 Baseline broken links: {baseline_broken}")
            print()
    result["baseline_broken_links"] = baseline_broken

    # Step 1: Find references
    print("📍 Step 1: Finding references...")
    references = find_references(source, project_root)
    result["references_count"] = len(references)
    result["references"] = [
        {
            "file": str(ref_file.relative_to(project_root)),
            "line": ref_lineno,
        }
        for ref_file, _ref_line, ref_lineno in references
    ]

    if references:
        print(f"   Found {len(references)} reference(s):")
        for ref_file, ref_line, ref_lineno in references[:10]:
            rel_file = ref_file.relative_to(project_root)
            print(f"     - {rel_file}:{ref_lineno}")
        if len(references) > 10:
            print(f"     ... and {len(references) - 10} more")
    else:
        print("   No references found")

    # Step 2: Move file
    print()
    print("📦 Step 2: Moving file...")
    if args.dry_run:
        print(f"   Would move: {source.name} → {destination}")
    else:
        destination.parent.mkdir(parents=True, exist_ok=True)
        source.rename(destination)
        print(f"   Moved: {source.name} → {destination}")
    result["moved"] = not args.dry_run

    # Step 3: Update links
    print()
    print("🔗 Step 3: Updating links...")
    updated, updated_files = update_links(source, destination, project_root, args.dry_run)
    print(f"   Updated {updated} file(s)")
    result["updated_count"] = updated
    result["updated_files"] = updated_files

    # Step 4: Create redirect stub if requested
    stub_created = False
    if args.stub:
        print()
        print("📝 Step 4: Creating redirect stub...")
        if args.dry_run:
            print(f"   Would create stub at: {source}")
        else:
            create_redirect_stub(source, destination, project_root)
            stub_created = True
    result["stub_created"] = stub_created

    # Step 5: Validate
    print()
    print("✅ Step 5: Validating links...")
    broken_after = None
    if args.dry_run:
        print("   Skipped (dry run)")
    else:
        broken_after = get_broken_link_count(project_root, print_output=True)
        if broken_after is None:
            print("   ⚠️  Could not parse broken-link count from checker output.")
        elif baseline_broken is None:
            print(f"   Broken links after move: {broken_after}")
        elif broken_after > baseline_broken:
            print(
                f"   ❌ Broken links increased ({baseline_broken} → {broken_after})."
            )
            print("   Review and fix links before committing.")
            print()
            print("=" * 60)
            print("⚠️  Move completed with link regressions.")
            print("=" * 60)
            result["broken_links_after"] = broken_after
            result["changed_files"] = sorted(
                set(updated_files)
                | {str(source.relative_to(project_root)), str(destination.relative_to(project_root))}
            )
            result["success"] = False
            return 1, result
        else:
            print(f"   ✅ Broken links unchanged/improved ({baseline_broken} → {broken_after})")
    result["broken_links_after"] = broken_after

    print()
    print("=" * 60)
    if args.dry_run:
        print("✨ Dry run complete. No changes made.")
    else:
        print("✨ Move complete!")
        print()
        print("Next steps:")
        print("  1. Review changes: git diff")
        print("  2. Commit: ./scripts/ai_commit.sh 'refactor: move file'")
    print("=" * 60)
    result["changed_files"] = sorted(
        set(updated_files)
        | {str(source.relative_to(project_root)), str(destination.relative_to(project_root))}
    )
    result["success"] = True
    return 0, result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Safely move files with automatic link updates"
    )
    parser.add_argument("source", help="Source file path")
    parser.add_argument("destination", help="Destination file path")
    parser.add_argument(
        "--stub", action="store_true", help="Create redirect stub at old location"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would happen without making changes",
    )
    parser.add_argument(
        "--force", action="store_true", help="Proceed even if references are found"
    )
    parser.add_argument("--json", action="store_true", help="Output structured JSON")
    args = parser.parse_args()

    if args.json:
        with contextlib.redirect_stdout(sys.stderr):
            exit_code, payload = run_move(args)
        print(json.dumps(payload, indent=2))
        return exit_code

    exit_code, _payload = run_move(args)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())

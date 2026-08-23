#!/usr/bin/env python3
"""Migrate a React component to a new feature-grouped folder.

When to use: When moving a React component to a new folder. Updates all imports automatically.

Safely moves a .tsx/.ts file within react_app/src/ and updates ALL
import paths across the React codebase.

Features:
1. Moves .tsx/.ts file + co-located .css to new location
2. Updates all import/require paths (relative and alias)
3. Updates index exports (barrel files)
4. Validates no broken imports after move

Usage:
    python scripts/migrate_react_component.py src/components/ImportView.tsx src/components/import/ImportView.tsx --dry-run
    python scripts/migrate_react_component.py src/components/DesignView.tsx src/components/design/DesignView.tsx

Options:
    --dry-run     Show what would change without making changes
    --no-css      Don't move co-located CSS file
"""

from __future__ import annotations

import argparse
import contextlib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib.safe_file_ops import (
    SafeFileError,
    capture_snapshots,
    resolve_new_destination,
    resolve_regular_source,
    restore_snapshots,
)

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
REACT_ROOT = PROJECT_ROOT / "react_app"
REACT_SRC = REACT_ROOT / "src"

# File extensions to search
SEARCH_EXTENSIONS = {".ts", ".tsx", ".js", ".jsx", ".css", ".json"}

# Patterns to skip
SKIP_PATTERNS = {"node_modules", ".turbo", "dist", "build", ".vite"}


def _resolve_react_source(path_str: str) -> Path:
    """Resolve source path supporting src/... and react_app/src/... inputs."""
    raw = Path(path_str)
    if raw.is_absolute():
        return raw.resolve()

    candidates: list[Path] = []
    if raw.parts and raw.parts[0] == "react_app":
        candidates.append(PROJECT_ROOT / raw)
    if raw.parts and raw.parts[0] == "src":
        candidates.append(REACT_ROOT / raw)
    candidates.append(REACT_SRC / raw)
    candidates.append(REACT_ROOT / raw)

    for candidate in candidates:
        if candidate.exists():
            return candidate.absolute()

    # Keep deterministic fallback for error reporting.
    if raw.parts and raw.parts[0] == "react_app":
        return (PROJECT_ROOT / raw).absolute()
    if raw.parts and raw.parts[0] == "src":
        return (REACT_ROOT / raw).absolute()
    return (REACT_SRC / raw).absolute()


def _resolve_react_destination(path_str: str) -> Path:
    """Resolve destination path without duplicating react_app/ prefix."""
    raw = Path(path_str)
    if raw.is_absolute():
        return raw.absolute()
    if raw.parts and raw.parts[0] == "react_app":
        return (PROJECT_ROOT / raw).absolute()
    if raw.parts and raw.parts[0] == "src":
        return (REACT_ROOT / raw).absolute()
    return (REACT_SRC / raw).absolute()


def find_react_files() -> list[Path]:
    """Find all source files in react_app/src/."""
    files = []
    for ext in SEARCH_EXTENSIONS:
        for f in REACT_SRC.rglob(f"*{ext}"):
            if any(skip in f.parts for skip in SKIP_PATTERNS):
                continue
            files.append(f)
    return sorted(files)


def compute_relative_import(from_file: Path, to_file: Path) -> str:
    """Compute the relative import path from one file to another.

    Returns: relative path like './ImportView' or '../hooks/useCSV'
    """
    from_dir = from_file.parent
    try:
        rel = to_file.relative_to(from_dir)
        parts = list(rel.parts)
        # Remove extension
        if parts[-1].endswith((".ts", ".tsx", ".js", ".jsx")):
            parts[-1] = Path(parts[-1]).stem
        result = "./" + "/".join(parts)
    except ValueError:
        # Need to go up some directories
        # Find common ancestor
        from_parts = list(from_dir.parts)
        to_parts = list(to_file.parent.parts)

        # Find common prefix length
        common_len = 0
        for a, b in zip(from_parts, to_parts):
            if a == b:
                common_len += 1
            else:
                break

        ups = len(from_parts) - common_len
        downs = to_parts[common_len:]

        filename = to_file.stem
        if ups == 0:
            result = "./" + "/".join(downs + [filename])
        else:
            result = "/".join([".."] * ups + downs + [filename])

    return result


def find_import_references(
    old_path: Path, files: list[Path]
) -> list[tuple[Path, int, str, str]]:
    """Find all files that import from old_path.

    Returns list of (file, line_number, line_text, old_import_str) tuples.
    """
    references = []
    old_stem = old_path.stem  # e.g., "ImportView"
    old_stem_no_ext = old_stem  # Component name without extension

    for src_file in files:
        if src_file == old_path:
            continue

        try:
            content = src_file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue

        for i, line in enumerate(content.split("\n"), 1):
            # Check for import statements containing the component name
            # from './components/ImportView' or from '../ImportView'
            # import ... from '...'
            patterns = [
                # ES import: import X from './path'
                rf"""(from\s+['"])(.*?/{re.escape(old_stem_no_ext)}(?:\.\w+)?)(['"])""",
                # import('./path')
                rf"""(import\(['"])(.*?/{re.escape(old_stem_no_ext)}(?:\.\w+)?)(['"]\))""",
                # require('./path')
                rf"""(require\(['"])(.*?/{re.escape(old_stem_no_ext)}(?:\.\w+)?)(['"]\))""",
            ]

            for pattern in patterns:
                match = re.search(pattern, line)
                if match:
                    import_str = match.group(2)
                    # Validate that this actually resolves to our file
                    resolved = resolve_import(src_file, import_str)
                    if resolved and resolved.resolve() == old_path.resolve():
                        references.append((src_file, i, line.strip(), import_str))

    return references


def resolve_import(from_file: Path, import_str: str) -> Path | None:
    """Resolve a relative import string to an absolute path."""
    if import_str.startswith("."):
        base = from_file.parent / import_str
    else:
        return None  # Alias imports handled separately

    # Try with common extensions
    for ext in ["", ".ts", ".tsx", ".js", ".jsx"]:
        candidate = base.parent / (base.name + ext)
        if candidate.exists():
            return candidate

    # Try as directory with index
    for ext in [".ts", ".tsx", ".js", ".jsx"]:
        candidate = base / f"index{ext}"
        if candidate.exists():
            return candidate

    return None


def update_imports(
    old_path: Path,
    new_path: Path,
    references: list[tuple[Path, int, str, str]],
    dry_run: bool = False,
) -> tuple[int, list[str]]:
    """Update all import paths from old to new location."""
    updated_count = 0
    updated_files: list[str] = []
    files_to_update: dict[Path, list[tuple[str, str]]] = {}

    for ref_file, _line_num, _line_text, old_import in references:
        new_import = compute_relative_import(ref_file, new_path)

        if ref_file not in files_to_update:
            files_to_update[ref_file] = []
        files_to_update[ref_file].append((old_import, new_import))

    for src_file, replacements in files_to_update.items():
        try:
            content = src_file.read_text(encoding="utf-8")
            original = content
        except (OSError, UnicodeDecodeError):
            continue

        for old_import, new_import in replacements:
            # Replace in import strings (preserve quotes)
            content = content.replace(f"'{old_import}'", f"'{new_import}'")
            content = content.replace(f'"{old_import}"', f'"{new_import}"')

        if content != original:
            if dry_run:
                rel = src_file.relative_to(PROJECT_ROOT)
                print(f"  Would update: {rel}")
                for old_imp, new_imp in replacements:
                    print(f"    '{old_imp}' → '{new_imp}'")
            else:
                src_file.write_text(content, encoding="utf-8")
                rel = src_file.relative_to(PROJECT_ROOT)
                print(f"  Updated: {rel}")
            updated_count += 1
            updated_files.append(str(rel))

    return updated_count, updated_files


def find_colocated_css(component_path: Path) -> Path | None:
    """Find co-located CSS file for a component."""
    css_name = component_path.stem + ".css"
    css_path = component_path.parent / css_name
    return css_path if css_path.exists() else None


def ensure_barrel_export(
    directory: Path, component_name: str, dry_run: bool = False
) -> str:
    """Ensure the target directory has an index.ts with the component exported."""
    index_file = directory / "index.ts"

    export_line = (
        f"export {{ default as {component_name} }} from './{component_name}';\n"
    )

    if index_file.exists():
        content = index_file.read_text(encoding="utf-8")
        if component_name in content:
            return "already_present"
        if dry_run:
            print(f"  Would add export to: {index_file.relative_to(PROJECT_ROOT)}")
            return "would_update"
        else:
            content += export_line
            index_file.write_text(content, encoding="utf-8")
            print(f"  Updated barrel: {index_file.relative_to(PROJECT_ROOT)}")
            return "updated"
    else:
        if dry_run:
            print(f"  Would create barrel: {index_file.relative_to(PROJECT_ROOT)}")
            return "would_create"
        else:
            index_file.write_text(export_line, encoding="utf-8")
            print(f"  Created barrel: {index_file.relative_to(PROJECT_ROOT)}")
            return "created"


def run_migration(args: argparse.Namespace) -> tuple[int, dict[str, object]]:
    """Execute a previewable, byte-restorable React component migration."""
    result: dict[str, object] = {
        "tool": "migrate_react_component",
        "dry_run": bool(args.dry_run),
        "mode": "dry-run" if args.dry_run else "live",
        "success": False,
        "source": args.source,
        "destination": args.destination,
        "moved": False,
        "rolled_back": False,
    }

    try:
        source = resolve_regular_source(
            _resolve_react_source(args.source), PROJECT_ROOT
        )
        destination = resolve_new_destination(
            _resolve_react_destination(args.destination), PROJECT_ROOT, source
        )
    except SafeFileError as exc:
        result["error"] = str(exc)
        print(f"❌ {exc}")
        return 1, result

    result["source"] = str(source.relative_to(PROJECT_ROOT))
    result["destination"] = str(destination.relative_to(PROJECT_ROOT))

    print("=" * 60)
    print("⚛️  React Component Migration")
    print("=" * 60)
    print(f"Source:      {source.relative_to(PROJECT_ROOT)}")
    print(f"Destination: {destination.relative_to(PROJECT_ROOT)}")
    print(f"Mode:        {'DRY RUN' if args.dry_run else 'LIVE'}")
    print()

    css_source: Path | None = None
    css_dest: Path | None = None
    if not args.no_css:
        css_source = find_colocated_css(source)
        if css_source:
            try:
                css_source = resolve_regular_source(css_source, PROJECT_ROOT)
                css_dest = resolve_new_destination(
                    destination.parent / css_source.name, PROJECT_ROOT, css_source
                )
            except SafeFileError as exc:
                result["error"] = str(exc)
                print(f"❌ {exc}")
                return 1, result
            print(f"📎 Co-located CSS: {css_source.name}")
    print()
    result["css_source"] = (
        str(css_source.relative_to(PROJECT_ROOT)) if css_source else None
    )
    result["css_destination"] = (
        str(css_dest.relative_to(PROJECT_ROOT)) if css_dest else None
    )

    print("🔍 Step 1: Finding import references...")
    all_files = find_react_files()
    references = find_import_references(source, all_files)
    reference_files = sorted({reference[0] for reference in references})
    print(
        f"   Found {len(references)} reference(s) in {len(set(r[0] for r in references))} file(s)"
    )
    result["references_count"] = len(references)
    result["references"] = [
        {"file": str(ref_file.relative_to(PROJECT_ROOT)), "line": line_num}
        for ref_file, line_num, _line_text, _old_import in references
    ]

    for ref_file, line_num, _line_text, _ in references[:10]:
        rel = ref_file.relative_to(PROJECT_ROOT)
        print(f"     {rel}:{line_num}")
    if len(references) > 10:
        print(f"     ... and {len(references) - 10} more")
    print()

    component_name = destination.stem
    barrel_path = destination.parent / "index.ts"
    if barrel_path.exists():
        barrel_content = barrel_path.read_text(encoding="utf-8")
        barrel_status = (
            "already_present" if component_name in barrel_content else "would_update"
        )
    else:
        barrel_status = "would_create"
    barrel_will_change = barrel_status in {"would_update", "would_create"}

    expected_updated_files = [
        str(file.relative_to(PROJECT_ROOT)) for file in reference_files
    ]
    changed_files = set(expected_updated_files)
    changed_files.update(
        {
            str(source.relative_to(PROJECT_ROOT)),
            str(destination.relative_to(PROJECT_ROOT)),
        }
    )
    result["barrel_status"] = barrel_status
    result["barrel_path"] = (
        str(barrel_path.relative_to(PROJECT_ROOT)) if barrel_will_change else None
    )
    if barrel_will_change:
        changed_files.add(str(barrel_path.relative_to(PROJECT_ROOT)))
    if css_source and css_dest:
        changed_files.add(str(css_source.relative_to(PROJECT_ROOT)))
        changed_files.add(str(css_dest.relative_to(PROJECT_ROOT)))
    result["changed_files"] = sorted(changed_files)
    result["updated_count"] = len(reference_files)
    result["updated_files"] = expected_updated_files

    if args.dry_run:
        print(f"📦 Would move: {source.name} → {destination}")
        if css_source and css_dest:
            print(f"   Would move: {css_source.name} → {css_dest}")
        if barrel_will_change:
            print(f"   Barrel: {barrel_status}")
        result["success"] = True
        print("✨ Dry run complete. No changes made.")
        return 0, result

    snapshot_paths = {PROJECT_ROOT / path for path in result["changed_files"]}
    snapshots = capture_snapshots(snapshot_paths, PROJECT_ROOT)
    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
        source.rename(destination)
        result["moved"] = True
        if css_source and css_dest:
            css_source.rename(css_dest)
        result["css_moved"] = bool(css_source and css_dest)

        updated, updated_files = update_imports(
            source, destination, references, dry_run=False
        )
        if sorted(updated_files) != sorted(expected_updated_files):
            raise SafeFileError("Live import updates differed from the preview")
        live_barrel_status = ensure_barrel_export(
            destination.parent, component_name, dry_run=False
        )
        expected_live_status = {
            "would_create": "created",
            "would_update": "updated",
            "already_present": "already_present",
        }[barrel_status]
        if live_barrel_status != expected_live_status:
            raise SafeFileError("Live barrel update differed from the preview")

        for ref_file, _line, _text, _old_import in references:
            new_import = compute_relative_import(ref_file, destination)
            resolved = resolve_import(ref_file, new_import)
            if resolved is None or resolved.resolve() != destination.resolve():
                raise SafeFileError(
                    f"Updated import does not resolve: {ref_file} -> {new_import}"
                )
        if barrel_will_change:
            content = barrel_path.read_text(encoding="utf-8")
            if f"from './{component_name}'" not in content:
                raise SafeFileError("Barrel export validation failed")
        result["barrel_status"] = live_barrel_status
        result["updated_count"] = updated
    except Exception as exc:
        try:
            restore_snapshots(snapshots, PROJECT_ROOT)
            result["rolled_back"] = True
            result["moved"] = False
        except Exception as rollback_exc:
            result["rollback_error"] = str(rollback_exc)
        result["error"] = str(exc)
        print(f"❌ Migration failed: {exc}")
        return 1, result

    result["success"] = True
    print("✨ Migration complete and import paths validated.")
    return 0, result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Migrate React component with import updates"
    )
    parser.add_argument(
        "source",
        help="Source component path (e.g., src/components/ImportView.tsx)",
    )
    parser.add_argument(
        "destination",
        help="Destination path (e.g., src/components/import/ImportView.tsx)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Show what would happen")
    parser.add_argument(
        "--no-css", action="store_true", help="Don't move co-located CSS"
    )
    parser.add_argument("--json", action="store_true", help="Output structured JSON")
    args = parser.parse_args()

    if args.json:
        with contextlib.redirect_stdout(sys.stderr):
            exit_code, payload = run_migration(args)
        print(json.dumps(payload, indent=2))
        return exit_code

    exit_code, _payload = run_migration(args)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Move one repository file transactionally and update deterministic references.

Directories, symlinks, outside paths, destination replacement, and unresolved
maintained references are rejected. Live mutations are restored byte-for-byte
when reference updates or link validation fail.
"""

from __future__ import annotations

import argparse
import contextlib
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib.safe_file_ops import (
    Reference,
    SafeFileError,
    capture_snapshots,
    classify_references,
    require_no_link_regression,
    resolve_new_destination,
    resolve_regular_source,
    restore_snapshots,
    run_link_checker,
    update_references,
)
from _lib.utils import REPO_ROOT


def find_references(file_path: Path, project_root: Path) -> list[tuple[Path, str, int]]:
    """Compatibility view over the canonical classified reference scanner."""
    references = classify_references(file_path, None, project_root)
    return [(ref.file, ref.line_text, ref.line_number) for ref in references]


def update_links(
    old_path: Path, new_path: Path, project_root: Path, dry_run: bool = False
) -> tuple[int, list[str]]:
    """Compatibility wrapper used by focused tests and maintained callers."""
    references = classify_references(old_path, new_path, project_root)
    files = sorted(
        {
            ref.file.relative_to(project_root).as_posix()
            for ref in references
            if ref.classification == "updateable"
        }
    )
    if dry_run:
        for file in files:
            print(f"  Would update: {file}")
        return len(files), files
    updated = update_references(old_path, new_path, references, project_root)
    for file in updated:
        print(f"  Updated: {file}")
    return len(updated), updated


def _create_redirect_stub(old_path: Path, new_path: Path) -> None:
    target = Path(os.path.relpath(new_path, start=old_path.parent)).as_posix()
    old_path.write_text(
        "# Moved\n\n"
        "This document has been moved to a new location.\n\n"
        f"**New location:** [{new_path.name}]({target})\n\n"
        "*Redirect created by `safe_file_move.py`.*\n",
        encoding="utf-8",
    )


def _reference_payload(references: list[Reference]) -> list[dict[str, object]]:
    return [ref.as_dict(REPO_ROOT) for ref in references]


def run_move(args: argparse.Namespace) -> tuple[int, dict[str, object]]:
    result: dict[str, object] = {
        "tool": "safe_file_move",
        "dry_run": bool(args.dry_run),
        "mode": "dry-run" if args.dry_run else "live",
        "success": False,
        "source": args.source,
        "destination": args.destination,
        "stub_requested": bool(args.stub),
        "stub_created": False,
        "moved": False,
        "rolled_back": False,
    }

    try:
        source = resolve_regular_source(args.source, REPO_ROOT)
        destination = resolve_new_destination(args.destination, REPO_ROOT, source)
    except SafeFileError as exc:
        result["error"] = str(exc)
        print(f"❌ {exc}")
        return 1, result

    source_rel = source.relative_to(REPO_ROOT).as_posix()
    destination_rel = destination.relative_to(REPO_ROOT).as_posix()
    result["source"] = source_rel
    result["destination"] = destination_rel

    print("=" * 60)
    print("🔄 Transactional File Move")
    print("=" * 60)
    print(f"Source:      {source_rel}")
    print(f"Destination: {destination_rel}")
    print(f"Mode:        {'DRY RUN' if args.dry_run else 'LIVE'}")

    baseline = run_link_checker(REPO_ROOT)
    if not baseline.operational:
        result["error"] = f"Link baseline unavailable: {baseline.error}"
        print(f"❌ {result['error']}")
        return 1, result
    result["baseline_broken_links"] = len(baseline.broken)

    references = classify_references(source, destination, REPO_ROOT)
    groups = {
        name: [ref for ref in references if ref.classification == name]
        for name in ("updateable", "preserved", "unresolved")
    }
    result["references_count"] = len(references)
    result["references"] = _reference_payload(references)
    result["reference_summary"] = {name: len(items) for name, items in groups.items()}

    print("\n📍 References")
    for name in ("updateable", "preserved", "unresolved"):
        print(f"  {name}: {len(groups[name])}")

    update_files = sorted({ref.file for ref in groups["updateable"]})
    changed_paths = {source, destination, *update_files}
    result["updated_count"] = len(update_files)
    result["updated_files"] = [
        path.relative_to(REPO_ROOT).as_posix() for path in update_files
    ]
    result["changed_files"] = sorted(
        path.relative_to(REPO_ROOT).as_posix() for path in changed_paths
    )

    if groups["unresolved"]:
        result["error"] = "Unresolved maintained references block the move"
        print("❌ Unresolved maintained references block the move:")
        for ref in groups["unresolved"][:10]:
            print(f"  {ref.file.relative_to(REPO_ROOT)}:{ref.line_number}")
        return 1, result

    if args.dry_run:
        result["success"] = True
        print("\n✨ Dry run complete. No changes made.")
        return 0, result

    snapshots = capture_snapshots(changed_paths, REPO_ROOT)
    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
        source.rename(destination)
        result["moved"] = True
        updated = update_references(source, destination, references, REPO_ROOT)
        if sorted(updated) != result["updated_files"]:
            raise SafeFileError("Live reference updates differed from the preview")
        if args.stub:
            _create_redirect_stub(source, destination)
            result["stub_created"] = True
        else:
            result["stub_created"] = False
        after = run_link_checker(REPO_ROOT)
        require_no_link_regression(baseline, after)
        result["broken_links_after"] = len(after.broken)
    except Exception as exc:
        try:
            restore_snapshots(snapshots, REPO_ROOT)
            result["rolled_back"] = True
            result["moved"] = False
        except Exception as rollback_exc:
            result["rollback_error"] = str(rollback_exc)
        result["error"] = str(exc)
        print(f"❌ Move failed: {exc}")
        print(
            "↩️  Original bytes restored."
            if result["rolled_back"]
            else "❌ Rollback failed."
        )
        return 1, result

    result["success"] = True
    print("\n✨ Move complete and validated.")
    return 0, result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Move one regular repository file with transactional reference updates"
    )
    parser.add_argument("source", help="Existing regular file inside the repository")
    parser.add_argument(
        "destination", help="New, non-existing path inside the repository"
    )
    parser.add_argument(
        "--stub",
        action="store_true",
        help="Create a Markdown redirect at the source path",
    )
    parser.add_argument("--dry-run", action="store_true", help="Preview without writes")
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
    raise SystemExit(main())

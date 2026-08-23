#!/usr/bin/env python3
"""Delete one unreferenced repository file with backup and rollback."""

from __future__ import annotations

import argparse
import contextlib
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib.safe_file_ops import (
    SafeFileError,
    capture_snapshots,
    classify_references,
    create_content_hashed_backup,
    require_no_link_regression,
    resolve_regular_source,
    restore_snapshots,
    run_link_checker,
)
from _lib.utils import REPO_ROOT


def check_git_history(file_path: Path, project_root: Path) -> dict[str, object]:
    """Return bounded Git history metadata for operator review."""
    relative = file_path.relative_to(project_root).as_posix()
    commits = subprocess.run(
        ["git", "log", "--oneline", "-5", "--", relative],
        cwd=project_root,
        capture_output=True,
        text=True,
        check=False,
    )
    modified = subprocess.run(
        ["git", "log", "-1", "--format=%ci", "--", relative],
        cwd=project_root,
        capture_output=True,
        text=True,
        check=False,
    )
    commit_lines = [line for line in commits.stdout.splitlines() if line]
    return {
        "recent_commits": len(commit_lines),
        "last_modified": modified.stdout.strip() or "Unknown",
        "commits": commit_lines[:3],
    }


def run_delete(args: argparse.Namespace) -> tuple[int, dict[str, object]]:
    result: dict[str, object] = {
        "tool": "safe_file_delete",
        "dry_run": bool(args.dry_run),
        "mode": "dry-run" if args.dry_run else "live",
        "success": False,
        "source": args.file,
        "deleted": False,
        "rolled_back": False,
    }
    try:
        file_path = resolve_regular_source(args.file, REPO_ROOT)
    except SafeFileError as exc:
        result["error"] = str(exc)
        print(f"❌ {exc}")
        return 1, result

    relative = file_path.relative_to(REPO_ROOT).as_posix()
    result["source"] = relative
    result["size_bytes"] = file_path.stat().st_size
    result["history"] = check_git_history(file_path, REPO_ROOT)

    print("=" * 60)
    print("🗑️  Transactional File Delete")
    print("=" * 60)
    print(f"File: {relative}")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")

    baseline = run_link_checker(REPO_ROOT)
    if not baseline.operational:
        result["error"] = f"Link baseline unavailable: {baseline.error}"
        print(f"❌ {result['error']}")
        return 1, result
    result["baseline_broken_links"] = len(baseline.broken)

    references = classify_references(file_path, None, REPO_ROOT)
    preserved = [ref for ref in references if ref.classification == "preserved"]
    blocking = [ref for ref in references if ref.classification != "preserved"]
    result["references_count"] = len(references)
    result["reference_summary"] = {
        "preserved": len(preserved),
        "unresolved": len(blocking),
    }
    result["references"] = [ref.as_dict(REPO_ROOT) for ref in references]

    print("\n📍 References")
    print(f"  preserved historical evidence: {len(preserved)}")
    print(f"  unresolved maintained references: {len(blocking)}")
    if blocking:
        result["error"] = "Maintained references block deletion"
        for ref in blocking[:10]:
            print(f"  ❌ {ref.file.relative_to(REPO_ROOT)}:{ref.line_number}")
        return 1, result

    result["changed_files"] = [relative]
    if args.dry_run:
        result["success"] = True
        print("\n✨ Dry run complete. No changes made.")
        return 0, result

    snapshots = capture_snapshots([file_path], REPO_ROOT)
    try:
        backup_path, manifest_path = create_content_hashed_backup(file_path, REPO_ROOT)
        result["backup"] = backup_path.relative_to(REPO_ROOT).as_posix()
        result["backup_manifest"] = manifest_path.relative_to(REPO_ROOT).as_posix()
        file_path.unlink()
        result["deleted"] = True
        after = run_link_checker(REPO_ROOT)
        require_no_link_regression(baseline, after)
        result["broken_links_after"] = len(after.broken)
    except Exception as exc:
        try:
            restore_snapshots(snapshots, REPO_ROOT)
            result["rolled_back"] = True
            result["deleted"] = False
        except Exception as rollback_exc:
            result["rollback_error"] = str(rollback_exc)
        result["error"] = str(exc)
        print(f"❌ Delete failed: {exc}")
        print(
            "↩️  Original bytes restored."
            if result["rolled_back"]
            else "❌ Rollback failed."
        )
        return 1, result

    result["success"] = True
    print("\n✨ Delete complete, backed up, and validated.")
    return 0, result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Delete one unreferenced regular repository file transactionally"
    )
    parser.add_argument("file", help="Existing regular file inside the repository")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writes")
    parser.add_argument("--json", action="store_true", help="Output structured JSON")
    args = parser.parse_args()

    if args.json:
        with contextlib.redirect_stdout(sys.stderr):
            exit_code, payload = run_delete(args)
        print(json.dumps(payload, indent=2))
        return exit_code
    exit_code, _payload = run_delete(args)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())

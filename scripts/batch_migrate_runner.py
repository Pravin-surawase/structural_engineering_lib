#!/usr/bin/env python3
"""Preflight and execute a complete migration batch with exact full rollback."""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import os
import shlex
import stat
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib.safe_file_ops import (
    FileSnapshot,
    SafeFileError,
    capture_snapshots,
    iter_repository_files,
    restore_snapshots,
    sha256_file,
)
from _lib.utils import REPO_ROOT

TOOL_SCRIPTS = {
    "python_module": REPO_ROOT / "scripts" / "migrate_python_module.py",
    "safe_move": REPO_ROOT / "scripts" / "safe_file_move.py",
    "react_component": REPO_ROOT / "scripts" / "migrate_react_component.py",
}
DISALLOWED_OPERATION_ARGS = {"--force", "--no-backup", "--dry-run", "--json"}


def _load_plan(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    operations = data.get("operations")
    if not isinstance(operations, list) or not operations:
        raise ValueError("Plan must contain a non-empty 'operations' list")
    if not all(isinstance(operation, dict) for operation in operations):
        raise ValueError("Every operation must be an object")
    return operations


def _normalize_tool(value: str) -> str:
    aliases = {
        "python": "python_module",
        "migrate_python_module": "python_module",
        "safe_file_move": "safe_move",
        "safe_move": "safe_move",
        "react": "react_component",
        "migrate_react_component": "react_component",
    }
    return aliases.get(value.strip(), value.strip())


def _normalize_args(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return shlex.split(value)
    if isinstance(value, list):
        return [str(item) for item in value]
    raise ValueError(f"Unsupported args type: {type(value).__name__}")


def _command(
    tool: str, source: str, destination: str, extra_args: list[str], *, dry_run: bool
) -> list[str]:
    command = [
        sys.executable,
        str(TOOL_SCRIPTS[tool]),
        source,
        destination,
        *extra_args,
        "--json",
    ]
    if dry_run:
        command.append("--dry-run")
    return command


def _run_json(
    command: list[str], *, exclude_roots: list[Path] | None = None
) -> tuple[int, dict[str, Any], str]:
    environment = os.environ.copy()
    if exclude_roots:
        environment["SAFE_FILE_EXCLUDE_ROOTS"] = os.pathsep.join(
            str(path.resolve()) for path in exclude_roots
        )
    process = subprocess.run(
        command,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
        env=environment,
    )
    try:
        payload = json.loads(process.stdout)
    except json.JSONDecodeError as exc:
        return (
            1,
            {"success": False, "error": f"Invalid JSON output: {exc}"},
            process.stderr,
        )
    return process.returncode, payload, process.stderr


def _normalize_operation(operation: dict[str, Any], index: int) -> dict[str, Any]:
    tool = _normalize_tool(str(operation.get("tool", "")))
    source = str(operation.get("source", "")).strip()
    destination = str(operation.get("destination", "")).strip()
    extra_args = _normalize_args(operation.get("args"))
    if tool not in TOOL_SCRIPTS:
        raise ValueError(f"Operation {index}: unsupported tool {tool!r}")
    if not source or not destination:
        raise ValueError(f"Operation {index}: source and destination are required")
    forbidden = sorted(set(extra_args) & DISALLOWED_OPERATION_ARGS)
    if forbidden:
        raise ValueError(
            f"Operation {index}: forbidden safety-bypass args: {', '.join(forbidden)}"
        )
    return {
        "index": index,
        "tool": tool,
        "source": source,
        "destination": destination,
        "args": extra_args,
    }


def _preflight(
    operations: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], set[str]]:
    planned: list[dict[str, Any]] = []
    all_changed: set[str] = set()
    sources: set[str] = set()
    destinations: set[str] = set()
    for index, raw in enumerate(operations, 1):
        operation = _normalize_operation(raw, index)
        exit_code, payload, stderr = _run_json(
            _command(
                operation["tool"],
                operation["source"],
                operation["destination"],
                operation["args"],
                dry_run=True,
            )
        )
        operation["plan_exit_code"] = exit_code
        operation["plan_payload"] = payload
        operation["plan_stderr"] = stderr
        operation["status"] = "dry-run"
        if exit_code != 0 or not payload.get("success"):
            raise SafeFileError(
                f"Operation {index} dry-run failed: {payload.get('error', stderr)}"
            )
        source = str(payload["source"])
        destination = str(payload["destination"])
        if source in sources:
            raise SafeFileError(f"Duplicate batch source: {source}")
        if destination in destinations:
            raise SafeFileError(f"Destination collision: {destination}")
        sources.add(source)
        destinations.add(destination)
        changed = payload.get("changed_files")
        if not isinstance(changed, list) or not all(
            isinstance(path, str) for path in changed
        ):
            raise SafeFileError(f"Operation {index} omitted changed_files preview")
        operation["predicted_changed_files"] = sorted(changed)
        all_changed.update(changed)
        planned.append(operation)
    chained = sorted(sources & destinations)
    if chained:
        raise SafeFileError(
            "Chained or cyclic paths require separate reviewed batches: "
            + ", ".join(chained)
        )
    return planned, all_changed


def _write_manifest(
    run_root: Path, snapshots: list[FileSnapshot], predicted: set[str]
) -> Path:
    files_root = run_root / "files"
    entries: list[dict[str, Any]] = []
    for snapshot in snapshots:
        relative = snapshot.path.relative_to(REPO_ROOT).as_posix()
        backup = files_root / relative
        entry: dict[str, Any] = {
            "path": relative,
            "existed": snapshot.existed,
            "mode": snapshot.mode,
            "size_bytes": len(snapshot.data or b""),
            "sha256": (
                hashlib.sha256(snapshot.data or b"").hexdigest()
                if snapshot.existed
                else None
            ),
            "backup": None,
        }
        if snapshot.existed:
            backup.parent.mkdir(parents=True, exist_ok=True)
            backup.write_bytes(snapshot.data or b"")
            entry["backup"] = backup.relative_to(run_root).as_posix()
        entries.append(entry)
    manifest = {
        "schema_version": 1,
        "repository": str(REPO_ROOT),
        "created_at_utc": datetime.now(UTC).isoformat(),
        "predicted_changed_files": sorted(predicted),
        "files": entries,
    }
    path = run_root / "rollback-manifest.json"
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return path


def _write_rollback_script(run_root: Path, manifest: Path) -> Path:
    script = run_root / "rollback.sh"
    command = " ".join(
        shlex.quote(part)
        for part in (
            sys.executable,
            str(REPO_ROOT / "scripts" / "batch_migrate_runner.py"),
            "--restore",
            str(manifest),
        )
    )
    script.write_text(
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        f"cd {shlex.quote(str(REPO_ROOT))}\n"
        f"{command}\n",
        encoding="utf-8",
    )
    script.chmod(stat.S_IMODE(script.stat().st_mode) | stat.S_IXUSR)
    return script


def _restore_manifest(path: Path) -> dict[str, Any]:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if manifest.get("repository") != str(REPO_ROOT):
        raise SafeFileError("Rollback manifest belongs to a different repository")
    entries = manifest.get("files")
    if not isinstance(entries, list):
        raise SafeFileError("Rollback manifest omitted files")
    snapshots: list[FileSnapshot] = []
    for entry in entries:
        if not isinstance(entry, dict):
            raise SafeFileError("Invalid rollback file entry")
        target = REPO_ROOT / str(entry["path"])
        existed = bool(entry["existed"])
        data: bytes | None = None
        if existed:
            backup = path.parent / str(entry["backup"])
            if not backup.is_file():
                raise SafeFileError(f"Rollback backup missing: {backup}")
            data = backup.read_bytes()
            if hashlib.sha256(data).hexdigest() != entry["sha256"]:
                raise SafeFileError(f"Rollback backup hash mismatch: {backup}")
        snapshots.append(
            FileSnapshot(
                target,
                existed,
                data,
                int(entry["mode"]) if entry.get("mode") is not None else None,
            )
        )
    restore_snapshots(snapshots, REPO_ROOT)
    for snapshot in snapshots:
        if snapshot.existed:
            if (
                not snapshot.path.is_file()
                or sha256_file(snapshot.path)
                != hashlib.sha256(snapshot.data or b"").hexdigest()
            ):
                raise SafeFileError(f"Rollback verification failed: {snapshot.path}")
        elif snapshot.path.exists() or snapshot.path.is_symlink():
            raise SafeFileError(f"Rollback failed to remove: {snapshot.path}")
    return {
        "tool": "batch_migrate_runner",
        "mode": "restore",
        "success": True,
        "manifest": str(path),
        "files_restored": len(snapshots),
    }


def _workspace_hashes(
    extra_paths: set[str], *, exclude_root: Path | None = None
) -> dict[str, str | None]:
    paths = {
        path.relative_to(REPO_ROOT).as_posix()
        for path in iter_repository_files(REPO_ROOT)
    } | set(extra_paths)
    hashes: dict[str, str | None] = {}
    for relative in paths:
        path = REPO_ROOT / relative
        if exclude_root is not None:
            try:
                path.relative_to(exclude_root)
                continue
            except ValueError:
                pass
        hashes[relative] = sha256_file(path) if path.is_file() else None
    return hashes


def _changed_paths(
    before: dict[str, str | None], after: dict[str, str | None]
) -> set[str]:
    return {
        path
        for path in before.keys() | after.keys()
        if before.get(path) != after.get(path)
    }


def _git_paths(*args: str) -> set[str]:
    process = subprocess.run(
        ["git", *args, "-z"],
        cwd=REPO_ROOT,
        capture_output=True,
        check=False,
    )
    if process.returncode != 0:
        raise SafeFileError(f"Git workspace query failed: git {' '.join(args)}")
    return {
        part.decode("utf-8", errors="surrogateescape")
        for part in process.stdout.split(b"\0")
        if part
    }


def _capture_workspace_guard() -> tuple[set[str], list[FileSnapshot]]:
    tracked = _git_paths("ls-files")
    dirty = (
        _git_paths("diff", "--name-only")
        | _git_paths("diff", "--cached", "--name-only")
        | _git_paths("ls-files", "--others", "--exclude-standard")
    )
    snapshots = capture_snapshots(
        [REPO_ROOT / relative for relative in dirty], REPO_ROOT
    )
    return tracked, snapshots


def _restore_unexpected(
    paths: set[str],
    *,
    before: dict[str, str | None],
    tracked: set[str],
    guard_snapshots: list[FileSnapshot],
) -> None:
    guarded = {
        snapshot.path.relative_to(REPO_ROOT).as_posix(): snapshot
        for snapshot in guard_snapshots
    }
    guarded_to_restore = [
        guarded[relative] for relative in paths if relative in guarded
    ]
    if guarded_to_restore:
        restore_snapshots(guarded_to_restore, REPO_ROOT)
    for relative in sorted(paths - set(guarded)):
        path = REPO_ROOT / relative
        if relative in tracked:
            process = subprocess.run(
                ["git", "show", f":{relative}"],
                cwd=REPO_ROOT,
                capture_output=True,
                check=False,
            )
            if process.returncode != 0:
                raise SafeFileError(
                    f"Cannot restore unexpected tracked path: {relative}"
                )
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(process.stdout)
            mode = subprocess.run(
                ["git", "ls-files", "-s", "--", relative],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=False,
            ).stdout.split(maxsplit=1)[0]
            if mode:
                path.chmod(int(mode, 8) & 0o777)
        elif before.get(relative) is None:
            if path.is_file() or path.is_symlink():
                path.unlink()
            elif path.exists():
                raise SafeFileError(
                    f"Rollback refuses unexpected directory: {relative}"
                )
        else:
            raise SafeFileError(f"No rollback source for unexpected path: {relative}")


def run_batch(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    summary: dict[str, Any] = {
        "tool": "batch_migrate_runner",
        "dry_run": bool(args.dry_run),
        "success": False,
        "operations": [],
    }
    try:
        operations = _load_plan(Path(args.plan))
        planned, predicted = _preflight(operations)
    except (OSError, ValueError, json.JSONDecodeError, SafeFileError) as exc:
        summary["error"] = str(exc)
        summary["operations_total"] = 0
        summary["operations_completed"] = 0
        summary["operations_failed"] = 1
        print(f"❌ Batch preflight failed: {exc}")
        return 1, summary

    summary["operations"] = planned
    summary["operations_total"] = len(planned)
    summary["predicted_changed_files"] = sorted(predicted)
    if args.dry_run:
        summary["operations_completed"] = len(planned)
        summary["operations_failed"] = 0
        summary["success"] = True
        summary["rollback_root"] = None
        print(f"✅ Full batch preflight passed for {len(planned)} operations.")
        return 0, summary

    run_id = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
    run_root = Path(args.rollback_dir)
    if not run_root.is_absolute():
        run_root = REPO_ROOT / run_root
    run_root = run_root / run_id
    run_root.mkdir(parents=True, exist_ok=False)
    snapshots = capture_snapshots(
        [REPO_ROOT / relative for relative in predicted], REPO_ROOT
    )
    manifest = _write_manifest(run_root, snapshots, predicted)
    rollback_script = _write_rollback_script(run_root, manifest)
    summary["run_id"] = run_id
    summary["rollback_root"] = str(run_root)
    summary["rollback_manifest"] = str(manifest)
    summary["rollback_script"] = str(rollback_script)
    tracked, guard_snapshots = _capture_workspace_guard()
    before = _workspace_hashes(predicted, exclude_root=run_root)

    failure: str | None = None
    completed = 0
    for operation in planned:
        exit_code, payload, stderr = _run_json(
            _command(
                operation["tool"],
                operation["source"],
                operation["destination"],
                operation["args"],
                dry_run=False,
            ),
            exclude_roots=[run_root],
        )
        operation["live_exit_code"] = exit_code
        operation["live_payload"] = payload
        operation["live_stderr"] = stderr
        if exit_code != 0 or not payload.get("success"):
            operation["status"] = "failed"
            failure = (
                f"Operation {operation['index']} failed: "
                f"{payload.get('error', stderr)}"
            )
            break
        actual_preview = payload.get("changed_files")
        if sorted(actual_preview or []) != operation["predicted_changed_files"]:
            operation["status"] = "failed"
            failure = f"Operation {operation['index']} changed-file report drifted"
            break
        operation["status"] = "ok"
        completed += 1

    after = _workspace_hashes(predicted, exclude_root=run_root)
    actual = _changed_paths(before, after)
    summary["actual_changed_files"] = sorted(actual)
    if failure is None and actual != predicted:
        missing = sorted(predicted - actual)
        unexpected = sorted(actual - predicted)
        failure = (
            f"Batch changed-path mismatch; missing={missing}, unexpected={unexpected}"
        )

    if failure is not None:
        summary["error"] = failure
        try:
            _restore_unexpected(
                actual - predicted,
                before=before,
                tracked=tracked,
                guard_snapshots=guard_snapshots,
            )
            rollback = _restore_manifest(manifest)
            summary["rollback"] = rollback
            summary["rolled_back"] = True
        except Exception as exc:
            summary["rolled_back"] = False
            summary["rollback_error"] = str(exc)
        summary["operations_completed"] = completed
        summary["operations_failed"] = 1
        summary_path = run_root / "run-summary.json"
        summary["summary_file"] = str(summary_path)
        summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        print(f"❌ {failure}")
        return 1, summary

    summary["operations_completed"] = completed
    summary["operations_failed"] = 0
    summary["success"] = True
    summary["rolled_back"] = False
    summary_path = run_root / "run-summary.json"
    summary["summary_file"] = str(summary_path)
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(f"✅ Batch completed with exact preview agreement: {len(actual)} paths.")
    return 0, summary


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Preflight and execute a transactional migration batch"
    )
    parser.add_argument("plan", nargs="?", help="Migration plan JSON")
    parser.add_argument(
        "--rollback-dir",
        default="logs/migration-rollbacks",
        help="Directory for exact rollback evidence",
    )
    parser.add_argument("--dry-run", action="store_true", help="Preflight only")
    parser.add_argument("--restore", help="Restore an exact rollback manifest")
    parser.add_argument("--json", action="store_true", help="Output structured JSON")
    args = parser.parse_args()

    if args.restore:
        if args.plan or args.dry_run:
            parser.error("--restore cannot be combined with a plan or --dry-run")
        try:
            payload = _restore_manifest(Path(args.restore))
            exit_code = 0
        except Exception as exc:
            payload = {
                "tool": "batch_migrate_runner",
                "mode": "restore",
                "success": False,
                "error": str(exc),
            }
            exit_code = 1
    else:
        if not args.plan:
            parser.error("plan is required unless --restore is used")
        if args.json:
            with contextlib.redirect_stdout(sys.stderr):
                exit_code, payload = run_batch(args)
        else:
            exit_code, payload = run_batch(args)

    if args.json:
        print(json.dumps(payload, indent=2))
    elif args.restore:
        print(
            "✅ Rollback restored exact original bytes."
            if exit_code == 0
            else f"❌ {payload['error']}"
        )
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())

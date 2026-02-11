#!/usr/bin/env python3
"""Batch migration runner with per-operation rollback logs.

Reads a migration plan and executes operations via the canonical scripts:
- migrate_python_module.py
- safe_file_move.py
- migrate_react_component.py

Each operation can be dry-run planned, backed up, executed, and logged with a
generated rollback script.

Plan format (JSON):
{
  "operations": [
    {
      "tool": "python_module",
      "source": "structural_lib/api.py",
      "destination": "structural_lib/services/api.py",
      "args": ["--no-stub"]
    },
    {
      "tool": "safe_move",
      "source": "docs/old.md",
      "destination": "docs/new.md",
      "args": ["--stub"]
    }
  ]
}
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import shlex
import shutil
import stat
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]

TOOL_SCRIPTS = {
    "python_module": REPO_ROOT / "scripts" / "migrate_python_module.py",
    "safe_move": REPO_ROOT / "scripts" / "safe_file_move.py",
    "react_component": REPO_ROOT / "scripts" / "migrate_react_component.py",
}


@dataclass
class CommandResult:
    exit_code: int
    payload: dict[str, Any]
    stdout: str
    stderr: str


def _load_plan(plan_path: Path) -> list[dict[str, Any]]:
    data = json.loads(plan_path.read_text(encoding="utf-8"))
    ops = data.get("operations")
    if not isinstance(ops, list):
        raise ValueError("Plan JSON must contain an 'operations' list")
    return ops


def _normalize_args(raw_args: Any) -> list[str]:
    if raw_args is None:
        return []
    if isinstance(raw_args, list):
        return [str(a) for a in raw_args]
    if isinstance(raw_args, str):
        return shlex.split(raw_args)
    raise ValueError(f"Unsupported args type: {type(raw_args).__name__}")


def _normalize_tool(tool: str) -> str:
    aliases = {
        "python": "python_module",
        "migrate_python_module": "python_module",
        "safe_file_move": "safe_move",
        "safe_move": "safe_move",
        "react": "react_component",
        "migrate_react_component": "react_component",
    }
    key = tool.strip()
    return aliases.get(key, key)


def _build_command(
    *,
    tool: str,
    source: str,
    destination: str,
    extra_args: list[str],
    force_dry_run: bool,
) -> list[str]:
    script = TOOL_SCRIPTS[tool]
    cmd = [sys.executable, str(script), source, destination]
    cmd.extend(extra_args)
    if "--json" not in cmd:
        cmd.append("--json")
    if force_dry_run and "--dry-run" not in cmd:
        cmd.append("--dry-run")
    return cmd


def _run_json_command(cmd: list[str]) -> CommandResult:
    proc = subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    stdout = proc.stdout.strip()
    payload: dict[str, Any] = {}
    if stdout:
        try:
            payload = json.loads(stdout)
        except json.JSONDecodeError as exc:
            payload = {
                "success": False,
                "error": f"Invalid JSON output: {exc}",
                "raw_stdout": stdout,
            }
            return CommandResult(1, payload, proc.stdout, proc.stderr)
    return CommandResult(proc.returncode, payload, proc.stdout, proc.stderr)


def _safe_slug(value: str) -> str:
    out = []
    for ch in value:
        if ch.isalnum() or ch in {"-", "_", "."}:
            out.append(ch)
        else:
            out.append("-")
    slug = "".join(out).strip("-")
    return slug[:80] or "op"


def _normalize_relpath(path_str: str) -> str:
    p = Path(path_str)
    if p.is_absolute():
        try:
            p = p.resolve().relative_to(REPO_ROOT)
        except ValueError:
            return p.as_posix()
    return p.as_posix()


def _backup_files(
    files: list[str],
    op_dir: Path,
) -> list[dict[str, Any]]:
    backups: list[dict[str, Any]] = []
    files_dir = op_dir / "files"
    files_dir.mkdir(parents=True, exist_ok=True)

    for rel in sorted(set(files)):
        rel_norm = _normalize_relpath(rel)
        src = REPO_ROOT / rel_norm
        dst = files_dir / rel_norm
        entry: dict[str, Any] = {
            "path": rel_norm,
            "existed": src.exists(),
            "backup": str(dst.relative_to(op_dir)),
        }
        if src.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            entry["size_bytes"] = src.stat().st_size
            with src.open("rb") as fh:
                entry["sha256"] = hashlib.sha256(fh.read()).hexdigest()
        else:
            entry["size_bytes"] = 0
            entry["sha256"] = None
        backups.append(entry)

    return backups


def _write_file_rollback_manifest(op_dir: Path, backups: list[dict[str, Any]]) -> Path:
    """Write per-file rollback metadata for automation/audit tooling."""
    manifest_path = op_dir / "rollback-files.json"
    manifest_path.write_text(
        json.dumps({"files": backups}, indent=2),
        encoding="utf-8",
    )
    return manifest_path


def _write_rollback_script(op_dir: Path, backups: list[dict[str, Any]]) -> Path:
    script_path = op_dir / "rollback.sh"
    lines = [
        "#!/usr/bin/env bash",
        "set -euo pipefail",
        f"cd {shlex.quote(str(REPO_ROOT))}",
        "",
        "echo 'Restoring files for operation rollback...'",
    ]
    for entry in backups:
        rel = str(entry["path"])
        backup_rel = str(entry["backup"])
        backup_abs = op_dir / backup_rel
        if entry["existed"]:
            lines.extend(
                [
                    f"mkdir -p {shlex.quote(str(Path(rel).parent))}",
                    f"cp {shlex.quote(str(backup_abs))} {shlex.quote(rel)}",
                ]
            )
        else:
            lines.append(f"rm -f {shlex.quote(rel)}")
    lines.append("echo 'Rollback complete.'")
    script_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    current_mode = script_path.stat().st_mode
    script_path.chmod(current_mode | stat.S_IXUSR)
    return script_path


def run_batch(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    operations = _load_plan(Path(args.plan))
    run_id = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    run_root = Path(args.rollback_dir) / run_id
    run_root.mkdir(parents=True, exist_ok=True)

    summary: dict[str, Any] = {
        "tool": "batch_migrate_runner",
        "run_id": run_id,
        "dry_run": bool(args.dry_run),
        "rollback_root": str(run_root),
        "operations_total": len(operations),
        "operations": [],
        "success": True,
    }

    print(f"Batch migration run: {run_id}")
    print(f"Plan: {args.plan}")
    print(f"Operations: {len(operations)}")
    print(f"Rollback logs: {run_root}")

    for idx, op in enumerate(operations, start=1):
        tool_raw = str(op.get("tool", "python_module"))
        tool = _normalize_tool(tool_raw)
        source = str(op.get("source", "")).strip()
        destination = str(op.get("destination", "")).strip()
        extra_args = _normalize_args(op.get("args"))
        op_name = _safe_slug(f"{idx:03d}-{tool}-{Path(source).name}")
        op_dir = run_root / op_name
        op_dir.mkdir(parents=True, exist_ok=True)

        op_log: dict[str, Any] = {
            "index": idx,
            "tool": tool,
            "tool_input": tool_raw,
            "source": source,
            "destination": destination,
            "args": extra_args,
            "status": "pending",
            "op_dir": str(op_dir),
        }
        print()
        print(f"[{idx}/{len(operations)}] {tool}: {source} -> {destination}")

        if tool not in TOOL_SCRIPTS:
            op_log["status"] = "failed"
            op_log["error"] = f"Unsupported tool: {tool_raw}"
            summary["operations"].append(op_log)
            summary["success"] = False
            if not args.continue_on_error:
                break
            continue
        if not source or not destination:
            op_log["status"] = "failed"
            op_log["error"] = "Operation requires 'source' and 'destination'"
            summary["operations"].append(op_log)
            summary["success"] = False
            if not args.continue_on_error:
                break
            continue

        plan_cmd = _build_command(
            tool=tool,
            source=source,
            destination=destination,
            extra_args=extra_args,
            force_dry_run=True,
        )
        op_log["plan_cmd"] = plan_cmd
        plan_res = _run_json_command(plan_cmd)
        op_log["plan_exit_code"] = plan_res.exit_code
        op_log["plan_payload"] = plan_res.payload
        op_log["plan_stderr"] = plan_res.stderr

        if plan_res.exit_code != 0:
            op_log["status"] = "failed"
            op_log["error"] = "Planning dry-run failed"
            summary["operations"].append(op_log)
            summary["success"] = False
            (op_dir / "operation-log.json").write_text(
                json.dumps(op_log, indent=2), encoding="utf-8"
            )
            if not args.continue_on_error:
                break
            continue

        predicted_files = list(plan_res.payload.get("changed_files", []))
        op_log["predicted_changed_files"] = predicted_files

        backups: list[dict[str, Any]] = []
        rollback_script: Path | None = None
        rollback_manifest: Path | None = None
        if not args.dry_run:
            backups = _backup_files(predicted_files, op_dir)
            rollback_manifest = _write_file_rollback_manifest(op_dir, backups)
            rollback_script = _write_rollback_script(op_dir, backups)
        op_log["backups"] = backups
        op_log["rollback_script"] = str(rollback_script) if rollback_script else None
        op_log["rollback_manifest"] = (
            str(rollback_manifest) if rollback_manifest else None
        )

        if args.dry_run:
            op_log["status"] = "dry-run"
            summary["operations"].append(op_log)
            (op_dir / "operation-log.json").write_text(
                json.dumps(op_log, indent=2), encoding="utf-8"
            )
            continue

        live_cmd = _build_command(
            tool=tool,
            source=source,
            destination=destination,
            extra_args=[a for a in extra_args if a != "--dry-run"],
            force_dry_run=False,
        )
        op_log["live_cmd"] = live_cmd
        live_res = _run_json_command(live_cmd)
        op_log["live_exit_code"] = live_res.exit_code
        op_log["live_payload"] = live_res.payload
        op_log["live_stderr"] = live_res.stderr

        if live_res.exit_code != 0:
            op_log["status"] = "failed"
            op_log["error"] = "Live execution failed"
            summary["success"] = False
            if args.auto_rollback and rollback_script:
                rb = subprocess.run(
                    [str(rollback_script)],
                    cwd=REPO_ROOT,
                    capture_output=True,
                    text=True,
                )
                op_log["rollback_attempted"] = True
                op_log["rollback_exit_code"] = rb.returncode
                op_log["rollback_stdout"] = rb.stdout
                op_log["rollback_stderr"] = rb.stderr
            else:
                op_log["rollback_attempted"] = False
        else:
            op_log["status"] = "ok"

        summary["operations"].append(op_log)
        (op_dir / "operation-log.json").write_text(
            json.dumps(op_log, indent=2), encoding="utf-8"
        )

        if op_log["status"] != "ok" and not args.continue_on_error:
            break

    summary["operations_completed"] = len(summary["operations"])
    summary["operations_failed"] = sum(
        1 for op in summary["operations"] if op.get("status") == "failed"
    )
    summary["summary_file"] = str((run_root / "run-summary.json"))
    (run_root / "run-summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return (0 if summary["success"] else 1), summary


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Batch migration runner with rollback logging"
    )
    parser.add_argument("plan", help="Path to migration plan JSON file")
    parser.add_argument(
        "--rollback-dir",
        default="logs/migration-rollbacks",
        help="Directory to store rollback logs and backups",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Plan only; do not execute live operations",
    )
    parser.add_argument(
        "--continue-on-error",
        action="store_true",
        help="Continue remaining operations after a failure",
    )
    parser.add_argument(
        "--auto-rollback",
        action="store_true",
        help="Attempt automatic rollback when an operation fails",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output run summary as JSON",
    )
    args = parser.parse_args()

    if args.json:
        with contextlib.redirect_stdout(sys.stderr):
            exit_code, payload = run_batch(args)
        print(json.dumps(payload, indent=2))
        return exit_code

    exit_code, payload = run_batch(args)
    print()
    print("Batch migration summary:")
    print(f"  Success: {payload['success']}")
    print(f"  Completed: {payload['operations_completed']}/{payload['operations_total']}")
    print(f"  Failed: {payload['operations_failed']}")
    print(f"  Summary: {payload['summary_file']}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())

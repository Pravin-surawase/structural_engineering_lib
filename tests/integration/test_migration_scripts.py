from __future__ import annotations

import importlib
import json
import shutil
import stat
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURES = REPO_ROOT / "tests" / "fixtures" / "migration"
GOLDEN = FIXTURES / "golden"
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
safe_file_move = importlib.import_module("safe_file_move")


def test_public_safe_file_entrypoints_keep_executable_compatibility() -> None:
    for name in ("safe_file_move.py", "safe_file_delete.py"):
        mode = (SCRIPTS_DIR / name).stat().st_mode
        assert mode & stat.S_IXUSR, f"scripts/{name} lost its executable file mode"


def _load_golden(name: str) -> dict[str, object]:
    return json.loads((GOLDEN / name).read_text(encoding="utf-8"))


def _run_script_json(script_name: str, args: list[str]) -> dict[str, object]:
    cmd = [sys.executable, str(REPO_ROOT / "scripts" / script_name), *args, "--json"]
    result = subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def test_migrate_python_module_dry_run_matches_golden() -> None:
    payload = _run_script_json(
        "migrate_python_module.py",
        [
            "structural_lib/_migration_fixtures/sample_module.py",
            "structural_lib/_migration_fixtures/moved/sample_module.py",
            "--dry-run",
            "--no-stub",
        ],
    )
    subset = {
        "tool": payload["tool"],
        "dry_run": payload["dry_run"],
        "success": payload["success"],
        "source": payload["source"],
        "destination": payload["destination"],
        "old_module": payload["old_module"],
        "new_module": payload["new_module"],
        "references_count": payload["references_count"],
        "updated_count": payload["updated_count"],
        "stub_created": payload["stub_created"],
        "changed_files": payload["changed_files"],
    }
    assert subset == _load_golden("migrate_python_module_dry_run.json")


def test_migrate_python_module_accepts_python_prefixed_paths() -> None:
    payload = _run_script_json(
        "migrate_python_module.py",
        [
            "Python/structural_lib/_migration_fixtures/sample_module.py",
            "Python/structural_lib/_migration_fixtures/moved/sample_module.py",
            "--dry-run",
            "--no-stub",
        ],
    )
    destination = str(payload["destination"])
    assert (
        destination
        == "Python/structural_lib/_migration_fixtures/moved/sample_module.py"
    )
    assert "Python/Python/" not in destination


def test_migrate_react_component_dry_run_matches_golden() -> None:
    payload = _run_script_json(
        "migrate_react_component.py",
        [
            "src/__fixtures__/migration/SampleWidget.tsx",
            "src/__fixtures__/migration/moved/SampleWidget.tsx",
            "--dry-run",
        ],
    )
    subset = {
        "tool": payload["tool"],
        "dry_run": payload["dry_run"],
        "success": payload["success"],
        "source": payload["source"],
        "destination": payload["destination"],
        "references_count": payload["references_count"],
        "updated_count": payload["updated_count"],
        "barrel_status": payload["barrel_status"],
        "changed_files": payload["changed_files"],
    }
    assert subset == _load_golden("migrate_react_component_dry_run.json")


def test_migrate_react_component_accepts_react_app_prefixed_paths() -> None:
    payload = _run_script_json(
        "migrate_react_component.py",
        [
            "react_app/src/__fixtures__/migration/SampleWidget.tsx",
            "react_app/src/__fixtures__/migration/moved/SampleWidget.tsx",
            "--dry-run",
        ],
    )
    source = str(payload["source"])
    destination = str(payload["destination"])
    assert source == "react_app/src/__fixtures__/migration/SampleWidget.tsx"
    assert destination == "react_app/src/__fixtures__/migration/moved/SampleWidget.tsx"
    assert "react_app/react_app/" not in source
    assert "react_app/react_app/" not in destination


def test_safe_file_move_dry_run_reports_complete_changed_paths() -> None:
    runtime = FIXTURES / "_runtime_safe_move"
    source = runtime / ("runtime-safe-" + "source.md")
    destination = runtime / "moved" / source.name
    reference = runtime / "reference.md"
    shutil.rmtree(runtime, ignore_errors=True)
    runtime.mkdir(parents=True)
    source.write_text("source\n", encoding="utf-8")
    reference.write_text(f"[source]({source.name})\n", encoding="utf-8")

    try:
        payload = _run_script_json(
            "safe_file_move.py",
            [
                str(source.relative_to(REPO_ROOT)),
                str(destination.relative_to(REPO_ROOT)),
                "--dry-run",
            ],
        )
        assert payload["success"] is True
        assert payload["moved"] is False
        assert payload["updated_count"] == 1
        assert payload["changed_files"] == sorted(
            [
                str(source.relative_to(REPO_ROOT)),
                str(destination.relative_to(REPO_ROOT)),
                str(reference.relative_to(REPO_ROOT)),
            ]
        )
        assert source.exists()
        assert not destination.exists()
    finally:
        shutil.rmtree(runtime, ignore_errors=True)


def test_safe_file_move_updates_live_refs_without_rewriting_evidence(
    tmp_path: Path,
) -> None:
    source = tmp_path / "scripts" / "old_tool.py"
    destination = tmp_path / "scripts" / "_archive" / "old_tool.py"
    source.parent.mkdir(parents=True)
    source.write_text("print('legacy')\n", encoding="utf-8")

    active = tmp_path / "docs" / "guides" / "current.md"
    active.parent.mkdir(parents=True)
    active.write_text("Run scripts/old_tool.py\n", encoding="utf-8")

    preserved_paths = [
        tmp_path / "docs" / "SESSION_LOG.md",
        tmp_path / "docs" / "audit" / "prior-audit.md",
        tmp_path / "docs" / "verification" / "receipt.json",
        tmp_path / "docs" / "_archive" / "history.md",
        tmp_path / "scripts" / "check_codex_git_workflow.py",
    ]
    for path in preserved_paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("Recorded scripts/old_tool.py\n", encoding="utf-8")

    updated, updated_files = safe_file_move.update_links(source, destination, tmp_path)

    assert updated == 1
    assert updated_files == ["docs/guides/current.md"]
    assert active.read_text(encoding="utf-8") == ("Run scripts/_archive/old_tool.py\n")
    for path in preserved_paths:
        assert path.read_text(encoding="utf-8") == ("Recorded scripts/old_tool.py\n")


def test_batch_runner_dry_run_matches_golden(tmp_path: Path) -> None:
    rollback_root = tmp_path / "dry-run-rollback-logs"
    cmd = [
        sys.executable,
        str(REPO_ROOT / "scripts" / "batch_migrate_runner.py"),
        str(FIXTURES / "plans" / "batch_plan_python_fixture.json"),
        "--dry-run",
        "--rollback-dir",
        str(rollback_root),
        "--json",
    ]
    result = subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    operation = payload["operations"][0]
    subset = {
        "tool": payload["tool"],
        "dry_run": payload["dry_run"],
        "success": payload["success"],
        "operations_total": payload["operations_total"],
        "operations_completed": payload["operations_completed"],
        "operations_failed": payload["operations_failed"],
        "operation": {
            "tool": operation["tool"],
            "status": operation["status"],
            "source": operation["source"],
            "destination": operation["destination"],
            "plan_exit_code": operation["plan_exit_code"],
            "plan_success": operation["plan_payload"]["success"],
            "predicted_changed_files": operation["predicted_changed_files"],
        },
    }
    assert subset == _load_golden("batch_runner_dry_run.json")
    assert not rollback_root.exists()


def test_batch_runner_executes_exact_full_rollback_and_rejects_corruption() -> None:
    runtime_dir = FIXTURES / "_runtime_batch"
    rollback_root = runtime_dir / "rollback-logs"
    source = runtime_dir / ("live_" + "source.md")
    destination = runtime_dir / "moved" / source.name

    if runtime_dir.exists():
        shutil.rmtree(runtime_dir)
    runtime_dir.mkdir(parents=True, exist_ok=True)
    source.write_text("runtime migration fixture\n", encoding="utf-8")

    source_rel = str(source.relative_to(REPO_ROOT))
    destination_rel = str(destination.relative_to(REPO_ROOT))
    plan = runtime_dir / "plan.json"
    plan.write_text(
        json.dumps(
            {
                "operations": [
                    {
                        "tool": "safe_move",
                        "source": source_rel,
                        "destination": destination_rel,
                    }
                ]
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    try:
        cmd = [
            sys.executable,
            str(REPO_ROOT / "scripts" / "batch_migrate_runner.py"),
            str(plan.relative_to(REPO_ROOT)),
            "--rollback-dir",
            str(rollback_root.relative_to(REPO_ROOT)),
            "--json",
        ]
        result = subprocess.run(
            cmd,
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result.stderr + result.stdout
        payload = json.loads(result.stdout)
        assert payload["operations"][0]["status"] == "ok"
        manifest_path = Path(payload["rollback_manifest"])
        if not manifest_path.is_absolute():
            manifest_path = REPO_ROOT / manifest_path
        assert manifest_path.exists()

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        files = manifest["files"]
        source_entry = next(item for item in files if item["path"] == source_rel)
        destination_entry = next(
            item for item in files if item["path"] == destination_rel
        )

        assert source_entry["existed"] is True
        assert source_entry["sha256"]
        assert source_entry["size_bytes"] > 0

        assert destination_entry["existed"] is False
        assert destination_entry["sha256"] is None
        assert destination_entry["size_bytes"] == 0

        rollback_script = Path(payload["rollback_script"])
        if not rollback_script.is_absolute():
            rollback_script = REPO_ROOT / rollback_script
        rollback_source = rollback_script.read_text(encoding="utf-8")
        assert sys.executable in rollback_source
        assert "batch_migrate_runner.py" in rollback_source
        assert "--restore" in rollback_source
        assert "--force" not in rollback_source
        assert "--no-backup" not in rollback_source

        rollback = subprocess.run(
            [str(rollback_script)],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        assert rollback.returncode == 0, rollback.stderr
        assert source.read_text(encoding="utf-8") == "runtime migration fixture\n"
        assert not destination.exists()

        backup = manifest_path.parent / str(source_entry["backup"])
        backup.write_bytes(b"corrupt")
        failed_rollback = subprocess.run(
            [str(rollback_script)],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        assert failed_rollback.returncode == 1
        assert source.read_text(encoding="utf-8") == "runtime migration fixture\n"
    finally:
        shutil.rmtree(runtime_dir, ignore_errors=True)


def test_batch_runner_rejects_safety_bypass_args_before_writes() -> None:
    runtime_dir = FIXTURES / "_runtime_batch_reject"
    rollback_root = runtime_dir / "rollback-logs"
    source = runtime_dir / "source.md"
    destination = runtime_dir / "destination.md"
    shutil.rmtree(runtime_dir, ignore_errors=True)
    runtime_dir.mkdir(parents=True)
    source.write_text("source\n", encoding="utf-8")
    plan = runtime_dir / "plan.json"
    plan.write_text(
        json.dumps(
            {
                "operations": [
                    {
                        "tool": "safe_move",
                        "source": str(source.relative_to(REPO_ROOT)),
                        "destination": str(destination.relative_to(REPO_ROOT)),
                        "args": ["--force"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    try:
        command = [
            sys.executable,
            str(REPO_ROOT / "scripts" / "batch_migrate_runner.py"),
            str(plan.relative_to(REPO_ROOT)),
            "--dry-run",
            "--rollback-dir",
            str(rollback_root.relative_to(REPO_ROOT)),
            "--json",
        ]
        result = subprocess.run(
            command,
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        payload = json.loads(result.stdout)
        assert result.returncode == 1
        assert "forbidden safety-bypass args" in payload["error"]
        assert source.exists()
        assert not destination.exists()
        assert not rollback_root.exists()
    finally:
        shutil.rmtree(runtime_dir, ignore_errors=True)

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURES = REPO_ROOT / "tests" / "fixtures" / "migration"
GOLDEN = FIXTURES / "golden"


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
    assert destination == "Python/structural_lib/_migration_fixtures/moved/sample_module.py"
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


def test_safe_file_move_dry_run_matches_golden() -> None:
    payload = _run_script_json(
        "safe_file_move.py",
        [
            "tests/fixtures/migration/docs/__4layer_fixture_source_qzv9.md",
            "tests/fixtures/migration/docs/moved/__4layer_fixture_source_qzv9.md",
            "--dry-run",
        ],
    )
    subset = {
        "tool": payload["tool"],
        "dry_run": payload["dry_run"],
        "success": payload["success"],
        "source": payload["source"],
        "destination": payload["destination"],
        "moved": payload["moved"],
        "updated_count": payload["updated_count"],
        "stub_created": payload["stub_created"],
        "changed_files": payload["changed_files"],
    }
    assert subset == _load_golden("safe_file_move_dry_run.json")


def test_batch_runner_dry_run_matches_golden() -> None:
    cmd = [
        sys.executable,
        str(REPO_ROOT / "scripts" / "batch_migrate_runner.py"),
        str(FIXTURES / "plans" / "batch_plan_python_fixture.json"),
        "--dry-run",
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


def test_batch_runner_live_writes_per_file_rollback_manifest() -> None:
    runtime_dir = FIXTURES / "_runtime_batch"
    rollback_root = runtime_dir / "rollback-logs"
    source = runtime_dir / "live_source.md"
    destination = runtime_dir / "moved" / "live_source.md"

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
        assert result.returncode == 0, result.stderr
        payload = json.loads(result.stdout)
        operation = payload["operations"][0]
        assert operation["status"] == "ok"

        manifest_path = Path(operation["rollback_manifest"])
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
    finally:
        shutil.rmtree(runtime_dir, ignore_errors=True)


"""Regression tests for agent-governance automation controls."""

from __future__ import annotations

import importlib
import json
import os
import subprocess
import sys
from datetime import date
from pathlib import Path

import pytest

pytestmark = pytest.mark.repo_only

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

agent_compliance = importlib.import_module("agent_compliance_checker")
agent_context = importlib.import_module("agent_context")
agent_data = importlib.import_module("_lib.agent_data")
agent_drift = importlib.import_module("agent_drift_detector")
agent_trends = importlib.import_module("agent_trends")
audit_permissions = importlib.import_module("audit_permissions")
check_all = importlib.import_module("check_all")
check_scripts_index = importlib.import_module("check_scripts_index")
cli_smoke = importlib.import_module("test_cli_smoke")
evolve = importlib.import_module("evolve")
external_cli = importlib.import_module("external_cli_test")
find_automation = importlib.import_module("find_automation")
project_health = importlib.import_module("project_health")
tool_permissions = importlib.import_module("tool_permissions")
tool_registry = importlib.import_module("tool_registry")


def test_python_runtime_launcher_uses_explicit_interpreter():
    launcher = SCRIPTS_DIR / "python_runtime.sh"
    env = os.environ.copy()
    env["STRUCTURAL_LIB_PYTHON"] = sys.executable

    result = subprocess.run(
        [str(launcher), "-c", "import sys; print(sys.executable)"],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=10,
    )

    assert result.returncode == 0, result.stderr
    assert Path(result.stdout.strip()).resolve() == Path(sys.executable).resolve()


def test_python_runtime_launcher_binds_invoking_repository_imports(tmp_path):
    launcher = SCRIPTS_DIR / "python_runtime.sh"
    caller_path = tmp_path / "caller-pythonpath"
    caller_path.mkdir()
    env = os.environ.copy()
    env["STRUCTURAL_LIB_PYTHON"] = sys.executable
    env["PYTHONPATH"] = str(caller_path)
    probe = """
import json
import os
from pathlib import Path
import structural_lib

print(json.dumps({
    "module": str(Path(structural_lib.__file__).resolve()),
    "pythonpath": os.environ["PYTHONPATH"].split(os.pathsep),
}))
"""

    result = subprocess.run(
        [str(launcher), "-c", probe],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=10,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["pythonpath"] == [
        str(REPO_ROOT / "Python"),
        str(REPO_ROOT),
        str(caller_path),
    ]
    assert Path(payload["module"]).is_relative_to(REPO_ROOT / "Python")


def test_control_paths_use_python_runtime_launcher():
    launcher = str(SCRIPTS_DIR / "python_runtime.sh")
    run_sh = (REPO_ROOT / "run.sh").read_text(encoding="utf-8")
    pre_commit = (REPO_ROOT / ".pre-commit-config.yaml").read_text(encoding="utf-8")
    entry_lines = [line for line in pre_commit.splitlines() if "entry:" in line]

    assert check_all.VENV_PYTHON == launcher
    assert cli_smoke.VENV == launcher
    assert str(project_health.PYTHON_RUNTIME) == launcher
    assert 'VENV="$SCRIPTS/python_runtime.sh"' in run_sh
    assert all(".venv/bin/python" not in line for line in entry_lines)

    for name in ("agent_start.sh", "preflight.py", "test_changed.py", "evolve.py"):
        source = (SCRIPTS_DIR / name).read_text(encoding="utf-8")
        assert "python_runtime.sh" in source

    agent_start_source = (SCRIPTS_DIR / "agent_start.sh").read_text(encoding="utf-8")
    assert ".venv/bin/python" not in agent_start_source
    assert "git config --global" not in agent_start_source
    assert "git fetch" not in agent_start_source
    assert "gh pr" not in agent_start_source
    assert "chmod +x" not in agent_start_source

    workflow = (REPO_ROOT / ".github" / "workflows" / "fast-checks.yml").read_text(
        encoding="utf-8"
    )
    install_offset = workflow.index("python -m pip install -e Python pytest PyYAML")
    smoke_offset = workflow.index("python scripts/test_cli_smoke.py")
    assert install_offset < smoke_offset


def test_watch_help_does_not_require_fswatch():
    result = subprocess.run(
        [str(SCRIPTS_DIR / "watch_tests.sh"), "--help"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=10,
    )

    assert result.returncode == 0
    assert "Python/tests/" in result.stdout


def test_current_session_ids_uses_injected_date_and_ignores_malformed_ids():
    sessions = [
        "2026-04-07T19:07",
        "not-a-session",
        "2026-08-09T09:00",
        "2026-08-09T18:00",
    ]

    assert agent_data.current_session_ids(sessions, today=date(2026, 8, 9)) == [
        "2026-08-09T09:00",
        "2026-08-09T18:00",
    ]


def test_agent_context_uses_all_registry_agents():
    registry = agent_context.load_agent_registry()

    assert len(registry) == 16
    assert {
        "structural-math",
        "security",
        "library-expert",
        "innovator",
        "agent-evolver",
    } <= set(registry)


def test_agent_context_commands_are_root_stable():
    source = (SCRIPTS_DIR / "agent_context.py").read_text(encoding="utf-8")

    assert "cd Python && .venv/bin/python" not in source
    assert ".venv/bin/python scripts/archive_old_files.sh" not in source
    assert "./run.sh frontend build" in source


def test_compliance_filter_without_attribution_fails_evidence():
    result = agent_compliance.check_compliance(
        {"session_id": "2026-08-09T10:00", "agents_active": ["backend"]},
        "orchestrator",
    )

    assert result["evidence_available"] is False
    assert result["compliance_results"] == {}
    assert "not attributed" in result["no_evidence_reason"]


def test_compliance_default_rejects_stale_latest_session(monkeypatch):
    monkeypatch.setattr(agent_compliance, "list_sessions", lambda: ["2026-04-07T19:07"])
    monkeypatch.setattr(sys, "argv", ["agent_compliance_checker.py"])

    assert agent_compliance.main() == 1


def _ops_session() -> dict:
    return {
        "session_id": "2026-04-07T19:07",
        "agents_active": ["ops"],
        "commits": [{"message": "ci: inspect checks"}],
        "files_changed": {},
    }


def test_drift_filter_without_attribution_fails_evidence():
    result = agent_drift.detect_drift(_ops_session(), agent_filter="frontend")

    assert result["evidence_available"] is False
    assert result["agents_analyzed"] == []
    assert "not attributed" in result["no_evidence_reason"]


def test_drift_default_is_read_only(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["agent_drift_detector.py", "--session", "old"])
    monkeypatch.setattr(agent_drift, "load_session", lambda _session: _ops_session())

    def unexpected_write(*_args, **_kwargs):
        raise AssertionError("read-only drift analysis attempted to write")

    monkeypatch.setattr(agent_drift, "save_drift_report", unexpected_write)

    assert agent_drift.main() == 0


def test_drift_write_mode_is_explicit(monkeypatch, tmp_path):
    written: list[dict] = []
    monkeypatch.setattr(
        sys, "argv", ["agent_drift_detector.py", "--session", "old", "--write"]
    )
    monkeypatch.setattr(agent_drift, "load_session", lambda _session: _ops_session())
    monkeypatch.setattr(
        agent_drift,
        "save_drift_report",
        lambda data, output_path=None: written.append(data) or tmp_path / "drift.json",
    )

    assert agent_drift.main() == 0
    assert len(written) == 1


def _trend_session(score: float) -> dict:
    return {"agent_scores": {"ops": {"composite": score}}}


def test_trends_default_is_read_only(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["agent_trends.py", "--weekly"])
    monkeypatch.setattr(agent_trends, "list_sessions", lambda: ["s1", "s2", "s3"])
    scores = iter([6.0, 7.0, 8.0])
    monkeypatch.setattr(
        agent_trends, "load_session", lambda _session: _trend_session(next(scores))
    )

    def unexpected_write(*_args, **_kwargs):
        raise AssertionError("read-only trend analysis attempted to write")

    monkeypatch.setattr(agent_trends, "save_trends", unexpected_write)

    assert agent_trends.main() == 0


def test_trends_missing_agent_fails_before_write(monkeypatch):
    monkeypatch.setattr(
        sys, "argv", ["agent_trends.py", "--weekly", "--agent", "frontend"]
    )
    monkeypatch.setattr(agent_trends, "list_sessions", lambda: ["s1"])
    monkeypatch.setattr(
        agent_trends, "load_session", lambda _session: _trend_session(8.0)
    )

    assert agent_trends.main() == 1


@pytest.mark.parametrize(
    ("operation", "mode", "expected"),
    [
        ("project health", None, "ReadOnly"),
        ("project health", "--fix", "WorkspaceWrite"),
        ("session summary", "--write", "WorkspaceWrite"),
        ("model usage checkpoint", None, "ReadOnly"),
        ("unknown task", None, "DangerFullAccess"),
        ("project health", "--unknown", "DangerFullAccess"),
    ],
)
def test_operation_permissions_are_explicit_and_fail_closed(operation, mode, expected):
    assert (
        tool_permissions.resolve_required_permission(operation, mode=mode) == expected
    )


def test_abstract_permission_operations_remain_compatible():
    assert tool_permissions.resolve_required_permission("read") == "ReadOnly"
    assert tool_permissions.resolve_required_permission("edit") == "WorkspaceWrite"
    assert tool_permissions.resolve_required_permission("delete") == "DangerFullAccess"


def test_agent_permission_check_uses_declared_task_mode():
    default = tool_permissions.check_permission("reviewer", "project health")
    mutating = tool_permissions.check_permission(
        "reviewer", "project health", mode="--fix"
    )

    assert default.allowed is True
    assert default.required_level == "ReadOnly"
    assert mutating.allowed is False
    assert mutating.required_level == "WorkspaceWrite"


def test_undeclared_operation_is_denied_even_to_danger_level_agent(monkeypatch):
    monkeypatch.setattr(
        tool_permissions,
        "_load_registry",
        lambda: [
            {
                "name": "danger-agent",
                "permission_level": "DangerFullAccess",
                "file_scope": None,
            }
        ],
    )

    result = tool_permissions.check_permission("danger-agent", "unknown task")
    unknown_mode = tool_permissions.check_permission(
        "danger-agent", "project health", mode="--unknown"
    )

    assert result.allowed is False
    assert result.required_level == "DangerFullAccess"
    assert "no explicit permission declaration" in result.reason
    assert unknown_mode.allowed is False


def test_tool_registry_does_not_infer_permission_from_git_text():
    registry = tool_registry.load_registry()

    assert registry["check git state"].permission == "ReadOnly"
    assert registry["project health"].permission_modes == {"--fix": "WorkspaceWrite"}
    assert registry["governance health score"].permission is None


@pytest.mark.parametrize(
    ("operation", "mode", "expected"),
    [
        ("generate folder index", None, "WorkspaceWrite"),
        ("generate folder index", "--dry-run", "ReadOnly"),
        ("batch migration", None, "WorkspaceWrite"),
        ("batch migration", "--dry-run", "ReadOnly"),
        ("pipeline state", "new", "WorkspaceWrite"),
        ("pipeline state", "list", "ReadOnly"),
        ("session store", "end", "WorkspaceWrite"),
        ("session store", "show", "ReadOnly"),
        ("self evolve", "--report", "WorkspaceWrite"),
    ],
)
def test_remaining_automation_permissions_match_modes(operation, mode, expected):
    assert (
        tool_permissions.resolve_required_permission(operation, mode=mode) == expected
    )


def test_automation_discovery_metadata_is_single_source():
    automation_map = json.loads(
        (SCRIPTS_DIR / "automation-map.json").read_text(encoding="utf-8")
    )

    assert check_scripts_index._automation_semantic_issues(automation_map) == {
        "legacy_categories": [],
        "missing_group": [],
        "removed_without_deprecation": [],
        "temporary_targets": [],
    }
    active = find_automation.active_tasks(automation_map)
    assert "add groups temp" not in active
    assert "test vba adapter" not in active
    assert all("streamlit" not in name for name in active)


def test_automation_semantics_reject_stale_and_temporary_entries():
    issues = check_scripts_index._automation_semantic_issues(
        {
            "categories": {"Legacy": ["removed task"]},
            "tasks": {
                "missing group": {"script": "./run.sh test"},
                "removed task": {
                    "group": "Testing",
                    "script": "./run.sh test",
                    "description": "Target (REMOVED)",
                },
                "temporary task": {
                    "group": "Infrastructure",
                    "script": "python scripts/_tmp_once.py",
                },
            },
        }
    )

    assert issues == {
        "legacy_categories": ["Legacy"],
        "missing_group": ["missing group"],
        "removed_without_deprecation": ["removed task"],
        "temporary_targets": ["temporary task"],
    }


def test_explicit_quick_category_cannot_false_green(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["check_all.py", "--quick", "--category", "api"])

    assert check_all.main() == 1


def test_evolution_preview_does_not_write_report(monkeypatch):
    monkeypatch.setattr(evolve, "step_health_scan", lambda fix=False: {"score": 100})
    monkeypatch.setattr(evolve, "step_sync_numbers", lambda fix=False: {})
    monkeypatch.setattr(evolve, "step_regenerate_indexes", lambda fix=False: {})
    monkeypatch.setattr(evolve, "step_process_feedback", dict)
    monkeypatch.setattr(evolve, "step_check_instruction_drift", dict)
    monkeypatch.setattr(evolve, "step_archive_stale_docs", lambda fix=False: {})
    monkeypatch.setattr(evolve, "step_generate_todo_items", lambda _data: [])

    def unexpected_write(*_args, **_kwargs):
        raise AssertionError("preview evolution attempted to write a report")

    monkeypatch.setattr(evolve, "_save_evolution_report", unexpected_write)

    result = evolve.run_evolution()

    assert result["mode"] == "dry-run"


def test_external_cli_refuses_existing_workdir(tmp_path):
    sentinel = tmp_path / "keep.txt"
    sentinel.write_text("preserve", encoding="utf-8")

    with pytest.raises(FileExistsError):
        external_cli._prepare_workdir(str(tmp_path))

    assert sentinel.read_text(encoding="utf-8") == "preserve"


def test_shell_maintenance_uses_safe_file_operations():
    archive_source = (SCRIPTS_DIR / "archive_old_files.sh").read_text(encoding="utf-8")
    root_count_source = (SCRIPTS_DIR / "check_root_file_count.sh").read_text(
        encoding="utf-8"
    )

    assert "safe_file_move.py" in archive_source
    assert "done < <(" in archive_source
    assert "git mv" not in root_count_source
    assert "scripts/safe_file_move.py <file>" in root_count_source
    assert "--dry-run" in root_count_source


def test_permission_metadata_audit_accepts_current_declarations():
    assert audit_permissions.audit_automation_permission_metadata() == []


def test_permission_metadata_audit_rejects_modes_without_default(tmp_path, monkeypatch):
    automation_map = tmp_path / "automation-map.json"
    automation_map.write_text(
        json.dumps(
            {"tasks": {"broken": {"permission_modes": {"--fix": "WorkspaceWrite"}}}}
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(audit_permissions, "_AUTOMATION_MAP", automation_map)

    anomalies = audit_permissions.audit_automation_permission_metadata()

    assert len(anomalies) == 1
    assert "explicit default" in anomalies[0].message

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
import yaml

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
check_docs = importlib.import_module("check_docs")
check_instruction_drift = importlib.import_module("check_instruction_drift")
check_scripts_index = importlib.import_module("check_scripts_index")
cli_smoke = importlib.import_module("test_cli_smoke")
config_precedence = importlib.import_module("config_precedence")
evolve = importlib.import_module("evolve")
external_cli = importlib.import_module("external_cli_test")
find_automation = importlib.import_module("find_automation")
project_health = importlib.import_module("project_health")
preflight = importlib.import_module("preflight")
sync_numbers = importlib.import_module("sync_numbers")
tool_permissions = importlib.import_module("tool_permissions")
tool_registry = importlib.import_module("tool_registry")
control_plane = importlib.import_module("control_plane")


def test_instruction_projections_and_semantic_contract_are_exact():
    pair_results = check_instruction_drift.check_all_pairs(REPO_ROOT)

    assert all(result["status"] == "ok" for result in pair_results)
    assert check_instruction_drift.instruction_contract_issues(REPO_ROOT) == []


def test_instruction_pair_rejects_approximate_but_nonexact_content(tmp_path):
    github_rule = tmp_path / "github.md"
    claude_rule = tmp_path / "claude.md"
    github_rule.write_text("---\napplyTo: x\n---\n# Rule\n\nExact\n", encoding="utf-8")
    claude_rule.write_text(
        "---\nglobs: x\n---\n# Rule\n\nAlmost exact\n", encoding="utf-8"
    )

    result = check_instruction_drift.check_pair("sample", github_rule, claude_rule)

    assert result["similarity"] > 0.5
    assert result["status"] == "content_drift"


def test_instruction_composition_audit_accepts_current_ownership():
    assert config_precedence.validate_precedence() == []

    applicable = config_precedence.show_precedence(
        "Python/structural_lib/services/api.py", agent="backend"
    )
    surfaces = [item.level for item in applicable]
    paths = [item.path.name for item in applicable]

    assert surfaces[0] == "contract"
    assert "platform" in surfaces
    assert "scoped-github" in surfaces
    assert "scoped-claude" in surfaces
    assert "backend.agent.md" in paths


def test_python_runtime_launcher_uses_explicit_interpreter():
    launcher = SCRIPTS_DIR / "python_runtime.sh"
    env = os.environ.copy()
    env["STRUCTURAL_LIB_PYTHON"] = sys.executable

    result = subprocess.run(
        ["bash", str(launcher), "-c", "import sys; print(sys.executable)"],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=10,
    )

    assert result.returncode == 0, result.stderr
    assert Path(result.stdout.strip()).resolve() == Path(sys.executable).resolve()


def test_python_runtime_launcher_discovers_windows_virtualenvs():
    launcher = (SCRIPTS_DIR / "python_runtime.sh").read_text(encoding="utf-8")

    assert 'export PYTHONUTF8="${PYTHONUTF8:-1}"' in launcher
    assert 'run_python_candidate "$REPO_ROOT/.venv/Scripts/python.exe"' in launcher
    assert (
        'run_python_candidate "$primary_worktree/.venv/Scripts/python.exe"' in launcher
    )
    assert 'run_python_candidate "$VIRTUAL_ENV/Scripts/python.exe"' in launcher


def test_agent_start_normalizes_windows_source_path_separators():
    binding = preflight.python_binding()
    assert binding["source_bound"] is True
    assert Path(binding["module"]).is_relative_to(REPO_ROOT / "Python/structural_lib")


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
        ["bash", str(launcher), "-c", probe],
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


def test_python_runtime_diagnostic_proves_worktree_source_binding():
    launcher = SCRIPTS_DIR / "python_runtime.sh"
    env = os.environ.copy()
    env["STRUCTURAL_LIB_PYTHON"] = sys.executable

    result = subprocess.run(
        ["bash", str(launcher), "--diagnose"],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=10,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["repository"] == str(REPO_ROOT)
    assert payload["source_bound"] is True
    assert Path(payload["module"]).is_relative_to(REPO_ROOT / "Python")


def test_agent_context_reads_latest_health_receipt_without_running_scanner(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    evolution = tmp_path / "logs" / "evolution"
    evolution.mkdir(parents=True)
    (evolution / "health_2026-08-23.json").write_text(
        json.dumps({"overall_score": 97}), encoding="utf-8"
    )
    monkeypatch.setattr(agent_context, "ROOT", tmp_path)

    assert agent_context.latest_health_score() == "Latest recorded: 97/100"


def test_control_paths_use_python_runtime_launcher():
    launcher = str(SCRIPTS_DIR / "python_runtime.sh")
    run_sh = (REPO_ROOT / "run.sh").read_text(encoding="utf-8")
    pre_commit = (REPO_ROOT / ".pre-commit-config.yaml").read_text(encoding="utf-8")
    entry_lines = [line for line in pre_commit.splitlines() if "entry:" in line]

    assert check_all.VENV_PYTHON == launcher
    assert check_all.PRE_COMMIT_TIMEOUT_SECONDS == 900
    assert check_all._python_runtime("-m", "pytest") == [
        "bash",
        launcher,
        "-m",
        "pytest",
    ]
    assert check_all._py("check_docs.py", "--all") == [
        "bash",
        launcher,
        str(SCRIPTS_DIR / "check_docs.py"),
        "--all",
    ]
    assert cli_smoke.VENV == launcher
    assert cli_smoke._portable_command([launcher, "-m", "pytest"]) == [
        "bash",
        launcher,
        "-m",
        "pytest",
    ]
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
    assert '"$SCRIPT_DIR/preflight.py"' in agent_start_source
    preflight_source = (SCRIPTS_DIR / "preflight.py").read_text(encoding="utf-8")
    assert "Python source binding: current worktree" in preflight_source
    assert "Python source shadowing detected" in preflight_source
    assert "collect_repository_state" in preflight_source
    assert "git status --porcelain" not in agent_start_source

    workflow = (REPO_ROOT / ".github" / "workflows" / "fast-checks.yml").read_text(
        encoding="utf-8"
    )
    control_validation = workflow.partition("  control-plane-validation:\n")[
        2
    ].partition("  documentation-validation:\n")[0]
    install_offset = control_validation.index(
        "python -m pip install -e 'Python/[dev]' PyYAML"
    )
    smoke_offset = control_validation.index("python scripts/test_cli_smoke.py")
    assert install_offset < smoke_offset


def test_pre_commit_contract_has_three_commit_guards_and_bounded_later_stages():
    config = yaml.safe_load(
        (REPO_ROOT / ".pre-commit-config.yaml").read_text(encoding="utf-8")
    )
    hooks = [hook for repo in config["repos"] for hook in repo["hooks"]]
    by_id = {hook["id"]: hook for hook in hooks}

    assert set(by_id) == {
        "check-merge-conflict",
        "check-added-large-files",
        "git-operation-guard",
        "file-integrity-read-only",
        "delivery-state-guard",
    }
    commit_hooks = {
        hook["id"]
        for hook in hooks
        if "pre-commit" in hook.get("stages", config["default_stages"])
    }
    manual_hooks = {hook["id"] for hook in hooks if "manual" in hook.get("stages", [])}
    assert commit_hooks == {
        "check-merge-conflict",
        "check-added-large-files",
        "git-operation-guard",
    }
    pre_push_hooks = {
        hook["id"] for hook in hooks if "pre-push" in hook.get("stages", [])
    }
    assert manual_hooks == {"file-integrity-read-only"}
    assert pre_push_hooks == {"delivery-state-guard"}
    operation_guard = by_id["git-operation-guard"]
    assert operation_guard["always_run"] is True
    assert operation_guard["pass_filenames"] is False
    assert operation_guard["entry"] == (
        "./scripts/python_runtime.sh scripts/git_state.py --guard operation "
        "--allow-operation-completion"
    )

    integrity_guard = by_id["file-integrity-read-only"]
    assert integrity_guard["entry"] == (
        "./scripts/python_runtime.sh scripts/verification.py integrity --all-files"
    )
    assert integrity_guard["always_run"] is True
    assert integrity_guard["pass_filenames"] is False

    delivery_guard = by_id["delivery-state-guard"]
    assert delivery_guard["entry"] == (
        "./scripts/python_runtime.sh scripts/session.py delivery --guard-push"
    )
    assert delivery_guard["always_run"] is True
    assert delivery_guard["pass_filenames"] is False

    assert not ({"black", "ruff", "mypy", "bandit", "pytest"} & set(by_id))


def test_pre_commit_manual_command_uses_repository_runtime():
    source = (REPO_ROOT / ".pre-commit-config.yaml").read_text(encoding="utf-8")
    assert (
        "./scripts/python_runtime.sh -m pre_commit run --hook-stage manual --all-files"
        in source
    )
    assert "# Run manually: pre-commit" not in source


def test_candidate_integrity_uses_the_exact_hosted_manual_hooks(
    monkeypatch: pytest.MonkeyPatch,
):
    calls: list[tuple[list[str], dict[str, object]]] = []

    def record(args, **kwargs):
        calls.append(([str(item) for item in args], kwargs))
        return subprocess.CompletedProcess(args, 1)

    monkeypatch.setattr(check_all.subprocess, "run", record)

    assert check_all._run_pre_commit(candidate_integrity=True) == 1
    assert calls == [
        (
            [
                "bash",
                str(SCRIPTS_DIR / "python_runtime.sh"),
                "-m",
                "pre_commit",
                "run",
                "--hook-stage",
                "manual",
                "--all-files",
            ],
            {
                "cwd": str(REPO_ROOT),
                "timeout": check_all.PRE_COMMIT_TIMEOUT_SECONDS,
            },
        )
    ]


def test_api_classification_moved_from_commit_hook_to_hosted_coverage():
    config = yaml.safe_load(
        (REPO_ROOT / ".pre-commit-config.yaml").read_text(encoding="utf-8")
    )
    hook_ids = {hook["id"] for repo in config["repos"] for hook in repo["hooks"]}
    coverage = json.loads(
        (SCRIPTS_DIR / "validation-coverage.json").read_text(encoding="utf-8")
    )
    entry = next(
        item
        for item in coverage["entries"]
        if item["source_id"] == "check-api-classification"
    )

    assert "check-api-classification" not in hook_ids
    assert entry["hosted_checks"] == [
        {
            "job": "documentation-validation",
            "token": "python scripts/generate_api_classification.py --check",
        }
    ]


def test_react_dependency_probe_is_worktree_local_and_actionable(tmp_path):
    assert preflight.missing_react_dependencies(tmp_path) == [
        "eslint",
        "tsc",
        "vite",
        "vitest",
    ]

    bin_dir = tmp_path / "react_app" / "node_modules" / ".bin"
    bin_dir.mkdir(parents=True)
    for tool in preflight.REACT_REQUIRED_TOOLS:
        (bin_dir / tool).touch()

    assert preflight.missing_react_dependencies(tmp_path) == []
    assert "npm --prefix react_app ci" in preflight.REACT_INSTALL_COMMAND


def test_live_full_gate_count_matches_active_instructions():
    full_count = sum(len(category.checks) for category in check_all.CATEGORIES)
    assert full_count == 32
    for path in (
        REPO_ROOT / "AGENTS.md",
        REPO_ROOT / "docs/guidelines/ai-token-efficiency.md",
        REPO_ROOT / "docs/getting-started/agent-bootstrap.md",
    ):
        assert "32 checks" in path.read_text(encoding="utf-8"), path


def test_api_classification_timeout_covers_the_generated_surface():
    checks = {
        check.name: check
        for category in check_all.CATEGORIES
        for check in category.checks
    }

    assert checks["API classification"].timeout >= 90


def test_active_agent_instructions_use_worktree_safe_python_launcher():
    instruction_paths = [REPO_ROOT / "AGENTS.md"]
    instruction_paths.extend((REPO_ROOT / ".github" / "skills").glob("*/SKILL.md"))
    instruction_paths.extend(
        (REPO_ROOT / ".github" / "instructions").glob("*.instructions.md")
    )

    for path in instruction_paths:
        source = path.read_text(encoding="utf-8")
        assert ".venv/bin/python" not in source, path
        assert ".venv/bin/pytest" not in source, path


def test_watch_help_does_not_require_fswatch():
    result = subprocess.run(
        ["bash", str(SCRIPTS_DIR / "watch_tests.sh"), "--help"],
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
        ("project health", "--write", "WorkspaceWrite"),
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


def test_project_health_persists_only_when_explicitly_requested(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    report = project_health.HealthReport(timestamp="2026-08-23", overall_score=100)
    monkeypatch.setattr(project_health, "EVOLUTION_DIR", tmp_path)
    monkeypatch.setattr(project_health, "run_health_scan", lambda **_kwargs: report)
    monkeypatch.setattr(project_health, "print_report", lambda *_args, **_kwargs: None)

    monkeypatch.setattr(sys, "argv", ["project_health.py", "--score"])
    with pytest.raises(SystemExit) as read_only_exit:
        project_health.main()
    assert read_only_exit.value.code == 0
    assert list(tmp_path.iterdir()) == []

    monkeypatch.setattr(sys, "argv", ["project_health.py", "--score", "--write"])
    with pytest.raises(SystemExit) as write_exit:
        project_health.main()
    assert write_exit.value.code == 0
    reports = list(tmp_path.glob("health_*.json"))
    assert len(reports) == 1
    assert json.loads(reports[0].read_text(encoding="utf-8"))["overall_score"] == 100


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
    assert registry["project health"].permission_modes == {
        "--fix": "WorkspaceWrite",
        "--write": "WorkspaceWrite",
    }
    assert tool_registry.resolve_alias("governance health score") == "project health"


@pytest.mark.parametrize(
    ("operation", "mode", "expected"),
    [
        ("repository context", None, "ReadOnly"),
        ("batch migration", None, "ReadOnly"),
        ("batch migration", "--dry-run", "ReadOnly"),
        ("batch migration", "live", "WorkspaceWrite"),
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
    registry = control_plane.load_registry()
    automation_map = control_plane.legacy_projection(registry)

    assert control_plane.legacy_is_current(registry)
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


def test_automation_discovery_resolves_retired_checker_names():
    automation_map = find_automation.load_automation_map()

    assert find_automation.find_task("check_scripts_index.py", automation_map)[0][
        0
    ] == ("check control coverage")
    assert find_automation.find_task("check_doc_metadata.py", automation_map)[0][0] == (
        "check docs metadata"
    )
    assert (
        find_automation.find_task("check_markdown_links.py", automation_map)[0][0]
        == "check markdown links"
    )


@pytest.mark.parametrize(
    ("query", "expected"),
    [
        ("check_not_main.sh", "check branch safety"),
        ("check_openapi_drift.py", "check openapi drift"),
        ("check_unfinished_merge.sh", "check merge state"),
        ("check_tasks.py", "check tasks format"),
        ("check_wip_limits.sh", "check tasks format"),
        ("fix_broken_links.py", "check markdown links"),
        ("generate_all_indexes.sh", "repository context"),
        ("generate_folder_index.py", "repository context"),
        ("governance_health_score.py", "project health"),
        ("repo_health_check.sh", "project health"),
        ("sync_numbers.py", "sync doc numbers"),
        ("global docs index", "repository context"),
        ("validate_git_state.sh", "check git state"),
    ],
)
def test_maintenance_commands_are_discoverable_by_legacy_and_intent_queries(
    query, expected
):
    automation_map = find_automation.load_automation_map()
    assert find_automation.find_task(query, automation_map)[0][0] == expected

    registry = tool_registry.load_registry()
    results = tool_registry.find_tools(query, registry, limit=10)
    assert expected in {tool.name for tool, _score in results}


def test_sync_numbers_separates_http_operations_paths_and_websockets(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    routers = tmp_path / "fastapi_app" / "routers"
    routers.mkdir(parents=True)
    (routers / "sample.py").write_text(
        '@router.get("/sample")\n@router.websocket("/live")\n', encoding="utf-8"
    )
    (tmp_path / "fastapi_app" / "main.py").write_text(
        '@app.get("/health")\n', encoding="utf-8"
    )
    (tmp_path / "fastapi_app" / "openapi_baseline.json").write_text(
        json.dumps({"paths": {"/sample": {}, "/health": {}}}), encoding="utf-8"
    )
    monkeypatch.setattr(sync_numbers, "REPO_ROOT", tmp_path)

    assert sync_numbers.scan_endpoints() == (2, 1)
    assert sync_numbers.scan_openapi_paths() == 2


def test_sync_numbers_repairs_every_maintained_api_inventory_surface(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    surfaces = {
        "AGENTS.md": "1 OpenAPI HTTP operations across 2 router modules",
        "llms.txt": "Key API Endpoints (FastAPI) — 3 endpoints across 4 routers",
        "docs/getting-started/agent-bootstrap.md": "\n".join(
            [
                "5 OpenAPI HTTP operation endpoints across 6 router modules",
                "scanner currently matches 7 OpenAPI paths",
                "8 public API functions; implementations split across `beam_api.py`, `column_api.py`, and `common_api.py` (9 private helpers)",
                "Swagger UI for all 10 current OpenAPI HTTP operations.",
            ]
        ),
        "docs/getting-started/mac-mini-setup.md": "\n".join(
            [
                "fastapi_app/ # REST backend (11 OpenAPI operations)",
                "routers/                #   12 routers",
            ]
        ),
    }
    for relative, content in surfaces.items():
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content + "\n", encoding="utf-8")

    monkeypatch.setattr(sync_numbers, "REPO_ROOT", tmp_path)
    metrics = sync_numbers.Metrics(
        endpoint_count=90,
        openapi_path_count=89,
        router_count=27,
        api_public_count=100,
        api_private_count=21,
    )
    updates = sync_numbers.find_updates(metrics)

    assert len(updates) == 8
    assert {update.metric for update in updates} == {
        "endpoint_count",
        "endpoint_router",
        "openapi_path_count",
        "api_functions",
        "router_count",
    }
    assert all(
        any(value in update.new_text for value in ("90", "89", "27", "100"))
        for update in updates
    )


def test_metadata_parser_recognizes_multiword_fields():
    metadata = check_docs._extract_metadata(
        "**Type:** Reference\n"
        "**Audience:** Maintainers\n"
        "**Status:** Complete\n"
        "**Last Updated:** 2026-08-11\n"
    )

    assert metadata["Last Updated"] == "2026-08-11"
    errors, warnings = check_docs._validate_metadata(
        "**Type:** Reference\n"
        "**Audience:** Maintainers\n"
        "**Status:** Complete\n"
        "**Importance:** Critical\n"
        "**Created:** 2026-08-11\n"
        "**Last Updated:** 2026-08-11\n"
    )
    assert errors == []
    assert warnings == []


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


def test_age_based_archiver_is_retired_from_active_scripts():
    root_count_source = (SCRIPTS_DIR / "check_root_file_count.sh").read_text(
        encoding="utf-8"
    )

    assert not (SCRIPTS_DIR / "archive_old_files.sh").exists()
    assert (SCRIPTS_DIR / "_archive" / "archive_old_files.sh").exists()
    assert "git mv" not in root_count_source
    assert "scripts/safe_file_move.py <file>" in root_count_source
    assert "--dry-run" in root_count_source


def test_permission_metadata_audit_accepts_current_declarations():
    assert audit_permissions.audit_automation_permission_metadata() == []


def test_permission_metadata_audit_rejects_missing_default(tmp_path, monkeypatch):
    registry_data = control_plane.load_registry()
    del registry_data["operations"]["project health"]["permission"]
    registry_path = tmp_path / "control-plane.json"
    registry_path.write_text(json.dumps(registry_data), encoding="utf-8")
    monkeypatch.setattr(audit_permissions, "_CONTROL_PLANE", registry_path)

    anomalies = audit_permissions.audit_automation_permission_metadata()

    assert len(anomalies) == 1
    assert "permission" in anomalies[0].message

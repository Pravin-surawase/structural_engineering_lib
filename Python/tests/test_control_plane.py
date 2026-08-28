"""Contract tests for the canonical repository control plane."""

from __future__ import annotations

import copy
import importlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.repo_only

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

control_plane = importlib.import_module("control_plane")
find_automation = importlib.import_module("find_automation")
tool_permissions = importlib.import_module("tool_permissions")
tool_registry = importlib.import_module("tool_registry")
openapi_snapshot = importlib.import_module("check_openapi_snapshot")


def test_openapi_snapshot_detects_full_spec_drift_but_ignores_version():
    baseline = {
        "info": {"title": "Structural API", "version": "1"},
        "paths": {"/beam": {"get": {"summary": "Before"}}},
        "components": {"schemas": {}},
    }
    version_only = json.loads(json.dumps(baseline))
    version_only["info"]["version"] = "2"
    changed_summary = json.loads(json.dumps(version_only))
    changed_summary["paths"]["/beam"]["get"]["summary"] = "After"

    assert not openapi_snapshot._has_changes(
        openapi_snapshot._diff_specs(baseline, version_only)
    )
    diff = openapi_snapshot._diff_specs(baseline, changed_summary)
    assert openapi_snapshot._has_changes(diff)
    assert "CHANGED paths./beam.get.summary" in diff["details"]


def test_current_registry_has_frozen_operation_and_script_parity():
    registry = control_plane.load_registry()
    all_operations = control_plane.operation_map(registry)
    active_operations = control_plane.operation_map(registry, active_only=True)

    assert len(all_operations) == 119
    assert len(active_operations) == 119
    assert len(control_plane.top_level_scripts()) == 105
    assert control_plane.referenced_top_level_scripts(registry) == (
        control_plane.top_level_scripts()
    )
    assert all(operation.get("permission") for operation in active_operations.values())
    assert active_operations["verification impact"]["command"]["display"] == (
        "./scripts/python_runtime.sh scripts/verification.py validate"
    )


def test_retired_executable_paths_are_absent_but_intent_has_one_alias_owner():
    retired = (
        "validate_git_state.sh",
        "check_unfinished_merge.sh",
        "check_not_main.sh",
        "generate_all_indexes.sh",
        "generate_docs_index.py",
        "generate_enhanced_index.py",
        "check_openapi_drift.py",
        "governance_health_score.py",
        "fix_broken_links.py",
        "check_wip_limits.sh",
        "repo_health_check.sh",
        "collect_metrics.sh",
        "export_paper_data.py",
    )
    for name in retired:
        assert not (SCRIPTS_DIR / name).exists()

    registry = control_plane.load_registry()
    expected = {
        "validate_git_state.sh": "check git state",
        "check_unfinished_merge.sh": "check merge state",
        "check_not_main.sh": "check branch safety",
        "generate_all_indexes.sh": "repository context",
        "check_openapi_drift.py": "check openapi drift",
        "governance_health_score.py": "project health",
        "fix_broken_links.py": "check markdown links",
        "check_wip_limits.sh": "check tasks format",
        "repo_health_check.sh": "project health",
    }
    for alias, owner in expected.items():
        assert control_plane.operation_name_for_alias(alias, registry) == owner


def test_control_validator_runs_without_site_packages():
    result = subprocess.run(
        [
            sys.executable,
            "-S",
            str(SCRIPTS_DIR / "control_plane" / "cli.py"),
            "validate",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=10,
    )

    assert result.returncode == 0, result.stderr
    assert "Control plane: PASS" in result.stdout


def test_legacy_projection_is_exact_and_deterministic():
    registry = control_plane.load_registry()
    first = control_plane.canonical_json(control_plane.legacy_projection(registry))
    second = control_plane.canonical_json(control_plane.legacy_projection(registry))

    assert first == second
    assert control_plane.legacy_is_current(registry)
    checked_in = (SCRIPTS_DIR / "automation-map.json").read_text(encoding="utf-8")
    assert checked_in == first


def test_aliases_have_one_owner_and_drive_all_discovery_consumers():
    registry = control_plane.load_registry()
    owners: dict[str, str] = {}
    for name, operation in control_plane.operation_map(
        registry, active_only=True
    ).items():
        for alias in operation.get("aliases", []):
            assert alias not in owners
            owners[alias] = name

    assert owners["move"] == "move file"
    assert control_plane.operation_name_for_alias("MOVE", registry) == "move file"
    assert tool_registry.resolve_alias("move") == "move file"
    legacy_view = find_automation.load_automation_map()
    assert find_automation.find_task("move", legacy_view)[0][0] == "move file"


def test_permission_lookup_uses_explicit_canonical_defaults_and_modes():
    assert tool_permissions.resolve_required_permission("project health") == "ReadOnly"
    assert (
        tool_permissions.resolve_required_permission("project health", mode="--fix")
        == "WorkspaceWrite"
    )
    assert (
        tool_permissions.resolve_required_permission(
            "check markdown links", mode="--fix"
        )
        == "WorkspaceWrite"
    )
    assert tool_permissions.resolve_required_permission("delete file") == "ReadOnly"
    assert (
        tool_permissions.resolve_required_permission("delete file", mode="live")
        == "DangerFullAccess"
    )
    assert tool_permissions.resolve_required_permission("unknown operation") == (
        "DangerFullAccess"
    )
    assert (
        tool_permissions.resolve_required_permission(
            "verification impact", mode="record"
        )
        == "WorkspaceWrite"
    )


def test_structured_commands_do_not_store_shell_chains_as_one_step():
    registry = control_plane.load_registry()
    operations = control_plane.operation_map(registry)

    assert len(operations["format code"]["command"]["steps"]) == 2
    for operation in operations.values():
        for step in operation["command"]["steps"]:
            assert not ({"&&", "||", ";", "|"} & set(step["argv"]))


def test_schema_rejects_missing_permission():
    registry = copy.deepcopy(control_plane.load_registry())
    del registry["operations"]["project health"]["permission"]

    errors = control_plane.validate_registry_data(registry)

    assert any("permission" in error for error in errors)


def test_schema_rejects_unknown_fields_wrong_types_and_missing_replacement():
    registry = copy.deepcopy(control_plane.load_registry())
    registry["unexpected"] = True
    registry["operations"]["project health"]["aliases"] = [42]
    registry["operations"]["project health"]["status"] = "deprecated"

    errors = control_plane.validate_registry_data(registry)

    assert any("additional property" in error for error in errors)
    assert any("expected string" in error for error in errors)
    assert any("replacement" in error for error in errors)


def test_semantics_reject_alias_collision_missing_target_and_display_drift():
    registry = copy.deepcopy(control_plane.load_registry())
    registry["operations"]["move file"].setdefault("aliases", []).append("check")
    registry["operations"]["move file"]["command"]["steps"][0]["argv"][
        1
    ] = "scripts/does_not_exist.py"

    errors = control_plane.validate_registry_data(registry)

    assert any("already belongs" in error for error in errors)
    assert any("missing command target" in error for error in errors)
    assert any("display command differs" in error for error in errors)


def test_loader_rejects_duplicate_json_keys(tmp_path):
    path = tmp_path / "duplicate.json"
    path.write_text('{"schema_version": 1, "schema_version": 1}', encoding="utf-8")

    with pytest.raises(control_plane.ControlPlaneError, match="duplicate JSON key"):
        control_plane.load_registry(path=path, validate=False)

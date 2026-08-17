"""Regression tests for fail-closed PR workflow routing."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest
import yaml

pytestmark = pytest.mark.repo_only

REPO_ROOT = Path(__file__).resolve().parents[2]
FAST_CHECKS = REPO_ROOT / ".github" / "workflows" / "fast-checks.yml"
DEPLOY_DOCS = REPO_ROOT / ".github" / "workflows" / "deploy-docs.yml"
NIGHTLY = REPO_ROOT / ".github" / "workflows" / "nightly.yml"
PUBLISH = REPO_ROOT / ".github" / "workflows" / "publish.yml"

BASE_GATE_ENV = {
    "CHANGES_RESULT": "success",
    "PYTHON_CHANGED": "false",
    "PYTHON_RESULT": "skipped",
    "FASTAPI_CHANGED": "false",
    "FASTAPI_RESULT": "skipped",
    "REACT_CHANGED": "false",
    "REACT_RESULT": "skipped",
    "CONTROL_PLANE_CHANGED": "false",
    "CONTROL_PLANE_RESULT": "skipped",
    "DOCS_CHANGED": "false",
    "DOCS_RESULT": "skipped",
    "REPOSITORY_RESULT": "success",
}


def _workflow() -> dict:
    return yaml.safe_load(FAST_CHECKS.read_text(encoding="utf-8"))


def _named_step_run(workflow_path: Path, job: str, step_name: str) -> str:
    workflow = yaml.safe_load(workflow_path.read_text(encoding="utf-8"))
    steps = workflow["jobs"][job]["steps"]
    return next(step["run"] for step in steps if step["name"] == step_name)


def test_hosted_full_suites_bind_the_setup_python_interpreter():
    expected = 'STRUCTURAL_LIB_PYTHON="$(command -v python)" python -m pytest'

    weekly = _named_step_run(
        NIGHTLY, "full-verification", "Full Python suite with coverage"
    )
    publication = _named_step_run(PUBLISH, "validate", "Run release tests")

    assert expected in weekly
    assert expected in publication


def test_weekly_benchmark_evidence_does_not_mutate_indexed_docs():
    workflow = yaml.safe_load(NIGHTLY.read_text(encoding="utf-8"))
    steps = workflow["jobs"]["full-verification"]["steps"]
    benchmark = next(
        step
        for step in steps
        if step["name"] == "FastAPI benchmark evidence (scheduled/manual lane)"
    )
    upload = next(
        step for step in steps if step["name"] == "Upload API benchmark evidence"
    )

    assert '"$RUNNER_TEMP/fastapi-benchmark-report.json"' in benchmark["run"]
    assert upload["with"]["path"] == "${{ runner.temp }}/fastapi-benchmark-report.json"
    assert "docs/reference/fastapi-benchmark-report.json" not in benchmark["run"]


def _pr_gate_script() -> str:
    steps = _workflow()["jobs"]["pr-gate"]["steps"]
    return next(
        step["run"]
        for step in steps
        if step["name"] == "Verify every applicable validation"
    )


def _run_pr_gate(**overrides: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", "-eu", "-o", "pipefail", "-c", _pr_gate_script()],
        cwd=REPO_ROOT,
        env={**os.environ, **BASE_GATE_ENV, **overrides},
        capture_output=True,
        text=True,
        timeout=10,
    )


def test_changed_path_routes_cover_controls_docs_and_their_tests():
    workflow = _workflow()
    jobs = workflow["jobs"]
    filters_text = next(
        step["with"]["filters"]
        for step in jobs["changes"]["steps"]
        if step["name"] == "Classify changed paths"
    )
    filters = yaml.safe_load(filters_text)
    control_paths = set(filters["control_plane"])
    docs_paths = set(filters["docs"])
    control_command = next(
        step["run"]
        for step in jobs["control-plane-validation"]["steps"]
        if step["name"] == "Validate Git, intake, session, and governance controls"
    )

    assert {
        "scripts/**",
        "run.sh",
        "agents/**",
        ".github/agents/**",
        ".github/workflows/**",
        "docs/git-automation/**",
        "docs/research/git-governance/**",
    } <= control_paths
    assert {
        "docs/**",
        "mkdocs.yml",
        "Python/pyproject.toml",
        "Python/structural_lib/**",
    } == docs_paths

    exact_tests = {
        "Python/tests/test_git_state.py",
        "Python/tests/test_session_automation.py",
        "Python/tests/test_session_store.py",
        "Python/tests/test_pipeline_state.py",
        "Python/tests/test_agent_governance_automation.py",
        "Python/tests/test_ci_workflow_contract.py",
    }
    assert exact_tests <= control_paths
    assert all(test_path in control_command for test_path in exact_tests)


def test_pr_gate_topology_and_cancellation_are_scoped_per_pr():
    workflow = _workflow()
    jobs = workflow["jobs"]
    pr_gate = jobs["pr-gate"]

    assert workflow["concurrency"] == {
        "group": "${{ github.workflow }}-${{ github.event.pull_request.number || github.run_id }}",
        "cancel-in-progress": "${{ github.event_name == 'pull_request' }}",
    }
    assert {
        "control-plane-validation",
        "documentation-validation",
    } <= set(pr_gate["needs"])
    assert jobs["documentation-validation"]["if"] == (
        "needs.changes.outputs.docs == 'true'"
    )
    docs_python = next(
        step["with"]["python-version"]
        for step in jobs["documentation-validation"]["steps"]
        if step["name"] == "Set up Python 3.11"
    )
    assert docs_python == "3.11"
    docs_run = next(
        step["run"]
        for step in jobs["documentation-validation"]["steps"]
        if step["name"] == "Build documentation strictly"
    )
    assert docs_run == "mkdocs build --strict"

    deploy_docs = DEPLOY_DOCS.read_text(encoding="utf-8")
    trigger_block = deploy_docs.partition("\non:\n")[2].partition("\npermissions:")[0]
    assert "pull_request:" not in trigger_block
    assert "group: ${{ github.workflow }}-${{ github.ref }}" in deploy_docs
    assert "group: deploy-docs" not in deploy_docs


def test_pr_gate_accepts_successful_applicable_routes():
    result = _run_pr_gate(
        CONTROL_PLANE_CHANGED="true",
        CONTROL_PLANE_RESULT="success",
        DOCS_CHANGED="true",
        DOCS_RESULT="success",
    )

    assert result.returncode == 0, result.stderr
    assert "All required and applicable validation jobs passed." in result.stdout


@pytest.mark.parametrize(
    ("changed_key", "result_key"),
    [
        ("CONTROL_PLANE_CHANGED", "CONTROL_PLANE_RESULT"),
        ("DOCS_CHANGED", "DOCS_RESULT"),
    ],
)
@pytest.mark.parametrize("bad_result", ["failure", "cancelled", "skipped", "timed_out"])
def test_pr_gate_rejects_non_successful_applicable_route(
    changed_key: str, result_key: str, bad_result: str
):
    result = _run_pr_gate(**{changed_key: "true", result_key: bad_result})

    assert result.returncode == 1
    assert f"concluded '{bad_result}'" in result.stdout


@pytest.mark.parametrize(
    ("changed_key", "result_key"),
    [
        ("CONTROL_PLANE_CHANGED", "CONTROL_PLANE_RESULT"),
        ("DOCS_CHANGED", "DOCS_RESULT"),
    ],
)
def test_pr_gate_rejects_unexpected_non_applicable_execution(
    changed_key: str, result_key: str
):
    result = _run_pr_gate(**{changed_key: "false", result_key: "success"})

    assert result.returncode == 1
    assert "should be skipped" in result.stdout

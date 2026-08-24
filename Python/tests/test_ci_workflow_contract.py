"""Regression tests for fail-closed PR workflow routing."""

from __future__ import annotations

import fnmatch
import json
import os
import re
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
EVIDENCE_ACTION = (
    REPO_ROOT / ".github" / "actions" / "verification-evidence" / "action.yml"
)
VERIFICATION_MANIFEST = REPO_ROOT / "scripts" / "verification-manifest.json"

BASE_GATE_ENV = {
    "CHANGES_RESULT": "success",
    "PYTHON_CHANGED": "false",
    "PYTHON_RESULT": "skipped",
    "FASTAPI_CHANGED": "false",
    "FASTAPI_RESULT": "skipped",
    "REACT_CHANGED": "false",
    "REACT_RESULT": "skipped",
    "EXCEL_CHANGED": "false",
    "EXCEL_RESULT": "skipped",
    "CONTROL_PLANE_CHANGED": "false",
    "CONTROL_PLANE_RESULT": "skipped",
    "DOCS_CHANGED": "false",
    "DOCS_RESULT": "skipped",
    "REPOSITORY_CHANGED": "false",
    "REPOSITORY_RESULT": "skipped",
    "FAIL_CLOSED": "false",
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


def test_publication_metadata_and_authorization_fail_before_release_tests():
    workflow = yaml.safe_load(PUBLISH.read_text(encoding="utf-8"))
    steps = workflow["jobs"]["validate"]["steps"]
    names = [step.get("name") for step in steps]

    assert names.index(
        "Enforce separate owner publication authorization"
    ) < names.index("Run release tests")


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


def test_weekly_repository_context_check_is_read_only():
    drift_step = _named_step_run(
        NIGHTLY, "full-verification", "Documentation and repository drift"
    )

    assert "python scripts/repo_context.py validate" in drift_step
    assert "generate_enhanced_index.py" not in drift_step
    assert "generate_docs_index.py" not in drift_step


def test_weekly_openapi_uses_the_canonical_snapshot_checker():
    workflow = NIGHTLY.read_text(encoding="utf-8")

    assert "python scripts/check_openapi_snapshot.py" in workflow
    assert "python scripts/check_openapi_drift.py" not in workflow


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


def test_hosted_change_routing_uses_the_canonical_fail_closed_planner():
    workflow = _workflow()
    jobs = workflow["jobs"]
    plan = next(
        step
        for step in jobs["changes"]["steps"]
        if step["name"] == "Plan exact validation domains"
    )
    control_command = next(
        step["run"]
        for step in jobs["control-plane-validation"]["steps"]
        if step["name"] == "Validate Git, intake, session, and governance controls"
    )

    assert "dorny/paths-filter" not in FAST_CHECKS.read_text(encoding="utf-8")
    assert "python scripts/verification.py plan" in plan["run"]
    assert '--github-output "$GITHUB_OUTPUT"' in plan["run"]
    assert plan["env"] == {
        "BASE_SHA": "${{ github.event.pull_request.base.sha || github.event.before }}",
        "HEAD_SHA": "${{ github.event.pull_request.head.sha || github.sha }}",
    }
    assert jobs["changes"]["outputs"]["fail_closed"] == (
        "${{ steps.impact.outputs.fail_closed }}"
    )

    exact_tests = {
        "Python/tests/test_git_state.py",
        "Python/tests/test_session_automation.py",
        "Python/tests/test_session_store.py",
        "Python/tests/test_pipeline_state.py",
        "Python/tests/test_agent_governance_automation.py",
        "Python/tests/test_audit_readiness_truth.py",
        "Python/tests/test_ci_workflow_contract.py",
        "Python/tests/test_verification_control.py",
    }
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
        "excel-validation",
        "control-plane-validation",
        "documentation-validation",
    } <= set(pr_gate["needs"])
    assert jobs["excel-validation"]["if"] == ("needs.changes.outputs.excel == 'true'")
    assert jobs["documentation-validation"]["if"] == (
        "needs.changes.outputs.docs == 'true'"
    )
    assert jobs["repository-validation"]["if"] == (
        "needs.changes.outputs.repository == 'true'"
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
    assert "python scripts/check_doc_versions.py --ci" in docs_run
    assert "python scripts/check_tasks_format.py" in docs_run
    assert "python scripts/check_links.py" in docs_run
    assert "python scripts/generate_api_classification.py --check" in docs_run
    assert docs_run.rstrip().endswith("mkdocs build --strict")

    excel_steps = jobs["excel-validation"]["steps"]
    excel_node = next(
        step["with"]["node-version"]
        for step in excel_steps
        if step["name"] == "Set up Node.js 24"
    )
    excel_test = next(
        step for step in excel_steps if step["name"] == "Run all Excel add-in tests"
    )
    assert excel_node == "24"
    assert excel_test["working-directory"] == "excel_addin"
    assert excel_test["run"] == "npm test"

    deploy_docs = DEPLOY_DOCS.read_text(encoding="utf-8")
    trigger_block = deploy_docs.partition("\non:\n")[2].partition("\npermissions:")[0]
    assert "pull_request:" not in trigger_block
    assert "group: ${{ github.workflow }}-${{ github.ref }}" in deploy_docs
    assert "group: deploy-docs" not in deploy_docs


def test_hosted_validation_checks_are_split_by_natural_domain_without_loss():
    python_policy = _named_step_run(
        FAST_CHECKS, "python-validation", "Architecture and code-quality policy"
    )
    fastapi_policy = _named_step_run(
        FAST_CHECKS, "fastapi-validation", "API and deployment contracts"
    )
    control_policy = _named_step_run(
        FAST_CHECKS,
        "control-plane-validation",
        "Validate Git, intake, session, and governance controls",
    )
    docs_policy = _named_step_run(
        FAST_CHECKS, "documentation-validation", "Build documentation strictly"
    )
    repository_policy = _named_step_run(
        FAST_CHECKS, "repository-validation", "Validate repository policy"
    )

    assert "check_architecture_boundaries.py" in python_policy
    assert "check_architecture_boundaries.py" in fastapi_policy
    for command in (
        "check_scripts_index.py",
        "validate_script_refs.py",
        "test_cli_smoke.py",
        "check_token_efficiency.py",
        "skill_tiers.py validate",
    ):
        assert command in control_policy
    for command in (
        "check_doc_versions.py --ci",
        "check_tasks_format.py",
        "check_links.py",
        "generate_api_classification.py --check",
        "mkdocs build --strict",
    ):
        assert command in docs_policy
    assert repository_policy.strip() == "python scripts/check_repo_hygiene.py"


def test_every_hosted_command_file_is_an_input_of_its_scheduled_domain():
    workflow = _workflow()
    manifest = json.loads(VERIFICATION_MANIFEST.read_text(encoding="utf-8"))
    scheduled = {
        "python-validation": "python",
        "fastapi-validation": "fastapi",
        "react-validation": "react",
        "excel-validation": "excel",
        "control-plane-validation": "control_plane",
        "documentation-validation": "docs",
        "repository-validation": "repository",
    }

    for job_name, domain in scheduled.items():
        run_source = "\n".join(
            step.get("run", "") for step in workflow["jobs"][job_name]["steps"]
        )
        command_paths = set(
            re.findall(
                r"\b(?:scripts/[A-Za-z0-9_./-]+\.(?:py|sh)|Python/tests/[A-Za-z0-9_./*-]+\.py)\b",
                run_source,
            )
        )
        assert command_paths
        for path in command_paths:
            owners = {
                owner
                for rule in manifest["rules"]
                if any(fnmatch.fnmatchcase(path, pattern) for pattern in rule["paths"])
                for owner in rule["domains"]
            }
            assert domain in owners, f"{job_name} reads unbound input {path}"


def test_every_scheduled_job_reuses_only_an_exact_verified_pass_receipt():
    jobs = _workflow()["jobs"]
    scheduled = {
        "python-validation": "python",
        "fastapi-validation": "fastapi",
        "react-validation": "react",
        "excel-validation": "excel",
        "control-plane-validation": "control-plane",
        "documentation-validation": "docs",
        "repository-validation": "repository",
    }

    for job_name, cache_name in scheduled.items():
        steps = jobs[job_name]["steps"]
        evidence = next(step for step in steps if step.get("id") == "evidence")
        record = next(step for step in steps if step["name"].startswith("Record exact"))
        validation_steps = [
            step
            for step in steps
            if step.get("if") == "steps.evidence.outputs.valid != 'true'"
        ]

        assert evidence["uses"] == "./.github/actions/verification-evidence"
        assert evidence["with"]["cache-name"] == cache_name
        assert evidence["with"]["domain"] == cache_name.replace("-", "_")
        assert steps.index(evidence) < steps.index(record)
        assert f"--profile {evidence['with']['profile']}" in record["run"]
        assert f"--domain {evidence['with']['domain']}" in record["run"]
        assert (
            f"--identity-command {evidence['with']['identity-command']}"
            in record["run"]
        )
        assert "verification.py record" in record["run"]
        assert record["if"] == "steps.evidence.outputs.valid != 'true'"
        assert len(validation_steps) >= 2

    action = yaml.safe_load(EVIDENCE_ACTION.read_text(encoding="utf-8"))
    steps = action["runs"]["steps"]
    restore = next(step for step in steps if step.get("id") == "cache")
    probe = next(step for step in steps if step.get("id") == "probe")

    assert restore["uses"] == "actions/cache@v6"
    assert "restore-keys" not in restore["with"]
    assert "steps.identity.outputs.fingerprint" in restore["with"]["key"]
    assert "verification.py" in probe["run"]
    assert "probe" in probe["run"]


def test_workflow_guidance_explains_excel_skip_and_performance_authorities():
    guidance = (REPO_ROOT / ".github" / "workflows" / "README.md").read_text(
        encoding="utf-8"
    )

    assert "Excel Add-in Validation` is expected to show `skipped`" in guidance
    assert "plan marks `excel` unchanged" in guidance
    assert "`excel_addin/**`, `.nvmrc`" in guidance
    assert "complete local Excel suite" in guidance
    assert "fastapi_app/tests/test_load.py" in guidance
    assert "executable latency and degradation thresholds" in guidance
    assert "baseline/comment reporting is parked" in guidance


def test_pr_gate_accepts_successful_applicable_routes():
    result = _run_pr_gate(
        EXCEL_CHANGED="true",
        EXCEL_RESULT="success",
        CONTROL_PLANE_CHANGED="true",
        CONTROL_PLANE_RESULT="success",
        DOCS_CHANGED="true",
        DOCS_RESULT="success",
        REPOSITORY_CHANGED="true",
        REPOSITORY_RESULT="success",
    )

    assert result.returncode == 0, result.stderr
    assert "All required and applicable validation jobs passed." in result.stdout


@pytest.mark.parametrize(
    ("changed_key", "result_key"),
    [
        ("PYTHON_CHANGED", "PYTHON_RESULT"),
        ("FASTAPI_CHANGED", "FASTAPI_RESULT"),
        ("REACT_CHANGED", "REACT_RESULT"),
        ("EXCEL_CHANGED", "EXCEL_RESULT"),
        ("CONTROL_PLANE_CHANGED", "CONTROL_PLANE_RESULT"),
        ("DOCS_CHANGED", "DOCS_RESULT"),
        ("REPOSITORY_CHANGED", "REPOSITORY_RESULT"),
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
        ("PYTHON_CHANGED", "PYTHON_RESULT"),
        ("FASTAPI_CHANGED", "FASTAPI_RESULT"),
        ("REACT_CHANGED", "REACT_RESULT"),
        ("EXCEL_CHANGED", "EXCEL_RESULT"),
        ("CONTROL_PLANE_CHANGED", "CONTROL_PLANE_RESULT"),
        ("DOCS_CHANGED", "DOCS_RESULT"),
        ("REPOSITORY_CHANGED", "REPOSITORY_RESULT"),
    ],
)
def test_pr_gate_rejects_unexpected_non_applicable_execution(
    changed_key: str, result_key: str
):
    result = _run_pr_gate(**{changed_key: "false", result_key: "success"})

    assert result.returncode == 1
    assert "should be skipped" in result.stdout


def test_pr_gate_rejects_missing_applicability_and_partial_fail_closed_plan():
    missing = _run_pr_gate(PYTHON_CHANGED="")
    assert missing.returncode == 1
    assert "applicability is ''" in missing.stdout

    partial = _run_pr_gate(FAIL_CLOSED="true")
    assert partial.returncode == 1
    assert "unknown impact did not select every validation domain" in partial.stdout


def test_pr_gate_accepts_fail_closed_all_domain_success():
    result = _run_pr_gate(
        FAIL_CLOSED="true",
        PYTHON_CHANGED="true",
        PYTHON_RESULT="success",
        FASTAPI_CHANGED="true",
        FASTAPI_RESULT="success",
        REACT_CHANGED="true",
        REACT_RESULT="success",
        EXCEL_CHANGED="true",
        EXCEL_RESULT="success",
        CONTROL_PLANE_CHANGED="true",
        CONTROL_PLANE_RESULT="success",
        DOCS_CHANGED="true",
        DOCS_RESULT="success",
        REPOSITORY_CHANGED="true",
        REPOSITORY_RESULT="success",
    )

    assert result.returncode == 0, result.stdout

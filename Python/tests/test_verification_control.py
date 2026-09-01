"""Regression tests for fail-closed impact planning and exact PASS reuse."""

from __future__ import annotations

import copy
import importlib
import json
import subprocess
import sys
from concurrent.futures import Future
from dataclasses import replace
from pathlib import Path

import pytest

pytestmark = pytest.mark.repo_only

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

verification = importlib.import_module("verification")
check_all = importlib.import_module("check_all")
test_changed = importlib.import_module("test_changed")
validate_imports = importlib.import_module("validate_imports")


@pytest.mark.parametrize(
    "package",
    [
        "ezdxf",
        "jsonschema",
        "jwt",
        "pydantic_core",
        "pydantic_settings",
        "sse_starlette",
        "weasyprint",
        "websockets",
    ],
)
def test_import_validator_knows_declared_project_dependencies(package: str):
    assert package in validate_imports.EXTERNAL_PACKAGES
    assert validate_imports.can_resolve_module(package)


def test_import_validator_resolves_checked_in_namespace_without_environment(
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr(
        validate_imports.importlib.util, "find_spec", lambda _name: None
    )

    assert validate_imports.can_resolve_module("scripts")


def test_parallel_fingerprints_preserve_exact_bytes_and_sorted_identity(tmp_path):
    manifest = verification.load_manifest()
    paths = []
    for index in range(40):
        path = f"docs/{index}.md"
        target = tmp_path / path
        target.parent.mkdir(exist_ok=True)
        target.write_bytes(f"bytes-{index}\r\n".encode())
        paths.append(path)
    identities = [
        verification.FingerprintContext(
            manifest, root=tmp_path, inventory=paths, workers=n
        ).identity(profile="parallel-parity", domains=("docs",), command=("test",))
        for n in (1, 4)
    ]
    assert identities[0] == identities[1]
    (tmp_path / paths[0]).write_bytes(b"changed\n")
    changed = verification.FingerprintContext(
        manifest, root=tmp_path, inventory=paths
    ).identity(profile="parallel-parity", domains=("docs",), command=("test",))
    assert changed.fingerprint != identities[0].fingerprint


def test_parallel_read_error_never_publishes_partial_digest_cache(
    tmp_path, monkeypatch
):
    context = verification.FingerprintContext(
        verification.load_manifest(), root=tmp_path, inventory=()
    )

    def read(path):
        if path == "docs/12.md":
            raise OSError("read denied")
        return "digest"

    monkeypatch.setattr(context, "_read_path_digest", read)
    with pytest.raises(OSError, match="read denied"):
        context._populate_path_digests([f"docs/{i}.md" for i in range(40)])
    assert context._path_digest_cache == {}


def test_timing_json_distinguishes_child_sum_from_wall(capsys):
    checks = [
        check_all.CheckResult(
            name="one", category="docs", passed=True, exit_code=0, duration=3
        ),
        check_all.CheckResult(
            name="two", category="docs", passed=True, exit_code=0, duration=4
        ),
    ]
    timings = {
        "wall_seconds": 6,
        "preparation_seconds": 1,
        "checks_wall_seconds": 4,
        "postflight_seconds": 1,
    }
    check_all._print_json_results(checks, timings)
    result = json.loads(capsys.readouterr().out)
    assert result["duration"] == 7
    assert result["timings"]["wall_seconds"] == 6
    assert result["duration_semantics"] == "sum_of_child_check_seconds_not_wall_time"


def test_failed_check_json_retains_actionable_output_without_rerunning(capsys):
    result = check_all.CheckResult(
        name="failed",
        category="docs",
        passed=False,
        exit_code=1,
        duration=1,
        stdout="ERROR: projection is stale",
    )
    check_all._print_json_results([result])
    output = json.loads(capsys.readouterr().out)
    assert output["checks"][0]["failure_output"] == "ERROR: projection is stale"


@pytest.mark.parametrize(
    ("argv", "label"),
    [
        (["--quick"], "check quick"),
        (["--pre-commit"], "check pre-commit"),
        (["--changed"], "check changed"),
        (["--category", "docs"], "check category"),
        ([], "check full"),
    ],
)
def test_check_orchestrator_timing_labels_are_stable(argv: list[str], label: str):
    assert check_all._timing_label(argv) == label


def test_check_timing_telemetry_never_changes_verdict(
    monkeypatch: pytest.MonkeyPatch,
):
    calls: list[list[str]] = []

    def record(args, **_kwargs):
        calls.append([str(item) for item in args])
        return subprocess.CompletedProcess(args, 1, "", "telemetry unavailable")

    monkeypatch.setattr(check_all.subprocess, "run", record)

    check_all._record_task_timing("check quick", 1.25, 0)

    assert calls[0][-7:] == [
        "usage",
        "--event",
        "check quick",
        "--duration-sec",
        "1.250",
        "--result-code",
        "0",
    ]


def test_live_verification_manifest_is_strict_and_covers_every_path():
    manifest = verification.load_manifest()

    assert tuple(manifest["domains"]) == verification.REQUIRED_DOMAINS
    assert manifest["metadata"]["unknown_impact"] == "all_domains"
    assert {
        name
        for name, info in manifest["domains"].items()
        if info.get("always_run") is True
    } == {"repository"}
    assert {info["hosted_job"] for info in manifest["domains"].values()} == {
        "python-validation",
        "fastapi-validation",
        "react-validation",
        "excel-validation",
        "control-plane-validation",
        "documentation-validation",
        "repository-validation",
    }


def test_manifest_rejects_duplicate_keys_and_unknown_fields(tmp_path):
    duplicate = tmp_path / "duplicate.json"
    duplicate.write_text('{"schema_version": 1, "schema_version": 1}\n')
    with pytest.raises(verification.VerificationError, match="duplicate JSON key"):
        verification.load_manifest(duplicate, inventory=())

    manifest = copy.deepcopy(verification.load_manifest())
    manifest["unexpected"] = True
    invalid = tmp_path / "invalid.json"
    invalid.write_text(json.dumps(manifest))
    with pytest.raises(verification.VerificationError, match="additional property"):
        verification.load_manifest(invalid, inventory=())


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        (
            "Python/structural_lib/services/api.py",
            {"python", "fastapi", "docs", "repository"},
        ),
        ("fastapi_app/main.py", {"fastapi", "repository"}),
        ("react_app/src/App.tsx", {"react", "fastapi", "repository"}),
        ("excel_addin/taskpane.mjs", {"excel", "repository"}),
        ("docs/contributing/testing-strategy.md", {"docs", "repository"}),
        ("mkdocs.yml", {"docs", "repository"}),
        ("scripts/check_all.py", set(verification.REQUIRED_DOMAINS)),
        (
            "scripts/check_openapi_snapshot.py",
            {"fastapi", "control_plane", "repository"},
        ),
        ("scripts/safe_file_move.py", {"control_plane", "repository"}),
        (
            "scripts/_lib/safe_file_ops.py",
            {"control_plane", "docs", "repository"},
        ),
        (
            "scripts/_lib/indian_code_manifest.py",
            {"python", "control_plane", "docs", "repository"},
        ),
        (
            "scripts/_lib/utils.py",
            {"python", "fastapi", "control_plane", "docs", "repository"},
        ),
        ("scripts/_lib/agent_data.py", {"control_plane", "repository"}),
        ("scripts/check_links.py", {"control_plane", "docs", "repository"}),
        (
            ".github/actions/verification-evidence/action.yml",
            set(verification.REQUIRED_DOMAINS),
        ),
    ],
)
def test_known_paths_map_to_explicit_domains(path, expected):
    manifest = verification.load_manifest()
    plan = verification.classify_paths([path], manifest)

    assert set(plan.domains) == expected
    assert plan.fail_closed is False
    assert plan.unknown_paths == ()


def test_unknown_path_and_git_query_failure_select_every_domain(monkeypatch):
    manifest = verification.load_manifest()
    unknown = verification.classify_paths(["future/unowned.file"], manifest)

    assert unknown.fail_closed is True
    assert unknown.unknown_paths == ("future/unowned.file",)
    assert unknown.domains == verification.REQUIRED_DOMAINS

    def fail_query(**_kwargs):
        raise verification.VerificationError("simulated Git failure")

    monkeypatch.setattr(verification, "changed_paths", fail_query)
    failed = verification.plan_changes(manifest)
    assert failed.fail_closed is True
    assert failed.domains == verification.REQUIRED_DOMAINS
    assert failed.failure_reasons == ("simulated Git failure",)


def test_repository_domain_is_universal_without_hiding_unknown_paths(tmp_path):
    manifest = verification.load_manifest()
    known = verification.classify_paths(["docs/known.md"], manifest)
    unknown = verification.classify_paths(["future/unowned.file"], manifest)

    assert "repository" in known.domains
    assert known.fail_closed is False
    assert unknown.fail_closed is True
    assert unknown.unknown_paths == ("future/unowned.file",)

    first = tmp_path / "known.txt"
    second = tmp_path / "other.txt"
    first.write_text("first\n", encoding="utf-8")
    second.write_text("other\n", encoding="utf-8")
    context = verification.FingerprintContext(
        manifest,
        root=tmp_path,
        inventory=("known.txt", "other.txt"),
        workers=1,
    )
    identity = context.identity(
        profile="repository-universal",
        domains=("repository",),
        command=("test",),
    )

    assert identity.input_count == 2


def test_unknown_live_path_is_plannable_but_strict_validation_rejects_it():
    manifest = verification.load_manifest()
    inventory = ("future/unowned.file",)

    verification.validate_manifest(
        manifest,
        inventory=inventory,
        require_coverage=False,
    )
    with pytest.raises(verification.VerificationError, match="lack an impact rule"):
        verification.validate_manifest(manifest, inventory=inventory)

    plan = verification.classify_paths(inventory, manifest)
    assert plan.fail_closed is True
    assert plan.domains == verification.REQUIRED_DOMAINS


def test_changed_paths_cover_the_whole_candidate_and_untracked_work(tmp_path):
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(
        ["git", "config", "user.email", "verification@example.invalid"],
        cwd=tmp_path,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Verification Test"],
        cwd=tmp_path,
        check=True,
    )
    initial = tmp_path / "README.md"
    initial.write_text("base\n")
    subprocess.run(["git", "add", "README.md"], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-qm", "base"], cwd=tmp_path, check=True)
    base = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=tmp_path, text=True
    ).strip()

    docs = tmp_path / "docs" / "first.md"
    docs.parent.mkdir()
    docs.write_text("first\n")
    subprocess.run(["git", "add", "docs/first.md"], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-qm", "first"], cwd=tmp_path, check=True)

    source = tmp_path / "Python" / "second.py"
    source.parent.mkdir()
    source.write_text("second = True\n")
    subprocess.run(["git", "add", "Python/second.py"], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-qm", "second"], cwd=tmp_path, check=True)

    untracked = tmp_path / "react_app" / "pending.ts"
    untracked.parent.mkdir()
    untracked.write_text("export {}\n")

    assert verification.changed_paths(root=tmp_path, base=base) == (
        "Python/second.py",
        "docs/first.md",
        "react_app/pending.ts",
    )


def test_fingerprint_binds_relevant_bytes_command_and_runtime(tmp_path):
    manifest = verification.load_manifest()
    python_file = tmp_path / "Python" / "structural_lib" / "sample.py"
    docs_file = tmp_path / "docs" / "note.md"
    python_file.parent.mkdir(parents=True)
    docs_file.parent.mkdir(parents=True)
    python_file.write_text("value = 1\n")
    docs_file.write_text("first\n")
    inventory = (
        "Python/structural_lib/sample.py",
        "docs/note.md",
    )

    first_context = verification.FingerprintContext(
        manifest, root=tmp_path, runtime_extra=b"runtime-a", inventory=inventory
    )
    first = first_context.identity(
        profile="local-check:test",
        domains=("python",),
        command=("tool", "--check"),
    )
    same = first_context.identity(
        profile="local-check:test",
        domains=("python",),
        command=("tool", "--check"),
    )
    assert same == first

    docs_file.write_text("second\n")
    docs_only_change = verification.FingerprintContext(
        manifest, root=tmp_path, runtime_extra=b"runtime-a", inventory=inventory
    ).identity(
        profile="local-check:test",
        domains=("python",),
        command=("tool", "--check"),
    )
    assert docs_only_change.fingerprint == first.fingerprint

    python_file.write_text("value = 2\n")
    relevant_change = verification.FingerprintContext(
        manifest, root=tmp_path, runtime_extra=b"runtime-a", inventory=inventory
    ).identity(
        profile="local-check:test",
        domains=("python",),
        command=("tool", "--check"),
    )
    assert relevant_change.fingerprint != first.fingerprint

    python_file.unlink()
    deletion = verification.FingerprintContext(
        manifest, root=tmp_path, runtime_extra=b"runtime-a", inventory=inventory
    ).identity(
        profile="local-check:test",
        domains=("python",),
        command=("tool", "--check"),
    )
    assert deletion.fingerprint != relevant_change.fingerprint

    command_change = first_context.identity(
        profile="local-check:test",
        domains=("python",),
        command=("tool", "--different"),
    )
    assert command_change.fingerprint != first.fingerprint

    runtime_change = verification.FingerprintContext(
        manifest, root=tmp_path, runtime_extra=b"runtime-b", inventory=inventory
    ).identity(
        profile="local-check:test",
        domains=("python",),
        command=("tool", "--check"),
    )
    assert runtime_change.fingerprint != first.fingerprint


def test_unknown_input_bytes_invalidate_every_domain_fingerprint(tmp_path):
    manifest = verification.load_manifest()
    unknown = tmp_path / "future" / "unowned.file"
    unknown.parent.mkdir()
    unknown.write_text("first\n")

    first = verification.FingerprintContext(
        manifest,
        root=tmp_path,
        inventory=("future/unowned.file",),
    ).identity(profile="unknown", domains=("excel",), command=("test",))
    unknown.write_text("second\n")
    second = verification.FingerprintContext(
        manifest,
        root=tmp_path,
        inventory=("future/unowned.file",),
    ).identity(profile="unknown", domains=("excel",), command=("test",))

    assert second.fingerprint != first.fingerprint


def test_only_exact_pass_receipt_is_reused(tmp_path):
    manifest = verification.load_manifest()
    source = tmp_path / "Python" / "sample.py"
    source.parent.mkdir()
    source.write_text("value = 1\n")
    context = verification.FingerprintContext(
        manifest, root=tmp_path, inventory=("Python/sample.py",)
    )
    command = (sys.executable, "-c", "raise SystemExit(7)")
    identity = context.identity(
        profile="local-check:receipt",
        domains=("python",),
        command=command,
    )
    receipt = tmp_path / "receipt.json"
    verification.write_receipt(receipt, identity)

    valid, reason = verification.probe_receipt(receipt, identity)
    assert (valid, reason) == (True, "exact-pass")

    wrong = replace(identity, fingerprint="0" * 64)
    assert verification.probe_receipt(receipt, wrong) == (
        False,
        "receipt-identity",
    )

    payload = json.loads(receipt.read_text())
    payload["status"] = "fail"
    receipt.write_text(json.dumps(payload))
    assert verification.probe_receipt(receipt, identity) == (
        False,
        "receipt-identity",
    )
    verification.write_receipt(receipt, identity)

    reused = check_all._run_check(
        check_all.Check("receipt", list(command)),
        "api",
        identity=identity,
        receipt_path=receipt,
    )
    assert reused.passed is True
    assert reused.reused is True

    fresh = check_all._run_check(
        check_all.Check("receipt", list(command)),
        "api",
        identity=identity,
        receipt_path=receipt,
        reuse=False,
    )
    assert fresh.passed is False
    assert fresh.exit_code == 7
    assert fresh.reused is False


def test_aggregate_runner_omission_is_an_explicit_failure():
    future = Future()
    results = []

    check_all._append_missing_results(
        results,
        {future: (check_all.Check("missing", ["true"]), "docs")},
    )

    assert future.cancelled()
    assert len(results) == 1
    assert results[0].passed is False
    assert results[0].timed_out is True
    assert results[0].error == "aggregate runner did not return a result"


def test_changed_test_files_map_to_themselves_without_forcing_a_broad_suite():
    paths = {
        "Python/tests/test_verification_control.py",
        "fastapi_app/tests/test_config.py",
    }

    assert test_changed.map_to_tests(sorted(paths)) == paths


def test_cli_receipt_write_scope_is_bounded(tmp_path, monkeypatch):
    manifest = verification.load_manifest()
    context = verification.FingerprintContext(manifest, root=tmp_path, inventory=())
    identity = context.identity(
        profile="hosted-test", domains=("excel",), command=("test",)
    )
    monkeypatch.setenv("RUNNER_TEMP", str(tmp_path / "runner"))

    assert verification._cli_receipt_is_allowed(
        tmp_path / "runner" / "verification-evidence" / "excel.json", identity
    )
    assert not verification._cli_receipt_is_allowed(
        tmp_path / "tracked-result.json", identity
    )


def test_changed_mode_manifest_failure_runs_every_domain(monkeypatch):
    def fail_manifest(**_kwargs):
        raise verification.VerificationError("broken manifest")

    monkeypatch.setattr(check_all, "load_manifest", fail_manifest)
    domains, fail_closed, reasons = check_all._detect_changed_domains()

    assert domains == set(verification.REQUIRED_DOMAINS)
    assert fail_closed is True
    assert reasons == ("broken manifest",)

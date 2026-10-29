"""Exercise publication byte gates and the workflow's actual target routing."""

from __future__ import annotations

import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import zipfile

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from _lib import release_retained as retained  # noqa: E402
from _lib.release_qualification import (  # noqa: E402
    REQUIRED_RESOURCES,
    inspect_distribution_pair,
)


@pytest.fixture
def candidate(tmp_path, monkeypatch):
    repo, dist, evidence = (tmp_path / name for name in ("repo", "dist", "evidence"))
    dist.mkdir()
    payload = dict.fromkeys(REQUIRED_RESOURCES, b"controlled package fixture")
    payload["structural_lib/__init__.py"] = b'__version__="0.26.0"\n'
    for name, content in payload.items():
        path = repo / "Python" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    project = repo / "Python/pyproject.toml"
    project.write_text('[project]\nversion="0.26.0"\n')
    wheel, sdist = dist / "candidate.whl", dist / "candidate.tar.gz"
    with zipfile.ZipFile(wheel, "w") as archive:
        archive.writestr(
            "candidate.dist-info/METADATA",
            "Name: structural-lib-is456\nVersion: 0.26.0\n",
        )
        for name, content in payload.items():
            archive.writestr(name, content)
    with tarfile.open(sdist, "w:gz") as archive:
        for name, content in {"PKG-INFO": b"Version: 0.26.0\n", **payload}.items():
            member = tarfile.TarInfo("candidate/" + name)
            member.size = len(content)
            archive.addfile(member, io.BytesIO(content))
    pair = inspect_distribution_pair(repo, wheel, sdist, "0.26.0")
    record = {
        "schema_version": "qualified-release-artifacts/v1",
        "version": "0.26.0",
        "python_tree_sha": "a" * 40,
        "s5_merge_sha": "b" * 40,
        "source_build_inputs_sha256": {
            "Python/pyproject.toml": retained.digest(project)
        },
        "package_payload_sha256": pair["package_payload_sha256"],
        "artifacts": [
            {"filename": p.name, "sha256": retained.digest(p)} for p in (wheel, sdist)
        ],
        "qualification": {"profiles": {str(i): "PASS" for i in range(16)}},
        "installed_wheel_uat": {
            "status": "PASS",
            "package_version": "0.26.0",
            "case_count": 29,
            "cases": [{"id": str(i), "status": "PASS"} for i in range(29)],
            "professional_approval": False,
        },
        "qualified_base_sbom": {
            "bomFormat": "CycloneDX",
            "specVersion": "1.6",
            "components": [],
        },
    }
    record_path = retained.record_path(repo, "0.26.0")
    record_path.parent.mkdir(parents=True)
    record_path.write_bytes(retained.encoded(record))
    for name in (
        "is456-public-distribution-permission.json",
        "footing-release-inclusion.json",
    ):
        (record_path.parent / name).write_text("{}")
    (record_path.parent / "release-publication-authorization.json").write_text(
        json.dumps(
            {
                "version": "0.26.0",
                "decision": "AUTHORIZED",
                "tag": "v0.26.0",
                "authorized_targets": ["testpypi", "pypi", "github-release"],
                "exact_candidate_review_receipt": "docs/verification/review.json",
                "exact_candidate_review_receipt_sha256": "e" * 64,
            }
        )
    )
    monkeypatch.setattr(
        retained,
        "_git",
        lambda _repo, *args: "a" * 40 if args[-1] == "HEAD:Python" else "c" * 40,
    )
    return repo, dist, evidence, record_path, record


def test_retained_pair_reuses_all_uat_without_a_build(candidate):
    repo, dist, evidence, _, _ = candidate
    result = retained.verify_retained(repo, "0.26.0", dist, evidence)
    assert result["retained_qualification"]["rebuild_performed"] is False
    assert result["retained_qualification"]["reuse_installed_uat"] is True
    assert (
        json.loads((evidence / "exact-wheel-uat.json").read_text())["case_count"] == 29
    )
    assert len(result["artifacts"]) == 2


@pytest.mark.parametrize(
    "change", ["bytes", "extra-file", "build-input", "profile", "uat"]
)
def test_drift_or_incomplete_qualification_cannot_reach_upload(candidate, change):
    repo, dist, evidence, path, record = candidate
    if change == "bytes":
        (dist / "candidate.whl").write_bytes(b"different wheel")
    elif change == "extra-file":
        (dist / "unselected.whl").write_bytes(b"wrong candidate")
    elif change == "build-input":
        (repo / "Python/pyproject.toml").write_text('version="0.27.0"')
    elif change == "profile":
        record["qualification"]["profiles"].pop("0")
    else:
        record["installed_wheel_uat"]["cases"].pop()
    path.write_bytes(retained.encoded(record))
    with pytest.raises(ValueError):
        retained.verify_retained(repo, "0.26.0", dist, evidence)
    assert not (evidence / "artifact-manifest.json").exists()


def test_python_tree_drift_is_rejected(candidate, monkeypatch):
    repo, dist, evidence, _, _ = candidate
    monkeypatch.setattr(retained, "_git", lambda *_: "d" * 40)
    with pytest.raises(ValueError, match="Python tree"):
        retained.verify_retained(repo, "0.26.0", dist, evidence)


@pytest.mark.parametrize("server_corruption", [False, True])
def test_draft_is_published_only_after_existing_package_assets_match(
    candidate, monkeypatch, server_corruption
):
    repo, dist, evidence, _, _ = candidate
    (repo / "CHANGELOG.md").write_text(
        "## [0.26.0] — 2026-10-29\nQualified release.\n\n## [0.25.0]\nOlder."
    )
    packages = list(dist.iterdir())
    release = {
        "tag_name": "v0.26.0",
        "draft": True,
        "target_commitish": "c" * 40,
        "assets": [
            {"id": i, "name": p.name, "state": "uploaded"}
            for i, p in enumerate(packages)
        ],
    }
    calls = []

    def fake_gh(*args, output=None):
        if output is None:
            return release
        index = int(args[-1].rsplit("/", 1)[-1])
        output.write_bytes(
            b"corrupt remote asset"
            if server_corruption
            else packages[index].read_bytes()
        )

    monkeypatch.setattr(retained, "_gh", fake_gh)
    monkeypatch.setattr(
        retained.subprocess, "run", lambda args, **kwargs: calls.append(args)
    )
    if server_corruption:
        with pytest.raises(ValueError, match="draft asset differs"):
            retained.promote_draft(repo, "0.26.0", dist, evidence, "owner/repo", "123")
        assert calls == []
    else:
        retained.promote_draft(repo, "0.26.0", dist, evidence, "owner/repo", "123")
        assert all(call[:3] == ["gh", "release", "upload"] for call in calls[:-1])
        assert calls[-1][:3] == ["gh", "release", "edit"]
        assert "--draft=false" in calls[-1] and "--verify-tag" in calls[-1]


@pytest.mark.parametrize(
    "event,ref,target,expected_execute,expected_target",
    [
        ("push", "refs/tags/v0.26.0", "testpypi", "false", "pypi"),
        ("workflow_dispatch", "refs/heads/main", "verify", "true", "verify"),
        ("workflow_dispatch", "refs/heads/main", "testpypi", "true", "testpypi"),
        ("workflow_dispatch", "refs/tags/v0.26.0", "verify", "true", "verify"),
        ("workflow_dispatch", "refs/tags/v0.26.0", "pypi", "true", "pypi"),
        ("workflow_dispatch", "refs/heads/main", "pypi", None, None),
    ],
)
def test_actual_workflow_routing_keeps_verification_nonpublishing(
    tmp_path, event, ref, target, expected_execute, expected_target
):
    project = tmp_path / "Python"
    project.mkdir()
    (project / "pyproject.toml").write_text(
        '[project]\nversion="0.26.0"\nclassifiers=["Development Status :: 4 - Beta"]'
    )
    record = retained.record_path(tmp_path, "0.26.0")
    record.parent.mkdir(parents=True)
    record.write_text("{}")
    workflow = yaml.safe_load((ROOT / ".github/workflows/publish.yml").read_text())
    step = next(
        s for s in workflow["jobs"]["validate"]["steps"] if s.get("id") == "version"
    )
    output = tmp_path / "outputs"
    env = {
        **os.environ,
        "PATH": str(Path(sys.executable).parent) + os.pathsep + os.environ["PATH"],
        "GITHUB_REF": ref,
        "GITHUB_REF_NAME": ref.rsplit("/", 1)[-1],
        "GITHUB_EVENT_NAME": event,
        "GITHUB_OUTPUT": str(output),
        "MANUAL_VERSION": "0.26.0",
        "MANUAL_TARGET": target,
        "RETAINED_RELEASE_ID": "123",
    }
    result = subprocess.run(
        ["bash", "-c", step["run"]],
        cwd=project,
        env=env,
        capture_output=True,
        text=True,
    )
    if expected_execute is None:
        assert result.returncode != 0
        assert "production must run from the exact version tag" in result.stdout
        return
    assert result.returncode == 0, result.stdout + result.stderr
    values = dict(line.split("=", 1) for line in output.read_text().splitlines())
    assert values["execute"] == expected_execute
    assert values["target"] == expected_target


def test_all_rebuild_and_retest_steps_are_excluded_from_retained_mode():
    workflow = yaml.safe_load((ROOT / ".github/workflows/publish.yml").read_text())
    for job, names in {
        "validate": ["Install package", "Run release tests"],
        "build": [
            "Build package",
            "Verify distribution contents and record artifact identity",
            "Clean-environment UAT on the exact built wheel",
            "Generate and validate CycloneDX SBOM",
            "Finalize immutable release evidence",
        ],
    }.items():
        for name in names:
            step = next(
                s for s in workflow["jobs"][job]["steps"] if s.get("name") == name
            )
            assert "outputs.retained != 'true'" in step["if"]

"""Retained S5 distribution transport owned by the release CLI.

No build or test execution occurs here. The committed qualification record,
frozen Python/build inputs and archive hashes bind the reused installed UAT.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from .release_qualification import inspect_distribution_pair


def encoded(value: Any) -> bytes:
    return (
        json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"
    ).encode()


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def record_path(repo: Path, version: str) -> Path:
    if not re.fullmatch(r"\d+\.\d+\.\d+(?:a\d+)?", version):
        raise ValueError("Invalid retained release version")
    return (
        repo
        / "docs/verification"
        / f"library-{version.replace('.', '')}-release-artifacts.json"
    )


def _git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=repo, text=True).strip()


def _gh(*args: str, output: Path | None = None) -> Any:
    if output is not None:
        with output.open("wb") as stream:
            subprocess.run(["gh", *args], stdout=stream, check=True)
        return None
    return json.loads(subprocess.check_output(["gh", *args], text=True))


def _release(repo: Path, version: str, repository: str, release_id: str) -> dict:
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
        raise ValueError("Expected owner/repository")
    if not release_id.isdecimal():
        raise ValueError("Expected an immutable numeric release ID")
    release = _gh("api", f"repos/{repository}/releases/{release_id}")
    if release["tag_name"] != f"v{version}" or not release["draft"]:
        raise ValueError("Retained source must be the selected draft release")
    if release["target_commitish"] != _git(repo, "rev-parse", "HEAD"):
        raise ValueError("Draft release target does not match publication HEAD")
    return release


def download_pair(
    repo: Path, version: str, dist: Path, repository: str, release_id: str
) -> None:
    """Download only the selected two assets, then let the byte gate verify them."""
    record = json.loads(record_path(repo, version).read_text())
    release = _release(repo, version, repository, release_id)
    assets = {asset["name"]: asset for asset in release["assets"]}
    dist.mkdir(parents=True, exist_ok=True)
    for item in record["artifacts"]:
        asset = assets.get(item["filename"])
        if not asset or asset["state"] != "uploaded":
            raise ValueError(f"Draft release lacks {item['filename']}")
        _gh(
            "api",
            "-H",
            "Accept: application/octet-stream",
            f"repos/{repository}/releases/assets/{asset['id']}",
            output=dist / item["filename"],
        )


def verify_retained(
    repo: Path, version: str, dist: Path, evidence: Path
) -> dict[str, Any]:
    """Reject drift and materialize only previously qualified evidence."""
    path = record_path(repo, version)
    record = json.loads(path.read_text())
    if (
        record.get("schema_version") != "qualified-release-artifacts/v1"
        or record.get("version") != version
    ):
        raise ValueError("Qualified artifact record identity is invalid")
    expected = {item["filename"]: item["sha256"] for item in record["artifacts"]}
    actual = {p.name: digest(p) for p in dist.iterdir() if p.is_file()}
    if actual != expected or len(actual) != 2:
        raise ValueError("Retained distribution filenames/hashes differ from S5")
    if _git(repo, "rev-parse", "HEAD:Python") != record["python_tree_sha"]:
        raise ValueError("Frozen Python tree changed after qualification")
    for name, sha in record["source_build_inputs_sha256"].items():
        if digest(repo / name) != sha:
            raise ValueError(f"Frozen build input changed: {name}")
    wheel = next(dist / name for name in expected if name.endswith(".whl"))
    sdist = next(dist / name for name in expected if name.endswith(".tar.gz"))
    pair = inspect_distribution_pair(repo, wheel, sdist, version)
    if pair["package_payload_sha256"] != record["package_payload_sha256"]:
        raise ValueError("Qualified package payload changed")
    qualification = record["qualification"]
    if len(qualification["profiles"]) != 16 or set(
        qualification["profiles"].values()
    ) != {"PASS"}:
        raise ValueError("Complete S5 installed qualification is required")
    uat = record["installed_wheel_uat"]
    if (
        uat["status"] != "PASS"
        or uat["package_version"] != version
        or uat["case_count"] != 29
        or len(uat["cases"]) != 29
        or any(case["status"] != "PASS" for case in uat["cases"])
        or uat["professional_approval"] is not False
    ):
        raise ValueError("Qualified exact-wheel UAT is incomplete")
    evidence.mkdir(parents=True, exist_ok=True)
    documents = {
        "exact-wheel-uat.json": uat,
        "qualification-summary.json": qualification,
        "sbom.json": record["qualified_base_sbom"],
    }
    for name, data in documents.items():
        (evidence / name).write_bytes(encoded(data))
    authorization = json.loads(
        (repo / "docs/verification/release-publication-authorization.json").read_text()
    )
    manifest = {
        "schema_version": "release-artifact-evidence/v3",
        "package_version": version,
        "source_sha": _git(repo, "rev-parse", "HEAD"),
        "source_tree_sha": _git(repo, "rev-parse", "HEAD^{tree}"),
        "python_tree_sha": record["python_tree_sha"],
        "artifacts": record["artifacts"],
        "content_allowlist_passed": True,
        "public_distribution_permission_gate_passed": True,
        "public_distribution_permission_record_sha256": digest(
            repo / "docs/verification/is456-public-distribution-permission.json"
        ),
        "footing_release_inclusion_gate_passed": True,
        "footing_release_inclusion_record_sha256": digest(
            repo / "docs/verification/footing-release-inclusion.json"
        ),
        "retained_qualification": {
            "record": str(path.relative_to(repo)),
            "record_sha256": digest(path),
            "s5_merge_sha": record["s5_merge_sha"],
            "reuse_installed_uat": True,
            "rebuild_performed": False,
            "evidence_sha256": {name: digest(evidence / name) for name in documents},
        },
        "publication_authorization": (
            {
                "decision": authorization["decision"],
                "version": authorization["version"],
                "tag": authorization["tag"],
                "authorized_targets": authorization["authorized_targets"],
                "exact_candidate_review_receipt": authorization[
                    "exact_candidate_review_receipt"
                ],
                "exact_candidate_review_receipt_sha256": authorization[
                    "exact_candidate_review_receipt_sha256"
                ],
                "record_sha256": digest(
                    repo / "docs/verification/release-publication-authorization.json"
                ),
            }
            if authorization["version"] == version
            else None
        ),
        "qualified_review_required": True,
        "professional_approval": False,
    }
    (evidence / "artifact-manifest.json").write_bytes(encoded(manifest))
    if os.environ.get("GITHUB_RUN_ID"):
        run = {
            "run_id": os.environ["GITHUB_RUN_ID"],
            "run_attempt": os.environ["GITHUB_RUN_ATTEMPT"],
            "source_sha": manifest["source_sha"],
            "source_ref": os.environ["GITHUB_REF"],
            "artifact_manifest_sha256": digest(evidence / "artifact-manifest.json"),
        }
        (
            evidence / f"publication-run-{run['run_id']}-{run['run_attempt']}.json"
        ).write_bytes(encoded(run))
    return manifest


def promote_draft(
    repo: Path,
    version: str,
    dist: Path,
    evidence: Path,
    repository: str,
    release_id: str,
) -> None:
    """Attach verified evidence once and publish the already populated draft."""
    verify_retained(repo, version, dist, evidence)
    release = _release(repo, version, repository, release_id)
    if _git(repo, "rev-parse", f"refs/tags/v{version}^{{commit}}") != _git(
        repo, "rev-parse", "HEAD"
    ):
        raise ValueError("Release tag does not match the publication commit")
    assets = {asset["name"]: asset for asset in release["assets"]}
    with tempfile.TemporaryDirectory(prefix="retained_asset_readback_") as raw:
        for path in sorted([*dist.iterdir(), *evidence.iterdir()]):
            if not path.is_file():
                continue
            if path.name in assets:
                downloaded = Path(raw) / path.name
                _gh(
                    "api",
                    "-H",
                    "Accept: application/octet-stream",
                    f"repos/{repository}/releases/assets/{assets[path.name]['id']}",
                    output=downloaded,
                )
                if digest(downloaded) != digest(path):
                    raise ValueError(f"Existing draft asset differs: {path.name}")
            else:
                subprocess.run(
                    [
                        "gh",
                        "release",
                        "upload",
                        f"v{version}",
                        str(path),
                        "--repo",
                        repository,
                    ],
                    check=True,
                )
        text = (repo / "CHANGELOG.md").read_text()
        notes = text.split(f"## [{version}]", 1)[1].split("\n## [", 1)[0]
        notes_path = Path(raw) / "notes.md"
        notes_path.write_text(f"## v{version}" + notes)
        subprocess.run(
            [
                "gh",
                "release",
                "edit",
                f"v{version}",
                "--repo",
                repository,
                "--verify-tag",
                "--draft=false",
                f"--prerelease={'true' if 'a' in version else 'false'}",
                "--latest=false" if "a" in version else "--latest",
                "--title",
                f"StructLib v{version}",
                "--notes-file",
                str(notes_path),
            ],
            check=True,
        )

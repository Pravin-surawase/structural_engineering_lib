"""Installed S5 evidence owned by ``release verify --qualification``.

This performs no Git mutation or publication. Every profile gets a fresh venv;
only the wheel's selected extra or named application-client requirements are
installed. Receipts distinguish dependency availability from product/native
acceptance. Explicit profile selection permits affected-evidence repairs.
"""

from __future__ import annotations

import email
import hashlib
import json
import os
import re
import subprocess
import sys
import tarfile
import tempfile
import time
import tomllib
import zipfile
from pathlib import Path
from typing import Any

PROBE = Path(__file__).with_name("release_qualification_probe.py")
REQUIRED_RESOURCES = (
    "structural_lib/py.typed",
    "structural_lib/codes/is456/clauses.json",
    "structural_lib/reports/templates/beam_design_report.html.j2",
)
FORBIDDEN_PREFIXES = (
    "structural_lib/research/",
    "structural_lib/_migration_fixtures/",
    "structural_lib/codes/aci318/",
    "structural_lib/codes/ec2/",
    "tests/",
    "examples/",
    "scripts/",
)
PERFORMANCE_BUDGETS = {
    "beam_p95_ms": 100.0,
    "batch100_p95_ms": 2000.0,
    "family_p95_ms": 1000.0,
    "median_regression_factor": 3.0,
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _payload_digest(payload: dict[str, str]) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def inspect_distribution_pair(
    repo: Path, wheel: Path, sdist: Path, version: str
) -> dict[str, Any]:
    """Compare complete wheel/sdist package payloads with frozen source files."""
    with zipfile.ZipFile(wheel) as archive:
        names = archive.namelist()
        metadata_names = [n for n in names if n.endswith(".dist-info/METADATA")]
        if len(metadata_names) != 1:
            raise ValueError("Wheel must contain one distribution METADATA")
        metadata = email.message_from_bytes(archive.read(metadata_names[0]))
        if metadata["Version"] != version:
            raise ValueError("Wheel version does not match the frozen candidate")
        wheel_payload = {
            name: hashlib.sha256(archive.read(name)).hexdigest()
            for name in names
            if name.startswith("structural_lib/") and not name.endswith("/")
        }
        forbidden = [n for n in names if n.startswith(FORBIDDEN_PREFIXES)]
    if forbidden:
        raise ValueError(f"Forbidden distribution payload: {forbidden[:5]}")
    if any(name not in wheel_payload for name in REQUIRED_RESOURCES):
        raise ValueError("Wheel is missing required typing, clause or template data")
    with tarfile.open(sdist, "r:gz") as archive:
        sdist_payload = {}
        sdist_metadata = []
        for member in archive.getmembers():
            relative = member.name.partition("/")[2]
            if relative.startswith(FORBIDDEN_PREFIXES):
                raise ValueError(f"Forbidden source distribution payload: {relative}")
            if not member.isfile():
                continue
            stream = archive.extractfile(member)
            if stream is None:
                raise ValueError(f"Unreadable sdist member: {member.name}")
            content = stream.read()
            if relative == "PKG-INFO":
                sdist_metadata.append(email.message_from_bytes(content)["Version"])
            if relative.startswith("structural_lib/"):
                sdist_payload[relative] = hashlib.sha256(content).hexdigest()
    if sdist_metadata != [version]:
        raise ValueError("Source distribution version does not match the candidate")
    if wheel_payload != sdist_payload:
        raise ValueError("Wheel and sdist package payloads differ")
    for name, digest in wheel_payload.items():
        source = repo / "Python" / name
        if not source.is_file() or sha256(source) != digest:
            raise ValueError(f"Distribution differs from frozen source: {name}")
    return {
        "wheel": {"path": str(wheel), "sha256": sha256(wheel)},
        "sdist": {"path": str(sdist), "sha256": sha256(sdist)},
        "version": version,
        "package_file_count": len(wheel_payload),
        "package_payload_sha256": _payload_digest(wheel_payload),
        "package_files": wheel_payload,
        "required_resources": list(REQUIRED_RESOURCES),
        "declared_extras": metadata.get_all("Provides-Extra", []),
    }


def _clean_env() -> dict[str, str]:
    removed = {"PYTHONPATH", "PYTHONHOME", "VIRTUAL_ENV", "PYTHONUSERBASE"}
    env = {key: value for key, value in os.environ.items() if key not in removed}
    env["PYTHONNOUSERSITE"] = "1"
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["MPLBACKEND"] = "Agg"
    return env


def _run(command: list[str], *, cwd: Path, env: dict[str, str]) -> str:
    result = subprocess.run(
        command, cwd=cwd, env=env, capture_output=True, text=True, timeout=900
    )
    if result.returncode:
        raise RuntimeError(
            f"Command failed ({result.returncode}): {' '.join(command)}\n"
            f"{result.stdout[-5000:]}\n{result.stderr[-5000:]}"
        )
    return result.stdout


def _client_requirements(repo: Path) -> list[str]:
    """Select only explicitly named application-client dependencies."""
    names = {
        "fastapi",
        "pydantic-settings",
        "pyjwt",
        "python-multipart",
        "httpx",
        "websockets",
    }
    result = []
    for raw in (repo / "requirements.txt").read_text().splitlines():
        line = raw.split("#", 1)[0].strip()
        name = re.split(r"[\[<>=!~; ]", line, maxsplit=1)[0].lower()
        if name in names:
            result.append(line)
    if len(result) != len(names):
        raise ValueError(
            "Explicit generated-client requirement inventory is incomplete"
        )
    return result


def qualify_artifacts(
    *,
    repo: Path,
    wheel: Path,
    sdist: Path,
    version: str,
    receipt: Path,
    profiles: list[str] | None = None,
) -> dict[str, Any]:
    """Qualify all declared profiles or refresh an explicitly selected subset."""
    repo, wheel, sdist, receipt = (p.resolve() for p in (repo, wheel, sdist, receipt))
    pair = inspect_distribution_pair(repo, wheel, sdist, version)
    project = tomllib.loads((repo / "Python/pyproject.toml").read_text())["project"]
    if project["version"] != version:
        raise ValueError("Source version does not match qualification version")
    extras = project["optional-dependencies"]
    if set(pair["declared_extras"]) != set(extras):
        raise ValueError("Wheel extra inventory differs from source metadata")
    required = ["base", "sdist", *extras, "exports", "transport", "baseline"]
    selected = required if profiles is None else profiles
    if (
        not selected
        or len(selected) != len(set(selected))
        or set(selected) - set(required)
    ):
        raise ValueError(f"Select unique qualification profiles from: {required}")
    receipt.parent.mkdir(parents=True, exist_ok=True)
    manifest = receipt.with_name("package-payload.json")
    manifest.write_text(
        json.dumps(pair["package_files"], sort_keys=True, indent=2) + "\n"
    )
    source_head = _run(["git", "rev-parse", "HEAD"], cwd=repo, env=_clean_env()).strip()
    python_tree = _run(
        ["git", "rev-parse", "HEAD:Python"], cwd=repo, env=_clean_env()
    ).strip()
    artifact_identity = {
        key: pair[key]
        for key in ("wheel", "sdist", "version", "package_payload_sha256")
    }
    records: dict[str, Any] = {}
    if receipt.exists() and profiles is not None:
        previous = json.loads(receipt.read_text())
        if previous["artifact_identity"] != artifact_identity:
            raise ValueError("Cannot combine evidence for different distribution bytes")
        records = previous["profiles"]
    evidence = {
        "schema_version": "s5-artifact-qualification/v1",
        "artifact_identity": artifact_identity,
        "source_head": source_head,
        "frozen_python_tree": python_tree,
        "source_build_inputs": {
            str(p.relative_to(repo)): sha256(p)
            for p in (
                repo / "Python/pyproject.toml",
                repo / "Python/MANIFEST.in",
                repo / "Python/README.md",
                repo / "Python/LICENSE",
            )
        },
        "package_file_count": pair["package_file_count"],
        "package_manifest": str(manifest),
        "required_profiles": required,
        "profiles": records,
        "declared_extras": extras,
        "generated_client_requirements": _client_requirements(repo),
        "performance_budgets": PERFORMANCE_BUDGETS,
        "verification_inputs_sha256": {
            str(path.relative_to(repo)): sha256(path)
            for path in (
                Path(__file__),
                PROBE,
                repo / "scripts/verify_lib_pro_013_f0_family_artifact.py",
                repo / "scripts/verify_lib_pro_012_s0_artifact.py",
                repo / "scripts/verify_canonical_transport_artifact.py",
                repo / "Python/tests/data/benchmark_vectors/family_review_inputs.json",
                repo
                / "Python/tests/data/benchmark_vectors/family_review_reference.json",
                repo / "Python/examples/complete_member_workflow.py",
                repo / "scripts/dxf_render.py",
            )
        },
        "limits": [
            "cad dependency availability is not an implemented library CAD export",
            "etabs dependency markers are not installed native-host acceptance",
            "pmm remains experimental; source/native/professional HOLDs remain explicit",
        ],
    }

    def save() -> None:
        passed = {name for name, value in records.items() if value["status"] == "PASS"}
        evidence["status"] = (
            "FAIL"
            if any(value["status"] == "FAIL" for value in records.values())
            else "PASS" if passed == set(required) else "PARTIAL"
        )
        receipt.write_text(json.dumps(evidence, indent=2, allow_nan=False) + "\n")

    env = _clean_env()
    for profile in selected:
        started = time.perf_counter()
        output = receipt.parent / "installed-outputs" / profile
        output.mkdir(parents=True, exist_ok=True)
        try:
            with tempfile.TemporaryDirectory(prefix=f"s5_{profile}_") as raw:
                scratch = Path(raw)
                venv = scratch / "venv"
                _run([sys.executable, "-m", "venv", str(venv)], cwd=scratch, env=env)
                python = venv / (
                    "Scripts/python.exe" if os.name == "nt" else "bin/python"
                )
                target = str(sdist) if profile == "sdist" else str(wheel)
                if profile in extras:
                    target += f"[{profile}]"
                if profile == "exports":
                    target += "[dxf,render,report,pdf,validation]"
                if profile == "baseline":
                    target = "structural-lib-is456==0.25.0"
                dependencies = (
                    evidence["generated_client_requirements"]
                    if profile == "transport"
                    else []
                )
                pip_report = output / "installation.json"
                _run(
                    [
                        str(python),
                        "-m",
                        "pip",
                        "install",
                        "--disable-pip-version-check",
                        "--report",
                        str(pip_report),
                        target,
                        *dependencies,
                    ],
                    cwd=scratch,
                    env=env,
                )
                _run([str(python), "-m", "pip", "check"], cwd=scratch, env=env)
                config = {
                    "repo": str(repo),
                    "wheel": str(wheel),
                    "profile": profile,
                    "version": "0.25.0" if profile == "baseline" else version,
                    "venv": str(venv),
                    "output": str(output),
                    "package_files": (
                        {} if profile == "baseline" else pair["package_files"]
                    ),
                    "budgets": PERFORMANCE_BUDGETS,
                }
                config_path = scratch / "probe.json"
                config_path.write_text(json.dumps(config))
                stdout = _run(
                    [str(python), "-I", str(PROBE), str(config_path)],
                    cwd=scratch,
                    env=env,
                )
                result = json.loads(
                    next(
                        line.removeprefix("S5_RESULT=")
                        for line in reversed(stdout.splitlines())
                        if line.startswith("S5_RESULT=")
                    )
                )
                installed = json.loads(pip_report.read_text())["install"]
                result["installed_distributions"] = [
                    {
                        "name": item["metadata"]["name"],
                        "version": item["metadata"]["version"],
                        "archive_hashes": item.get("download_info", {})
                        .get("archive_info", {})
                        .get("hashes", {}),
                    }
                    for item in installed
                ]
                records[profile] = {
                    "status": "PASS",
                    "elapsed_seconds": time.perf_counter() - started,
                    "source_head_at_execution": source_head,
                    "frozen_python_tree": python_tree,
                    "verification_inputs_sha256": evidence[
                        "verification_inputs_sha256"
                    ],
                    **result,
                }
        except (OSError, RuntimeError, ValueError, subprocess.TimeoutExpired) as exc:
            records[profile] = {
                "status": "FAIL",
                "error": str(exc),
                "elapsed_seconds": time.perf_counter() - started,
            }
        save()
        print(f"S5 profile {profile}: {records[profile]['status']}", flush=True)
    if (
        "base" in records
        and "baseline" in records
        and all(records[p]["status"] == "PASS" for p in ("base", "baseline"))
    ):
        comparisons = {}
        for case in ("beam", "batch100"):
            baseline = records["baseline"]["performance"][case]["median_ms"]
            current = records["base"]["performance"][case]["median_ms"]
            ratio = current / baseline
            comparisons[case] = {
                "median_ratio": ratio,
                "limit": PERFORMANCE_BUDGETS["median_regression_factor"],
                "passed": ratio <= PERFORMANCE_BUDGETS["median_regression_factor"],
            }
        evidence["performance_comparison"] = comparisons
        if not all(c["passed"] for c in comparisons.values()):
            evidence["status"] = "FAIL"
            receipt.write_text(json.dumps(evidence, indent=2, allow_nan=False) + "\n")
    save_status = evidence["status"]
    receipt.write_text(json.dumps(evidence, indent=2, allow_nan=False) + "\n")
    if any(records[p]["status"] != "PASS" for p in selected) or save_status == "FAIL":
        raise RuntimeError(
            f"Artifact qualification has failed profiles; inspect {receipt}"
        )
    return evidence

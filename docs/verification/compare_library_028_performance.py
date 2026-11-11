#!/usr/bin/env python3
"""Compare frozen ordinary and T-member examples across two installed wheels.

This is an S4 measurement harness, not a performance gate.  It requires exact
installed-wheel identity, copies the two public drivers into neutral temporary
directories, checks their calculation and exported-artifact equality outside
the timers, then collects alternating paired timings.  Any outcome mismatch is
an error; a timing ratio is recorded but never treated as a pass/fail budget.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import statistics
import subprocess
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

BASELINE_WHEEL_SHA256 = (
    "205acfde8500909aaf766e9cf263fc13bf76bfa680376527e29048b954cd2ea6"
)
BASELINE_VERSION = "0.27.0"
CANDIDATE_VERSION = "0.28.0"
DRIVERS = ("complete_member_workflow.py", "t_beam_member.py")


@dataclass(frozen=True)
class Installation:
    label: str
    python: Path
    wheel: Path
    version: str
    wheel_sha256: str
    package_payload_sha256: str
    installed: dict[str, Any]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _json_command(command: list[str], *, cwd: Path | None = None) -> dict[str, Any]:
    completed = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
    if completed.returncode:
        raise RuntimeError(
            f"Child failed ({completed.returncode}): {' '.join(command[:3])}\n"
            f"stdout: {completed.stdout[-1000:]}\nstderr: {completed.stderr[-3000:]}"
        )
    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"Non-JSON child output: {completed.stdout[-1000:]}"
        ) from exc


def _wheel_payload(wheel: Path) -> tuple[str, str, dict[str, str]]:
    """Return metadata version, payload digest and member hashes for one wheel."""
    with zipfile.ZipFile(wheel) as archive:
        metadata = [n for n in archive.namelist() if n.endswith(".dist-info/METADATA")]
        if len(metadata) != 1:
            raise ValueError(f"Expected one METADATA file in {wheel}")
        version = next(
            line.partition(":")[2].strip()
            for line in archive.read(metadata[0]).decode("utf-8").splitlines()
            if line.startswith("Version:")
        )
        payload = {
            name: hashlib.sha256(archive.read(name)).hexdigest()
            for name in archive.namelist()
            if name.startswith("structural_lib/") and not name.endswith("/")
        }
    digest = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return version, digest, payload


_IDENTITY_CHILD = r"""
import hashlib, importlib.metadata, json, pathlib, subprocess, sys
import structural_lib
prefix = pathlib.Path(sys.prefix).resolve()
origin = pathlib.Path(structural_lib.__file__).resolve()
if not origin.is_relative_to(prefix):
    raise RuntimeError(f"foreign structural_lib import: {origin}")
files = {}
for path in sorted(origin.parent.rglob("*")):
    if path.is_file() and "__pycache__" not in path.parts:
        files["structural_lib/" + str(path.relative_to(origin.parent))] = hashlib.sha256(path.read_bytes()).hexdigest()
payload_sha256 = hashlib.sha256(json.dumps(files, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
dist = importlib.metadata.distribution("structural-lib-is456")
direct = dist.locate_file("structural_lib_is456-" + dist.version + ".dist-info/direct_url.json")
direct_data = json.loads(direct.read_text()) if direct.is_file() else None
freeze = subprocess.run([sys.executable, "-I", "-m", "pip", "freeze", "--all"], check=True, capture_output=True, text=True).stdout.splitlines()
print(json.dumps({"origin": str(origin), "version": dist.version, "prefix": str(prefix), "package_files": files, "package_payload_sha256": payload_sha256, "direct_url": direct_data, "dependencies": freeze}, sort_keys=True))
"""


_RUN_CHILD = r"""
import argparse
import hashlib
import json
import runpy
import tempfile
import time
from dataclasses import asdict, is_dataclass
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--driver", required=True)
parser.add_argument("--mode", choices=("check", "time"), required=True)
args = parser.parse_args()
scope = runpy.run_path(args.driver)
run_workflow, write_artifacts = scope["run_workflow"], scope["write_artifacts"]

def normal(value):
    if is_dataclass(value):
        return normal(asdict(value))
    if hasattr(value, "to_dict"):
        return normal(value.to_dict())
    if isinstance(value, dict):
        return {str(k): normal(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [normal(v) for v in value]
    if hasattr(value, "value"):
        return value.value
    return value

def artifact_hashes(directory):
    return {
        str(path.relative_to(directory)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(directory.rglob("*"))
        if path.is_file()
    }

def summary(workflow):
    results = getattr(workflow, "results", None)
    if not isinstance(results, dict):
        raise RuntimeError("driver workflow lacks result map")
    raw = {str(key): normal(value) for key, value in results.items()}
    canonical = json.dumps(raw, sort_keys=True, separators=(",", ":"), allow_nan=False)
    def collect(value, path=""):
        found = {}
        if isinstance(value, dict):
            for key, item in value.items():
                child = f"{path}.{key}" if path else key
                if key.endswith("_id") or key in {
                    "status", "engineering_status", "calculation_status", "intake_status"
                }:
                    found[child] = item
                found.update(collect(item, child))
        elif isinstance(value, list):
            for index, item in enumerate(value):
                found.update(collect(item, f"{path}[{index}]"))
        return found
    return {
        "canonical_sha256": hashlib.sha256(canonical.encode()).hexdigest(),
        "ids_and_statuses": collect(raw),
    }

if args.mode == "check":
    workflow = run_workflow()
    with tempfile.TemporaryDirectory(prefix="structlib-028-export-") as raw:
        target = Path(raw)
        write_artifacts(workflow, target)
        checked = {"summary": summary(workflow), "artifacts": artifact_hashes(target)}
    print(json.dumps(checked, sort_keys=True, allow_nan=False))
    raise SystemExit(0)

started = time.perf_counter()
workflow = run_workflow()
workflow_ms = (time.perf_counter() - started) * 1000
workflow_summary = summary(workflow)
with tempfile.TemporaryDirectory(prefix="structlib-028-export-") as raw:
    target = Path(raw)
    started = time.perf_counter()
    write_artifacts(workflow, target)
    export_ms = (time.perf_counter() - started) * 1000
    artifacts = artifact_hashes(target)
print(json.dumps({"workflow_ms": workflow_ms, "export_ms": export_ms, "summary": workflow_summary, "artifacts": artifacts}, sort_keys=True, allow_nan=False))
"""


def _installation(
    label: str, python: Path, wheel: Path, expected_version: str
) -> Installation:
    if not python.is_file() or not wheel.is_file():
        raise ValueError(f"{label} interpreter or wheel is missing")
    wheel_hash = _sha256(wheel)
    if label == "baseline" and wheel_hash != BASELINE_WHEEL_SHA256:
        raise ValueError("Baseline wheel does not match verified public v0.27 SHA-256")
    wheel_version, wheel_payload_digest, wheel_payload = _wheel_payload(wheel)
    if wheel_version != expected_version:
        raise ValueError(
            f"{label} wheel version {wheel_version}, expected {expected_version}"
        )
    installed = _json_command([str(python), "-I", "-c", _IDENTITY_CHILD])
    if installed["version"] != expected_version:
        raise ValueError(f"{label} installed version does not match wheel")
    if installed["package_files"] != wheel_payload:
        raise ValueError(
            f"{label} installed package payload does not match selected wheel"
        )
    direct = installed["direct_url"]
    if direct is not None:
        recorded = direct.get("archive_info", {}).get("hash", "")
        if recorded and recorded != f"sha256={wheel_hash}":
            raise ValueError(
                f"{label} direct_url wheel hash differs from selected wheel"
            )
    return Installation(
        label,
        python,
        wheel,
        expected_version,
        wheel_hash,
        wheel_payload_digest,
        installed,
    )


def _copy_drivers(repo: Path, target: Path) -> dict[str, str]:
    copied: dict[str, str] = {}
    for name in DRIVERS:
        source = repo / "Python/examples" / name
        destination = target / name
        shutil.copyfile(source, destination)
        copied[name] = _sha256(destination)
    return copied


def _non_project_dependencies(installation: Installation) -> list[str]:
    """Return the exact frozen dependency inventory, excluding the compared wheel."""
    return sorted(
        line
        for line in installation.installed["dependencies"]
        if not line.lower().startswith("structural-lib-is456")
    )


def _run_driver(installation: Installation, driver: Path, mode: str) -> dict[str, Any]:
    return _json_command(
        [
            str(installation.python),
            "-I",
            "-c",
            _RUN_CHILD,
            "--driver",
            str(driver),
            "--mode",
            mode,
        ],
        cwd=driver.parent,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-python", type=Path, required=True)
    parser.add_argument("--candidate-python", type=Path, required=True)
    parser.add_argument("--baseline-wheel", type=Path, required=True)
    parser.add_argument("--candidate-wheel", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--pairs", type=int, default=30)
    args = parser.parse_args()
    if args.pairs <= 0:
        raise ValueError("--pairs must be positive")

    repo = Path(__file__).resolve().parents[2]
    baseline = _installation(
        "baseline", args.baseline_python, args.baseline_wheel, BASELINE_VERSION
    )
    candidate = _installation(
        "candidate", args.candidate_python, args.candidate_wheel, CANDIDATE_VERSION
    )
    if _non_project_dependencies(baseline) != _non_project_dependencies(candidate):
        raise AssertionError("Baseline and candidate dependency inventories differ")
    with tempfile.TemporaryDirectory(prefix="structlib-028-drivers-") as raw:
        drivers = Path(raw)
        driver_hashes = _copy_drivers(repo, drivers)
        checks: dict[str, dict[str, dict[str, Any]]] = {}
        for name in DRIVERS:
            checks[name] = {
                "baseline": _run_driver(baseline, drivers / name, "check"),
                "candidate": _run_driver(candidate, drivers / name, "check"),
            }
            if checks[name]["baseline"] != checks[name]["candidate"]:
                raise AssertionError(
                    f"{name} canonical result IDs/statuses or artifact hashes differ"
                )

        samples: dict[str, dict[str, list[dict[str, Any]]]] = {
            name: {"baseline": [], "candidate": []} for name in DRIVERS
        }
        for pair in range(args.pairs):
            round_number = pair // 10 + 1
            installations = (
                (("baseline", baseline), ("candidate", candidate))
                if pair % 2 == 0
                else (("candidate", candidate), ("baseline", baseline))
            )
            for label, installation in installations:
                for name in DRIVERS:
                    data = _run_driver(installation, drivers / name, "time")
                    if (
                        data["summary"] != checks[name]["baseline"]["summary"]
                        or data["artifacts"] != checks[name]["baseline"]["artifacts"]
                    ):
                        raise AssertionError(
                            f"{label} {name} changed outcome during timing"
                        )
                    samples[name][label].append(
                        {
                            "pair": pair + 1,
                            "round": round_number,
                            "workflow_ms": data["workflow_ms"],
                            "export_ms": data["export_ms"],
                        }
                    )

    metrics = {}
    for name in DRIVERS:
        metrics[name] = {}
        for metric in ("workflow_ms", "export_ms"):
            left = [item[metric] for item in samples[name]["baseline"]]
            right = [item[metric] for item in samples[name]["candidate"]]
            base_median = statistics.median(left)
            candidate_median = statistics.median(right)
            metrics[name][metric] = {
                "baseline_median_ms": base_median,
                "candidate_median_ms": candidate_median,
                "candidate_over_baseline_ratio": candidate_median / base_median,
            }

    receipt = {
        "schema_version": "library-028-performance-comparison/v1",
        "status": "PASS",
        "pairs": args.pairs,
        "rounds": (args.pairs + 9) // 10,
        "order": "AB/BA alternation by pair; each interpreter/driver check runs once before fresh measured children",
        "installations": {
            item.label: {
                "python": str(item.python),
                "wheel": str(item.wheel),
                "wheel_sha256": item.wheel_sha256,
                "wheel_package_payload_sha256": item.package_payload_sha256,
                "installed": item.installed,
            }
            for item in (baseline, candidate)
        },
        "driver_sha256": driver_hashes,
        "matched_dependency_inventory": _non_project_dependencies(baseline),
        "checks": checks,
        "samples": samples,
        "metrics": metrics,
        "limitations": [
            "No performance threshold is applied.",
            "Equality is exact: no version-only fields are ignored; any such difference fails and must be explained outside this harness.",
            "Measurements are sequential local-host samples and do not establish general throughput, tail latency, or memory behavior.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(receipt, indent=2, sort_keys=True, allow_nan=False) + "\n"
    )
    print(
        json.dumps(
            {"status": "PASS", "receipt": str(args.output), "metrics": metrics},
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()

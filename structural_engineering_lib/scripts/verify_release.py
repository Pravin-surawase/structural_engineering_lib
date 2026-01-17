#!/usr/bin/env python3
"""
Release verification helper.

Creates a clean virtual environment, installs the package, and runs a small
smoke check to confirm version and CLI entrypoints.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path


def _bin_path(venv_dir: Path, name: str) -> Path:
    if os.name == "nt":
        return venv_dir / "Scripts" / f"{name}.exe"
    return venv_dir / "bin" / name


def _run(cmd: list[str], *, cwd: Path | None = None) -> None:
    print(f"+ {' '.join(cmd)}")
    subprocess.run(cmd, check=True, cwd=cwd)


def _find_wheel(wheel_dir: Path, version: str | None) -> Path:
    if version:
        pattern = f"structural_lib_is456-{version}*.whl"
    else:
        pattern = "structural_lib_is456-*.whl"
    wheels = sorted(wheel_dir.glob(pattern))
    if not wheels:
        raise FileNotFoundError(f"No wheel found in {wheel_dir} (pattern: {pattern})")
    return wheels[-1]


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify release in a clean venv")
    parser.add_argument("--version", help="Version to verify (e.g., 0.11.0)")
    parser.add_argument(
        "--source",
        choices=["wheel", "pypi"],
        default="wheel",
        help="Install source (default: wheel)",
    )
    parser.add_argument(
        "--wheel-dir",
        default="Python/dist",
        help="Directory containing built wheels (default: Python/dist)",
    )
    parser.add_argument(
        "--job",
        default="Python/examples/sample_job_is456.json",
        help="Job spec for CLI smoke test",
    )
    parser.add_argument(
        "--skip-cli",
        action="store_true",
        help="Skip CLI smoke checks (version check still runs)",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    wheel_dir = repo_root / args.wheel_dir
    job_path = repo_root / args.job

    with tempfile.TemporaryDirectory(prefix="verify_release_") as tmp:
        venv_dir = Path(tmp) / "venv"
        _run([sys.executable, "-m", "venv", str(venv_dir)])

        pip = _bin_path(venv_dir, "pip")
        python = _bin_path(venv_dir, "python")

        _run([str(pip), "install", "--upgrade", "pip"])

        if args.source == "wheel":
            wheel = _find_wheel(wheel_dir, args.version)
            _run([str(pip), "install", str(wheel)])
        else:
            if not args.version:
                print("error: --version is required when using --source pypi")
                return 2
            _run([str(pip), "install", f"structural-lib-is456=={args.version}"])

        _run(
            [
                str(python),
                "-c",
                "from structural_lib import api; print(api.get_library_version())",
            ]
        )

        if not args.skip_cli:
            if not job_path.exists():
                print(f"error: job file not found: {job_path}")
                return 2

            out_dir = Path(tmp) / "job_out"
            _run(
                [
                    str(python),
                    "-m",
                    "structural_lib",
                    "job",
                    str(job_path),
                    "-o",
                    str(out_dir),
                ]
            )
            _run(
                [
                    str(python),
                    "-m",
                    "structural_lib",
                    "critical",
                    str(out_dir),
                    "--top",
                    "1",
                    "--format",
                    "csv",
                ]
            )
            _run(
                [
                    str(python),
                    "-m",
                    "structural_lib",
                    "report",
                    str(out_dir),
                    "--format",
                    "html",
                    "-o",
                    str(out_dir / "report.html"),
                ]
            )

        print("Release verification OK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

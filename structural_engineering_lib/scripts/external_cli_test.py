"""External CLI smoke test (S-007).

Goal: a cold-start user can install and run the CLI end-to-end without help.

This script is designed to be:
- Copy/paste runnable (works from any folder)
- Deterministic and self-contained (writes its own sample inputs)
- Shareable (writes a single log file + a small output folder)

Typical usage (after installing the package):
    python external_cli_test.py

Repo usage (if running from this repository without installing the package):
    .venv/bin/python scripts/external_cli_test.py

The script will:
- Run `python -m structural_lib --help`
- Run a small `job` using an embedded sample job JSON
- Run `critical` (CSV)
- Run `report` (HTML + JSON)

Optional:
- Run `design` → `bbs` → `dxf` using an embedded sample CSV (enable --include-dxf)

Exit code:
- 0 if all required steps pass
- non-zero if any required step fails
"""

from __future__ import annotations

import argparse
import os
import platform
import shutil
import subprocess
import sys
import textwrap
import time
from dataclasses import dataclass
from pathlib import Path


SAMPLE_JOB_IS456_JSON = """{
  \"schema_version\": 1,
  \"job_id\": \"external_cli_test_job_001\",
  \"code\": \"IS456\",
  \"units\": \"IS456\",
  \"beam\": {
    \"b_mm\": 300.0,
    \"D_mm\": 500.0,
    \"d_mm\": 450.0,
    \"d_dash_mm\": 50.0,
    \"fck_nmm2\": 25.0,
    \"fy_nmm2\": 500.0,
    \"asv_mm2\": 100.0,
    \"pt_percent\": null
  },
  \"cases\": [
    {\"case_id\": \"DL+LL\", \"mu_knm\": 80.0, \"vu_kn\": 60.0},
    {\"case_id\": \"1.5(DL+LL)\", \"mu_knm\": 120.0, \"vu_kn\": 200.0},
    {\"case_id\": \"EQ-X\", \"mu_knm\": 160.0, \"vu_kn\": 120.0}
  ]
}
"""

SAMPLE_BEAM_DESIGN_CSV = """BeamID,Story,b,D,Span,Cover,fck,fy,Mu,Vu,Ast_req,Asc_req,Stirrup_Dia,Stirrup_Spacing,Status
B1,Story1,300,500,4000,40,25,500,150,100,942.5,0,8,150,OK
B2,Story1,300,450,3000,40,25,500,100,80,628.3,0,8,175,OK
B3,Story2,350,600,5000,40,30,500,250,150,1570.8,314.2,10,125,OK
B4,Story2,300,500,4500,40,25,500,180,120,1130.9,0,8,150,OK
B5,Ground,400,700,6000,50,30,500,400,200,2513.3,502.7,10,100,OK
"""


@dataclass(frozen=True)
class CmdResult:
    cmd: list[str]
    returncode: int
    seconds: float
    stdout: str
    stderr: str


def _repo_root_from_script() -> Path | None:
    # If this script is run from the repo, it lives in <repo>/scripts/external_cli_test.py
    p = Path(__file__).resolve()
    if p.parent.name != "scripts":
        return None
    repo = p.parent.parent
    if (repo / "Python" / "structural_lib").exists():
        return repo
    return None


def _subprocess_env(repo_root: Path | None) -> dict[str, str]:
    env = dict(os.environ)
    if repo_root is None:
        return env

    python_dir = repo_root / "Python"
    # Make `python -m structural_lib` work even if the package isn't installed.
    if python_dir.exists():
        old = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = (
            str(python_dir) if not old else f"{python_dir}{os.pathsep}{old}"
        )
    return env


def _run(cmd: list[str], cwd: Path, env: dict[str, str], timeout_s: int) -> CmdResult:
    start = time.perf_counter()
    p = subprocess.run(
        cmd,
        cwd=str(cwd),
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout_s,
    )
    seconds = time.perf_counter() - start
    return CmdResult(
        cmd=cmd,
        returncode=p.returncode,
        seconds=seconds,
        stdout=p.stdout,
        stderr=p.stderr,
    )


def _write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _log_block(f, title: str, body: str) -> None:
    f.write("\n" + "=" * 78 + "\n")
    f.write(title.strip() + "\n")
    f.write("-" * 78 + "\n")
    f.write(body.rstrip() + "\n")


def _format_cmd_result(r: CmdResult) -> str:
    cmd_str = " ".join(r.cmd)
    return (
        textwrap.dedent(
            f"""
        $ {cmd_str}
        returncode: {r.returncode}
        seconds: {r.seconds:.3f}

        --- stdout ---
        {r.stdout.rstrip()}

        --- stderr ---
        {r.stderr.rstrip()}
        """
        ).strip()
        + "\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="external_cli_test.py",
        description="External CLI smoke test (S-007): job → critical → report with logging.",
    )
    parser.add_argument(
        "--workdir",
        default="external_cli_test_run",
        help="Folder to write inputs/outputs/logs (default: external_cli_test_run)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=120,
        help="Per-command timeout in seconds (default: 120)",
    )
    parser.add_argument(
        "--include-dxf",
        action="store_true",
        help="Also run design → bbs → dxf (requires optional DXF deps).",
    )
    args = parser.parse_args()

    repo_root = _repo_root_from_script()
    env = _subprocess_env(repo_root)

    workdir = Path(args.workdir).resolve()
    if workdir.exists():
        shutil.rmtree(workdir)
    workdir.mkdir(parents=True, exist_ok=True)

    inputs_dir = workdir / "inputs"
    outputs_dir = workdir / "outputs"
    outputs_dir.mkdir(parents=True, exist_ok=True)

    job_json_path = inputs_dir / "sample_job_is456.json"
    design_csv_path = inputs_dir / "sample_beam_design.csv"

    _write_file(job_json_path, SAMPLE_JOB_IS456_JSON)
    _write_file(design_csv_path, SAMPLE_BEAM_DESIGN_CSV)

    log_path = workdir / "external_cli_test.log"

    required_steps: list[tuple[str, list[str]]] = [
        ("CLI help", [sys.executable, "-m", "structural_lib", "--help"]),
        (
            "Library version",
            [
                sys.executable,
                "-c",
                "from structural_lib import api; print(api.get_library_version())",
            ],
        ),
        (
            "Run job",
            [
                sys.executable,
                "-m",
                "structural_lib",
                "job",
                str(job_json_path),
                "-o",
                str(outputs_dir / "job_out"),
            ],
        ),
        (
            "Critical set (CSV)",
            [
                sys.executable,
                "-m",
                "structural_lib",
                "critical",
                str(outputs_dir / "job_out"),
                "--top",
                "5",
                "--format=csv",
                "-o",
                str(outputs_dir / "critical.csv"),
            ],
        ),
        (
            "Report (HTML)",
            [
                sys.executable,
                "-m",
                "structural_lib",
                "report",
                str(outputs_dir / "job_out"),
                "--format=html",
                "-o",
                str(outputs_dir / "report.html"),
            ],
        ),
        (
            "Report (JSON)",
            [
                sys.executable,
                "-m",
                "structural_lib",
                "report",
                str(outputs_dir / "job_out"),
                "--format=json",
                "-o",
                str(outputs_dir / "report.json"),
            ],
        ),
    ]

    optional_steps: list[tuple[str, list[str]]] = []
    if args.include_dxf:
        optional_steps.extend(
            [
                (
                    "Design (CSV)",
                    [
                        sys.executable,
                        "-m",
                        "structural_lib",
                        "design",
                        str(design_csv_path),
                        "-o",
                        str(outputs_dir / "results.json"),
                    ],
                ),
                (
                    "BBS",
                    [
                        sys.executable,
                        "-m",
                        "structural_lib",
                        "bbs",
                        str(outputs_dir / "results.json"),
                        "-o",
                        str(outputs_dir / "schedule.csv"),
                    ],
                ),
                (
                    "DXF",
                    [
                        sys.executable,
                        "-m",
                        "structural_lib",
                        "dxf",
                        str(outputs_dir / "results.json"),
                        "-o",
                        str(outputs_dir / "drawings.dxf"),
                    ],
                ),
            ]
        )

    header = (
        textwrap.dedent(
            f"""
        External CLI Test (S-007)

        Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}
        Platform:  {platform.platform()}
        Python:    {sys.version.replace(os.linesep, ' ')}
        Executable:{sys.executable}
        Workdir:   {workdir}

        Notes:
        - Required steps: {len(required_steps)}
        - Optional steps: {len(optional_steps)}
        - Repo mode: {'yes' if repo_root else 'no'}
        """
        ).strip()
        + "\n"
    )

    with log_path.open("w", encoding="utf-8") as f:
        f.write(header)

        failed_required = False

        for title, cmd in required_steps:
            try:
                r = _run(cmd, cwd=workdir, env=env, timeout_s=args.timeout)
            except subprocess.TimeoutExpired:
                _log_block(
                    f,
                    f"REQUIRED: {title}",
                    f"TIMEOUT after {args.timeout}s\n$ {' '.join(cmd)}\n",
                )
                failed_required = True
                continue

            _log_block(f, f"REQUIRED: {title}", _format_cmd_result(r))
            if r.returncode != 0:
                failed_required = True

        for title, cmd in optional_steps:
            try:
                r = _run(cmd, cwd=workdir, env=env, timeout_s=args.timeout)
            except subprocess.TimeoutExpired:
                _log_block(
                    f,
                    f"OPTIONAL: {title}",
                    f"TIMEOUT after {args.timeout}s\n$ {' '.join(cmd)}\n",
                )
                continue

            _log_block(f, f"OPTIONAL: {title}", _format_cmd_result(r))

        _log_block(
            f,
            "OUTPUTS",
            "\n".join(
                [
                    f"log: {log_path}",
                    f"inputs/: {inputs_dir}",
                    f"outputs/: {outputs_dir}",
                ]
            )
            + "\n",
        )

    # Minimal console summary
    print(f"Log written: {log_path}")
    if failed_required:
        print("RESULT: FAIL (one or more required steps failed)")
        return 2

    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

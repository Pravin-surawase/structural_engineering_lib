"""job_cli

Tiny CLI wrapper for the job runner.

Usage:
  python -m structural_lib.job_cli run --job path/to/job.json --out ./output/job_001
"""

from __future__ import annotations

import argparse

from . import job_runner


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Run a structural_lib job")
    sub = p.add_subparsers(dest="cmd", required=True)

    run = sub.add_parser("run", help="Run a job.json and write outputs")
    run.add_argument("--job", required=True, help="Path to job.json")
    run.add_argument("--out", required=True, help="Output directory")

    return p


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    if args.cmd == "run":
        job_runner.run_job(job_path=args.job, out_dir=args.out)
        return 0

    raise AssertionError("unreachable")


if __name__ == "__main__":
    raise SystemExit(main())

"""Generate synthetic beam inputs and run the full CLI pipeline.

This script samples three authored single-layer beam cases into a CSV, then runs:
  - design -> results.json
  - bbs -> schedule.csv
  - dxf -> drawings.dxf (optional, requires ezdxf)

Usage (from Python/):
  python examples/full_pipeline_synthetic.py --count 500 --output-dir ./output/demo_500
  python examples/full_pipeline_synthetic.py --count 50 --skip-dxf
"""

from __future__ import annotations

import argparse
import csv
import random
import subprocess
import sys
from pathlib import Path

FIELDNAMES = [
    "BeamID",
    "Story",
    "b",
    "D",
    "eff_d",
    "Span",
    "Cover",
    "fck",
    "fy",
    "Mu",
    "Vu",
    "Stirrup_Dia",
    "Stirrup_Spacing",
]


def _generate_rows(count: int, seed: int) -> list[dict]:
    rng = random.Random(seed)
    stories = ["G", "L1", "L2", "L3", "L4", "L5"]
    spans = [3000, 3500, 4000, 4500, 5000, 5500]
    # These demands select single-layer 16 mm tension bars in the maintained
    # generator. Arbitrary random demands can select other sizes or multiple
    # layers, so they cannot reuse a guessed 16 mm centroid for a BBS example.
    cases = [(450, 100), (500, 150), (550, 150)]
    cover = 40
    stirrup_dia = 8
    main_bar_dia = 16
    rows: list[dict] = []
    for idx in range(count):
        D, mu = rng.choice(cases)
        rows.append(
            {
                "BeamID": f"B{idx + 1:04d}",
                "Story": stories[idx % len(stories)],
                "b": 300,
                "D": D,
                "eff_d": D - cover - stirrup_dia - main_bar_dia / 2,
                "Span": rng.choice(spans),
                "Cover": cover,
                "fck": 25,
                "fy": 500,
                "Mu": mu,
                "Vu": 80,
                "Stirrup_Dia": stirrup_dia,
                "Stirrup_Spacing": 150,
            }
        )
    return rows


def _write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def _run_cmd(label: str, cmd: list[str]) -> bool:
    print(f"\n[{label}] {' '.join(cmd)}")
    result = subprocess.run(cmd, check=False)
    if result.returncode != 0:
        print(f"{label} failed with exit code {result.returncode}.")
        return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate synthetic beams and run full CLI pipeline."
    )
    parser.add_argument("--count", type=int, default=50, help="Number of beams.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed.")
    parser.add_argument(
        "--output-dir",
        default="output/synthetic_demo",
        help="Output folder for CSV/results/BBS/DXF.",
    )
    parser.add_argument(
        "--skip-dxf",
        action="store_true",
        help="Skip DXF generation (faster, no ezdxf required).",
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    csv_path = output_dir / f"beams_synthetic_{args.count}.csv"
    results_path = output_dir / "results.json"
    bbs_path = output_dir / "schedule.csv"
    dxf_path = output_dir / "drawings.dxf"

    rows = _generate_rows(args.count, args.seed)
    _write_csv(csv_path, rows)
    print(f"Wrote CSV: {csv_path}")

    python = sys.executable
    if not _run_cmd(
        "design",
        [
            python,
            "-m",
            "structural_lib",
            "design",
            str(csv_path),
            "-o",
            str(results_path),
            "--deflection",
        ],
    ):
        return 1

    if not _run_cmd(
        "bbs",
        [python, "-m", "structural_lib", "bbs", str(results_path), "-o", str(bbs_path)],
    ):
        return 1

    if args.skip_dxf:
        print("\n[skip] DXF generation disabled.")
        return 0

    if not _run_cmd(
        "dxf",
        [python, "-m", "structural_lib", "dxf", str(results_path), "-o", str(dxf_path)],
    ):
        print("DXF step failed. Install ezdxf with: pip install ezdxf")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

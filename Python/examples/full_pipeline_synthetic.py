"""Generate synthetic beam inputs and run the full CLI pipeline.

This script creates a CSV with realistic beam data, then runs:
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
import math
import random
import subprocess
import sys
from pathlib import Path

from structural_lib import flexure, shear, tables


FIELDNAMES = [
    "BeamID",
    "Story",
    "b",
    "D",
    "Span",
    "Cover",
    "fck",
    "fy",
    "Mu",
    "Vu",
    "Ast_req",
    "Asc_req",
    "Stirrup_Dia",
    "Stirrup_Spacing",
]


def _round_to_step(value: float, step: int) -> int:
    return int(round(value / step) * step)


def _generate_rows(count: int, seed: int) -> list[dict]:
    rng = random.Random(seed)

    stories = ["G", "L1", "L2", "L3", "L4", "L5"]
    widths = [230, 250, 300, 350]
    depths = [450, 500, 550, 600]
    spans = [3000, 3500, 4000, 4500, 5000, 5500]
    covers = [30, 40, 50]
    fcks = [20, 25, 30, 35]
    fys = [415, 500]
    stirrup_dias = [8, 10]

    rows: list[dict] = []
    main_bar_dia = 16.0

    for idx in range(count):
        beam_id = f"B{idx + 1:04d}"
        story = stories[idx % len(stories)]

        b = rng.choice(widths)
        D = rng.choice(depths)
        span = rng.choice(spans)
        cover = rng.choice(covers)
        fck = rng.choice(fcks)
        fy = rng.choice(fys)
        stirrup_dia = rng.choice(stirrup_dias)

        d = D - cover - stirrup_dia - main_bar_dia / 2
        if d <= 0:
            d = D * 0.85

        probe = flexure.design_singly_reinforced(
            b=b, d=d, d_total=D, mu_knm=1.0, fck=fck, fy=fy
        )
        mu_lim = probe.mu_lim if probe.mu_lim > 0 else 150.0
        mu = mu_lim * rng.uniform(0.45, 0.7)
        mu = max(mu, 20.0)

        flex = flexure.design_singly_reinforced(
            b=b, d=d, d_total=D, mu_knm=mu, fck=fck, fy=fy
        )
        if not flex.is_safe and mu_lim > 0:
            mu = mu_lim * 0.5
            flex = flexure.design_singly_reinforced(
                b=b, d=d, d_total=D, mu_knm=mu, fck=fck, fy=fy
            )

        tc_max = tables.get_tc_max_value(fck)
        vu_cap = 0.7 * tc_max * b * d / 1000.0
        span_m = span / 1000.0
        vu_from_mu = (4.0 * mu) / span_m
        vu = min(vu_from_mu, vu_cap)
        vu = max(vu, 20.0)

        asv = 2.0 * math.pi * (stirrup_dia / 2) ** 2
        pt = max(flex.pt_provided, 0.2)
        shear_res = shear.design_shear(
            vu_kn=vu, b=b, d=d, fck=fck, fy=fy, asv=asv, pt=pt
        )

        spacing = _round_to_step(shear_res.spacing, 25)
        if spacing <= 0:
            spacing = 150

        rows.append(
            {
                "BeamID": beam_id,
                "Story": story,
                "b": round(b, 1),
                "D": round(D, 1),
                "Span": round(span, 1),
                "Cover": round(cover, 1),
                "fck": round(fck, 1),
                "fy": round(fy, 1),
                "Mu": round(mu, 2),
                "Vu": round(vu, 2),
                "Ast_req": round(flex.ast_required, 2),
                "Asc_req": 0.0,
                "Stirrup_Dia": round(stirrup_dia, 1),
                "Stirrup_Spacing": round(spacing, 1),
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

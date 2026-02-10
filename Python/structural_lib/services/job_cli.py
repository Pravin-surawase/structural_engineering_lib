# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""job_cli

Tiny CLI wrapper for the job runner and cost optimization.

Usage:
  python -m structural_lib.job_cli run --job path/to/job.json --out ./output/job_001
  python -m structural_lib.job_cli optimize --span 5000 --mu 120 --vu 80
"""

from __future__ import annotations

import argparse
import json

from . import api, beam_pipeline, job_runner


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Run a structural_lib job or optimize beam cost"
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    run = sub.add_parser("run", help="Run a job.json and write outputs")
    run.add_argument("--job", required=True, help="Path to job.json")
    run.add_argument("--out", required=True, help="Output directory")

    optimize = sub.add_parser("optimize", help="Find cost-optimal beam design")
    optimize.add_argument("--span", type=float, required=True, help="Beam span (mm)")
    optimize.add_argument(
        "--mu", type=float, required=True, help="Factored moment (kNm)"
    )
    optimize.add_argument("--vu", type=float, required=True, help="Factored shear (kN)")
    optimize.add_argument(
        "--cover", type=int, default=40, help="Concrete cover (mm, default: 40)"
    )
    optimize.add_argument("--output", "-o", help="Output JSON file (optional)")
    optimize.add_argument(
        "--units", default="IS456", help="Units system (default: IS456)"
    )

    suggest = sub.add_parser("suggest", help="Get design improvement suggestions")
    suggest.add_argument("--span", type=float, required=True, help="Beam span (mm)")
    suggest.add_argument(
        "--mu", type=float, required=True, help="Factored moment (kNm)"
    )
    suggest.add_argument("--vu", type=float, required=True, help="Factored shear (kN)")
    suggest.add_argument("--b", type=float, required=True, help="Beam width (mm)")
    suggest.add_argument("--D", type=float, required=True, help="Overall depth (mm)")
    suggest.add_argument("--d", type=float, required=True, help="Effective depth (mm)")
    suggest.add_argument(
        "--fck", type=float, default=25, help="Concrete grade (N/mm², default: 25)"
    )
    suggest.add_argument(
        "--fy", type=float, default=500, help="Steel grade (N/mm², default: 500)"
    )
    suggest.add_argument(
        "--cover", type=int, default=40, help="Concrete cover (mm, default: 40)"
    )
    suggest.add_argument("--output", "-o", help="Output JSON file (optional)")
    suggest.add_argument(
        "--units", default="IS456", help="Units system (default: IS456)"
    )

    return p


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    if args.cmd == "run":
        job_runner.run_job(job_path=args.job, out_dir=args.out)
        return 0

    if args.cmd == "optimize":
        result = api.optimize_beam_cost(
            units=args.units,
            span_mm=args.span,
            mu_knm=args.mu,
            vu_kn=args.vu,
            cover_mm=args.cover,
        )

        # Print results to console
        opt = result.optimal_design
        cost = opt.cost_breakdown
        print("\n" + "=" * 60)
        print("COST OPTIMIZATION RESULT")
        print("=" * 60)
        print("\n✅ Optimal Design:")
        print(f"   Dimensions: {opt.b_mm}mm × {opt.D_mm}mm (d = {opt.d_mm}mm)")
        print(f"   Materials:  M{opt.fck_nmm2} concrete, Fe{opt.fy_nmm2} steel")
        print(f"\n💰 Cost Breakdown ({cost.currency}):")
        print(f"   Concrete:  {cost.concrete_cost:>10,.2f}")
        print(f"   Steel:     {cost.steel_cost:>10,.2f}")
        print(f"   Formwork:  {cost.formwork_cost:>10,.2f}")
        print(f"   Labor:     {cost.labor_adjustment:>10,.2f}")
        print(f"   {'-' * 25}")
        print(f"   TOTAL:     {cost.total_cost:>10,.2f}")
        print("\n📊 Savings vs Conservative Design:")
        print(f"   Baseline cost: {result.baseline_cost:>10,.2f}")
        print(
            f"   Savings:       {result.savings_amount:>10,.2f} ({result.savings_percent:.1f}%)"
        )

        if result.alternatives:
            print("\n📋 Alternative Designs (next 3 cheapest):")
            for i, alt in enumerate(result.alternatives, 1):
                if alt and alt.cost_breakdown:
                    alt_cost = alt.cost_breakdown
                    print(
                        f"   {i}. {alt.b_mm}×{alt.D_mm}mm, M{alt.fck_nmm2}, Fe{alt.fy_nmm2} → "
                        f"{alt_cost.currency}{alt_cost.total_cost:,.2f}"
                    )

        print("\n⚙️  Metadata:")
        print(
            f"   Evaluated {result.candidates_evaluated} combinations, {result.candidates_valid} valid"
        )
        print(f"   Computation time: {result.computation_time_sec:.3f}s")
        print("=" * 60 + "\n")

        # Save to JSON if requested
        if args.output:
            with open(args.output, "w") as f:
                json.dump(result.to_dict(), f, indent=2)
            print(f"✅ Results saved to {args.output}")

        return 0

    if args.cmd == "suggest":
        # Design the beam first using design_single_beam
        design = beam_pipeline.design_single_beam(
            units=args.units,
            beam_id="CLI-BEAM",
            story="CLI",
            b_mm=args.b,
            D_mm=args.D,
            d_mm=args.d,
            cover_mm=args.cover,
            span_mm=args.span,
            mu_knm=args.mu,
            vu_kn=args.vu,
            fck_nmm2=args.fck,
            fy_nmm2=args.fy,
        )

        # Get suggestions
        suggestions = api.suggest_beam_design_improvements(
            units=args.units,
            design=design,
            span_mm=args.span,
            mu_knm=args.mu,
            vu_kn=args.vu,
        )

        # Print results to console
        print("\n" + "=" * 70)
        print("DESIGN IMPROVEMENT SUGGESTIONS")
        print("=" * 70)
        print("\n📊 Analysis Summary:")
        print(f"   Total suggestions: {suggestions.total_count}")
        print(f"   High impact:       {suggestions.high_impact_count}")
        print(f"   Medium impact:     {suggestions.medium_impact_count}")
        print(f"   Low impact:        {suggestions.low_impact_count}")
        print(f"   Analysis time:     {suggestions.analysis_time_ms:.1f}ms")

        if suggestions.suggestions:
            print("\n💡 Top Recommendations:\n")
            for i, sug in enumerate(suggestions.suggestions[:5], 1):  # Top 5
                impact_key = sug.impact.lower()
                icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}[impact_key]
                print(f"{i}. {icon} {sug.title}")
                print(
                    f"   Category: {sug.category} | Impact: {sug.impact} | Confidence: {sug.confidence:.0%}"
                )
                print(f"   {sug.rationale}")
                if sug.estimated_benefit:
                    print(f"   💰 {sug.estimated_benefit}")
                if sug.action_steps:
                    print("   Actions:")
                    for step in sug.action_steps[:2]:  # First 2 steps
                        print(f"      • {step}")
                print()

        print("=" * 70 + "\n")

        # Save to JSON if requested
        if args.output:
            with open(args.output, "w") as f:
                json.dump(suggestions.to_dict(), f, indent=2)
            print(f"✅ Full report saved to {args.output}")

        return 0

    raise AssertionError("unreachable")


if __name__ == "__main__":
    raise SystemExit(main())

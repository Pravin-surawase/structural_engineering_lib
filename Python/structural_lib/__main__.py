"""
Unified CLI entrypoint for structural_lib.

Usage:
    python -m structural_lib design input.csv -o results.json
    python -m structural_lib bbs results.json -o bbs.csv
    python -m structural_lib dxf results.json -o drawings.dxf
    python -m structural_lib job job.json -o output/

This module provides a unified command-line interface with subcommands
for beam design, bar bending schedules, DXF generation, and job processing.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List

from . import api
from . import bbs
from . import detailing
from . import dxf_export
from . import excel_integration
from . import job_runner


def cmd_design(args: argparse.Namespace) -> int:
    """
    Run beam design from CSV/JSON input file.

    Reads beam parameters from CSV or JSON, performs IS456 design calculations,
    and outputs design results in JSON format.
    """
    input_path = Path(args.input)

    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        return 1

    try:
        # Load beam data
        print(f"Loading beam data from {input_path}...", file=sys.stderr)

        if input_path.suffix.lower() == ".csv":
            beams = excel_integration.load_beam_data_from_csv(str(input_path))
        elif input_path.suffix.lower() == ".json":
            beams = excel_integration.load_beam_data_from_json(str(input_path))
        else:
            print(
                f"Error: Unsupported file format: {input_path.suffix}", file=sys.stderr
            )
            print("Supported formats: .csv, .json", file=sys.stderr)
            return 1

        print(f"Loaded {len(beams)} beam(s)", file=sys.stderr)

        # Process each beam and collect results
        results = []
        for beam in beams:
            print(f"  Processing {beam.story}/{beam.beam_id}...", file=sys.stderr)

            # Calculate stirrup area (2-legged)
            asv_mm2 = 3.14159 * (beam.stirrup_dia / 2) ** 2 * 2

            # Run complete design using API
            case_result = api.design_beam_is456(
                units="IS456",
                case_id=f"{beam.story}_{beam.beam_id}",
                b_mm=beam.b,
                D_mm=beam.D,
                d_mm=beam.d,
                d_dash_mm=beam.cover,
                fck_nmm2=beam.fck,
                fy_nmm2=beam.fy,
                mu_knm=beam.Mu,
                vu_kn=beam.Vu,
                asv_mm2=asv_mm2,
            )

            # Create detailing
            detailing_result = detailing.create_beam_detailing(
                beam_id=beam.beam_id,
                story=beam.story,
                b=beam.b,
                D=beam.D,
                span=beam.span,
                cover=beam.cover,
                fck=beam.fck,
                fy=beam.fy,
                ast_start=beam.Ast_req,
                ast_mid=beam.Ast_req,
                ast_end=beam.Ast_req,
                asc_start=beam.Asc_req,
                asc_mid=beam.Asc_req,
                asc_end=beam.Asc_req,
                stirrup_dia=beam.stirrup_dia,
                stirrup_spacing_start=beam.stirrup_spacing,
                stirrup_spacing_mid=beam.stirrup_spacing * 1.33,
                stirrup_spacing_end=beam.stirrup_spacing,
            )

            # Compile result
            beam_result = {
                "beam_id": beam.beam_id,
                "story": beam.story,
                "geometry": {
                    "b": beam.b,
                    "D": beam.D,
                    "d": beam.d,
                    "span": beam.span,
                    "cover": beam.cover,
                },
                "materials": {
                    "fck": beam.fck,
                    "fy": beam.fy,
                },
                "loads": {
                    "Mu": beam.Mu,
                    "Vu": beam.Vu,
                },
                "flexure": {
                    "ast_req": case_result.flexure.ast_required,
                    "asc_req": case_result.flexure.asc_required,
                    "status": "OK" if case_result.flexure.is_safe else "FAIL",
                    "xu_d": case_result.flexure.xu / beam.d if beam.d > 0 else 0,
                    "mu_lim": case_result.flexure.mu_lim,
                    "section_type": (
                        case_result.flexure.section_type.value
                        if hasattr(case_result.flexure.section_type, "value")
                        else str(case_result.flexure.section_type)
                    ),
                },
                "shear": {
                    "tau_v": case_result.shear.tv,
                    "tau_c": case_result.shear.tc,
                    "sv_req": case_result.shear.spacing,
                    "status": "OK" if case_result.shear.is_safe else "FAIL",
                },
                "detailing": {
                    "bottom_bars": [
                        {
                            "count": bar.count,
                            "diameter": bar.diameter,
                            "callout": bar.callout(),
                        }
                        for bar in detailing_result.bottom_bars
                    ],
                    "top_bars": [
                        {
                            "count": bar.count,
                            "diameter": bar.diameter,
                            "callout": bar.callout(),
                        }
                        for bar in detailing_result.top_bars
                    ],
                    "stirrups": [
                        {
                            "diameter": stir.diameter,
                            "spacing": stir.spacing,
                            "callout": stir.callout(),
                        }
                        for stir in detailing_result.stirrups
                    ],
                    "ld_tension": detailing_result.ld_tension,
                    "lap_length": detailing_result.lap_length,
                },
                "status": "OK" if case_result.is_ok else "FAIL",
            }

            results.append(beam_result)

        # Prepare output
        output_data = {
            "schema_version": 1,
            "code": "IS456",
            "beams": results,
        }

        # Write output
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with output_path.open("w", encoding="utf-8") as f:
                json.dump(output_data, f, indent=2)

            print(f"Design results written to {output_path}", file=sys.stderr)
        else:
            # Print to stdout
            print(json.dumps(output_data, indent=2))

        print(f"Design complete: {len(results)} beam(s) processed", file=sys.stderr)
        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc(file=sys.stderr)
        return 1


def cmd_bbs(args: argparse.Namespace) -> int:
    """
    Generate bar bending schedule from design results JSON.

    Reads design results and generates a detailed bar bending schedule
    with cut lengths, weights, and bar marks.
    """
    input_path = Path(args.input)

    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        return 1

    try:
        # Load design results
        print(f"Loading design results from {input_path}...", file=sys.stderr)

        with input_path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        beams = data.get("beams", [])
        if not beams:
            print("Error: No beams found in input file", file=sys.stderr)
            return 1

        print(f"Loaded {len(beams)} beam(s)", file=sys.stderr)

        # Generate detailing results for BBS
        detailing_list = []
        for beam in beams:
            print(f"  Processing {beam['story']}/{beam['beam_id']}...", file=sys.stderr)

            # Reconstruct detailing from design results
            geom = beam["geometry"]
            mat = beam["materials"]
            det = beam["detailing"]

            # Create simplified detailing result for BBS
            detailing_result = detailing.create_beam_detailing(
                beam_id=beam["beam_id"],
                story=beam["story"],
                b=geom["b"],
                D=geom["D"],
                span=geom["span"],
                cover=geom["cover"],
                fck=mat["fck"],
                fy=mat["fy"],
                ast_start=beam["flexure"]["ast_req"],
                ast_mid=beam["flexure"]["ast_req"],
                ast_end=beam["flexure"]["ast_req"],
                asc_start=beam["flexure"].get("asc_req", 0),
                asc_mid=beam["flexure"].get("asc_req", 0),
                asc_end=beam["flexure"].get("asc_req", 0),
                stirrup_dia=det["stirrups"][0]["diameter"] if det["stirrups"] else 8,
                stirrup_spacing_start=(
                    det["stirrups"][0]["spacing"] if det["stirrups"] else 150
                ),
                stirrup_spacing_mid=(
                    det["stirrups"][1]["spacing"] if len(det["stirrups"]) > 1 else 200
                ),
                stirrup_spacing_end=(
                    det["stirrups"][2]["spacing"] if len(det["stirrups"]) > 2 else 150
                ),
            )

            detailing_list.append(detailing_result)

        # Generate BBS document
        print("Generating bar bending schedule...", file=sys.stderr)
        bbs_doc = bbs.generate_bbs_document(
            detailing_list, project_name=data.get("project_name", "Beam Design BBS")
        )

        # Write output
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            if output_path.suffix.lower() == ".json":
                bbs.export_bbs_to_json(bbs_doc, str(output_path))
            else:
                # Default to CSV
                bbs.export_bbs_to_csv(bbs_doc.items, str(output_path))

            print(f"Bar bending schedule written to {output_path}", file=sys.stderr)
        else:
            # Print CSV to stdout
            import csv
            import io

            output = io.StringIO()
            fieldnames = [
                "bar_mark",
                "member_id",
                "location",
                "zone",
                "shape_code",
                "diameter_mm",
                "no_of_bars",
                "cut_length_mm",
                "total_length_mm",
                "unit_weight_kg",
                "total_weight_kg",
                "remarks",
            ]

            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()

            for item in bbs_doc.items:
                writer.writerow(
                    {
                        "bar_mark": item.bar_mark,
                        "member_id": item.member_id,
                        "location": item.location,
                        "zone": item.zone,
                        "shape_code": item.shape_code,
                        "diameter_mm": item.diameter_mm,
                        "no_of_bars": item.no_of_bars,
                        "cut_length_mm": item.cut_length_mm,
                        "total_length_mm": item.total_length_mm,
                        "unit_weight_kg": item.unit_weight_kg,
                        "total_weight_kg": item.total_weight_kg,
                        "remarks": item.remarks,
                    }
                )

            print(output.getvalue())

        print(
            f"BBS complete: {bbs_doc.summary.total_bars} bars, "
            f"{bbs_doc.summary.total_weight_kg:.2f} kg",
            file=sys.stderr,
        )
        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc(file=sys.stderr)
        return 1


def cmd_dxf(args: argparse.Namespace) -> int:
    """
    Generate DXF drawings from design results JSON.

    Creates detailed reinforcement drawings in DXF format suitable
    for CAD software and fabrication.
    """
    input_path = Path(args.input)

    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        return 1

    # Check if dxf_export module is available
    if dxf_export is None:
        print("Error: dxf_export module not available", file=sys.stderr)
        print("Install with: pip install ezdxf", file=sys.stderr)
        return 1

    # Check if ezdxf is available
    if not dxf_export.EZDXF_AVAILABLE:
        print("Error: ezdxf library not installed", file=sys.stderr)
        print("Install with: pip install ezdxf", file=sys.stderr)
        return 1

    try:
        # Load design results
        print(f"Loading design results from {input_path}...", file=sys.stderr)

        with input_path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        beams = data.get("beams", [])
        if not beams:
            print("Error: No beams found in input file", file=sys.stderr)
            return 1

        print(f"Loaded {len(beams)} beam(s)", file=sys.stderr)

        # Generate detailing results for DXF
        detailing_list = []
        for beam in beams:
            print(f"  Processing {beam['story']}/{beam['beam_id']}...", file=sys.stderr)

            geom = beam["geometry"]
            mat = beam["materials"]
            det = beam["detailing"]

            detailing_result = detailing.create_beam_detailing(
                beam_id=beam["beam_id"],
                story=beam["story"],
                b=geom["b"],
                D=geom["D"],
                span=geom["span"],
                cover=geom["cover"],
                fck=mat["fck"],
                fy=mat["fy"],
                ast_start=beam["flexure"]["ast_req"],
                ast_mid=beam["flexure"]["ast_req"],
                ast_end=beam["flexure"]["ast_req"],
                asc_start=beam["flexure"].get("asc_req", 0),
                asc_mid=beam["flexure"].get("asc_req", 0),
                asc_end=beam["flexure"].get("asc_req", 0),
                stirrup_dia=det["stirrups"][0]["diameter"] if det["stirrups"] else 8,
                stirrup_spacing_start=(
                    det["stirrups"][0]["spacing"] if det["stirrups"] else 150
                ),
                stirrup_spacing_mid=(
                    det["stirrups"][1]["spacing"] if len(det["stirrups"]) > 1 else 200
                ),
                stirrup_spacing_end=(
                    det["stirrups"][2]["spacing"] if len(det["stirrups"]) > 2 else 150
                ),
            )

            detailing_list.append(detailing_result)

        # Generate DXF
        if not args.output:
            print(
                "Error: Output file path is required for DXF generation",
                file=sys.stderr,
            )
            return 1

        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        print("Generating DXF drawings...", file=sys.stderr)

        if len(detailing_list) == 1:
            # Single beam - use standard function
            dxf_export.generate_beam_dxf(detailing_list[0], str(output_path))
        else:
            # Multiple beams - use multi-beam layout
            dxf_export.generate_multi_beam_dxf(detailing_list, str(output_path))

        print(f"DXF drawings written to {output_path}", file=sys.stderr)
        print(f"DXF complete: {len(detailing_list)} beam(s) drawn", file=sys.stderr)
        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc(file=sys.stderr)
        return 1


def cmd_job(args: argparse.Namespace) -> int:
    """
    Run complete job from JSON specification.

    Executes a full job including design calculations, BBS generation,
    and optional DXF drawing generation.
    """
    input_path = Path(args.input)

    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        return 1

    if not args.output:
        print("Error: Output directory is required for job processing", file=sys.stderr)
        return 1

    try:
        print(f"Running job from {input_path}...", file=sys.stderr)

        # Use existing job_runner
        job_runner.run_job(job_path=str(input_path), out_dir=args.output)

        print(f"Job complete: outputs written to {args.output}", file=sys.stderr)
        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc(file=sys.stderr)
        return 1


def _build_parser() -> argparse.ArgumentParser:
    """Build the main argument parser with subcommands."""

    parser = argparse.ArgumentParser(
        prog="structural_lib",
        description="IS 456 RC Beam Design Library - Unified CLI",
        epilog='Use "python -m structural_lib <command> --help" for command-specific help',
    )

    subparsers = parser.add_subparsers(
        dest="command", required=True, help="Available commands"
    )

    # Design subcommand
    design_parser = subparsers.add_parser(
        "design",
        help="Run beam design from CSV/JSON input",
        description="""
        Run beam design calculations from CSV or JSON input file.
        
        Examples:
          python -m structural_lib design input.csv -o results.json
          python -m structural_lib design beams.json -o design_output.json
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    design_parser.add_argument(
        "input", help="Input CSV or JSON file with beam parameters"
    )
    design_parser.add_argument(
        "-o", "--output", help="Output JSON file (if omitted, prints to stdout)"
    )
    design_parser.set_defaults(func=cmd_design)

    # BBS subcommand
    bbs_parser = subparsers.add_parser(
        "bbs",
        help="Generate bar bending schedule from design results",
        description="""
        Generate bar bending schedule (BBS) from design results JSON.
        
        Examples:
          python -m structural_lib bbs results.json -o bbs.csv
          python -m structural_lib bbs results.json -o bbs.json
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    bbs_parser.add_argument("input", help="Input JSON file with design results")
    bbs_parser.add_argument(
        "-o",
        "--output",
        help="Output CSV or JSON file (if omitted, prints CSV to stdout)",
    )
    bbs_parser.set_defaults(func=cmd_bbs)

    # DXF subcommand
    dxf_parser = subparsers.add_parser(
        "dxf",
        help="Generate DXF drawings from design results",
        description="""
        Generate DXF reinforcement drawings from design results JSON.
        Requires ezdxf library: pip install ezdxf
        
        Examples:
          python -m structural_lib dxf results.json -o drawings.dxf
          python -m structural_lib dxf design_output.json -o beam_details.dxf
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    dxf_parser.add_argument("input", help="Input JSON file with design results")
    dxf_parser.add_argument(
        "-o", "--output", required=True, help="Output DXF file path"
    )
    dxf_parser.set_defaults(func=cmd_dxf)

    # Job subcommand
    job_parser = subparsers.add_parser(
        "job",
        help="Run complete job from JSON specification",
        description="""
        Run a complete job including design, analysis, and report generation.
        
        Examples:
          python -m structural_lib job job.json -o output/
          python -m structural_lib job project_spec.json -o results/
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    job_parser.add_argument("input", help="Input JSON job specification file")
    job_parser.add_argument(
        "-o", "--output", required=True, help="Output directory for job results"
    )
    job_parser.set_defaults(func=cmd_job)

    return parser


def main(argv: List[str] | None = None) -> int:
    """Main entry point for the CLI."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    # Call the appropriate command function
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())

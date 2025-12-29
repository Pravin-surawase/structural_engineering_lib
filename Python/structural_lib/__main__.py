"""
Unified CLI entrypoint for structural_lib.

Usage:
    python -m structural_lib design input.csv -o results.json
    python -m structural_lib bbs results.json -o bbs.csv
    python -m structural_lib detail results.json -o detailing.json
    python -m structural_lib dxf results.json -o drawings.dxf
    python -m structural_lib job job.json -o output/
    python -m structural_lib validate job.json
    python -m structural_lib report ./output/ --format=html
    python -m structural_lib critical ./output/ --top=10 --format=csv
    python -m structural_lib mark-diff --bbs schedule.csv --dxf drawings.dxf

This module provides a unified command-line interface with subcommands
for beam design, bar bending schedules, DXF generation, job processing,
report generation, and critical set export.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import List

from . import api
from . import beam_pipeline
from . import detailing
from . import dxf_export
from . import excel_integration
from . import job_runner
from . import report


def _fmt_cell(v: object) -> str:
    if v is None:
        return ""
    if isinstance(v, bool):
        return "TRUE" if v else "FALSE"
    if isinstance(v, float):
        return repr(v)
    return str(v)


def _write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: _fmt_cell(row.get(k)) for k in fieldnames})


def _print_error(message: str, hint: str | None = None) -> None:
    print(f"Error: {message}", file=sys.stderr)
    if hint:
        print(f"Hint: {hint}", file=sys.stderr)


def _format_validation_text(report: api.ValidationReport) -> str:
    status = "OK" if report.ok else "FAIL"
    lines = [f"Validation: {status}"]

    if report.details:
        lines.append("Details:")
        for key in sorted(report.details):
            lines.append(f"  {key}: {report.details[key]}")

    if report.warnings:
        lines.append("Warnings:")
        for warn in report.warnings:
            lines.append(f"  - {warn}")

    if report.errors:
        lines.append("Errors:")
        for err in report.errors:
            lines.append(f"  - {err}")

    return "\n".join(lines)


def _format_mark_diff_text(result: dict) -> str:
    summary = result.get("summary", {})
    ok = result.get("ok", False)
    lines = [
        f"BBS/DXF bar mark check: {'OK' if ok else 'FAIL'}",
        f"Beams checked: {summary.get('beams_checked', 0)}",
        f"BBS marks: {summary.get('bbs_marks', 0)}",
        f"DXF marks: {summary.get('dxf_marks', 0)}",
    ]

    missing = result.get("missing_in_dxf", {}) or {}
    extra = result.get("extra_in_dxf", {}) or {}

    if missing:
        lines.append("Missing in DXF:")
        for beam_id in sorted(missing):
            marks = ", ".join(missing[beam_id])
            lines.append(f"  {beam_id}: {marks}")

    if extra:
        lines.append("Extra in DXF:")
        for beam_id in sorted(extra):
            marks = ", ".join(extra[beam_id])
            lines.append(f"  {beam_id}: {marks}")

    return "\n".join(lines)


def _extract_beam_params_from_schema(beam: dict) -> dict:
    """Shim for tests; delegates to api helper for schema normalization."""
    return api._extract_beam_params_from_schema(beam)


def cmd_design(args: argparse.Namespace) -> int:
    """
    Run beam design from CSV/JSON input file.

    Reads beam parameters from CSV or JSON, performs IS456 design calculations
    using the canonical beam_pipeline, and outputs design results in JSON format.
    """
    input_path = Path(args.input)

    if not input_path.exists():
        _print_error(f"Input file not found: {input_path}")
        return 1

    try:
        # Load beam data
        print(f"Loading beam data from {input_path}...", file=sys.stderr)

        if input_path.suffix.lower() == ".csv":
            beams = excel_integration.load_beam_data_from_csv(str(input_path))
        elif input_path.suffix.lower() == ".json":
            beams = excel_integration.load_beam_data_from_json(str(input_path))
        else:
            _print_error(
                f"Unsupported file format: {input_path.suffix}",
                hint="Supported formats: .csv, .json",
            )
            return 1

        print(f"Loaded {len(beams)} beam(s)", file=sys.stderr)

        crack_width_params = None
        if args.crack_width_params:
            params_path = Path(args.crack_width_params)
            if not params_path.exists():
                _print_error(f"Crack width params file not found: {params_path}")
                return 1
            with params_path.open("r", encoding="utf-8") as f:
                crack_width_params = json.load(f)
            if not isinstance(crack_width_params, dict):
                _print_error(
                    "Crack width params must be a JSON object.",
                    hint='Example: {"acr_mm": 120, "cmin_mm": 25, "h_mm": 500}',
                )
                return 1
            # Warn if applying global params to multiple beams
            if len(beams) > 1:
                print(
                    "Warning: --crack-width-params applies the same parameters to all "
                    f"{len(beams)} beams. For mixed geometry/materials, consider "
                    "per-beam crack width input.",
                    file=sys.stderr,
                )

        # Process each beam using canonical pipeline
        results: list[beam_pipeline.BeamDesignOutput] = []
        for beam in beams:
            print(f"  Processing {beam.story}/{beam.beam_id}...", file=sys.stderr)

            # Calculate stirrup area (2-legged)
            asv_mm2 = 3.14159 * (beam.stirrup_dia / 2) ** 2 * 2
            deflection_params = None
            if args.deflection:
                deflection_params = {
                    "span_mm": beam.span,
                    "d_mm": beam.d,
                    "support_condition": args.support_condition,
                }

            # Use canonical pipeline for design
            result = beam_pipeline.design_single_beam(
                units="IS456",
                beam_id=beam.beam_id,
                story=beam.story,
                b_mm=beam.b,
                D_mm=beam.D,
                d_mm=beam.d,
                span_mm=beam.span,
                cover_mm=beam.cover,
                fck_nmm2=beam.fck,
                fy_nmm2=beam.fy,
                mu_knm=beam.Mu,
                vu_kn=beam.Vu,
                case_id=f"{beam.story}_{beam.beam_id}",
                d_dash_mm=beam.cover,
                asv_mm2=asv_mm2,
                include_detailing=True,
                stirrup_dia_mm=beam.stirrup_dia,
                stirrup_spacing_start_mm=beam.stirrup_spacing,
                stirrup_spacing_mid_mm=beam.stirrup_spacing * 1.33,
                stirrup_spacing_end_mm=beam.stirrup_spacing,
                deflection_params=deflection_params,
                crack_width_params=crack_width_params,
            )

            results.append(result)

        # Build multi-beam output using canonical schema
        output = beam_pipeline.MultiBeamOutput(
            schema_version=beam_pipeline.SCHEMA_VERSION,
            code="IS456",
            units="IS456",
            beams=results,
            summary={
                "total_beams": len(results),
                "passed": sum(1 for r in results if r.is_ok),
                "failed": sum(1 for r in results if not r.is_ok),
            },
        )

        # Write output
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with output_path.open("w", encoding="utf-8") as f:
                json.dump(output.to_dict(), f, indent=2)

            print(f"Design results written to {output_path}", file=sys.stderr)
        else:
            # Print to stdout
            print(json.dumps(output.to_dict(), indent=2))

        if args.summary is not None:
            if args.summary == "":
                if args.output:
                    summary_path = Path(args.output).with_name("design_summary.csv")
                else:
                    summary_path = Path("design_summary.csv")
            else:
                summary_path = Path(args.summary)

            rows = []
            for res in results:
                rows.append(
                    {
                        "beam_id": res.beam_id,
                        "story": res.story,
                        "is_ok": res.is_ok,
                        "governing_utilization": res.governing_utilization,
                        "governing_check": res.governing_check,
                        "util_flexure": res.flexure.utilization,
                        "util_shear": res.shear.utilization,
                        "util_deflection": res.serviceability.deflection_utilization,
                        "util_crack_width": res.serviceability.crack_width_utilization,
                        "mu_knm": res.loads.mu_knm,
                        "vu_kn": res.loads.vu_kn,
                        "ast_required_mm2": res.flexure.ast_required_mm2,
                        "sv_required_mm": res.shear.sv_required_mm,
                    }
                )

            fieldnames = [
                "beam_id",
                "story",
                "is_ok",
                "governing_utilization",
                "governing_check",
                "util_flexure",
                "util_shear",
                "util_deflection",
                "util_crack_width",
                "mu_knm",
                "vu_kn",
                "ast_required_mm2",
                "sv_required_mm",
            ]
            _write_csv(summary_path, rows, fieldnames)
            print(f"Summary written to {summary_path}", file=sys.stderr)

        print(f"Design complete: {len(results)} beam(s) processed", file=sys.stderr)
        return 0

    except beam_pipeline.UnitsValidationError as e:
        _print_error(f"Units error: {e}")
        return 1
    except Exception as e:
        _print_error(str(e))
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
        _print_error(f"Input file not found: {input_path}")
        return 1

    try:
        # Load design results
        print(f"Loading design results from {input_path}...", file=sys.stderr)

        with input_path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        beams = data.get("beams", [])
        if not beams:
            _print_error("No beams found in input file")
            return 1

        print(f"Loaded {len(beams)} beam(s)", file=sys.stderr)

        # Generate detailing results for BBS
        detailing_list = api.compute_detailing(data)

        # Generate BBS document
        print("Generating bar bending schedule...", file=sys.stderr)
        bbs_doc = api.compute_bbs(
            detailing_list, project_name=data.get("project_name", "Beam Design BBS")
        )

        # Write output
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            if output_path.suffix.lower() == ".json":
                api.export_bbs(bbs_doc, output_path, fmt="json")
            else:
                api.export_bbs(bbs_doc, output_path, fmt="csv")

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
        _print_error(str(e))
        import traceback

        traceback.print_exc(file=sys.stderr)
        return 1


def cmd_detail(args: argparse.Namespace) -> int:
    """Generate detailing JSON from design results."""
    input_path = Path(args.input)

    if not input_path.exists():
        _print_error(f"Input file not found: {input_path}")
        return 1

    try:
        print(f"Loading design results from {input_path}...", file=sys.stderr)
        with input_path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        detailing_list = api.compute_detailing(data)

        output = {
            "schema_version": data.get("schema_version", beam_pipeline.SCHEMA_VERSION),
            "code": data.get("code", "IS456"),
            "units": data.get("units", "IS456"),
            "beams": [
                api._detailing_result_to_dict(result) for result in detailing_list
            ],
        }

        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with output_path.open("w", encoding="utf-8") as f:
                json.dump(output, f, indent=2)
            print(f"Detailing output written to {output_path}", file=sys.stderr)
        else:
            print(json.dumps(output, indent=2))

        return 0

    except Exception as exc:
        _print_error(str(exc))
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
        _print_error(f"Input file not found: {input_path}")
        return 1

    # Check if dxf_export module is available
    if dxf_export is None:
        _print_error(
            "DXF export module not available.",
            hint='Install with: pip install "structural-lib-is456[dxf]"',
        )
        return 1

    # Check if ezdxf is available
    if not dxf_export.EZDXF_AVAILABLE:
        _print_error(
            "ezdxf library not installed.",
            hint='Install with: pip install "structural-lib-is456[dxf]"',
        )
        return 1

    try:
        # Load design results
        print(f"Loading design results from {input_path}...", file=sys.stderr)

        with input_path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        beams = data.get("beams", [])
        if not beams:
            _print_error("No beams found in input file")
            return 1

        print(f"Loaded {len(beams)} beam(s)", file=sys.stderr)

        # Generate detailing results for DXF
        detailing_list = []
        for beam in beams:
            print(f"  Processing {beam['story']}/{beam['beam_id']}...", file=sys.stderr)

            # Extract parameters using schema-agnostic helper
            params = api._extract_beam_params_from_schema(beam)
            det = params["detailing"]

            detailing_result = detailing.create_beam_detailing(
                beam_id=params["beam_id"],
                story=params["story"],
                b=params["b"],
                D=params["D"],
                span=params["span"],
                cover=params["cover"],
                fck=params["fck"],
                fy=params["fy"],
                ast_start=params["ast"],
                ast_mid=params["ast"],
                ast_end=params["ast"],
                asc_start=params["asc"],
                asc_mid=params["asc"],
                asc_end=params["asc"],
                stirrup_dia=(
                    det["stirrups"][0]["diameter"] if det.get("stirrups") else 8
                ),
                stirrup_spacing_start=(
                    det["stirrups"][0]["spacing"] if det.get("stirrups") else 150
                ),
                stirrup_spacing_mid=(
                    det["stirrups"][1]["spacing"]
                    if det.get("stirrups") and len(det["stirrups"]) > 1
                    else 200
                ),
                stirrup_spacing_end=(
                    det["stirrups"][2]["spacing"]
                    if det.get("stirrups") and len(det["stirrups"]) > 2
                    else 150
                ),
            )

            detailing_list.append(detailing_result)

        # Generate DXF
        if not args.output:
            _print_error(
                "Output file path is required for DXF generation.",
                hint="Use -o <drawings.dxf>",
            )
            return 1

        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        print("Generating DXF drawings...", file=sys.stderr)

        title_block = {"title": args.title} if args.title else None

        if len(detailing_list) == 1:
            # Single beam - use standard function
            dxf_export.generate_beam_dxf(
                detailing_list[0],
                str(output_path),
                include_title_block=args.title_block or args.title is not None,
                title_block=title_block,
                sheet_margin_mm=args.sheet_margin,
                title_block_width_mm=args.title_block_width,
                title_block_height_mm=args.title_block_height,
            )
        else:
            # Multiple beams - use multi-beam layout
            dxf_export.generate_multi_beam_dxf(
                detailing_list,
                str(output_path),
                include_title_block=args.title_block or args.title is not None,
                title_block=title_block,
                sheet_margin_mm=args.sheet_margin,
                title_block_width_mm=args.title_block_width,
                title_block_height_mm=args.title_block_height,
            )

        print(f"DXF drawings written to {output_path}", file=sys.stderr)
        print(f"DXF complete: {len(detailing_list)} beam(s) drawn", file=sys.stderr)
        return 0

    except Exception as e:
        _print_error(str(e))
        import traceback

        traceback.print_exc(file=sys.stderr)
        return 1


def cmd_mark_diff(args: argparse.Namespace) -> int:
    """Compare bar marks between a BBS CSV and a DXF file."""
    bbs_path = Path(args.bbs)
    dxf_path = Path(args.dxf)

    if not bbs_path.exists():
        _print_error(f"BBS file not found: {bbs_path}")
        return 1
    if not dxf_path.exists():
        _print_error(f"DXF file not found: {dxf_path}")
        return 1

    if dxf_export is None or not dxf_export.EZDXF_AVAILABLE:
        _print_error(
            "ezdxf library not installed.",
            hint='Install with: pip install "structural-lib-is456[dxf]"',
        )
        return 1

    try:
        result = dxf_export.compare_bbs_dxf_marks(bbs_path, dxf_path)
    except Exception as e:
        _print_error(str(e))
        return 1

    if args.format == "json":
        payload = json.dumps(result, indent=2)
        if args.output:
            out_path = Path(args.output)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(payload + "\n", encoding="utf-8")
        else:
            print(payload)
    else:
        text = _format_mark_diff_text(result)
        if args.output:
            out_path = Path(args.output)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(text + "\n", encoding="utf-8")
        else:
            print(text)

    return 0 if result.get("ok") else 2


def _guess_validation_type(data: dict) -> str:
    if isinstance(data, dict):
        if "beam" in data and "cases" in data:
            return "job"
        if "beams" in data:
            return "results"
    return "unknown"


def cmd_validate(args: argparse.Namespace) -> int:
    """Validate a job.json or design results JSON file."""
    input_path = Path(args.input)
    if not input_path.exists():
        _print_error(f"Input file not found: {input_path}")
        return 1

    mode = args.type
    if mode == "auto":
        try:
            data = json.loads(input_path.read_text(encoding="utf-8"))
        except Exception as exc:
            _print_error(str(exc))
            return 1
        mode = _guess_validation_type(data)
        if mode == "unknown":
            _print_error(
                "Could not determine file type. Use --type job or --type results."
            )
            return 1

    if mode == "job":
        report = api.validate_job_spec(input_path)
    else:
        report = api.validate_design_results(input_path)

    if args.format == "json":
        payload = json.dumps(report.to_dict(), indent=2)
        if args.output:
            out_path = Path(args.output)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(payload + "\n", encoding="utf-8")
        else:
            print(payload)
    else:
        text = _format_validation_text(report)
        if args.output:
            out_path = Path(args.output)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(text + "\n", encoding="utf-8")
        else:
            print(text)

    return 0 if report.ok else 2


def cmd_job(args: argparse.Namespace) -> int:
    """
    Run complete job from JSON specification.

    Executes a full job including design calculations, BBS generation,
    and optional DXF drawing generation.
    """
    input_path = Path(args.input)

    if not input_path.exists():
        _print_error(f"Input file not found: {input_path}")
        return 1

    if not args.output:
        _print_error(
            "Output directory is required for job processing.",
            hint="Use -o <output_dir>",
        )
        return 1

    try:
        print(f"Running job from {input_path}...", file=sys.stderr)

        # Use existing job_runner
        job_runner.run_job(job_path=str(input_path), out_dir=args.output)

        print(f"Job complete: outputs written to {args.output}", file=sys.stderr)
        return 0

    except Exception as e:
        _print_error(str(e))
        import traceback

        traceback.print_exc(file=sys.stderr)
        return 1


def cmd_report(args: argparse.Namespace) -> int:
    """Generate report from job output folder or design results JSON.

    Generates human-readable reports (JSON or HTML).
    """
    output_dir = Path(args.output_dir)
    is_file_input = output_dir.is_file()

    if not output_dir.exists():
        _print_error(f"Output path not found: {output_dir}")
        return 1

    # Resolve optional overrides
    job_path = Path(args.job) if args.job else None
    results_path = Path(args.results) if args.results else None

    try:
        print(f"Loading report data from {output_dir}...", file=sys.stderr)

        fmt = args.format.lower()
        if is_file_input:
            design_results = report.load_design_results(output_dir)

            if fmt == "json":
                output = report.export_design_json(design_results)
                if args.output:
                    out_path = Path(args.output)
                    out_path.parent.mkdir(parents=True, exist_ok=True)
                    out_path.write_text(output, encoding="utf-8")
                    print(f"Report written to {out_path}", file=sys.stderr)
                else:
                    print(output)
                return 0

            if fmt != "html":
                _print_error(
                    f"Unknown format: {fmt}",
                    hint="Use --format=json or --format=html",
                )
                return 1

            beams = design_results.get("beams", [])
            if not args.output:
                if len(beams) >= args.batch_threshold:
                    _print_error(
                        "Batch report requires --output for folder packaging",
                        hint="Use -o report/ or increase --batch-threshold",
                    )
                    return 1
                output = report.render_design_report_single(
                    design_results, batch_threshold=args.batch_threshold
                )
                print(output)
                return 0

            out_path = Path(args.output)
            written = report.write_design_report_package(
                design_results,
                output_path=out_path,
                batch_threshold=args.batch_threshold,
            )
            if written:
                print(f"Report written to {written[0]}", file=sys.stderr)
            return 0

        data = report.load_report_data(
            output_dir,
            job_path=job_path,
            results_path=results_path,
        )

        # Generate output based on format
        if fmt == "json":
            output = report.export_json(data)
        elif fmt == "html":
            output = report.export_html(data)
        else:
            _print_error(
                f"Unknown format: {fmt}",
                hint="Use --format=json or --format=html",
            )
            return 1

        # Write to file or stdout
        if args.output:
            out_path = Path(args.output)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(output, encoding="utf-8")
            print(f"Report written to {out_path}", file=sys.stderr)
        else:
            print(output)

        return 0

    except FileNotFoundError as e:
        _print_error(str(e))
        return 1
    except ValueError as e:
        _print_error(str(e))
        return 1
    except Exception as e:
        _print_error(str(e))
        import traceback

        traceback.print_exc(file=sys.stderr)
        return 1


def cmd_critical(args: argparse.Namespace) -> int:
    """Generate critical set export (sorted utilization table).

    Outputs a table of cases sorted by utilization ratio (highest first).
    """
    output_dir = Path(args.output_dir)

    if not output_dir.exists():
        _print_error(f"Output directory not found: {output_dir}")
        return 1

    # Resolve optional overrides
    job_path = Path(args.job) if args.job else None
    results_path = Path(args.results) if args.results else None

    try:
        print(f"Loading report data from {output_dir}...", file=sys.stderr)

        data = report.load_report_data(
            output_dir,
            job_path=job_path,
            results_path=results_path,
        )

        # Get critical set with optional top N filter
        top_n = args.top if args.top and args.top > 0 else None
        critical_cases = report.get_critical_set(data, top=top_n)

        if not critical_cases:
            print("No cases found in results.", file=sys.stderr)
            return 0

        print(
            f"Found {len(critical_cases)} case(s) "
            f"(top={top_n if top_n else 'all'})",
            file=sys.stderr,
        )

        # Generate output based on format
        fmt = args.format.lower()
        if fmt == "csv":
            output = report.export_critical_csv(critical_cases)
        elif fmt == "html":
            output = report.export_critical_html(critical_cases)
        else:
            _print_error(
                f"Unknown format: {fmt}",
                hint="Use --format=csv or --format=html",
            )
            return 1

        # Write to file or stdout
        if args.output:
            out_path = Path(args.output)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(output, encoding="utf-8")
            print(f"Critical set written to {out_path}", file=sys.stderr)
        else:
            print(output)

        return 0

    except FileNotFoundError as e:
        _print_error(str(e))
        return 1
    except ValueError as e:
        _print_error(str(e))
        return 1
    except Exception as e:
        _print_error(str(e))
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
        Run IS456 beam design from CSV or JSON input and emit results JSON
        (schema_version=1, units=IS456).

        Examples:
          python -m structural_lib design input.csv -o results.json
          python -m structural_lib design beams.json -o design_output.json
          python -m structural_lib design input.csv  # prints JSON to stdout
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    design_parser.add_argument(
        "input", help="Input CSV or JSON file with beam parameters"
    )
    design_parser.add_argument(
        "-o", "--output", help="Output JSON file (if omitted, prints to stdout)"
    )
    design_parser.add_argument(
        "--summary",
        nargs="?",
        const="",
        help=(
            "Write a compact CSV summary. "
            "If no path is supplied, writes design_summary.csv next to output."
        ),
    )
    design_parser.add_argument(
        "--deflection",
        action="store_true",
        help="Run Level A deflection check (span/depth).",
    )
    design_parser.add_argument(
        "--support-condition",
        default="simply_supported",
        help="Support condition for deflection check (simply_supported, continuous, cantilever).",
    )
    design_parser.add_argument(
        "--crack-width-params",
        help="JSON file with crack width parameters (applies to all beams).",
    )
    design_parser.set_defaults(func=cmd_design)

    # BBS subcommand
    bbs_parser = subparsers.add_parser(
        "bbs",
        help="Generate bar bending schedule from design results",
        description="""
        Generate bar bending schedule (BBS) from design results JSON
        produced by the design pipeline.

        Examples:
          python -m structural_lib bbs results.json -o bbs.csv
          python -m structural_lib bbs results.json -o bbs.json
          python -m structural_lib bbs results.json  # prints CSV to stdout
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

    detail_parser = subparsers.add_parser(
        "detail",
        help="Generate detailing JSON from design results",
        description=(
            "Generate detailing outputs (bars, stirrups, development lengths) "
            "from design results JSON."
        ),
        epilog="""
Examples:
  python -m structural_lib detail results.json -o detailing.json
  python -m structural_lib detail results.json  # prints JSON to stdout
""",
    )
    detail_parser.add_argument("input", help="Input JSON file with design results")
    detail_parser.add_argument(
        "-o", "--output", help="Output JSON file (defaults to stdout)"
    )
    detail_parser.set_defaults(func=cmd_detail)

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
    dxf_parser.add_argument(
        "--title-block",
        action="store_true",
        help="Draw a deliverable border and title block.",
    )
    dxf_parser.add_argument(
        "--title",
        help="Optional title text for the title block.",
    )
    dxf_parser.add_argument(
        "--sheet-margin",
        type=float,
        default=200.0,
        help="Sheet margin in mm (default: 200).",
    )
    dxf_parser.add_argument(
        "--title-block-width",
        type=float,
        default=900.0,
        help="Title block width in mm (default: 900).",
    )
    dxf_parser.add_argument(
        "--title-block-height",
        type=float,
        default=250.0,
        help="Title block height in mm (default: 250).",
    )
    dxf_parser.set_defaults(func=cmd_dxf)

    # Validate subcommand
    validate_parser = subparsers.add_parser(
        "validate",
        help="Validate a job.json or design results JSON file",
        description="""
        Validate job specs or design results for required fields and schema version.

        Examples:
          python -m structural_lib validate job.json
          python -m structural_lib validate results.json --type results --format json
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    validate_parser.add_argument("input", help="Input JSON file to validate")
    validate_parser.add_argument(
        "--type",
        default="auto",
        choices=["auto", "job", "results"],
        help="Validation type (default: auto)",
    )
    validate_parser.add_argument(
        "--format",
        default="text",
        choices=["text", "json"],
        help="Output format (default: text)",
    )
    validate_parser.add_argument(
        "-o",
        "--output",
        help="Output file path (if omitted, prints to stdout)",
    )
    validate_parser.set_defaults(func=cmd_validate)

    # BBS/DXF consistency check
    mark_diff_parser = subparsers.add_parser(
        "mark-diff",
        help="Check bar marks in BBS vs DXF outputs",
        description="""
        Compare bar marks between a BBS CSV file and a DXF file.

        Examples:
          python -m structural_lib mark-diff --bbs schedule.csv --dxf drawings.dxf
          python -m structural_lib mark-diff --bbs schedule.csv --dxf drawings.dxf --format json -o mark_diff.json
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    mark_diff_parser.add_argument("--bbs", required=True, help="BBS CSV file path")
    mark_diff_parser.add_argument("--dxf", required=True, help="DXF file path")
    mark_diff_parser.add_argument(
        "--format",
        default="text",
        choices=["text", "json"],
        help="Output format (default: text)",
    )
    mark_diff_parser.add_argument(
        "-o",
        "--output",
        help="Output file path (if omitted, prints to stdout)",
    )
    mark_diff_parser.set_defaults(func=cmd_mark_diff)

    # Job subcommand
    job_parser = subparsers.add_parser(
        "job",
        help="Run complete job from JSON specification",
        description="""
        Run a complete job from JSON specification and write outputs to a folder.

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

    # Report subcommand
    report_parser = subparsers.add_parser(
        "report",
        help="Generate report from job output folder or design results JSON",
        description="""
        Generate human-readable reports (JSON or HTML).

        Examples:
          python -m structural_lib report ./output/ --format=json
          python -m structural_lib report ./output/ --format=html -o report.html
          python -m structural_lib report ./output/ --job custom_job.json --format=json
          python -m structural_lib report design_results.json -o report/ --batch-threshold 80
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    report_parser.add_argument(
        "output_dir",
        help="Job output directory or design results JSON file",
    )
    report_parser.add_argument(
        "--format",
        default="json",
        choices=["json", "html"],
        help="Output format (default: json)",
    )
    report_parser.add_argument(
        "-o", "--output", help="Output file path (if omitted, prints to stdout)"
    )
    report_parser.add_argument(
        "--job",
        help="Override path to job.json (default: output_dir/inputs/job.json)",
    )
    report_parser.add_argument(
        "--results",
        help="Override path to design_results.json (default: output_dir/design/design_results.json)",
    )
    report_parser.add_argument(
        "--batch-threshold",
        type=int,
        default=80,
        help="Batch threshold for design results HTML packaging",
    )
    report_parser.set_defaults(func=cmd_report)

    # Critical subcommand
    critical_parser = subparsers.add_parser(
        "critical",
        help="Generate critical set (sorted utilization table)",
        description="""
        Generate a table of cases sorted by utilization ratio (highest first).
        Useful for identifying critical load cases that govern the design.

        Examples:
          python -m structural_lib critical ./output/ --format=csv
          python -m structural_lib critical ./output/ --format=html -o critical.html
          python -m structural_lib critical ./output/ --top=10 --format=csv
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    critical_parser.add_argument("output_dir", help="Job output directory to read from")
    critical_parser.add_argument(
        "--format",
        default="csv",
        choices=["csv", "html"],
        help="Output format (default: csv)",
    )
    critical_parser.add_argument(
        "-o", "--output", help="Output file path (if omitted, prints to stdout)"
    )
    critical_parser.add_argument(
        "--top",
        type=int,
        help="Limit to top N cases by utilization",
    )
    critical_parser.add_argument(
        "--job",
        help="Override path to job.json",
    )
    critical_parser.add_argument(
        "--results",
        help="Override path to design_results.json",
    )
    critical_parser.set_defaults(func=cmd_critical)

    return parser


def main(argv: List[str] | None = None) -> int:
    """Main entry point for the CLI."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    # Call the appropriate command function
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())

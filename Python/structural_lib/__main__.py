# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
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
    python -m structural_lib capabilities --json
    python -m structural_lib gravity-v1 example -o gravity-request.json
    python -m structural_lib gravity-v1 request.json -o calculation-book.json
    python -m structural_lib excel-v1 definition
    python -m structural_lib excel-v1 preview workbook-table.json
    python -m structural_lib excel-v1 run workbook-table.json --mapping-hash HASH
    python -m structural_lib mark-diff --bbs schedule.csv --dxf drawings.dxf
    python -m structural_lib beam-v1 request.json --mode design

This module provides a unified command-line interface with subcommands
for beam design, bar bending schedules, DXF generation, job processing,
report generation, and critical set export.
"""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import sys
from pathlib import Path
from typing import cast

from . import (
    beam_pipeline,
    detailing,
)
from .core.data_types import CrackWidthParams, ValidationReport
from .services import api, cli_design, dxf_export, job_runner, report


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


def _format_validation_text(report: ValidationReport) -> str:
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


def cmd_gravity_v1(args: argparse.Namespace) -> int:
    """Emit the maintained example or run one Gravity Workflow V1 request."""

    try:
        if args.input == "example":
            if args.format != "json":
                raise ValueError("The gravity example supports JSON output only.")
            from structural_lib.services.gravity_builder import (
                get_gravity_workflow_example_document_v1,
            )

            output = (
                json.dumps(
                    get_gravity_workflow_example_document_v1(),
                    allow_nan=False,
                    ensure_ascii=True,
                    indent=2,
                    sort_keys=True,
                )
                + "\n"
            )
        else:
            input_path = Path(args.input)
            if not input_path.is_file():
                raise ValueError(f"Input file not found: {input_path}")
            from structural_lib.core.gravity_workflow import GravityWorkflowRequestV1
            from structural_lib.services.gravity_calculation_book import (
                render_gravity_calculation_book_markdown_v1,
                run_gravity_workflow_with_book_v1,
            )

            request = GravityWorkflowRequestV1.model_validate_json(
                input_path.read_text(encoding="utf-8")
            )
            bundle = run_gravity_workflow_with_book_v1(request)
            output = (
                render_gravity_calculation_book_markdown_v1(bundle.calculation_book)
                if args.format == "markdown"
                else json.dumps(
                    bundle.model_dump(mode="json"),
                    allow_nan=False,
                    ensure_ascii=True,
                    indent=2,
                    sort_keys=True,
                )
                + "\n"
            )
    except (OSError, RuntimeError, TypeError, ValueError) as exc:
        _print_error(f"Gravity V1 request was not accepted: {exc}")
        return 1

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(output, encoding="utf-8")
    else:
        print(output, end="" if output.endswith("\n") else "\n")
    return 0


def cmd_beam_v1(args: argparse.Namespace) -> int:
    """Run the canonical nested beam request without dictionary guessing."""

    from structural_lib.core.errors import InputContractError
    from structural_lib.design.is456 import beam

    try:
        input_path = Path(args.input)
        if not input_path.is_file():
            raise InputContractError(
                (
                    beam.InputIssueV1(
                        code="INPUT_FILE_NOT_FOUND",
                        path="input",
                        message="canonical beam request file was not found",
                        received=str(input_path),
                    ),
                )
            )
        request = beam.load(json.loads(input_path.read_text(encoding="utf-8")))
        if args.mode == "design":
            payload = beam.design(request).to_dict()
        else:
            if request.detailing is None:
                raise InputContractError(
                    (
                        beam.InputIssueV1(
                            code="DOWNSTREAM_INPUT_MISSING",
                            path="detailing",
                            message=f"detailing is required for {args.mode}",
                        ),
                    )
                )
            combined = beam.design_and_detail(
                request, detailing_standard=request.detailing.standard
            )
            payload = (
                combined.to_dict()
                if args.mode == "design-and-detail"
                else beam.bbs(combined).to_dict()
            )
        output = (
            json.dumps(
                payload,
                allow_nan=False,
                ensure_ascii=True,
                indent=2,
                sort_keys=True,
            )
            + "\n"
        )
    except (InputContractError, json.JSONDecodeError) as exc:
        problem = (
            exc.to_problem()
            if isinstance(exc, InputContractError)
            else {
                "schema_version": "structural-problem/v1",
                "code": "INPUT_JSON_INVALID",
                "message": str(exc),
                "details": None,
            }
        )
        print(json.dumps(problem, allow_nan=False, sort_keys=True), file=sys.stderr)
        return 2
    except OSError as exc:
        _print_error(f"Canonical beam request could not be read: {exc}")
        return 1

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(output, encoding="utf-8")
    else:
        print(output, end="")
    return 0


def cmd_excel_v1(args: argparse.Namespace) -> int:
    """Preview or run the bounded selected-table Excel Workbench V1."""

    try:
        from structural_lib.core.excel_workbook import (
            ExcelWorkbookPreviewRequestV1,
            ExcelWorkbookRunRequestV1,
        )
        from structural_lib.services.excel_workbench import (
            build_excel_mapping_preview_v1,
            get_excel_workbench_definition_v1,
            render_excel_review_bundle_markdown_v1,
            run_excel_workbook_v1,
        )

        if args.phase == "definition":
            if args.format != "json":
                raise ValueError(
                    "Excel workbench definition supports JSON output only."
                )
            output = (
                json.dumps(
                    get_excel_workbench_definition_v1().model_dump(mode="json"),
                    allow_nan=False,
                    ensure_ascii=True,
                    indent=2,
                    sort_keys=True,
                )
                + "\n"
            )
            preview_request = None
        else:
            if not args.input:
                raise ValueError(f"Excel {args.phase} requires an input JSON file.")
            input_path = Path(args.input)
            if not input_path.is_file():
                raise ValueError(f"Input file not found: {input_path}")
            preview_request = ExcelWorkbookPreviewRequestV1.model_validate_json(
                input_path.read_text(encoding="utf-8")
            )

        if args.phase == "preview":
            assert preview_request is not None
            if args.format != "json":
                raise ValueError("Excel mapping preview supports JSON output only.")
            payload = build_excel_mapping_preview_v1(preview_request).model_dump(
                mode="json"
            )
            output = (
                json.dumps(
                    payload,
                    allow_nan=False,
                    ensure_ascii=True,
                    indent=2,
                    sort_keys=True,
                )
                + "\n"
            )
        elif args.phase == "run":
            assert preview_request is not None
            if not args.mapping_hash:
                raise ValueError(
                    "Excel run requires --mapping-hash from the reviewed preview."
                )
            run_request = ExcelWorkbookRunRequestV1(
                selection=preview_request.selection,
                headers=preview_request.headers,
                rows=preview_request.rows,
                confirmed_mapping_hash=args.mapping_hash,
            )
            result = run_excel_workbook_v1(run_request)
            output = (
                render_excel_review_bundle_markdown_v1(result)
                if args.format == "markdown"
                else json.dumps(
                    result.model_dump(mode="json"),
                    allow_nan=False,
                    ensure_ascii=True,
                    indent=2,
                    sort_keys=True,
                )
                + "\n"
            )
    except (OSError, TypeError, ValueError) as exc:
        _print_error(f"Excel Workbench V1 request was not accepted: {exc}")
        return 1

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(output, encoding="utf-8")
    else:
        print(output, end="" if output.endswith("\n") else "\n")
    return 0


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

    Reads complete beam parameters through the strict project boundary and
    outputs the retained versioned ``beams`` compatibility envelope.
    """
    input_path = Path(args.input)

    if not input_path.exists():
        _print_error(f"Input file not found: {input_path}")
        return 1

    try:
        # Load beam data
        print(f"Loading beam data from {input_path}...", file=sys.stderr)

        intake = cli_design.load_cli_design_input_v1(
            input_path, input_format=args.input_format
        )
        beams = intake.records

        print(f"Loaded {len(beams)} beam(s)", file=sys.stderr)

        crack_width_params = None
        if args.crack_width_params:
            params_path = Path(args.crack_width_params)
            if not params_path.exists():
                _print_error(f"Crack width params file not found: {params_path}")
                return 1
            with params_path.open("r", encoding="utf-8") as f:
                loaded_params = json.load(f)
            if not isinstance(loaded_params, dict):
                _print_error(
                    "Crack width params must be a JSON object.",
                    hint='Example: {"acr_mm": 120, "cmin_mm": 25, "h_mm": 500}',
                )
                return 1
            crack_width_params = cast(CrackWidthParams, loaded_params)
            # Warn if applying global params to multiple beams
            if len(beams) > 1:
                print(
                    "Warning: --crack-width-params applies the same parameters to all "
                    f"{len(beams)} beams. For mixed geometry/materials, consider "
                    "per-beam crack width input.",
                    file=sys.stderr,
                )

        output = cli_design.design_cli_project_v1(
            beams,
            include_deflection=args.deflection,
            support_condition=args.support_condition,
            crack_width_params=crack_width_params,
        )
        results = output.beams

        # Compute insights if requested
        insights_output = None
        if args.insights:
            print("Computing advisory insights...", file=sys.stderr)
            from . import insights

            beam_insights = []
            for _i, beam in enumerate(beams):
                print(f"  Insights for {beam.story}/{beam.beam_id}...", file=sys.stderr)

                try:
                    # Precheck
                    precheck = insights.quick_precheck(
                        span_mm=beam.span,
                        b_mm=beam.b,
                        d_mm=beam.d,
                        D_mm=beam.D,
                        mu_knm=beam.Mu,
                        fck_nmm2=beam.fck,
                        fy_nmm2=beam.fy,
                    )

                    # Sensitivity analysis (top 4 parameters)
                    params_dict = {
                        "units": "IS456",
                        "mu_knm": beam.Mu,
                        "vu_kn": beam.Vu,
                        "b_mm": beam.b,
                        "D_mm": beam.D,
                        "d_mm": beam.d,
                        "fck_nmm2": beam.fck,
                        "fy_nmm2": beam.fy,
                    }
                    sensitivities, robustness = insights.sensitivity_analysis(
                        api.design_beam_is456,
                        params_dict,
                        ["d_mm", "b_mm", "fck_nmm2", "fy_nmm2"],
                    )

                    # Constructability scoring deferred to v0.16
                    # CLI smart command uses simplified param-based sensitivity only
                    # Full constructability requires BeamDesignOutput (not available in param-only context)
                    constructability = None

                    beam_insights.append(
                        {
                            "beam_id": beam.beam_id,
                            "story": beam.story,
                            "precheck": precheck.to_dict(),
                            "sensitivities": [s.to_dict() for s in sensitivities],
                            "robustness": robustness.to_dict(),
                            "constructability": (
                                constructability.to_dict()
                                if constructability is not None
                                else None
                            ),
                        }
                    )

                except Exception as exc:
                    print(
                        f"  Warning: Failed to compute insights for {beam.story}/{beam.beam_id}: {exc}",
                        file=sys.stderr,
                    )
                    beam_insights.append(
                        {
                            "beam_id": beam.beam_id,
                            "story": beam.story,
                            "error": str(exc),
                        }
                    )

            insights_output = {
                "schema_version": "1.0",
                "insights_version": "preview",
                "beams": beam_insights,
            }

        # Write output
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with output_path.open("w", encoding="utf-8") as f:
                json.dump(output.to_dict(), f, indent=2)

            print(f"Design results written to {output_path}", file=sys.stderr)

            # Write insights output if available
            if insights_output:
                insights_path = output_path.with_stem(output_path.stem + "_insights")
                with insights_path.open("w", encoding="utf-8") as f:
                    json.dump(insights_output, f, indent=2)
                print(f"Insights written to {insights_path}", file=sys.stderr)
        else:
            # Print to stdout
            print(json.dumps(output.to_dict(), indent=2))

            # Print insights to stderr if available (don't mix with main output)
            if insights_output:
                print(
                    "\n# Insights output saved separately (use -o flag to write to file)",
                    file=sys.stderr,
                )
                print(
                    f"# Insights summary: {len(insights_output['beams'])} beam(s) analyzed",
                    file=sys.stderr,
                )

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

    except cli_design.CLIDesignBlockedError as exc:
        for issue in exc.issues:
            _print_error(f"[{issue.code}] {issue.path}: {issue.message}")
        return 2
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


def _validate_cli_path(path: Path, label: str = "path") -> Path:
    """Resolve path and block relative path traversal outside cwd."""
    resolved = path.resolve()
    if not path.is_absolute():
        cwd = Path.cwd().resolve()
        if not str(resolved).startswith(str(cwd)):
            raise ValueError(f"{label} must be within working directory: {path}")
    return resolved


def cmd_dxf(args: argparse.Namespace) -> int:
    """
    Generate DXF drawings from design results JSON.

    Creates detailed reinforcement drawings in DXF format suitable
    for CAD software and fabrication.
    """
    input_path = _validate_cli_path(Path(args.input), "input")

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
            # Extract parameters using schema-agnostic helper
            params = api._extract_beam_params_from_schema(beam)

            print(
                f"  Processing {params['story']}/{params['beam_id']}...",
                file=sys.stderr,
            )
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

        output_path = _validate_cli_path(Path(args.output), "output")
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


def cmd_smart(args: argparse.Namespace) -> int:
    """Run smart design analysis dashboard."""
    input_path = Path(args.input)
    if not input_path.exists():
        _print_error(f"Input file not found: {input_path}")
        return 1

    try:
        # Load design result
        with input_path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        # Check if it's a design result or need to design first
        if "beams" in data:
            # Design results JSON
            if not data["beams"]:
                _print_error("No beams in design results")
                return 1

            # Use first beam for now (could enhance to process all)
            beam = data["beams"][0]

            # Extract parameters from metadata or beam dict
            span_mm = args.span or beam.get("span_mm", 5000.0)
            mu_knm = beam.get("loads", {}).get("mu_knm", beam.get("mu_knm", 120.0))
            vu_kn = beam.get("loads", {}).get("vu_kn", beam.get("vu_kn", 80.0))

            # design_single_beam returns the correct BeamDesignOutput type
            from .services.beam_pipeline import design_single_beam

            design_result = design_single_beam(
                units="IS456",
                beam_id=beam.get("beam_id", "B1"),
                story=beam.get("story", "Story1"),
                b_mm=beam.get("b_mm", 300.0),
                D_mm=beam.get("D_mm", 500.0),
                d_mm=beam.get("d_mm", 450.0),
                span_mm=span_mm,
                cover_mm=beam.get("cover_mm", 30.0),
                fck_nmm2=beam.get("fck_nmm2", 25.0),
                fy_nmm2=beam.get("fy_nmm2", 500.0),
                mu_knm=mu_knm,
                vu_kn=vu_kn,
            )
        else:
            # Raw parameters - design via pipeline for correct BeamDesignOutput type
            from .services.beam_pipeline import design_single_beam

            span_mm = args.span or data.get("span_mm", 5000.0)
            mu_knm = data.get("mu_knm", 120.0)
            vu_kn = data.get("vu_kn", 80.0)

            design_result = design_single_beam(
                units="IS456",
                beam_id=data.get("beam_id", "B1"),
                story=data.get("story", "Story1"),
                b_mm=data.get("b_mm", 300.0),
                D_mm=data.get("D_mm", 500.0),
                d_mm=data.get("d_mm", 450.0),
                span_mm=span_mm,
                cover_mm=data.get("cover_mm", 30.0),
                fck_nmm2=data.get("fck_nmm2", 25.0),
                fy_nmm2=data.get("fy_nmm2", 500.0),
                mu_knm=mu_knm,
                vu_kn=vu_kn,
            )

        # Import SmartDesigner
        from .insights import SmartDesigner

        # Run analysis
        dashboard = SmartDesigner.analyze(
            design=design_result,
            span_mm=span_mm,
            mu_knm=mu_knm,
            vu_kn=vu_kn,
            include_cost=not args.no_cost,
            include_suggestions=not args.no_suggestions,
            include_sensitivity=not args.no_sensitivity,
            include_constructability=not args.no_constructability,
        )

        # Output results
        if args.format == "json":
            output = json.dumps(dashboard.to_dict(), indent=2)
            if args.output:
                out_path = Path(args.output)
                out_path.parent.mkdir(parents=True, exist_ok=True)
                out_path.write_text(output + "\n", encoding="utf-8")
                print(f"Smart analysis saved to: {out_path}")
            else:
                print(output)
        else:
            # Text format (default)
            output = dashboard.summary_text()
            if args.output:
                out_path = Path(args.output)
                out_path.parent.mkdir(parents=True, exist_ok=True)
                out_path.write_text(output + "\n", encoding="utf-8")
                print(f"Smart analysis saved to: {out_path}")
            else:
                print(output)

        return 0

    except Exception as e:
        import traceback

        _print_error(f"Smart analysis failed: {str(e)}")
        if args.verbose:
            traceback.print_exc()
        return 1


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
            f"Found {len(critical_cases)} case(s) (top={top_n if top_n else 'all'})",
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


def cmd_capabilities(args: argparse.Namespace) -> int:
    """Print the canonical supported/held IS 456 capability contract."""
    document = api.get_supported_is456_capability_document()
    if args.as_json:
        json.dump(document, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
        return 0

    print(f"Code edition: {document['code_edition']}")
    print(f"Capability schema: {document['schema_version']}")
    for capability in document["capabilities"]:
        review = (
            "final engineer review remains deferred until the integrated library"
            if capability["qualified_review_required"]
            else "no final review flag"
        )
        print(f"- {capability['capability_id']}: {capability['supported_case']}")
        for held_case in capability["held_cases"]:
            print(f"  held: {held_case}")
        print(f"  boundary: {review}")
    return 0


def cmd_install_preflight(args: argparse.Namespace) -> int:
    """Report the exact interpreter, package origin/version, and optional extras."""
    import structural_lib
    from structural_lib.core.version import get_runtime_version_identity

    optional_modules = {
        "dxf": "ezdxf",
        "report": "jinja2",
        "pdf": "weasyprint",
        "render": "matplotlib",
        "validation": "jsonschema",
    }
    origin = str(Path(structural_lib.__file__).resolve())
    version = structural_lib.__version__
    runtime_identity = get_runtime_version_identity(origin)
    optional_extras: dict[str, bool] = {
        name: importlib.util.find_spec(module_name) is not None
        for name, module_name in optional_modules.items()
    }
    report = {
        "interpreter": sys.executable,
        "interpreter_resolved": str(Path(sys.executable).resolve()),
        "python_version": sys.version.split()[0],
        "package_version": version,
        "package_origin": origin,
        "runtime_identity": runtime_identity.to_dict(),
        "optional_extras": optional_extras,
        "qualified_review_required": True,
        "professional_review_is_intermediate_programme_gate": False,
        "final_engineer_review_stage": "DEFERRED_UNTIL_INTEGRATED_LIBRARY",
        "repair_command": (
            f"{sys.executable} -m pip install --upgrade "
            f'"structural-lib-is456==={version}"'
        ),
    }
    if args.as_json:
        json.dump(report, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
        return 0

    print(f"Interpreter: {report['interpreter']}")
    print(f"Python: {report['python_version']}")
    print(f"structural_lib: {report['package_version']}")
    print(f"Package origin: {report['package_origin']}")
    print("Optional extras:")
    for name, available in optional_extras.items():
        print(f"  {name}: {'installed' if available else 'not installed'}")
    print(f"Repair/install: {report['repair_command']}")
    return 0


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

    preflight_parser = subparsers.add_parser(
        "install-preflight",
        help="Show interpreter, package origin/version, extras, and repair command",
    )
    preflight_parser.add_argument(
        "--json",
        dest="as_json",
        action="store_true",
        help="Emit the preflight report as JSON",
    )
    preflight_parser.set_defaults(func=cmd_install_preflight)

    capabilities_parser = subparsers.add_parser(
        "capabilities",
        help="Show the supported and held IS 456 capability contract",
        description=(
            "Show the canonical supported/held workflow, unit, limitation, and "
            "final-review claim boundary for this library version."
        ),
    )
    capabilities_parser.add_argument(
        "--json",
        dest="as_json",
        action="store_true",
        help="Emit the canonical machine-readable JSON contract",
    )
    capabilities_parser.set_defaults(func=cmd_capabilities)

    beam_v1_parser = subparsers.add_parser(
        "beam-v1",
        help="Run the canonical beam-design-input/v1 JSON contract",
        description=(
            "Validate one nested canonical beam request, then emit a design, "
            "combined detailing, or BBS result without partial artifacts."
        ),
    )
    beam_v1_parser.add_argument("input", help="BeamDesignInputV1 JSON file")
    beam_v1_parser.add_argument(
        "--mode",
        choices=["design", "design-and-detail", "bbs"],
        default="design",
    )
    beam_v1_parser.add_argument(
        "-o", "--output", help="Output JSON file (if omitted, prints to stdout)"
    )
    beam_v1_parser.set_defaults(func=cmd_beam_v1)

    gravity_parser = subparsers.add_parser(
        "gravity-v1",
        help="Create an example or run Building Gravity Workflow V1",
        description=(
            "Use 'example' to emit a complete maintained request, or supply a JSON "
            "file to reconcile its dead/live load path, run only ready component "
            "adapters, and emit a calculation book."
        ),
    )
    gravity_parser.add_argument(
        "input", help="GravityWorkflowRequestV1 JSON file, or 'example'"
    )
    gravity_parser.add_argument(
        "--format",
        choices=["json", "markdown"],
        default="json",
        help="Output format (default: json)",
    )
    gravity_parser.add_argument(
        "-o", "--output", help="Output file (if omitted, prints to stdout)"
    )
    gravity_parser.set_defaults(func=cmd_gravity_v1)

    excel_parser = subparsers.add_parser(
        "excel-v1",
        help="Discover, preview, or run Excel Routine Workbench V1",
        description=(
            "Discover the installed workbook identity, preview the selected-table "
            "mapping, then run only with the exact reviewed mapping hash."
        ),
    )
    excel_parser.add_argument("phase", choices=["definition", "preview", "run"])
    excel_parser.add_argument(
        "input", nargs="?", help="ExcelWorkbookPreviewRequestV1 JSON file"
    )
    excel_parser.add_argument(
        "--mapping-hash",
        help="Exact mapping hash emitted by the preview phase",
    )
    excel_parser.add_argument(
        "--format",
        choices=["json", "markdown"],
        default="json",
        help="Run output format (preview is JSON only)",
    )
    excel_parser.add_argument(
        "-o", "--output", help="Output file (if omitted, prints to stdout)"
    )
    excel_parser.set_defaults(func=cmd_excel_v1)

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
        "--input-format",
        default="generic",
        choices=["generic", "auto", "etabs", "safe", "staad"],
        help=(
            "CSV adapter identity (default: generic). Use auto only when the "
            "source format is expected to be uniquely detectable."
        ),
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
    design_parser.add_argument(
        "--insights",
        action="store_true",
        help="Generate advisory insights (precheck, sensitivity, constructability) and save to separate JSON file.",
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

    # Smart analysis subcommand
    smart_parser = subparsers.add_parser(
        "smart",
        help="Run smart design analysis dashboard",
        description="""
        Run comprehensive smart design analysis combining:
        - Cost optimization
        - Design suggestions
        - Sensitivity analysis
        - Constructability assessment

        Examples:
          python -m structural_lib smart design_result.json --span 5000
          python -m structural_lib smart params.json -o dashboard.txt
          python -m structural_lib smart design.json --format json -o analysis.json
          python -m structural_lib smart design.json --no-cost --no-sensitivity
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    smart_parser.add_argument(
        "input",
        help="Design result JSON or beam parameters JSON",
    )
    smart_parser.add_argument(
        "--span",
        type=float,
        help="Beam span in mm (required if not in input JSON)",
    )
    smart_parser.add_argument(
        "--format",
        default="text",
        choices=["text", "json"],
        help="Output format (default: text)",
    )
    smart_parser.add_argument(
        "-o",
        "--output",
        help="Output file path (if omitted, prints to stdout)",
    )
    smart_parser.add_argument(
        "--no-cost",
        action="store_true",
        help="Skip cost optimization analysis",
    )
    smart_parser.add_argument(
        "--no-suggestions",
        action="store_true",
        help="Skip design suggestions",
    )
    smart_parser.add_argument(
        "--no-sensitivity",
        action="store_true",
        help="Skip sensitivity analysis",
    )
    smart_parser.add_argument(
        "--no-constructability",
        action="store_true",
        help="Skip constructability assessment",
    )
    smart_parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed error messages",
    )
    smart_parser.set_defaults(func=cmd_smart)

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


def main(argv: list[str] | None = None) -> int:
    """Main entry point for the CLI."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    # Call the appropriate command function
    exit_code: int = args.func(args)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())

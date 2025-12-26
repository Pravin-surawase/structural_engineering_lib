"""
Excel Integration Module — Bridge between Excel data and Detailing/DXF

This module provides utilities to:
1. Parse beam design data from CSV/JSON exports
2. Batch process multiple beams for DXF generation
3. Create summary reports

Usage:
    from structural_lib.excel_integration import process_beam_schedule, batch_generate_dxf
"""

import json
import csv
import logging
import os

_logger = logging.getLogger(__name__)
from typing import List, Dict, Optional
from pathlib import Path
from dataclasses import dataclass, asdict

from .detailing import create_beam_detailing, BeamDetailingResult
from .dxf_export import generate_beam_dxf, EZDXF_AVAILABLE


# =============================================================================
# Data Classes
# =============================================================================


@dataclass
class BeamDesignData:
    """Represents a row from tbl_BeamDesign."""

    beam_id: str
    story: str
    b: float  # mm
    D: float  # mm
    d: float  # mm (effective depth)
    span: float  # mm
    cover: float  # mm
    fck: float  # N/mm²
    fy: float  # N/mm²
    Mu: float  # kN-m
    Vu: float  # kN
    Ast_req: float  # mm²
    Asc_req: float  # mm²
    stirrup_dia: float  # mm
    stirrup_spacing: float  # mm
    status: str  # "OK" or "REVISE"

    @classmethod
    def from_dict(cls, data: Dict) -> "BeamDesignData":
        """Create from dictionary (flexible key matching)."""
        # Normalize keys (handle both camelCase and snake_case)
        normalized = {}
        key_map = {
            "beamid": "beam_id",
            "beam_id": "beam_id",
            "BeamID": "beam_id",
            "story": "story",
            "Story": "story",
            "b": "b",
            "width": "b",
            "d": "D",
            "D": "D",
            "depth": "D",
            "eff_d": "d",
            "effective_depth": "d",
            "span": "span",
            "Span": "span",
            "cover": "cover",
            "Cover": "cover",
            "fck": "fck",
            "Fck": "fck",
            "fy": "fy",
            "Fy": "fy",
            "mu": "Mu",
            "Mu": "Mu",
            "moment": "Mu",
            "vu": "Vu",
            "Vu": "Vu",
            "shear": "Vu",
            "ast_req": "Ast_req",
            "Ast_req": "Ast_req",
            "ast": "Ast_req",
            "asc_req": "Asc_req",
            "Asc_req": "Asc_req",
            "asc": "Asc_req",
            "stirrup_dia": "stirrup_dia",
            "Stirrup_Dia": "stirrup_dia",
            "stirrup_spacing": "stirrup_spacing",
            "Stirrup_Spacing": "stirrup_spacing",
            "status": "status",
            "Status": "status",
        }

        for key, value in data.items():
            mapped_key = key_map.get(key, key.lower())

            # Deterministic conflict handling:
            # - Lowercase 'd' is treated as an alias for overall depth 'D' (legacy input),
            #   but should not overwrite an explicitly provided 'D'.
            if key == "d" and mapped_key == "D" and "D" in normalized:
                continue

            normalized[mapped_key] = value

        # Apply defaults
        defaults = {
            "cover": 40,
            "Asc_req": 0,
            "status": "OK",
        }

        for key, default in defaults.items():
            if key not in normalized or normalized[key] in (None, ""):
                normalized[key] = default

        # Calculate effective depth after cover is set
        cover_val = float(normalized.get("cover", 40))
        D_val = float(normalized.get("D", 500))
        if "d" not in normalized or normalized["d"] in (None, "", 0):
            normalized["d"] = D_val - cover_val

        return cls(
            beam_id=str(normalized["beam_id"]),
            story=str(normalized["story"]),
            b=float(normalized["b"]),
            D=float(normalized["D"]),
            d=float(normalized["d"]),
            span=float(normalized["span"]),
            cover=float(normalized["cover"]),
            fck=float(normalized["fck"]),
            fy=float(normalized["fy"]),
            Mu=float(normalized["Mu"]),
            Vu=float(normalized["Vu"]),
            Ast_req=float(normalized["Ast_req"]),
            Asc_req=float(normalized.get("Asc_req", 0)),
            stirrup_dia=float(normalized["stirrup_dia"]),
            stirrup_spacing=float(normalized["stirrup_spacing"]),
            status=str(normalized.get("status", "OK")),
        )


@dataclass
class ProcessingResult:
    """Result of processing a beam for DXF generation."""

    beam_id: str
    story: str
    success: bool
    dxf_path: Optional[str]
    detailing: Optional[BeamDetailingResult]
    error: Optional[str]


# =============================================================================
# File Parsing Functions
# =============================================================================


def load_beam_data_from_csv(filepath: str) -> List[BeamDesignData]:
    """
    Load beam design data from a CSV file.

    Expected columns (flexible matching):
        BeamID, Story, b, D, Span, Cover, fck, fy,
        Ast_req, Asc_req, Stirrup_Dia, Stirrup_Spacing
    """
    beams = []

    with open(filepath, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                beam = BeamDesignData.from_dict(row)
                beams.append(beam)
            except (KeyError, ValueError) as e:
                print(f"Warning: Skipping row due to error: {e}")
                continue

    return beams


def load_beam_data_from_json(filepath: str) -> List[BeamDesignData]:
    """
    Load beam design data from a JSON file.

    Expected format:
        {"beams": [{"beam_id": "B1", ...}, ...]}
        or
        [{"beam_id": "B1", ...}, ...]
    """
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Handle both formats
    if isinstance(data, dict) and "beams" in data:
        beam_list = data["beams"]
    elif isinstance(data, list):
        beam_list = data
    else:
        raise ValueError("Invalid JSON format. Expected list or {'beams': [...]}")

    return [BeamDesignData.from_dict(b) for b in beam_list]


def export_beam_data_to_json(beams: List[BeamDesignData], filepath: str):
    """Export beam data to JSON file."""
    data = {"beams": [asdict(b) for b in beams]}
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


# =============================================================================
# Processing Functions
# =============================================================================


def process_single_beam(
    beam: BeamDesignData,
    output_folder: str,
    is_seismic: bool = False,
    generate_dxf: bool = True,
) -> ProcessingResult:
    """
    Process a single beam: create detailing and optionally generate DXF.

    Args:
        beam: Beam design data
        output_folder: Folder to save DXF files
        is_seismic: Apply IS 13920 seismic detailing rules
        generate_dxf: Whether to generate DXF file

    Returns:
        ProcessingResult with success status and paths
    """
    try:
        # 1. Create detailing
        # Note: create_beam_detailing expects ast/asc for start/mid/end zones
        # For simplified input with single Ast_req, use same value for all zones
        detailing = create_beam_detailing(
            beam_id=beam.beam_id,
            story=beam.story,
            b=beam.b,
            D=beam.D,
            span=beam.span,
            cover=beam.cover,
            fck=beam.fck,
            fy=beam.fy,
            ast_start=beam.Ast_req,  # Use same Ast for all zones (simplified)
            ast_mid=beam.Ast_req,
            ast_end=beam.Ast_req,
            asc_start=beam.Asc_req,
            asc_mid=beam.Asc_req,
            asc_end=beam.Asc_req,
            stirrup_dia=beam.stirrup_dia,
            stirrup_spacing_start=beam.stirrup_spacing,
            stirrup_spacing_mid=beam.stirrup_spacing * 1.33,  # ~200mm for 150mm input
            stirrup_spacing_end=beam.stirrup_spacing,
            is_seismic=is_seismic,
        )

        dxf_path = None

        # 2. Generate DXF if requested and library available
        if generate_dxf:
            if not EZDXF_AVAILABLE:
                return ProcessingResult(
                    beam_id=beam.beam_id,
                    story=beam.story,
                    success=True,
                    dxf_path=None,
                    detailing=detailing,
                    error="ezdxf not installed - DXF generation skipped",
                )

            # Ensure output folder exists
            os.makedirs(output_folder, exist_ok=True)

            # Generate filename
            filename = f"{beam.story}_{beam.beam_id}_detail.dxf"
            dxf_path = os.path.join(output_folder, filename)

            generate_beam_dxf(detailing, dxf_path)

        return ProcessingResult(
            beam_id=beam.beam_id,
            story=beam.story,
            success=True,
            dxf_path=dxf_path,
            detailing=detailing,
            error=None,
        )

    except Exception as e:
        _logger.exception("Failed to process beam %s/%s", beam.story, beam.beam_id)
        return ProcessingResult(
            beam_id=beam.beam_id,
            story=beam.story,
            success=False,
            dxf_path=None,
            detailing=None,
            error=str(e),
        )


def batch_generate_dxf(
    input_file: str, output_folder: str, is_seismic: bool = False
) -> List[ProcessingResult]:
    """
    Batch process multiple beams from a CSV or JSON file.

    Args:
        input_file: Path to CSV or JSON file with beam data
        output_folder: Folder to save DXF files
        is_seismic: Apply IS 13920 seismic detailing rules

    Returns:
        List of ProcessingResult for each beam
    """
    # Load data based on file extension
    ext = Path(input_file).suffix.lower()

    if ext == ".csv":
        beams = load_beam_data_from_csv(input_file)
    elif ext == ".json":
        beams = load_beam_data_from_json(input_file)
    else:
        raise ValueError(f"Unsupported file format: {ext}")

    # Process each beam
    results = []
    for beam in beams:
        result = process_single_beam(beam, output_folder, is_seismic)
        results.append(result)

        # Log progress
        status = "✓" if result.success else "✗"
        print(f"  {status} {beam.story}/{beam.beam_id}")

    return results


# =============================================================================
# Summary & Reporting
# =============================================================================


def generate_summary_report(results: List[ProcessingResult]) -> str:
    """Generate a text summary of batch processing results."""
    total = len(results)
    success = sum(1 for r in results if r.success)
    failed = total - success

    lines = [
        "=" * 60,
        "BEAM DETAILING - BATCH PROCESSING SUMMARY",
        "=" * 60,
        f"Total Beams:     {total}",
        f"Successful:      {success}",
        f"Failed:          {failed}",
        "-" * 60,
    ]

    if failed > 0:
        lines.append("\nFailed Beams:")
        for r in results:
            if not r.success:
                lines.append(f"  - {r.story}/{r.beam_id}: {r.error}")

    if success > 0:
        lines.append("\nGenerated Files:")
        for r in results:
            if r.success and r.dxf_path:
                lines.append(f"  - {r.dxf_path}")

    lines.append("=" * 60)
    return "\n".join(lines)


def generate_detailing_schedule(results: List[ProcessingResult]) -> List[Dict]:
    """
    Generate a detailing schedule from processing results.

    Returns list of dicts suitable for export to CSV/Excel.
    """
    schedule = []

    for r in results:
        if not r.success or not r.detailing:
            continue

        d = r.detailing

        # Get main bar callouts
        if not d.bottom_bars:
            bot_bars = None
        elif len(d.bottom_bars) == 1:
            bot_bars = d.bottom_bars[0]
        else:
            bot_bars = d.bottom_bars[1]  # Mid-span
        top_bars = d.top_bars[0] if d.top_bars else None  # Support
        stirrups_end = d.stirrups[0] if d.stirrups else None
        stirrups_mid = d.stirrups[1] if len(d.stirrups) > 1 else stirrups_end

        row = {
            "Story": d.story,
            "Beam": d.beam_id,
            "Size": f"{int(d.b)}x{int(d.D)}",
            "Span": int(d.span),
            "Bottom_Main": bot_bars.callout() if bot_bars else "-",
            "Top_Main": top_bars.callout() if top_bars else "-",
            "Stirrups_End": stirrups_end.callout() if stirrups_end else "-",
            "Stirrups_Mid": stirrups_mid.callout() if stirrups_mid else "-",
            "Ld_Tension": int(d.ld_tension),
            "Lap_Length": int(d.lap_length),
            "Status": "OK" if d.is_valid else "CHECK",
        }
        schedule.append(row)

    return schedule


def export_schedule_to_csv(schedule: List[Dict], filepath: str):
    """Export detailing schedule to CSV file."""
    if not schedule:
        return

    fieldnames = list(schedule[0].keys())

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(schedule)


# =============================================================================
# Main Entry Point (CLI)
# =============================================================================


def main():
    """Command-line interface for batch DXF generation."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate beam detail DXF drawings from design data"
    )
    parser.add_argument("input_file", help="CSV or JSON file with beam design data")
    parser.add_argument(
        "-o",
        "--output",
        default="./dxf_output",
        help="Output folder for DXF files (default: ./dxf_output)",
    )
    parser.add_argument(
        "--seismic", action="store_true", help="Apply IS 13920 seismic detailing rules"
    )
    parser.add_argument("--schedule", help="Export detailing schedule to CSV file")

    args = parser.parse_args()

    print(f"Processing: {args.input_file}")
    print(f"Output to:  {args.output}")
    print()

    results = batch_generate_dxf(args.input_file, args.output, is_seismic=args.seismic)

    print()
    print(generate_summary_report(results))

    if args.schedule:
        schedule = generate_detailing_schedule(results)
        export_schedule_to_csv(schedule, args.schedule)
        print(f"\nSchedule exported to: {args.schedule}")


if __name__ == "__main__":
    main()

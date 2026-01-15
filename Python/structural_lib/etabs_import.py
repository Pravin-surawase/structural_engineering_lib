# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""ETABS CSV Import Module.

This module provides utilities for importing ETABS beam force exports
and converting them to the structural_engineering_lib job format.

The workflow is CSV-first (no COM/API dependencies), making it portable
across Windows, Mac, and Linux.

Typical workflow:
1. Export from ETABS: Display -> Show Tables -> Element Forces - Beams
2. Save as CSV
3. Use this module to normalize and convert to job.json format

References:
    docs/_archive/misc/etabs-integration.md - Complete mapping guide
    IS 456:2000 - Design code

Example:
    >>> from structural_lib.etabs_import import normalize_etabs_forces, create_job_from_etabs
    >>> envelope = normalize_etabs_forces("ETABS_export.csv")
    >>> job = create_job_from_etabs(
    ...     envelope_data=envelope[0],  # First beam
    ...     b_mm=300, D_mm=500, fck_nmm2=25
    ... )
"""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Sequence

__all__ = [
    "ETABSForceRow",
    "ETABSEnvelopeResult",
    "normalize_etabs_forces",
    "load_etabs_csv",
    "create_job_from_etabs",
    "create_jobs_from_etabs_csv",
    "export_normalized_csv",
    "validate_etabs_csv",
]


# =============================================================================
# Data Classes
# =============================================================================


@dataclass
class ETABSForceRow:
    """Parsed row from ETABS beam forces export.

    Attributes:
        story: Floor/level name (e.g., "Story1", "Level 2")
        beam_id: Beam label (e.g., "B1", "B2")
        unique_name: Internal ETABS ID (optional)
        case_id: Load combination name (e.g., "1.5(DL+LL)")
        station: Location along beam (mm or m)
        m3: Bending moment M3 about local 3 axis (kN·m)
        v2: Shear force V2 in local 2 plane (kN)
        p: Axial force (kN), usually 0 for beams
    """

    story: str
    beam_id: str
    case_id: str
    station: float
    m3: float
    v2: float
    unique_name: str = ""
    p: float = 0.0


@dataclass
class ETABSEnvelopeResult:
    """Envelope result for a beam across all stations.

    Contains the maximum absolute values for design.

    Attributes:
        story: Floor/level name
        beam_id: Beam label
        case_id: Load combination name
        mu_knm: Maximum absolute moment (kN·m)
        vu_kn: Maximum absolute shear (kN)
        station_count: Number of output stations processed
    """

    story: str
    beam_id: str
    case_id: str
    mu_knm: float
    vu_kn: float
    station_count: int = 1


# =============================================================================
# Column Name Mappings (ETABS versions vary)
# =============================================================================

# Possible column names for each field (case-insensitive matching)
_COLUMN_MAPPINGS: dict[str, list[str]] = {
    "story": ["Story", "Level", "Floor"],
    "beam_id": ["Label", "Frame", "Element", "Beam", "Name"],
    "unique_name": ["Unique Name", "UniqueName", "Unique", "GUID"],
    "case_id": [
        "Output Case",
        "Load Case/Combo",
        "Load Case",
        "LoadCase",
        "Combo",
        "Case",
    ],
    "station": ["Station", "Distance", "Location", "Loc"],
    "m3": ["M3", "Moment3", "Mz", "BendingMoment"],
    "v2": ["V2", "Shear2", "Vy", "ShearForce"],
    "p": ["P", "Axial", "N", "AxialForce"],
}


def _find_column(headers: Sequence[str], field: str) -> str | None:
    """Find the actual column name for a field.

    Args:
        headers: List of column headers from CSV
        field: Internal field name to find

    Returns:
        Actual column name if found, None otherwise
    """
    possible_names = _COLUMN_MAPPINGS.get(field, [])
    headers_lower = {h.lower().strip(): h for h in headers}

    for name in possible_names:
        name_lower = name.lower()
        if name_lower in headers_lower:
            return headers_lower[name_lower]

    return None


# =============================================================================
# CSV Loading and Validation
# =============================================================================


def validate_etabs_csv(
    csv_path: str | Path,
) -> tuple[bool, list[str], dict[str, str]]:
    """Validate ETABS CSV file structure.

    Checks for required columns and reports any issues.

    Args:
        csv_path: Path to ETABS CSV file

    Returns:
        Tuple of:
        - is_valid: True if all required columns found
        - issues: List of issue messages
        - column_map: Mapping of internal names to actual column names

    Example:
        >>> is_valid, issues, col_map = validate_etabs_csv("export.csv")
        >>> if not is_valid:
        ...     print("Issues:", issues)
    """
    path = Path(csv_path)
    issues: list[str] = []
    column_map: dict[str, str] = {}

    if not path.exists():
        return False, [f"File not found: {csv_path}"], {}

    try:
        with open(path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None:
                return False, ["CSV file is empty or has no headers"], {}

            headers = list(reader.fieldnames)

            # Required columns
            required = ["story", "beam_id", "case_id", "m3", "v2"]
            optional = ["unique_name", "station", "p"]

            for field in required:
                col_name = _find_column(headers, field)
                if col_name:
                    column_map[field] = col_name
                else:
                    issues.append(
                        f"Required column '{field}' not found. "
                        f"Expected one of: {_COLUMN_MAPPINGS[field]}"
                    )

            for field in optional:
                col_name = _find_column(headers, field)
                if col_name:
                    column_map[field] = col_name

            # Check for at least one data row
            try:
                next(reader)
            except StopIteration:
                issues.append("CSV file has no data rows")

    except UnicodeDecodeError:
        return False, ["File encoding error. Try saving as UTF-8."], {}
    except csv.Error as e:
        return False, [f"CSV parsing error: {e}"], {}

    is_valid = len([i for i in issues if "Required" in i]) == 0
    return is_valid, issues, column_map


def load_etabs_csv(
    csv_path: str | Path,
    *,
    station_multiplier: float = 1.0,
) -> list[ETABSForceRow]:
    """Load ETABS beam forces CSV file.

    Handles various ETABS export formats by detecting column names.

    Args:
        csv_path: Path to ETABS CSV file
        station_multiplier: Multiplier for station values (e.g., 1000 if in meters)

    Returns:
        List of ETABSForceRow objects

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If required columns are missing

    Example:
        >>> rows = load_etabs_csv("ETABS_export.csv")
        >>> for row in rows:
        ...     print(f"{row.beam_id}: M3={row.m3}, V2={row.v2}")
    """
    path = Path(csv_path)
    is_valid, issues, column_map = validate_etabs_csv(path)

    if not is_valid:
        raise ValueError(f"Invalid ETABS CSV: {'; '.join(issues)}")

    rows: list[ETABSForceRow] = []

    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                # Extract values using column map
                story = row.get(column_map.get("story", ""), "").strip()
                beam_id = row.get(column_map.get("beam_id", ""), "").strip()
                case_id = row.get(column_map.get("case_id", ""), "").strip()

                # Parse numeric values with defaults
                station_str = row.get(column_map.get("station", ""), "0")
                m3_str = row.get(column_map.get("m3", ""), "0")
                v2_str = row.get(column_map.get("v2", ""), "0")
                p_str = row.get(column_map.get("p", ""), "0")

                station = _parse_float(station_str) * station_multiplier
                m3 = _parse_float(m3_str)
                v2 = _parse_float(v2_str)
                p = _parse_float(p_str)

                unique_name = row.get(column_map.get("unique_name", ""), "").strip()

                rows.append(
                    ETABSForceRow(
                        story=story,
                        beam_id=beam_id,
                        case_id=case_id,
                        station=station,
                        m3=m3,
                        v2=v2,
                        unique_name=unique_name,
                        p=p,
                    )
                )
            except (ValueError, TypeError):
                # Skip rows with parsing errors
                continue

    return rows


def _parse_float(value: str) -> float:
    """Parse float, handling common ETABS format issues."""
    if not value or value.strip() in ("", "-", "N/A", "NA"):
        return 0.0
    try:
        return float(value.strip())
    except ValueError:
        return 0.0


# =============================================================================
# Normalization and Envelope Calculation
# =============================================================================


def normalize_etabs_forces(
    csv_path: str | Path,
    output_path: str | Path | None = None,
    *,
    station_multiplier: float = 1.0,
) -> list[ETABSEnvelopeResult]:
    """Normalize ETABS beam forces export to envelope format.

    Extracts envelope (max abs) for each (story, beam_id, case_id) combination.
    This is the primary function for converting ETABS data to design inputs.

    Args:
        csv_path: Path to ETABS CSV file
        output_path: Optional path to save normalized CSV
        station_multiplier: Multiplier for station values

    Returns:
        List of envelope results with max |M3| and max |V2| per beam/case

    Example:
        >>> envelopes = normalize_etabs_forces("ETABS_export.csv")
        >>> for env in envelopes:
        ...     print(f"{env.beam_id}: Mu={env.mu_knm:.1f}, Vu={env.vu_kn:.1f}")
    """
    rows = load_etabs_csv(csv_path, station_multiplier=station_multiplier)

    # Group by (story, beam_id, case_id)
    grouped: dict[tuple[str, str, str], list[ETABSForceRow]] = defaultdict(list)
    for r in rows:
        key = (r.story, r.beam_id, r.case_id)
        grouped[key].append(r)

    # Calculate envelopes
    envelopes: list[ETABSEnvelopeResult] = []
    for (story, beam_id, case_id), stations in grouped.items():
        max_mu = max(abs(s.m3) for s in stations)
        max_vu = max(abs(s.v2) for s in stations)
        envelopes.append(
            ETABSEnvelopeResult(
                story=story,
                beam_id=beam_id,
                case_id=case_id,
                mu_knm=max_mu,
                vu_kn=max_vu,
                station_count=len(stations),
            )
        )

    # Sort by story, beam_id, case_id for consistent output
    envelopes.sort(key=lambda e: (e.story, e.beam_id, e.case_id))

    # Export if requested
    if output_path:
        export_normalized_csv(envelopes, output_path)

    return envelopes


def export_normalized_csv(
    envelopes: Sequence[ETABSEnvelopeResult],
    output_path: str | Path,
) -> None:
    """Export normalized envelope data to CSV.

    Args:
        envelopes: List of envelope results
        output_path: Path for output CSV file
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["story", "beam_id", "case_id", "mu_knm", "vu_kn", "stations"])
        for env in envelopes:
            writer.writerow(
                [
                    env.story,
                    env.beam_id,
                    env.case_id,
                    f"{env.mu_knm:.3f}",
                    f"{env.vu_kn:.3f}",
                    env.station_count,
                ]
            )


# =============================================================================
# Job Creation
# =============================================================================


def create_job_from_etabs(
    envelope_data: ETABSEnvelopeResult | Sequence[ETABSEnvelopeResult],
    *,
    b_mm: float,
    D_mm: float,
    fck_nmm2: float,
    fy_nmm2: float = 500.0,
    d_mm: float | None = None,
    d_dash_mm: float = 50.0,
    cover_mm: float = 40.0,
    stirrup_dia_mm: float = 8.0,
    bar_dia_mm: float = 20.0,
    asv_mm2: float = 100.0,
    job_id: str | None = None,
) -> dict[str, Any]:
    """Create a job.json dict from ETABS envelope data.

    Converts ETABS envelope results to the library's JobSpec format.

    Args:
        envelope_data: Single envelope or list of envelopes for the same beam
        b_mm: Beam width (mm)
        D_mm: Overall beam depth (mm)
        fck_nmm2: Characteristic concrete strength (N/mm²)
        fy_nmm2: Characteristic steel yield strength (N/mm²). Default 500.
        d_mm: Effective depth (mm). Calculated from D if not provided.
        d_dash_mm: Cover to compression steel (mm). Default 50.
        cover_mm: Clear cover (mm). Default 40.
        stirrup_dia_mm: Stirrup diameter (mm). Default 8.
        bar_dia_mm: Main bar diameter (mm). Default 20.
        asv_mm2: Area of stirrup legs (mm²). Default 100.
        job_id: Optional job identifier. Auto-generated if not provided.

    Returns:
        JobSpec dictionary ready for job_runner

    Example:
        >>> env = ETABSEnvelopeResult("Story1", "B1", "1.5DL+LL", 150.0, 100.0)
        >>> job = create_job_from_etabs(env, b_mm=300, D_mm=500, fck_nmm2=25)
        >>> with open("job.json", "w") as f:
        ...     json.dump(job, f, indent=2)
    """
    # Normalize to list
    if isinstance(envelope_data, ETABSEnvelopeResult):
        envelopes = [envelope_data]
    else:
        envelopes = list(envelope_data)

    if not envelopes:
        raise ValueError("No envelope data provided")

    # Calculate effective depth if not provided
    if d_mm is None:
        d_mm = D_mm - cover_mm - stirrup_dia_mm - bar_dia_mm / 2

    # Generate job_id from first envelope
    first = envelopes[0]
    if job_id is None:
        job_id = f"ETABS_{first.story}_{first.beam_id}"

    # Create load cases
    cases = [
        {
            "case_id": env.case_id,
            "mu_knm": env.mu_knm,
            "vu_kn": env.vu_kn,
        }
        for env in envelopes
    ]

    return {
        "schema_version": 1,
        "job_id": job_id,
        "code": "IS456",
        "units": "SI-mm",
        "beam": {
            "b_mm": b_mm,
            "D_mm": D_mm,
            "d_mm": d_mm,
            "d_dash_mm": d_dash_mm,
            "fck_nmm2": fck_nmm2,
            "fy_nmm2": fy_nmm2,
            "asv_mm2": asv_mm2,
        },
        "cases": cases,
    }


def create_jobs_from_etabs_csv(
    csv_path: str | Path,
    geometry: dict[str, dict[str, float]],
    *,
    output_dir: str | Path | None = None,
    default_fck: float = 25.0,
    default_fy: float = 500.0,
    station_multiplier: float = 1.0,
) -> list[dict[str, Any]]:
    """Create job.json files for all beams in ETABS export.

    Batch processes an ETABS export to create one job per beam.

    Args:
        csv_path: Path to ETABS CSV file
        geometry: Dict mapping beam_id to geometry dict.
            Required keys per beam: 'b_mm', 'D_mm'
            Optional: 'fck_nmm2', 'fy_nmm2', 'd_mm', 'cover_mm'
        output_dir: Optional directory to save job.json files
        default_fck: Default concrete strength if not in geometry
        default_fy: Default steel strength if not in geometry
        station_multiplier: Multiplier for station values

    Returns:
        List of JobSpec dictionaries

    Example:
        >>> geometry = {
        ...     "B1": {"b_mm": 300, "D_mm": 500},
        ...     "B2": {"b_mm": 250, "D_mm": 450},
        ... }
        >>> jobs = create_jobs_from_etabs_csv("export.csv", geometry, output_dir="jobs/")
    """
    envelopes = normalize_etabs_forces(csv_path, station_multiplier=station_multiplier)

    # Group by beam_id
    beams: dict[str, list[ETABSEnvelopeResult]] = defaultdict(list)
    for env in envelopes:
        beams[env.beam_id].append(env)

    jobs: list[dict[str, Any]] = []

    for beam_id, beam_envs in beams.items():
        # Get geometry for this beam
        geom = geometry.get(beam_id, {})
        if "b_mm" not in geom or "D_mm" not in geom:
            # Skip beams without geometry
            continue

        job = create_job_from_etabs(
            beam_envs,
            b_mm=geom["b_mm"],
            D_mm=geom["D_mm"],
            fck_nmm2=geom.get("fck_nmm2", default_fck),
            fy_nmm2=geom.get("fy_nmm2", default_fy),
            d_mm=geom.get("d_mm"),
            cover_mm=geom.get("cover_mm", 40.0),
        )
        jobs.append(job)

        # Save to file if output_dir provided
        if output_dir:
            out_path = Path(output_dir) / f"{job['job_id']}.json"
            out_path.parent.mkdir(parents=True, exist_ok=True)
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(job, f, indent=2)

    return jobs

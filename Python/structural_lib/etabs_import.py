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

from structural_lib.models import (
    BeamForces,
    BeamGeometry,
    FrameType,
    Point3D,
    SectionProperties,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

__all__ = [
    "ETABSForceRow",
    "ETABSEnvelopeResult",
    "FrameGeometry",
    "normalize_etabs_forces",
    "load_etabs_csv",
    "create_job_from_etabs",
    "create_jobs_from_etabs_csv",
    "export_normalized_csv",
    "validate_etabs_csv",
    "load_frames_geometry",
    "merge_forces_and_geometry",
    # Pydantic model conversion
    "to_beam_geometry",
    "to_beam_forces",
    "frames_to_beam_geometries",
    "envelopes_to_beam_forces",
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
class FrameGeometry:
    """Frame element geometry from ETABS frames_geometry export.

    Contains 3D coordinates and section properties for beams and columns.

    Attributes:
        unique_name: Internal ETABS ID (e.g., "C1")
        label: User-friendly label (e.g., "B1", "C2")
        story: Floor/level name (e.g., "Ground", "Story 1")
        frame_type: Element type ("Beam" or "Column")
        section_name: Section identifier (e.g., "B230X450M20")
        point1_name: Node name at start (e.g., "1")
        point2_name: Node name at end (e.g., "2")
        point1_x: X coordinate of Point 1 (m)
        point1_y: Y coordinate of Point 1 (m)
        point1_z: Z coordinate of Point 1 (m)
        point2_x: X coordinate of Point 2 (m)
        point2_y: Y coordinate of Point 2 (m)
        point2_z: Z coordinate of Point 2 (m)
        angle: Rotation angle (degrees)
        cardinal_point: Section insertion point (1-11)
    """

    unique_name: str
    label: str
    story: str
    frame_type: str
    section_name: str
    point1_name: str
    point2_name: str
    point1_x: float
    point1_y: float
    point1_z: float
    point2_x: float
    point2_y: float
    point2_z: float
    angle: float = 0.0
    cardinal_point: int = 10

    @property
    def length_m(self) -> float:
        """Calculate element length in meters."""
        dx = self.point2_x - self.point1_x
        dy = self.point2_y - self.point1_y
        dz = self.point2_z - self.point1_z
        return (dx**2 + dy**2 + dz**2) ** 0.5

    @property
    def is_vertical(self) -> bool:
        """Check if element is vertical (column-like)."""
        dx = abs(self.point2_x - self.point1_x)
        dy = abs(self.point2_y - self.point1_y)
        abs(self.point2_z - self.point1_z)
        horizontal_length = (dx**2 + dy**2) ** 0.5
        return horizontal_length < 0.01  # < 10mm horizontal movement


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
# Column Name Mappings (ETABS/SAFE versions vary)
# =============================================================================

# Possible column names for each field (case-insensitive matching)
# Supports: ETABS, SAFE, and generic formats
_COLUMN_MAPPINGS: dict[str, list[str]] = {
    # Story/Level identification
    "story": ["Story", "Level", "Floor", "Storey"],
    # Beam/Strip identification
    "beam_id": [
        "Label",
        "Frame",
        "Element",
        "Beam",
        "Name",
        # SAFE format additions
        "Strip",
        "SpanName",
        "Band",
        "StripID",
        # Generic format
        "beam_id",
        "BeamID",
        "ID",
    ],
    "unique_name": ["Unique Name", "UniqueName", "Unique", "GUID"],
    # Load case/combination
    "case_id": [
        "Output Case",
        "Load Case/Combo",
        "Load Case",
        "LoadCase",
        "Combo",
        "Case",
        # SAFE format additions
        "LoadCombo",
        "Combination",
    ],
    # Station along element
    "station": [
        "Station",
        "Distance",
        "Location",
        "Loc",
        # SAFE format additions
        "Position",
        "Pos",
    ],
    # Moment (local 3 axis / about 2 axis)
    "m3": [
        "M3",
        "Moment3",
        "Mz",
        "BendingMoment",
        # SAFE format additions (M22 is moment about 2 axis)
        "M22",
        "Moment22",
        "M2",
        # Generic format
        "mu_knm",
        "Mu",
        "Moment",
    ],
    # Shear (local 2 plane / 23 plane)
    "v2": [
        "V2",
        "Shear2",
        "Vy",
        "ShearForce",
        # SAFE format additions (V23 is shear in 23 plane)
        "V23",
        "Shear23",
        "V3",
        # Generic format
        "vu_kn",
        "Vu",
        "Shear",
    ],
    # Axial force
    "p": ["P", "Axial", "N", "AxialForce", "P1", "Axial1"],
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


# =============================================================================
# Geometry Import Functions
# =============================================================================


def load_frames_geometry(
    csv_path: str | Path, *, validate: bool = True
) -> list[FrameGeometry]:
    """Load frame geometry from ETABS frames_geometry.csv export.

    Args:
        csv_path: Path to frames_geometry.csv file
        validate: If True, validate coordinates (default: True)

    Returns:
        List of FrameGeometry objects with 3D coordinates

    Raises:
        ValueError: If CSV format is invalid or required columns missing
        FileNotFoundError: If csv_path does not exist

    Example:
        >>> frames = load_frames_geometry("frames_geometry.csv")
        >>> print(f"Loaded {len(frames)} frames")
        >>> beams = [f for f in frames if f.frame_type == "Beam"]
        >>> print(f"Found {len(beams)} beams")

    Expected CSV columns:
        UniqueName, Label, Story, FrameType, SectionName,
        Point1Name, Point2Name, Point1X, Point1Y, Point1Z,
        Point2X, Point2Y, Point2Z, Angle, CardinalPoint
    """
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {csv_path}")

    required_cols = {
        "UniqueName",
        "Label",
        "Story",
        "FrameType",
        "SectionName",
        "Point1X",
        "Point1Y",
        "Point1Z",
        "Point2X",
        "Point2Y",
        "Point2Z",
    }

    frames: list[FrameGeometry] = []

    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        header = set(reader.fieldnames or [])

        # Check required columns
        missing = required_cols - header
        if missing:
            raise ValueError(
                f"Missing required columns in frames_geometry.csv: {', '.join(missing)}"
            )

        for row_idx, row in enumerate(reader, start=2):  # Row 2 = first data row
            try:
                frame = FrameGeometry(
                    unique_name=row["UniqueName"],
                    label=row["Label"],
                    story=row["Story"],
                    frame_type=row["FrameType"],
                    section_name=row["SectionName"],
                    point1_name=row.get("Point1Name", ""),
                    point2_name=row.get("Point2Name", ""),
                    point1_x=float(row["Point1X"]),
                    point1_y=float(row["Point1Y"]),
                    point1_z=float(row["Point1Z"]),
                    point2_x=float(row["Point2X"]),
                    point2_y=float(row["Point2Y"]),
                    point2_z=float(row["Point2Z"]),
                    angle=float(row.get("Angle", 0.0)),
                    cardinal_point=int(row.get("CardinalPoint", 10)),
                )

                # Validation
                if validate:
                    # Check element has length
                    if frame.length_m < 0.001:  # < 1mm
                        raise ValueError(
                            f"Row {row_idx}: Element {frame.label} has zero length"
                        )

                    # Check vertical elements are marked as columns
                    if frame.is_vertical and frame.frame_type != "Column":
                        pass  # Warning only, don't fail

                frames.append(frame)

            except (ValueError, KeyError) as e:
                raise ValueError(
                    f"Row {row_idx}: Failed to parse frame data: {e}"
                ) from e

    return frames


def merge_forces_and_geometry(
    envelopes: list[ETABSEnvelopeResult], frames: list[FrameGeometry]
) -> dict[str, tuple[ETABSEnvelopeResult, FrameGeometry | None]]:
    """Merge force envelopes with frame geometry by UniqueName.

    Args:
        envelopes: Force envelopes from beam_forces.csv
        frames: Frame geometry from frames_geometry.csv

    Returns:
        Dictionary mapping UniqueName to (envelope, geometry)
        geometry will be None if no match found

    Example:
        >>> envelopes = normalize_etabs_forces("beam_forces.csv")
        >>> frames = load_frames_geometry("frames_geometry.csv")
        >>> merged = merge_forces_and_geometry(envelopes, frames)
        >>> for uid, (env, geom) in merged.items():
        ...     if geom:
        ...         print(f"{uid}: {env.mu_knm} kNm at ({geom.point1_x}, {geom.point1_y})")
    """
    # Build geometry lookup by label (beam_id in envelopes)
    geom_by_label = {f.label: f for f in frames}

    merged = {}
    for env in envelopes:
        # Try to match by beam_id (which is Label in frames_geometry)
        geom = geom_by_label.get(env.beam_id)
        key = env.beam_id  # Use beam_id as key
        merged[key] = (env, geom)

    return merged


# =============================================================================
# Pydantic Model Conversion Functions
# =============================================================================


def to_beam_geometry(
    frame: FrameGeometry,
    *,
    width_mm: float = 300.0,
    depth_mm: float = 500.0,
    fck_mpa: float = 25.0,
    fy_mpa: float = 500.0,
    cover_mm: float = 40.0,
) -> BeamGeometry:
    """Convert FrameGeometry dataclass to Pydantic BeamGeometry model.

    This function bridges the existing etabs_import workflow with the new
    canonical data format. It converts the dataclass-based FrameGeometry
    to a validated Pydantic BeamGeometry model.

    Args:
        frame: FrameGeometry dataclass from load_frames_geometry()
        width_mm: Section width in mm (default: 300)
        depth_mm: Section depth in mm (default: 500)
        fck_mpa: Concrete strength in MPa (default: 25)
        fy_mpa: Steel yield strength in MPa (default: 500)
        cover_mm: Clear cover in mm (default: 40)

    Returns:
        Validated BeamGeometry Pydantic model

    Example:
        >>> frames = load_frames_geometry("frames_geometry.csv")
        >>> beam = to_beam_geometry(frames[0], width_mm=300, depth_mm=500)
        >>> print(beam.model_dump_json())
    """
    # Map frame_type string to FrameType enum
    frame_type_map = {
        "Beam": FrameType.BEAM,
        "Column": FrameType.COLUMN,
        "Brace": FrameType.BRACE,
    }
    frame_type = frame_type_map.get(frame.frame_type, FrameType.BEAM)

    return BeamGeometry(
        id=f"{frame.label}_{frame.story}",
        label=frame.label,
        story=frame.story,
        frame_type=frame_type,
        point1=Point3D(x=frame.point1_x, y=frame.point1_y, z=frame.point1_z),
        point2=Point3D(x=frame.point2_x, y=frame.point2_y, z=frame.point2_z),
        section=SectionProperties(
            width_mm=width_mm,
            depth_mm=depth_mm,
            fck_mpa=fck_mpa,
            fy_mpa=fy_mpa,
            cover_mm=cover_mm,
        ),
        angle=frame.angle,
        source_id=frame.unique_name,
    )


def to_beam_forces(envelope: ETABSEnvelopeResult) -> BeamForces:
    """Convert ETABSEnvelopeResult dataclass to Pydantic BeamForces model.

    This function bridges the existing etabs_import workflow with the new
    canonical data format. It converts the dataclass-based envelope result
    to a validated Pydantic BeamForces model.

    Args:
        envelope: ETABSEnvelopeResult from normalize_etabs_forces()

    Returns:
        Validated BeamForces Pydantic model

    Example:
        >>> envelopes = normalize_etabs_forces("beam_forces.csv")
        >>> forces = to_beam_forces(envelopes[0])
        >>> print(forces.model_dump_json())
    """
    return BeamForces(
        id=f"{envelope.beam_id}_{envelope.story}",
        load_case=envelope.case_id,
        mu_knm=envelope.mu_knm,
        vu_kn=envelope.vu_kn,
        pu_kn=0.0,  # Axial not in envelope
        station_count=envelope.station_count,
    )


def frames_to_beam_geometries(
    frames: list[FrameGeometry],
    section_map: dict[str, dict[str, float]] | None = None,
    *,
    default_width_mm: float = 300.0,
    default_depth_mm: float = 500.0,
    default_fck_mpa: float = 25.0,
    default_fy_mpa: float = 500.0,
    default_cover_mm: float = 40.0,
    beam_only: bool = True,
) -> list[BeamGeometry]:
    """Convert list of FrameGeometry to list of BeamGeometry models.

    Batch conversion with optional section property lookup by section_name.

    Args:
        frames: List of FrameGeometry from load_frames_geometry()
        section_map: Optional dict mapping section_name to properties.
            Each entry can have: width_mm, depth_mm, fck_mpa, fy_mpa, cover_mm
        default_width_mm: Default width if not in section_map
        default_depth_mm: Default depth if not in section_map
        default_fck_mpa: Default concrete strength
        default_fy_mpa: Default steel strength
        default_cover_mm: Default cover
        beam_only: If True (default), filter to only "Beam" type frames

    Returns:
        List of validated BeamGeometry Pydantic models

    Example:
        >>> frames = load_frames_geometry("frames_geometry.csv")
        >>> section_map = {
        ...     "B300x500": {"width_mm": 300, "depth_mm": 500},
        ...     "B400x600": {"width_mm": 400, "depth_mm": 600},
        ... }
        >>> beams = frames_to_beam_geometries(frames, section_map)
        >>> print(f"Converted {len(beams)} beams")
    """
    section_map = section_map or {}
    result: list[BeamGeometry] = []

    for frame in frames:
        # Filter by frame type if requested
        if beam_only and frame.frame_type != "Beam":
            continue

        # Get section properties from map or use defaults
        props = section_map.get(frame.section_name, {})
        width_mm = props.get("width_mm", default_width_mm)
        depth_mm = props.get("depth_mm", default_depth_mm)
        fck_mpa = props.get("fck_mpa", default_fck_mpa)
        fy_mpa = props.get("fy_mpa", default_fy_mpa)
        cover_mm = props.get("cover_mm", default_cover_mm)

        beam = to_beam_geometry(
            frame,
            width_mm=width_mm,
            depth_mm=depth_mm,
            fck_mpa=fck_mpa,
            fy_mpa=fy_mpa,
            cover_mm=cover_mm,
        )
        result.append(beam)

    return result


def envelopes_to_beam_forces(
    envelopes: list[ETABSEnvelopeResult],
) -> list[BeamForces]:
    """Convert list of ETABSEnvelopeResult to list of BeamForces models.

    Batch conversion for all envelope results.

    Args:
        envelopes: List of ETABSEnvelopeResult from normalize_etabs_forces()

    Returns:
        List of validated BeamForces Pydantic models

    Example:
        >>> envelopes = normalize_etabs_forces("beam_forces.csv")
        >>> forces = envelopes_to_beam_forces(envelopes)
        >>> print(f"Converted {len(forces)} force records")
    """
    return [to_beam_forces(env) for env in envelopes]

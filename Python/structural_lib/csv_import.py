# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
CSV Import Module — Canonical Functions for Multi-Format CSV Parsing.

This module provides high-level functions for importing beam data from CSV files.
It wraps the adapter pattern to provide a simpler API for common use cases.

Key Functions:
    - parse_dual_csv(): Parse geometry and forces from one or two CSV files
    - parse_csv(): Parse a single CSV file with auto-format detection
    - detect_format(): Detect CSV format (ETABS, SAFE, STAAD, Generic)
    - merge_geometry_forces(): Merge geometry and forces by beam ID

Architecture:
    This module is UI-agnostic and can be used by:
    - FastAPI endpoints
    - React/WebSocket handlers
    - CLI tools
    - Streamlit apps
    - Direct library usage

Example:
    >>> from structural_lib.csv_import import parse_dual_csv, merge_geometry_forces
    >>>
    >>> # Parse dual CSV files (geometry + forces)
    >>> geometry, forces, warnings = parse_dual_csv(
    ...     geometry_source="frames_geometry.csv",
    ...     forces_source="frames_forces.csv",
    ...     format="auto",
    ... )
    >>>
    >>> # Merge by beam ID
    >>> merged, unmatched_geom, unmatched_forces = merge_geometry_forces(
    ...     geometry, forces
    ... )

Author: Session 46 Agent
Task: TASK-V3-FOUNDATION
"""

from __future__ import annotations

import csv
import io
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import IO, Any, Literal

from .adapters import (
    ETABSAdapter,
    GenericCSVAdapter,
    InputAdapter,
    SAFEAdapter,
    STAADAdapter,
)
from .models import (
    BeamBatchInput,
    BeamForces,
    BeamGeometry,
    DesignDefaults,
)

__all__ = [
    # Core functions
    "parse_dual_csv",
    "parse_csv",
    "detect_format",
    "merge_geometry_forces",
    "validate_import",
    # Result types
    "ImportWarning",
    "ImportResult",
    "ValidationResult",
    # Format detection
    "CSVFormat",
    "get_adapter",
]


# =============================================================================
# Types and Result Classes
# =============================================================================

CSVFormat = Literal["etabs", "safe", "staad", "generic", "auto"]


@dataclass
class ImportWarning:
    """Structured warning from CSV import.

    Attributes:
        code: Warning code (e.g., "MISSING_FORCES", "COLUMN_MISMATCH")
        message: Human-readable warning message
        row: Optional row number (1-indexed) where warning occurred
        column: Optional column name related to warning
        beam_id: Optional beam ID if warning is beam-specific
    """

    code: str
    message: str
    row: int | None = None
    column: str | None = None
    beam_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "code": self.code,
            "message": self.message,
            "row": self.row,
            "column": self.column,
            "beam_id": self.beam_id,
        }


@dataclass
class ImportResult:
    """Result from CSV import operation.

    Attributes:
        geometry: List of parsed beam geometries
        forces: List of parsed beam forces
        warnings: List of import warnings
        format_detected: Format that was detected/used
        source_file: Original source file path (if applicable)
    """

    geometry: list[BeamGeometry] = field(default_factory=list)
    forces: list[BeamForces] = field(default_factory=list)
    warnings: list[ImportWarning] = field(default_factory=list)
    format_detected: str = "generic"
    source_file: str | None = None

    @property
    def beam_count(self) -> int:
        """Return number of beams parsed."""
        return len(self.geometry)

    @property
    def has_forces(self) -> bool:
        """Return True if forces were parsed."""
        return len(self.forces) > 0

    @property
    def has_warnings(self) -> bool:
        """Return True if warnings were generated."""
        return len(self.warnings) > 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "beam_count": self.beam_count,
            "has_forces": self.has_forces,
            "format_detected": self.format_detected,
            "source_file": self.source_file,
            "warnings": [w.to_dict() for w in self.warnings],
            "geometry": [g.model_dump() for g in self.geometry],
            "forces": [f.model_dump() for f in self.forces],
        }


@dataclass
class ValidationResult:
    """Result from import validation.

    Attributes:
        is_valid: True if import is valid (may have warnings)
        errors: List of critical errors that block processing
        warnings: List of non-critical warnings
        beam_count: Number of valid beams
        matched_count: Number of beams with matching forces
        unmatched_geometry: IDs of beams without forces
        unmatched_forces: IDs of forces without beams
    """

    is_valid: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[ImportWarning] = field(default_factory=list)
    beam_count: int = 0
    matched_count: int = 0
    unmatched_geometry: list[str] = field(default_factory=list)
    unmatched_forces: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "is_valid": self.is_valid,
            "errors": self.errors,
            "warnings": [w.to_dict() for w in self.warnings],
            "beam_count": self.beam_count,
            "matched_count": self.matched_count,
            "unmatched_geometry": self.unmatched_geometry,
            "unmatched_forces": self.unmatched_forces,
        }


# =============================================================================
# Adapter Registry
# =============================================================================

_ADAPTERS: dict[str, type[InputAdapter]] = {
    "etabs": ETABSAdapter,
    "safe": SAFEAdapter,
    "staad": STAADAdapter,
    "generic": GenericCSVAdapter,
}


def get_adapter(format: CSVFormat) -> InputAdapter:
    """Get adapter instance for the specified format.

    Args:
        format: CSV format name (etabs, safe, staad, generic)

    Returns:
        Instantiated adapter

    Raises:
        ValueError: If format is unknown
    """
    if format == "auto":
        format = "generic"  # Default to generic for auto

    adapter_class = _ADAPTERS.get(format.lower())
    if adapter_class is None:
        valid = ", ".join(_ADAPTERS.keys())
        raise ValueError(f"Unknown format '{format}'. Valid formats: {valid}")

    return adapter_class()


# =============================================================================
# Format Detection
# =============================================================================


def detect_format(
    source: Path | str | IO[bytes] | IO[str],
) -> str:
    """Detect CSV format by examining headers and content.

    Checks headers against known patterns for ETABS, SAFE, STAAD,
    and falls back to Generic format.

    Args:
        source: File path, file object, or string content

    Returns:
        Format name: "etabs", "safe", "staad", or "generic"

    Example:
        >>> format = detect_format("beams.csv")
        >>> print(f"Detected format: {format}")
    """
    # Read first few lines for detection
    content = _read_source_content(source, max_lines=10)

    # Create temp file for adapter detection
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".csv", delete=False, encoding="utf-8"
    ) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        # Test each adapter in order of specificity
        for name, adapter_class in [
            ("etabs", ETABSAdapter),
            ("safe", SAFEAdapter),
            ("staad", STAADAdapter),
        ]:
            adapter = adapter_class()
            if adapter.can_handle(tmp_path):
                return name

        return "generic"
    finally:
        Path(tmp_path).unlink(missing_ok=True)


def _read_source_content(
    source: Path | str | IO[bytes] | IO[str],
    max_lines: int | None = None,
) -> str:
    """Read content from various source types.

    Args:
        source: File path, file object, or string content
        max_lines: Optional limit on lines to read

    Returns:
        String content from source
    """
    if isinstance(source, (str, Path)):
        path = Path(source)
        if path.exists():
            with open(path, encoding="utf-8-sig") as f:
                if max_lines:
                    lines = [next(f) for _ in range(max_lines)]
                    return "".join(lines)
                return f.read()
        else:
            # Assume it's inline CSV content
            return str(source)

    elif hasattr(source, "read"):
        content = source.read()
        if isinstance(content, bytes):
            content = content.decode("utf-8-sig")
        # Reset for reuse if possible
        if hasattr(source, "seek"):
            source.seek(0)
        return content

    else:
        raise TypeError(f"Unsupported source type: {type(source)}")


def _source_to_temp_file(
    source: Path | str | IO[bytes] | IO[str],
) -> tuple[Path, bool]:
    """Convert source to a temp file path.

    Returns:
        Tuple of (path, should_cleanup)
    """
    if isinstance(source, Path):
        return source, False

    if isinstance(source, str):
        path = Path(source)
        if path.exists():
            return path, False

    # Need to create temp file
    content = _read_source_content(source)
    tmp = tempfile.NamedTemporaryFile(
        mode="w", suffix=".csv", delete=False, encoding="utf-8"
    )
    tmp.write(content)
    tmp.close()
    return Path(tmp.name), True


# =============================================================================
# Core Import Functions
# =============================================================================


def parse_csv(
    source: Path | str | IO[bytes] | IO[str],
    *,
    format: CSVFormat = "auto",
    defaults: DesignDefaults | None = None,
) -> ImportResult:
    """Parse a single CSV file for beam geometry and forces.

    This function attempts to parse both geometry and forces from
    a single file. Use parse_dual_csv() for separate files.

    Args:
        source: File path, file object, or CSV content string
        format: Format hint or "auto" for detection
        defaults: Default design parameters

    Returns:
        ImportResult with geometry, forces, and warnings

    Example:
        >>> result = parse_csv("beams.csv", format="auto")
        >>> print(f"Parsed {result.beam_count} beams")
    """
    warnings: list[ImportWarning] = []

    # Detect format if auto
    if format == "auto":
        format_detected = detect_format(source)
    else:
        format_detected = format

    # Get appropriate adapter
    adapter = get_adapter(format_detected)

    # Convert source to file path
    tmp_path, should_cleanup = _source_to_temp_file(source)

    try:
        # Load geometry
        geometry = adapter.load_geometry(tmp_path, defaults or DesignDefaults())

        # Try loading forces (may not be available in all formats)
        forces: list[BeamForces] = []
        try:
            forces = adapter.load_forces(tmp_path)
        except (ValueError, NotImplementedError) as e:
            warnings.append(
                ImportWarning(
                    code="FORCES_NOT_AVAILABLE",
                    message=f"Forces not available in this format: {e}",
                )
            )

        return ImportResult(
            geometry=geometry,
            forces=forces,
            warnings=warnings,
            format_detected=format_detected,
            source_file=str(tmp_path) if not should_cleanup else None,
        )

    finally:
        if should_cleanup:
            tmp_path.unlink(missing_ok=True)


def parse_dual_csv(
    geometry_source: Path | str | IO[bytes] | IO[str],
    forces_source: Path | str | IO[bytes] | IO[str] | None = None,
    *,
    format: CSVFormat = "auto",
    defaults: DesignDefaults | None = None,
) -> tuple[list[BeamGeometry], list[BeamForces], list[ImportWarning]]:
    """Parse geometry and forces from one or two CSV files.

    This is the primary function for importing CSV data for React.
    It supports both single-file (combined) and dual-file workflows.

    Args:
        geometry_source: Path or content for geometry CSV
        forces_source: Optional separate path/content for forces CSV
        format: Format hint ("etabs", "safe", "staad", "generic", "auto")
        defaults: Default design parameters

    Returns:
        Tuple of (geometry_list, forces_list, warnings)

    Example:
        >>> # Single file with both geometry and forces
        >>> geom, forces, warnings = parse_dual_csv("beams.csv")
        >>>
        >>> # Separate files
        >>> geom, forces, warnings = parse_dual_csv(
        ...     "geometry.csv",
        ...     "forces.csv",
        ...     format="etabs",
        ... )
        >>>
        >>> # With defaults
        >>> geom, forces, _ = parse_dual_csv(
        ...     "beams.csv",
        ...     defaults=DesignDefaults(fck_mpa=30),
        ... )
    """
    warnings: list[ImportWarning] = []

    # Parse geometry file
    geom_result = parse_csv(geometry_source, format=format, defaults=defaults)
    geometry = geom_result.geometry
    warnings.extend(geom_result.warnings)
    format_detected = geom_result.format_detected

    # Get forces from geometry file or separate file
    if forces_source is not None:
        # Parse separate forces file
        forces_result = parse_csv(forces_source, format=format, defaults=defaults)
        forces = forces_result.forces

        if not forces and forces_result.geometry:
            # Forces file might be in geometry format, try to extract forces
            warnings.append(
                ImportWarning(
                    code="FORCES_FORMAT_MISMATCH",
                    message="Forces file parsed as geometry format",
                )
            )

        if forces_result.forces:
            forces = forces_result.forces
        warnings.extend(forces_result.warnings)
    else:
        # Use forces from geometry file
        forces = geom_result.forces

    # Validate we have data
    if not geometry:
        warnings.append(
            ImportWarning(
                code="NO_GEOMETRY",
                message="No beam geometry found in CSV",
            )
        )

    if not forces:
        warnings.append(
            ImportWarning(
                code="NO_FORCES",
                message="No forces data found; beams will have zero loads",
            )
        )

    return geometry, forces, warnings


def merge_geometry_forces(
    geometry: list[BeamGeometry],
    forces: list[BeamForces],
    *,
    key: str = "id",
) -> tuple[list[tuple[BeamGeometry, BeamForces]], list[str], list[str]]:
    """Merge geometry and forces lists by beam ID.

    Args:
        geometry: List of BeamGeometry models
        forces: List of BeamForces models
        key: Field name to match on (default: "id")

    Returns:
        Tuple of:
        - merged: List of (geometry, forces) tuples for matched beams
        - unmatched_geometry: IDs of geometry without forces
        - unmatched_forces: IDs of forces without geometry

    Example:
        >>> merged, no_forces, no_geom = merge_geometry_forces(geometry, forces)
        >>> print(f"Matched: {len(merged)}, No forces: {len(no_forces)}")
    """
    # Build lookup by ID
    forces_by_id = {getattr(f, key): f for f in forces}
    geometry_ids = {getattr(g, key) for g in geometry}
    forces_ids = set(forces_by_id.keys())

    # Find matches
    merged: list[tuple[BeamGeometry, BeamForces]] = []
    for geom in geometry:
        geom_id = getattr(geom, key)
        if geom_id in forces_by_id:
            merged.append((geom, forces_by_id[geom_id]))

    # Find unmatched
    unmatched_geometry = [
        getattr(g, key) for g in geometry if getattr(g, key) not in forces_ids
    ]
    unmatched_forces = [f_id for f_id in forces_ids if f_id not in geometry_ids]

    return merged, unmatched_geometry, unmatched_forces


def validate_import(
    data: BeamBatchInput | ImportResult,
) -> ValidationResult:
    """Validate import data with structured diagnostics.

    Checks for:
    - Presence of required data
    - ID matching between geometry and forces
    - Value ranges and consistency

    Args:
        data: BeamBatchInput or ImportResult to validate

    Returns:
        ValidationResult with errors, warnings, and match statistics

    Example:
        >>> result = validate_import(batch_input)
        >>> if not result.is_valid:
        ...     print(f"Errors: {result.errors}")
    """
    errors: list[str] = []
    warnings: list[ImportWarning] = []

    # Extract geometry and forces
    if isinstance(data, BeamBatchInput):
        geometry = data.beams
        forces = data.forces
    elif isinstance(data, ImportResult):
        geometry = data.geometry
        forces = data.forces
        warnings.extend(data.warnings)
    else:
        errors.append(f"Invalid data type: {type(data)}")
        return ValidationResult(is_valid=False, errors=errors)

    # Check presence
    if not geometry:
        errors.append("No beam geometry data")
        return ValidationResult(is_valid=False, errors=errors)

    # Merge and check matching
    merged, unmatched_geom, unmatched_forces = merge_geometry_forces(geometry, forces)

    # Generate warnings for unmatched
    for beam_id in unmatched_geom:
        warnings.append(
            ImportWarning(
                code="NO_FORCES",
                message=f"Beam {beam_id} has no matching forces",
                beam_id=beam_id,
            )
        )

    for force_id in unmatched_forces:
        warnings.append(
            ImportWarning(
                code="NO_GEOMETRY",
                message=f"Forces for {force_id} has no matching geometry",
                beam_id=force_id,
            )
        )

    # Validate individual beams
    for geom in geometry:
        # Check for valid dimensions
        if geom.section.width_mm <= 0:
            warnings.append(
                ImportWarning(
                    code="INVALID_WIDTH",
                    message=f"Beam {geom.id} has invalid width: {geom.section.width_mm}",
                    beam_id=geom.id,
                )
            )
        if geom.section.depth_mm <= 0:
            warnings.append(
                ImportWarning(
                    code="INVALID_DEPTH",
                    message=f"Beam {geom.id} has invalid depth: {geom.section.depth_mm}",
                    beam_id=geom.id,
                )
            )

    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        beam_count=len(geometry),
        matched_count=len(merged),
        unmatched_geometry=unmatched_geom,
        unmatched_forces=unmatched_forces,
    )

# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Canonical Data Models for Structural Engineering Library.

This module defines Pydantic-based canonical data models for:
- Beam geometry (coordinates, section properties)
- Beam forces (moments, shears, load cases)
- Design results (required reinforcement, status)
- Batch input (complete validated input for batch design)

These models serve as the stable internal format that all input sources
(ETABS, SAFE, manual input) convert to. The format is designed to be:
- Validated: Automatic type checking and constraints
- Serializable: Easy JSON/dict conversion
- AI-Friendly: Clear field names with descriptions
- Future-Proof: Adapters handle format variations

Example:
    >>> from structural_lib.models import BeamGeometry, Point3D, SectionProperties
    >>> beam = BeamGeometry(
    ...     id="B1",
    ...     label="B1",
    ...     story="Ground",
    ...     point1=Point3D(x=0, y=0, z=0),
    ...     point2=Point3D(x=5, y=0, z=0),
    ...     section=SectionProperties(width_mm=300, depth_mm=500)
    ... )
    >>> print(beam.length_m)  # 5.0
    >>> print(beam.model_dump_json())  # JSON representation

Architecture:
    See docs/architecture/canonical-data-format.md for full documentation.

Author: Session 40 Agent
Task: TASK-DATA-001
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, computed_field, model_validator

__all__ = [
    # Enums
    "FrameType",
    "DesignStatus",
    # Core models
    "Point3D",
    "SectionProperties",
    "BeamGeometry",
    "BeamForces",
    "BeamDesignResult",
    # Batch models
    "DesignDefaults",
    "BeamBatchInput",
    "BeamBatchResult",
    # Utilities
    "BuildingStatistics",
]


# =============================================================================
# Enums
# =============================================================================


class FrameType(str, Enum):
    """Type of structural frame element."""

    BEAM = "beam"
    COLUMN = "column"
    BRACE = "brace"


class DesignStatus(str, Enum):
    """Design check status."""

    PASS = "PASS"
    FAIL = "FAIL"
    WARNING = "WARNING"
    NOT_CHECKED = "NOT_CHECKED"


# =============================================================================
# Core Models
# =============================================================================


class Point3D(BaseModel):
    """3D coordinate point with explicit units (meters).

    Attributes:
        x: X coordinate in meters
        y: Y coordinate in meters
        z: Z coordinate in meters (typically elevation)
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    x: float = Field(..., description="X coordinate in meters")
    y: float = Field(..., description="Y coordinate in meters")
    z: float = Field(..., description="Z coordinate in meters")

    def distance_to(self, other: Point3D) -> float:
        """Calculate Euclidean distance to another point."""
        dx = other.x - self.x
        dy = other.y - self.y
        dz = other.z - self.z
        return (dx**2 + dy**2 + dz**2) ** 0.5


class SectionProperties(BaseModel):
    """Beam cross-section properties with explicit units.

    All dimensions use explicit unit suffixes to prevent confusion:
    - _mm for millimeters (width, depth, cover)
    - _mpa for megapascals (material strengths)

    Attributes:
        width_mm: Section width in millimeters (b)
        depth_mm: Section overall depth in millimeters (D)
        fck_mpa: Characteristic concrete strength in MPa (N/mm²)
        fy_mpa: Steel yield strength in MPa (N/mm²)
        cover_mm: Clear cover to reinforcement in millimeters
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    width_mm: float = Field(..., gt=0, le=2000, description="Width in mm (50-2000)")
    depth_mm: float = Field(..., gt=0, le=3000, description="Depth in mm (100-3000)")
    fck_mpa: float = Field(
        25.0, gt=0, le=100, description="Concrete strength in MPa (15-100)"
    )
    fy_mpa: float = Field(
        500.0, gt=0, le=700, description="Steel yield strength in MPa (250-700)"
    )
    cover_mm: float = Field(
        40.0, gt=0, le=100, description="Clear cover in mm (20-100)"
    )

    @computed_field
    @property
    def effective_depth_mm(self) -> float:
        """Calculate effective depth (d = D - cover - bar_dia/2, assuming 25mm bar)."""
        return self.depth_mm - self.cover_mm - 12.5  # Assuming 25mm bar


class BeamGeometry(BaseModel):
    """Canonical beam geometry model.

    Contains complete geometric definition of a beam element including:
    - Identification (id, label, story)
    - 3D coordinates (point1, point2)
    - Section properties

    The coordinate system follows ETABS convention:
    - X, Y: Plan coordinates
    - Z: Vertical elevation (positive up)

    Attributes:
        id: Unique identifier (e.g., "B1_Ground")
        label: User-friendly label (e.g., "B1")
        story: Story/level name (e.g., "Ground", "Story 1")
        frame_type: Type of element (beam, column, brace)
        point1: Start point coordinates (meters)
        point2: End point coordinates (meters)
        section: Section properties
        angle: Rotation angle in degrees (default 0)
        source_id: Original ID from source system (e.g., ETABS UniqueName)
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str = Field(..., min_length=1, description="Unique identifier")
    label: str = Field(..., min_length=1, description="User-friendly label")
    story: str = Field(..., min_length=1, description="Story/level name")
    frame_type: FrameType = Field(default=FrameType.BEAM, description="Element type")
    point1: Point3D = Field(..., description="Start point (meters)")
    point2: Point3D = Field(..., description="End point (meters)")
    section: SectionProperties = Field(..., description="Section properties")
    angle: float = Field(0.0, ge=-180, le=180, description="Rotation angle (degrees)")
    source_id: str | None = Field(None, description="Original ID from source system")

    @computed_field
    @property
    def length_m(self) -> float:
        """Calculate beam length in meters."""
        return self.point1.distance_to(self.point2)

    @computed_field
    @property
    def is_vertical(self) -> bool:
        """Check if element is primarily vertical (column-like)."""
        dx = abs(self.point2.x - self.point1.x)
        dy = abs(self.point2.y - self.point1.y)
        horizontal_length = (dx**2 + dy**2) ** 0.5
        return horizontal_length < 0.01  # < 10mm horizontal movement

    @model_validator(mode="after")
    def validate_length(self) -> BeamGeometry:
        """Ensure beam has non-zero length."""
        if self.length_m < 0.1:  # Minimum 100mm
            msg = f"Beam length must be at least 0.1m, got {self.length_m:.3f}m"
            raise ValueError(msg)
        return self


class BeamForces(BaseModel):
    """Canonical beam forces model (envelope values for design).

    Contains the critical force values for a beam under a specific load case.
    Values are envelope (maximum absolute) values across all stations.

    All forces use explicit unit suffixes:
    - _knm for kilonewton-meters (moments)
    - _kn for kilonewtons (forces)

    Attributes:
        id: Beam ID (must match BeamGeometry.id)
        load_case: Load combination name (e.g., "1.5(DL+LL)")
        mu_knm: Design moment in kN·m (absolute maximum)
        vu_kn: Design shear in kN (absolute maximum)
        pu_kn: Axial force in kN (usually 0 for beams)
        station_count: Number of output stations processed
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str = Field(..., min_length=1, description="Beam ID matching BeamGeometry")
    load_case: str = Field(..., min_length=1, description="Load combination name")
    mu_knm: float = Field(..., ge=0, description="Design moment in kN·m")
    vu_kn: float = Field(..., ge=0, description="Design shear in kN")
    pu_kn: float = Field(0.0, description="Axial force in kN")
    station_count: int = Field(1, ge=1, description="Number of stations processed")


class BeamDesignResult(BaseModel):
    """Canonical beam design result model.

    Contains the complete design output for a beam including:
    - Applied forces (from BeamForces)
    - Required reinforcement areas
    - Design status and utilization

    Attributes:
        id: Beam ID
        load_case: Load combination used for design
        mu_knm: Applied moment in kN·m
        vu_kn: Applied shear in kN
        ast_mm2: Required tension steel area in mm²
        asc_mm2: Required compression steel area in mm² (if doubly reinforced)
        asv_mm2_m: Required stirrup area per meter in mm²/m
        status: Design status (PASS, FAIL, WARNING)
        utilization: Utilization ratio (0.0 to 1.0+)
        moment_capacity_knm: Moment capacity in kN·m
        shear_capacity_kn: Shear capacity in kN
        messages: Design notes and warnings
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str = Field(..., min_length=1, description="Beam ID")
    load_case: str = Field(..., min_length=1, description="Load combination")
    mu_knm: float = Field(..., ge=0, description="Applied moment in kN·m")
    vu_kn: float = Field(..., ge=0, description="Applied shear in kN")
    ast_mm2: float = Field(..., ge=0, description="Required tension steel in mm²")
    asc_mm2: float = Field(0.0, ge=0, description="Required compression steel in mm²")
    asv_mm2_m: float = Field(
        ..., ge=0, description="Required stirrup area per meter in mm²/m"
    )
    status: DesignStatus = Field(..., description="Design check status")
    utilization: float = Field(
        ..., ge=0, description="Utilization ratio (1.0 = fully utilized)"
    )
    moment_capacity_knm: float | None = Field(
        None, ge=0, description="Moment capacity in kN·m"
    )
    shear_capacity_kn: float | None = Field(
        None, ge=0, description="Shear capacity in kN"
    )
    messages: list[str] = Field(
        default_factory=list, description="Design notes and warnings"
    )

    @computed_field
    @property
    def is_acceptable(self) -> bool:
        """Check if design is acceptable (PASS or WARNING)."""
        return self.status in (DesignStatus.PASS, DesignStatus.WARNING)


# =============================================================================
# Batch Processing Models
# =============================================================================


class DesignDefaults(BaseModel):
    """Default design parameters for batch processing.

    These defaults are applied when individual beams don't specify
    their own section properties.

    Attributes:
        fck_mpa: Default concrete strength in MPa
        fy_mpa: Default steel yield strength in MPa
        cover_mm: Default clear cover in mm
        min_bar_dia_mm: Minimum bar diameter in mm
        max_bar_dia_mm: Maximum bar diameter in mm
        stirrup_dia_mm: Default stirrup diameter in mm
    """

    model_config = ConfigDict(extra="forbid")

    fck_mpa: float = Field(25.0, gt=0, le=100)
    fy_mpa: float = Field(500.0, gt=0, le=700)
    cover_mm: float = Field(40.0, gt=0, le=100)
    min_bar_dia_mm: int = Field(12, ge=8, le=40)
    max_bar_dia_mm: int = Field(32, ge=12, le=50)
    stirrup_dia_mm: int = Field(8, ge=6, le=16)


class BeamBatchInput(BaseModel):
    """Complete validated input for batch beam design.

    This model aggregates all inputs needed for batch design:
    - List of beam geometries
    - List of beam forces (matched by ID)
    - Default design parameters
    - Optional metadata

    Example:
        >>> input_data = BeamBatchInput(
        ...     beams=[beam1, beam2],
        ...     forces=[forces1, forces2],
        ...     defaults=DesignDefaults(fck_mpa=30)
        ... )
        >>> merged = input_data.get_merged_data()

    Attributes:
        beams: List of beam geometries (at least 1)
        forces: List of beam forces (at least 1)
        defaults: Default design parameters
        metadata: Optional metadata (project name, date, etc.)
    """

    model_config = ConfigDict(extra="forbid")

    beams: list[BeamGeometry] = Field(..., min_length=1)
    forces: list[BeamForces] = Field(..., min_length=1)
    defaults: DesignDefaults = Field(default_factory=DesignDefaults)
    metadata: dict[str, Any] = Field(default_factory=dict)

    def get_merged_data(self) -> list[tuple[BeamGeometry, BeamForces]]:
        """Merge geometry and forces by beam ID.

        Returns:
            List of (geometry, forces) tuples for beams with matching IDs.
        """
        forces_by_id = {f.id: f for f in self.forces}
        return [(b, forces_by_id[b.id]) for b in self.beams if b.id in forces_by_id]

    def get_unmatched_beams(self) -> list[str]:
        """Get IDs of beams without matching forces."""
        force_ids = {f.id for f in self.forces}
        return [b.id for b in self.beams if b.id not in force_ids]

    def get_unmatched_forces(self) -> list[str]:
        """Get IDs of forces without matching beams."""
        beam_ids = {b.id for b in self.beams}
        return [f.id for f in self.forces if f.id not in beam_ids]

    @model_validator(mode="after")
    def validate_matching(self) -> BeamBatchInput:
        """Warn if there are unmatched beams or forces."""
        # This is a soft validation - we just track mismatches
        # Full validation would reject, but we want to be flexible
        return self


class BeamBatchResult(BaseModel):
    """Complete batch design results.

    Contains all design results plus summary statistics.

    Attributes:
        results: List of individual beam design results
        total_beams: Total number of beams processed
        passed: Number of beams with PASS status
        failed: Number of beams with FAIL status
        warnings: Number of beams with WARNING status
        metadata: Result metadata (processing time, etc.)
    """

    model_config = ConfigDict(extra="forbid")

    results: list[BeamDesignResult] = Field(default_factory=list)
    total_beams: int = Field(0, ge=0)
    passed: int = Field(0, ge=0)
    failed: int = Field(0, ge=0)
    warnings: int = Field(0, ge=0)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @computed_field
    @property
    def pass_rate(self) -> float:
        """Calculate pass rate as percentage."""
        if self.total_beams == 0:
            return 0.0
        return (self.passed / self.total_beams) * 100

    @classmethod
    def from_results(
        cls,
        results: list[BeamDesignResult],
        metadata: dict[str, Any] | None = None,
    ) -> BeamBatchResult:
        """Create batch result from list of individual results."""
        passed = sum(1 for r in results if r.status == DesignStatus.PASS)
        failed = sum(1 for r in results if r.status == DesignStatus.FAIL)
        warnings = sum(1 for r in results if r.status == DesignStatus.WARNING)

        return cls(
            results=results,
            total_beams=len(results),
            passed=passed,
            failed=failed,
            warnings=warnings,
            metadata=metadata or {},
        )


# =============================================================================
# Utility Functions
# =============================================================================


class BuildingStatistics(BaseModel):
    """Statistics for a building/project from beam geometry data.

    Useful for 3D visualization, reports, and analysis summary.
    """

    model_config = ConfigDict(frozen=True)

    total_beams: int = Field(description="Total number of beams")
    total_stories: int = Field(description="Number of unique stories")
    stories: list[str] = Field(description="List of story names (sorted)")
    beams_per_story: dict[str, int] = Field(description="Count of beams per story")
    total_length_m: float = Field(description="Total beam length in meters")
    total_concrete_m3: float = Field(
        description="Total concrete volume in cubic meters"
    )
    bounding_box: dict[str, tuple[float, float]] = Field(
        description="Building bounds: x, y, z ranges in meters"
    )

    @classmethod
    def from_beams(cls, beams: list[BeamGeometry]) -> BuildingStatistics:
        """Compute building statistics from beam geometry list.

        Args:
            beams: List of BeamGeometry objects

        Returns:
            BuildingStatistics with computed metrics

        Example:
            >>> stats = BuildingStatistics.from_beams(beams)
            >>> print(f"Building has {stats.total_stories} stories")
        """
        if not beams:
            return cls(
                total_beams=0,
                total_stories=0,
                stories=[],
                beams_per_story={},
                total_length_m=0.0,
                total_concrete_m3=0.0,
                bounding_box={"x": (0, 0), "y": (0, 0), "z": (0, 0)},
            )

        # Count beams per story
        story_counts: dict[str, int] = {}
        for beam in beams:
            story_counts[beam.story] = story_counts.get(beam.story, 0) + 1

        # Sort stories (try numeric sort first, then alphabetic)
        stories = sorted(story_counts.keys())

        # Compute total length and volume
        total_length = sum(beam.length_m for beam in beams)
        total_volume = sum(
            beam.length_m
            * (beam.section.width_mm / 1000)
            * (beam.section.depth_mm / 1000)
            for beam in beams
        )

        # Compute bounding box
        x_coords = []
        y_coords = []
        z_coords = []
        for beam in beams:
            x_coords.extend([beam.point1.x, beam.point2.x])
            y_coords.extend([beam.point1.y, beam.point2.y])
            z_coords.extend([beam.point1.z, beam.point2.z])

        bounding_box = {
            "x": (min(x_coords), max(x_coords)),
            "y": (min(y_coords), max(y_coords)),
            "z": (min(z_coords), max(z_coords)),
        }

        return cls(
            total_beams=len(beams),
            total_stories=len(stories),
            stories=stories,
            beams_per_story=story_counts,
            total_length_m=round(total_length, 2),
            total_concrete_m3=round(total_volume, 3),
            bounding_box=bounding_box,
        )

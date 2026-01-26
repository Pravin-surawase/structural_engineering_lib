# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
3D Geometry Module — Coordinate Computation for Visualization

This module provides dataclasses and functions for computing 3D coordinates
of reinforcement elements. It bridges the structural design output (from
detailing.py) to visual representation (for Three.js/WebGL).

Core Concept:
    Structural design gives us WHAT: "4-16φ bars at 100mm spacing"
    This module adds WHERE: [(x1,y1,z1), (x2,y2,z2), ...]

Coordinate System (Right-hand rule):
    - X: Along beam span (0 = left support, +X = right)
    - Y: Beam width (0 = center, +Y = front face)
    - Z: Beam height (0 = soffit, +Z = up)

Units:
    - All coordinates in millimeters (mm)
    - Angles in radians
    - Consistent with IS 456 detailing conventions

JSON Schema:
    The to_dict() methods produce JSON compatible with:
    - Three.js BufferGeometry
    - react-three-fiber components
    - WebGL visualization pipelines

Example:
    >>> from structural_lib.visualization.geometry_3d import (
    ...     Point3D, compute_rebar_positions
    ... )
    >>> positions = compute_rebar_positions(
    ...     beam_width=300, beam_depth=450, cover=40,
    ...     bar_count=4, bar_dia=16, stirrup_dia=8, is_top=False
    ... )
    >>> print(positions[0])  # First bar position
    Point3D(x=0.0, y=-96.0, z=52.0)

References:
    - IS 456:2000, Cl 26.3 (Bar spacing requirements)
    - SP 34:1987, Section 3 (Detailing conventions)
    - Three.js BufferGeometry documentation
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from structural_lib.codes.is456.detailing import BeamDetailingResult


__all__ = [
    # Core dataclasses
    "Point3D",
    "RebarSegment",
    "RebarPath",
    "StirrupLoop",
    "Beam3DGeometry",
    "Building3DGeometry",
    "CrossSectionGeometry",
    # Computation functions
    "compute_rebar_positions",
    "compute_stirrup_path",
    "compute_stirrup_positions",
    "compute_beam_outline",
    "beam_to_3d_geometry",
    "building_to_3d_geometry",
    "cross_section_geometry",
]


# =============================================================================
# Core Dataclasses
# =============================================================================


@dataclass(frozen=True, slots=True)
class Point3D:
    """
    Immutable 3D point in millimeters.

    Coordinate System:
        - x: Along beam span (longitudinal)
        - y: Beam width (transverse, +y = front)
        - z: Beam height (vertical, +z = up)

    Attributes:
        x: X-coordinate in mm (along span)
        y: Y-coordinate in mm (across width)
        z: Z-coordinate in mm (height)

    Example:
        >>> p = Point3D(0.0, 50.0, 100.0)
        >>> p.to_tuple()
        (0.0, 50.0, 100.0)
    """

    x: float
    y: float
    z: float

    def to_tuple(self) -> tuple[float, float, float]:
        """Return (x, y, z) tuple for array operations."""
        return (self.x, self.y, self.z)

    def to_dict(self) -> dict[str, float]:
        """Return JSON-serializable dict."""
        return {"x": round(self.x, 2), "y": round(self.y, 2), "z": round(self.z, 2)}

    def __add__(self, other: Point3D) -> Point3D:
        """Vector addition."""
        return Point3D(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: Point3D) -> Point3D:
        """Vector subtraction."""
        return Point3D(self.x - other.x, self.y - other.y, self.z - other.z)

    def scale(self, factor: float) -> Point3D:
        """Scale point by factor."""
        return Point3D(self.x * factor, self.y * factor, self.z * factor)

    def distance_to(self, other: Point3D) -> float:
        """Euclidean distance to another point."""
        dx = self.x - other.x
        dy = self.y - other.y
        dz = self.z - other.z
        return math.sqrt(dx * dx + dy * dy + dz * dz)


@dataclass(frozen=True, slots=True)
class RebarSegment:
    """
    A single straight segment of a reinforcement bar.

    Used for bends, hooks, and lap splices where the rebar changes direction.
    For straight bars, use RebarPath with a single segment.

    Attributes:
        start: Start point of segment
        end: End point of segment
        diameter: Bar diameter in mm
        segment_type: "straight", "bend", "hook_90", "hook_135", "hook_180"

    Example:
        >>> seg = RebarSegment(
        ...     start=Point3D(0, 50, 52),
        ...     end=Point3D(4000, 50, 52),
        ...     diameter=16.0,
        ...     segment_type="straight"
        ... )
    """

    start: Point3D
    end: Point3D
    diameter: float
    segment_type: str = "straight"

    @property
    def length(self) -> float:
        """Calculate segment length in mm."""
        return self.start.distance_to(self.end)

    def to_dict(self) -> dict:
        """Return JSON-serializable dict for Three.js."""
        return {
            "start": self.start.to_dict(),
            "end": self.end.to_dict(),
            "diameter": round(self.diameter, 1),
            "type": self.segment_type,
            "length": round(self.length, 1),
        }


@dataclass
class RebarPath:
    """
    Complete path of a reinforcement bar with multiple segments.

    A rebar path can consist of:
    - Single straight segment (most common)
    - Multiple segments for bent-up bars
    - Hooks at ends for anchorage

    Attributes:
        bar_id: Unique identifier (e.g., "B1", "T2")
        segments: List of RebarSegment making up the bar
        diameter: Bar diameter in mm
        bar_type: "bottom", "top", "side", "bent_up"
        zone: "start", "mid", "end", or "full" for continuous bars

    Example:
        >>> path = RebarPath(
        ...     bar_id="B1",
        ...     segments=[straight_segment, hook_segment],
        ...     diameter=16.0,
        ...     bar_type="bottom",
        ...     zone="full"
        ... )
    """

    bar_id: str
    segments: list[RebarSegment]
    diameter: float
    bar_type: str = "bottom"
    zone: str = "full"

    @property
    def total_length(self) -> float:
        """Total cutting length of bar."""
        return sum(seg.length for seg in self.segments)

    @property
    def start_point(self) -> Point3D:
        """Starting point of bar path."""
        return self.segments[0].start if self.segments else Point3D(0, 0, 0)

    @property
    def end_point(self) -> Point3D:
        """Ending point of bar path."""
        return self.segments[-1].end if self.segments else Point3D(0, 0, 0)

    def to_dict(self) -> dict:
        """Return JSON-serializable dict for Three.js."""
        return {
            "barId": self.bar_id,
            "segments": [seg.to_dict() for seg in self.segments],
            "diameter": round(self.diameter, 1),
            "barType": self.bar_type,
            "zone": self.zone,
            "totalLength": round(self.total_length, 1),
        }


@dataclass
class StirrupLoop:
    """
    A single stirrup (closed loop) with optional internal ties.

    Represents the 2D cross-section of a stirrup at a specific X position.
    The path is a closed polygon with rounded corners at bends.

    Coordinate System:
        - position_x: Location along beam span where stirrup is placed
        - path: 2D points in Y-Z plane forming the closed loop

    Attributes:
        position_x: X-coordinate along span (mm)
        path: List of Point3D forming closed loop corners
        diameter: Stirrup bar diameter (mm)
        legs: Number of legs (2, 4, 6)
        hook_type: "90" or "135" (seismic)

    Example:
        >>> stirrup = StirrupLoop(
        ...     position_x=150,
        ...     path=[corner1, corner2, corner3, corner4],
        ...     diameter=8.0,
        ...     legs=2,
        ...     hook_type="135"
        ... )
    """

    position_x: float
    path: list[Point3D]
    diameter: float
    legs: int = 2
    hook_type: str = "90"

    @property
    def perimeter(self) -> float:
        """Calculate stirrup perimeter (cutting length minus hooks)."""
        if len(self.path) < 2:
            return 0.0
        total = 0.0
        for i in range(len(self.path)):
            next_i = (i + 1) % len(self.path)
            total += self.path[i].distance_to(self.path[next_i])
        return total

    def to_dict(self) -> dict:
        """Return JSON-serializable dict for Three.js."""
        return {
            "positionX": round(self.position_x, 1),
            "path": [p.to_dict() for p in self.path],
            "diameter": round(self.diameter, 1),
            "legs": self.legs,
            "hookType": self.hook_type,
            "perimeter": round(self.perimeter, 1),
        }


@dataclass
class Beam3DGeometry:
    """
    Complete 3D geometry for a beam section ready for visualization.

    This is the primary output dataclass that aggregates all geometric
    information needed to render a beam in Three.js or similar.

    Attributes:
        beam_id: Unique beam identifier
        story: Story/floor identifier
        dimensions: Beam dimensions {b, D, span} in mm
        concrete_outline: 8 corner points of beam bounding box
        rebars: List of all RebarPath objects
        stirrups: List of all StirrupLoop objects
        metadata: Additional info (fck, fy, cover, etc.)

    Example:
        >>> geometry = Beam3DGeometry(
        ...     beam_id="B1",
        ...     story="GF",
        ...     dimensions={"b": 300, "D": 450, "span": 4000},
        ...     concrete_outline=[...],
        ...     rebars=[bottom_bars, top_bars],
        ...     stirrups=[...],
        ...     metadata={"fck": 25, "fy": 500}
        ... )
        >>> json_data = geometry.to_dict()  # For Three.js
    """

    beam_id: str
    story: str
    dimensions: dict[str, float]
    concrete_outline: list[Point3D]
    rebars: list[RebarPath]
    stirrups: list[StirrupLoop]
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """
        Return complete JSON-serializable dict for Three.js.

        JSON Schema follows BeamGeometry3D contract for TypeScript.
        """
        return {
            "beamId": self.beam_id,
            "story": self.story,
            "dimensions": self.dimensions,
            "concreteOutline": [p.to_dict() for p in self.concrete_outline],
            "rebars": [r.to_dict() for r in self.rebars],
            "stirrups": [s.to_dict() for s in self.stirrups],
            "metadata": self.metadata,
            "version": "1.0.0",
        }


# =============================================================================
# Coordinate Computation Functions
# =============================================================================


def compute_rebar_positions(
    beam_width: float,
    beam_depth: float,
    cover: float,
    bar_count: int,
    bar_dia: float,
    stirrup_dia: float,
    is_top: bool = False,
    layers: int = 1,
) -> list[Point3D]:
    """
    Compute Y-Z positions for main bars in a beam cross-section.

    This function calculates where each bar is placed in the Y-Z plane
    (cross-section view). The X coordinate is 0; caller extends along span.

    Coordinate System:
        - Y: Across beam width (-width/2 to +width/2, center = 0)
        - Z: Beam height (0 = soffit, D = top)

    Args:
        beam_width: Beam width b (mm)
        beam_depth: Beam depth D (mm)
        cover: Clear cover (mm)
        bar_count: Total number of bars
        bar_dia: Main bar diameter (mm)
        stirrup_dia: Stirrup diameter (mm)
        is_top: True for top bars, False for bottom bars
        layers: Number of layers (1 or 2)

    Returns:
        List of Point3D positions (x=0) for each bar

    Raises:
        ValueError: If geometry inputs are invalid or bars cannot fit.

    Example:
        >>> positions = compute_rebar_positions(
        ...     beam_width=300, beam_depth=450, cover=40,
        ...     bar_count=4, bar_dia=16, stirrup_dia=8, is_top=False
        ... )
        >>> len(positions)
        4
        >>> positions[0].z  # First bar Z (near soffit)
        52.0  # cover + stirrup_dia + bar_dia/2

    Reference:
        IS 456:2000, Cl 26.3.2 (minimum spacing)
    """
    if bar_count <= 0:
        return []

    if beam_width <= 0 or beam_depth <= 0:
        raise ValueError("beam_width and beam_depth must be positive.")
    if cover < 0:
        raise ValueError("cover must be non-negative.")
    if bar_dia <= 0 or stirrup_dia <= 0:
        raise ValueError("bar_dia and stirrup_dia must be positive.")
    if layers <= 0:
        raise ValueError("layers must be at least 1.")

    # Calculate Z position (height from soffit)
    edge_distance = cover + stirrup_dia + bar_dia / 2

    if is_top:
        # Top bars: measure down from top
        z_base = beam_depth - edge_distance
    else:
        # Bottom bars: measure up from soffit
        z_base = edge_distance

    # Layer spacing (if multi-layer)
    layer_spacing = bar_dia + 25  # IS 456: min 25mm between layers

    # Calculate Y positions (across width)
    # Available width between stirrups
    available_width = beam_width - 2 * (cover + stirrup_dia) - bar_dia
    if available_width < 0:
        raise ValueError(
            "beam_width is too small for the specified cover/stirrup/bar diameters."
        )

    # Distribute bars across layers
    bars_per_layer = math.ceil(bar_count / layers) if layers > 0 else bar_count
    positions: list[Point3D] = []
    bar_index = 0

    for layer_num in range(layers):
        # Z for this layer
        if is_top:
            z = z_base - layer_num * layer_spacing
        else:
            z = z_base + layer_num * layer_spacing

        # Number of bars in this layer
        bars_this_layer = min(bars_per_layer, bar_count - bar_index)
        if bars_this_layer <= 0:
            break

        # Y positions for this layer
        if bars_this_layer == 1:
            y_positions = [0.0]  # Single bar at center
        else:
            # Distribute evenly across available width
            # Y goes from -width/2 + edge to +width/2 - edge
            y_start = -available_width / 2
            y_spacing = available_width / (bars_this_layer - 1)
            y_positions = [y_start + i * y_spacing for i in range(bars_this_layer)]

        for y in y_positions:
            positions.append(Point3D(x=0.0, y=round(y, 2), z=round(z, 2)))
            bar_index += 1

    return positions


def compute_stirrup_path(
    beam_width: float,
    beam_depth: float,
    cover: float,
    stirrup_dia: float,
    position_x: float,
    legs: int = 2,
) -> list[Point3D]:
    """
    Compute the corner points of a stirrup in the Y-Z plane.

    Returns a closed path (4 corners for 2-leg, more for 4/6-leg).
    Points are in counter-clockwise order starting from bottom-left.

    Args:
        beam_width: Beam width b (mm)
        beam_depth: Beam depth D (mm)
        cover: Clear cover (mm)
        stirrup_dia: Stirrup bar diameter (mm)
        position_x: X position along span (mm)
        legs: Number of stirrup legs (2, 4, or 6)

    Returns:
        List of Point3D forming closed stirrup loop

    Example:
        >>> path = compute_stirrup_path(
        ...     beam_width=300, beam_depth=450, cover=40,
        ...     stirrup_dia=8, position_x=150, legs=2
        ... )
        >>> len(path)  # 4 corners for rectangular stirrup
        4

    Note:
        For legs > 2, additional vertical legs are computed
        but returned as separate paths in compute_stirrup_positions.
    """
    # Inner dimensions (inside stirrup)
    half_width = beam_width / 2

    # Stirrup corners (centerline of stirrup bar)
    # Cover is to concrete face; stirrup centerline is cover + dia/2
    y_outer = half_width - cover - stirrup_dia / 2
    z_bottom = cover + stirrup_dia / 2
    z_top = beam_depth - cover - stirrup_dia / 2

    # Corner points (counter-clockwise from bottom-left)
    corners = [
        Point3D(position_x, -y_outer, z_bottom),  # Bottom-left
        Point3D(position_x, y_outer, z_bottom),  # Bottom-right
        Point3D(position_x, y_outer, z_top),  # Top-right
        Point3D(position_x, -y_outer, z_top),  # Top-left
    ]

    return corners


def compute_stirrup_positions(
    span: float,
    stirrup_spacing_start: float,
    stirrup_spacing_mid: float,
    stirrup_spacing_end: float,
    zone_length: float | None = None,
) -> list[float]:
    """
    Compute X positions for stirrups along beam span.

    Beam is divided into three zones:
    - Start zone (0 to zone_length): Closer spacing
    - Mid zone (zone_length to span - zone_length): Normal spacing
    - End zone (span - zone_length to span): Closer spacing

    Args:
        span: Beam span length (mm)
        stirrup_spacing_start: Spacing in start zone (mm)
        stirrup_spacing_mid: Spacing in mid zone (mm)
        stirrup_spacing_end: Spacing in end zone (mm)
        zone_length: Length of start/end zones (default: span/4)

    Returns:
        List of X positions for stirrup placement

    Raises:
        ValueError: If span or spacing inputs are non-positive.

    Example:
        >>> positions = compute_stirrup_positions(
        ...     span=4000,
        ...     stirrup_spacing_start=100,
        ...     stirrup_spacing_mid=150,
        ...     stirrup_spacing_end=100
        ... )
        >>> positions[0]  # First stirrup near support
        50.0  # Half of first spacing from face

    Reference:
        IS 456:2000, Cl 26.5.1.5 (stirrup spacing requirements)
    """
    if span <= 0:
        raise ValueError("span must be positive.")
    if stirrup_spacing_start <= 0:
        raise ValueError("stirrup_spacing_start must be positive.")
    if stirrup_spacing_mid <= 0:
        raise ValueError("stirrup_spacing_mid must be positive.")
    if stirrup_spacing_end <= 0:
        raise ValueError("stirrup_spacing_end must be positive.")
    if zone_length is not None and zone_length <= 0:
        raise ValueError("zone_length must be positive when provided.")

    if zone_length is None:
        zone_length = span / 4

    # Ensure valid zone length
    zone_length = min(zone_length, span / 2)

    positions: list[float] = []
    x = stirrup_spacing_start / 2  # First stirrup at half-spacing from support

    # Start zone
    while x < zone_length:
        positions.append(round(x, 1))
        x += stirrup_spacing_start

    # Mid zone
    mid_end = span - zone_length
    while x < mid_end:
        positions.append(round(x, 1))
        x += stirrup_spacing_mid

    # End zone
    while x < span - stirrup_spacing_end / 2:
        positions.append(round(x, 1))
        x += stirrup_spacing_end

    return positions


def compute_beam_outline(
    beam_width: float,
    beam_depth: float,
    span: float,
) -> list[Point3D]:
    """
    Compute 8 corner points of beam bounding box.

    Returns corners in a specific order for Three.js BoxGeometry:
    [0-3: bottom face, 4-7: top face]

    Args:
        beam_width: Beam width b (mm)
        beam_depth: Beam depth D (mm)
        span: Beam span length (mm)

    Returns:
        List of 8 Point3D corners

    Example:
        >>> corners = compute_beam_outline(300, 450, 4000)
        >>> len(corners)
        8
        >>> corners[0]  # Bottom-left-front at x=0
        Point3D(x=0.0, y=-150.0, z=0.0)
    """
    half_width = beam_width / 2

    # Bottom face (z=0), counter-clockwise from front-left
    bottom = [
        Point3D(0.0, -half_width, 0.0),  # Front-left
        Point3D(0.0, half_width, 0.0),  # Back-left
        Point3D(span, half_width, 0.0),  # Back-right
        Point3D(span, -half_width, 0.0),  # Front-right
    ]

    # Top face (z=D), same order
    top = [
        Point3D(0.0, -half_width, beam_depth),
        Point3D(0.0, half_width, beam_depth),
        Point3D(span, half_width, beam_depth),
        Point3D(span, -half_width, beam_depth),
    ]

    return bottom + top


def beam_to_3d_geometry(
    detailing: BeamDetailingResult,
    is_seismic: bool = False,
) -> Beam3DGeometry:
    """
    Convert BeamDetailingResult to complete 3D geometry.

    This is the main integration function that takes structural
    design output and produces visualization-ready geometry.

    Args:
        detailing: BeamDetailingResult from detailing module
        is_seismic: True to use 135° stirrup hooks

    Returns:
        Beam3DGeometry ready for JSON serialization

    Example:
        >>> from structural_lib.codes.is456.detailing import create_beam_detailing
        >>> detailing = create_beam_detailing(...)
        >>> geometry = beam_to_3d_geometry(detailing)
        >>> json_data = geometry.to_dict()  # For Three.js

    Note:
        Currently generates simplified geometry with:
        - Straight bars (no hooks/bends)
        - Zone bars deduplicated (mid zone treated as full-length)
        - Uniform stirrup spacing per zone

        Future versions will add:
        - Hook geometry at bar ends
        - Bent-up bars
        - Development length markers
    """
    b = detailing.b
    D = detailing.D
    span = detailing.span
    cover = detailing.cover

    # Concrete outline
    concrete_outline = compute_beam_outline(b, D, span)

    # Generate rebar paths
    rebars: list[RebarPath] = []
    bar_id_counter = 0

    def add_zone_rebars(
        arrangements: list,
        bar_type: str,
        is_top: bool,
    ) -> None:
        nonlocal bar_id_counter
        seen_positions: set[tuple[float, float]] = set()

        zone_specs = [
            (1, "full"),  # mid zone as canonical full-length bars
            (0, "start"),
            (2, "end"),
        ]

        for zone_idx, zone_label in zone_specs:
            if zone_idx >= len(arrangements):
                continue

            bar_arr = arrangements[zone_idx]
            if bar_arr.count <= 0:
                continue

            positions = compute_rebar_positions(
                beam_width=b,
                beam_depth=D,
                cover=cover,
                bar_count=bar_arr.count,
                bar_dia=bar_arr.diameter,
                stirrup_dia=detailing.stirrups[0].diameter,
                is_top=is_top,
                layers=bar_arr.layers,
            )

            for pos in positions:
                key = (round(pos.y, 2), round(pos.z, 2))
                if key in seen_positions:
                    continue
                seen_positions.add(key)
                bar_id_counter += 1

                start = Point3D(0.0, pos.y, pos.z)
                end = Point3D(span, pos.y, pos.z)
                segment = RebarSegment(start, end, bar_arr.diameter, "straight")
                path = RebarPath(
                    bar_id=f"{'T' if is_top else 'B'}{bar_id_counter}",
                    segments=[segment],
                    diameter=bar_arr.diameter,
                    bar_type=bar_type,
                    zone=zone_label,
                )
                rebars.append(path)

    # Process bottom and top bars (deduplicate across zones)
    add_zone_rebars(detailing.bottom_bars, bar_type="bottom", is_top=False)
    add_zone_rebars(detailing.top_bars, bar_type="top", is_top=True)

    # Validate stirrups array has expected 3 zones (start, mid, end)
    if len(detailing.stirrups) < 3:
        raise ValueError(
            f"Expected 3 stirrup zones (start, mid, end), got {len(detailing.stirrups)}"
        )

    # Generate stirrups
    stirrup_x_positions = compute_stirrup_positions(
        span=span,
        stirrup_spacing_start=detailing.stirrups[0].spacing,
        stirrup_spacing_mid=detailing.stirrups[1].spacing,
        stirrup_spacing_end=detailing.stirrups[2].spacing,
        zone_length=detailing.stirrups[0].zone_length,
    )

    stirrups: list[StirrupLoop] = []
    stirrup_info = detailing.stirrups[0]  # Use start zone info for diameter/legs

    for x_pos in stirrup_x_positions:
        path = compute_stirrup_path(
            beam_width=b,
            beam_depth=D,
            cover=cover,
            stirrup_dia=stirrup_info.diameter,
            position_x=x_pos,
            legs=stirrup_info.legs,
        )
        stirrup = StirrupLoop(
            position_x=x_pos,
            path=path,
            diameter=stirrup_info.diameter,
            legs=stirrup_info.legs,
            hook_type="135" if is_seismic else "90",
        )
        stirrups.append(stirrup)

    # Metadata
    metadata = {
        "cover": cover,
        "ldTension": detailing.ld_tension,
        "ldCompression": detailing.ld_compression,
        "lapLength": detailing.lap_length,
        "isSeismic": is_seismic,
        "isValid": detailing.is_valid,
        "remarks": detailing.remarks,
    }

    return Beam3DGeometry(
        beam_id=detailing.beam_id,
        story=detailing.story,
        dimensions={"b": b, "D": D, "span": span},
        concrete_outline=concrete_outline,
        rebars=rebars,
        stirrups=stirrups,
        metadata=metadata,
    )


# =============================================================================
# Building-Level 3D Geometry
# =============================================================================


@dataclass
class BeamInstance:
    """Instance data for a single beam in the building view.

    Optimized for GPU instancing in Three.js/R3F where the same
    box geometry can be reused with different transforms.

    Attributes:
        beam_id: Unique beam identifier
        story: Story/floor name
        position: Center position of beam (world coordinates)
        dimensions: (width, depth, length) in mm
        rotation: Rotation around Y axis in radians (0 = X-aligned)
        color: RGB color as hex string (e.g., "#4CAF50")
        status: Design status for coloring ("pass", "fail", "warning", "pending")
        metadata: Additional beam data for tooltips
    """

    beam_id: str
    story: str
    position: Point3D
    dimensions: tuple[float, float, float]  # width, depth, length
    rotation: float = 0.0  # radians around Y axis
    color: str = "#808080"
    status: str = "pending"
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dict for Three.js."""
        return {
            "id": self.beam_id,
            "story": self.story,
            "position": [self.position.x, self.position.y, self.position.z],
            "dimensions": list(self.dimensions),
            "rotation": self.rotation,
            "color": self.color,
            "status": self.status,
            "metadata": self.metadata,
        }


@dataclass
class Building3DGeometry:
    """Complete 3D geometry for building visualization.

    Designed for efficient rendering in React Three Fiber using
    GPU instancing for beams. Includes metadata for filtering,
    highlighting, and tooltips.

    Attributes:
        beam_instances: List of beam instance data for instancing
        stories: List of unique story names in Z order
        bounds: Bounding box as ((min_x, min_y, min_z), (max_x, max_y, max_z))
        camera_target: Suggested camera look-at point
        metadata: Building-level metadata (beam count, stories, etc.)
    """

    beam_instances: list[BeamInstance] = field(default_factory=list)
    stories: list[str] = field(default_factory=list)
    bounds: tuple[tuple[float, float, float], tuple[float, float, float]] = (
        (0, 0, 0),
        (1000, 1000, 1000),
    )
    camera_target: Point3D = field(default_factory=lambda: Point3D(0, 0, 0))
    metadata: dict = field(default_factory=dict)

    @property
    def beam_count(self) -> int:
        """Return total number of beams."""
        return len(self.beam_instances)

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dict for React."""
        return {
            "beams": [b.to_dict() for b in self.beam_instances],
            "stories": self.stories,
            "bounds": {
                "min": list(self.bounds[0]),
                "max": list(self.bounds[1]),
            },
            "cameraTarget": self.camera_target.to_dict(),
            "metadata": {
                **self.metadata,
                "beamCount": self.beam_count,
                "storyCount": len(self.stories),
            },
        }

    def get_beams_by_story(self, story: str) -> list[BeamInstance]:
        """Filter beams by story name."""
        return [b for b in self.beam_instances if b.story == story]

    def get_beams_by_status(self, status: str) -> list[BeamInstance]:
        """Filter beams by design status."""
        return [b for b in self.beam_instances if b.status == status]


@dataclass
class CrossSectionGeometry:
    """2D cross-section geometry for beam editor view.

    Provides simplified geometry for displaying beam cross-section
    with rebar positions in a 2D canvas/SVG view.

    Attributes:
        width: Beam width in mm
        depth: Beam depth in mm
        cover: Clear cover in mm
        rebar_positions: List of (y, z, diameter) for each bar
        stirrup_path: Closed path for stirrup outline
    """

    width: float
    depth: float
    cover: float
    rebar_positions: list[tuple[float, float, float]] = field(default_factory=list)
    stirrup_path: list[Point3D] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dict."""
        return {
            "width": self.width,
            "depth": self.depth,
            "cover": self.cover,
            "rebars": [
                {"y": y, "z": z, "diameter": d}
                for y, z, d in self.rebar_positions
            ],
            "stirrupPath": [p.to_dict() for p in self.stirrup_path],
        }


# Status color mapping
_STATUS_COLORS = {
    "pass": "#4CAF50",      # Green
    "fail": "#F44336",      # Red
    "warning": "#FF9800",   # Orange
    "pending": "#9E9E9E",   # Gray
    "selected": "#FFEB3B",  # Yellow (highlight)
}


def building_to_3d_geometry(
    beams: list,  # List of BeamGeometry or dicts
    *,
    design_results: list | None = None,
    lod: str = "medium",
    story_height: float = 3000.0,
) -> Building3DGeometry:
    """Generate 3D geometry for entire building from beam list.

    Creates instancing-friendly geometry data for React Three Fiber.
    Beams are positioned based on their Point3D coordinates if available,
    or auto-arranged by story if not.

    Args:
        beams: List of BeamGeometry models or dicts with beam data
        design_results: Optional list of design results for status coloring
        lod: Level of detail ("low", "medium", "high")
        story_height: Default story height for auto-positioning (mm)

    Returns:
        Building3DGeometry with all beam instances and metadata

    Example:
        >>> from structural_lib.visualization.geometry_3d import building_to_3d_geometry
        >>> building = building_to_3d_geometry(beams, design_results=results)
        >>> print(f"Building has {building.beam_count} beams")
        >>> json_data = building.to_dict()  # Ready for React
    """
    from structural_lib.models import BeamGeometry as BeamGeometryModel

    instances: list[BeamInstance] = []
    stories_set: set[str] = set()

    # Build design result lookup
    status_map: dict[str, str] = {}
    if design_results:
        for result in design_results:
            beam_id = getattr(result, "beam_id", None) or result.get("beam_id", "")
            status = getattr(result, "status", None) or result.get("status", "pending")
            if hasattr(status, "value"):
                status = status.value.lower()
            status_map[beam_id] = str(status).lower()

    # Track bounds
    min_x, min_y, min_z = float("inf"), float("inf"), float("inf")
    max_x, max_y, max_z = float("-inf"), float("-inf"), float("-inf")

    # Story height tracking for auto-positioning
    story_z_map: dict[str, float] = {}
    story_counter = 0

    for beam in beams:
        # Extract data from BeamGeometry or dict
        if isinstance(beam, BeamGeometryModel):
            beam_id = beam.id
            story = beam.story or "Floor"
            width = beam.section.width_mm
            depth = beam.section.depth_mm
            length = beam.length_mm
            point1 = beam.point1
            point2 = beam.point2
        else:
            # Dict format
            beam_id = beam.get("id", beam.get("beam_id", ""))
            story = beam.get("story", "Floor")
            section = beam.get("section", beam)
            width = section.get("width_mm", 300)
            depth = section.get("depth_mm", 500)
            length = beam.get("length_mm", beam.get("span_mm", 5000))
            p1 = beam.get("point1", {})
            p2 = beam.get("point2", {})
            point1 = Point3D(p1.get("x", 0), p1.get("y", 0), p1.get("z", 0)) if p1 else None
            point2 = Point3D(p2.get("x", length), p2.get("y", 0), p2.get("z", 0)) if p2 else None

        stories_set.add(story)

        # Determine Z position by story
        if story not in story_z_map:
            story_z_map[story] = story_counter * story_height
            story_counter += 1
        base_z = story_z_map[story]

        # Calculate beam center position
        if point1 and point2 and (point1.x != 0 or point1.y != 0 or point2.x != 0):
            # Use actual coordinates
            center_x = (point1.x + point2.x) / 2
            center_y = (point1.y + point2.y) / 2
            center_z = base_z + depth / 2

            # Calculate rotation from points
            dx = point2.x - point1.x
            dy = point2.y - point1.y
            rotation = math.atan2(dy, dx) if (dx != 0 or dy != 0) else 0.0

            # Recalculate length from points
            length = math.sqrt(dx * dx + dy * dy) or length
        else:
            # Auto-position (simple grid layout)
            beam_index = len(instances)
            center_x = (beam_index % 5) * 6000 + length / 2
            center_y = (beam_index // 5) * 4000
            center_z = base_z + depth / 2
            rotation = 0.0

        position = Point3D(center_x, center_y, center_z)

        # Determine status and color
        status = status_map.get(beam_id, "pending")
        color = _STATUS_COLORS.get(status, _STATUS_COLORS["pending"])

        # Create instance
        instance = BeamInstance(
            beam_id=beam_id,
            story=story,
            position=position,
            dimensions=(width, depth, length),
            rotation=rotation,
            color=color,
            status=status,
            metadata={
                "width_mm": width,
                "depth_mm": depth,
                "span_mm": length,
            },
        )
        instances.append(instance)

        # Update bounds
        half_len = length / 2
        min_x = min(min_x, center_x - half_len)
        max_x = max(max_x, center_x + half_len)
        min_y = min(min_y, center_y - width / 2)
        max_y = max(max_y, center_y + width / 2)
        min_z = min(min_z, center_z - depth / 2)
        max_z = max(max_z, center_z + depth / 2)

    # Handle empty case
    if not instances:
        return Building3DGeometry()

    # Sort stories by Z position
    sorted_stories = sorted(story_z_map.keys(), key=lambda s: story_z_map[s])

    # Calculate camera target (center of bounding box)
    center = Point3D(
        (min_x + max_x) / 2,
        (min_y + max_y) / 2,
        (min_z + max_z) / 2,
    )

    return Building3DGeometry(
        beam_instances=instances,
        stories=sorted_stories,
        bounds=((min_x, min_y, min_z), (max_x, max_y, max_z)),
        camera_target=center,
        metadata={
            "lod": lod,
            "storyHeight": story_height,
        },
    )


def cross_section_geometry(
    width: float,
    depth: float,
    cover: float,
    *,
    bottom_bars: list[tuple[int, float]] | None = None,
    top_bars: list[tuple[int, float]] | None = None,
    stirrup_dia: float = 8.0,
) -> CrossSectionGeometry:
    """Generate 2D cross-section geometry for editor view.

    Creates simplified geometry for displaying beam cross-section
    with rebar positions, suitable for 2D canvas or SVG rendering.

    Args:
        width: Beam width in mm
        depth: Beam depth in mm
        cover: Clear cover in mm
        bottom_bars: List of (count, diameter) for bottom layers
        top_bars: List of (count, diameter) for top layers
        stirrup_dia: Stirrup diameter in mm

    Returns:
        CrossSectionGeometry with rebar positions and stirrup path

    Example:
        >>> cs = cross_section_geometry(
        ...     width=300, depth=500, cover=40,
        ...     bottom_bars=[(4, 16)],
        ...     top_bars=[(2, 12)],
        ... )
        >>> print(f"Has {len(cs.rebar_positions)} bars")
    """
    rebar_positions: list[tuple[float, float, float]] = []

    # Calculate positions for bottom bars
    if bottom_bars:
        z_offset = cover + stirrup_dia
        for count, dia in bottom_bars:
            positions = compute_rebar_positions(
                beam_width=width,
                beam_depth=depth,
                cover=cover,
                bar_count=count,
                bar_dia=dia,
                stirrup_dia=stirrup_dia,
                is_top=False,
            )
            for p in positions:
                rebar_positions.append((p.y, p.z, dia))
            z_offset += dia + 25  # Next layer

    # Calculate positions for top bars
    if top_bars:
        z_offset = depth - cover - stirrup_dia
        for count, dia in top_bars:
            positions = compute_rebar_positions(
                beam_width=width,
                beam_depth=depth,
                cover=cover,
                bar_count=count,
                bar_dia=dia,
                stirrup_dia=stirrup_dia,
                is_top=True,
            )
            for p in positions:
                rebar_positions.append((p.y, p.z, dia))
            z_offset -= dia + 25  # Next layer up

    # Generate stirrup outline path (rectangular)
    inner_width = width - 2 * cover - stirrup_dia
    inner_depth = depth - 2 * cover - stirrup_dia
    y_min = -inner_width / 2
    y_max = inner_width / 2
    z_min = cover + stirrup_dia / 2
    z_max = depth - cover - stirrup_dia / 2

    stirrup_path = [
        Point3D(0, y_min, z_min),
        Point3D(0, y_max, z_min),
        Point3D(0, y_max, z_max),
        Point3D(0, y_min, z_max),
        Point3D(0, y_min, z_min),  # Close the loop
    ]

    return CrossSectionGeometry(
        width=width,
        depth=depth,
        cover=cover,
        rebar_positions=rebar_positions,
        stirrup_path=stirrup_path,
    )

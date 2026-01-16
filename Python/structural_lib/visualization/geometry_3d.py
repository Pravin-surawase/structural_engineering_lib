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
    # Computation functions
    "compute_rebar_positions",
    "compute_stirrup_path",
    "compute_stirrup_positions",
    "compute_beam_outline",
    "beam_to_3d_geometry",
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

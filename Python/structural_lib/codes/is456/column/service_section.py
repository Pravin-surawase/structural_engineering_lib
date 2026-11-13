"""Equilibrium of solid rectangular and circular sections under signed elastic service actions."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from math import acos, atan2, cos, degrees, fsum, hypot, pi, sin, sqrt

from .circular import _GAUSS
from .positioned_biaxial import Point, PositionedColumnBar, _clip_depth
from .section_properties import ColumnSectionProperties

Vector = tuple[float, float, float]


@dataclass(frozen=True)
class ServiceBarResponse:
    bar: PositionedColumnBar
    strain: float
    steel_stress_nmm2: float
    displaced_concrete_stress_nmm2: float
    net_axial_kn: float


@dataclass(frozen=True)
class ServiceSectionResponse:
    strain_at_centroid: float
    strain_gradient_x_per_mm: float
    strain_gradient_y_per_mm: float
    max_concrete_compression_nmm2: float
    neutral_axis_angle_deg: float | None
    neutral_axis_from_top_left_mm: tuple[Point, ...]
    compression_polygon_from_top_left_mm: tuple[Point, ...]
    corner_strains_top_left_clockwise: tuple[float, ...]
    properties: ColumnSectionProperties
    bars: tuple[ServiceBarResponse, ...]
    gross_concrete_actions: Vector
    equilibrated_actions: Vector
    residual_actions: Vector


def _dot(left: Vector, right: Vector) -> float:
    return fsum(a * b for a, b in zip(left, right, strict=True))


def _concrete_points(
    polygon: tuple[Point, ...],
) -> Iterator[tuple[float, float, float]]:
    """Degree-two integration of the affine strain basis over the polygon."""
    if len(polygon) < 3:
        return
    ax, ay = polygon[0]
    for (bx, by), (cx, cy) in zip(polygon[1:-1], polygon[2:], strict=True):
        weight = abs((bx - ax) * (cy - ay) - (by - ay) * (cx - ax)) / 6
        for x, y in ((ax, ay), (bx, by), (cx, cy)):
            yield (ax + bx + cx + 3 * x) / 6, (ay + by + cy + 3 * y) / 6, weight


@dataclass(frozen=True)
class _CircularCompression:
    radius: float
    nx: float
    ny: float
    limit: float

    @classmethod
    def from_plane(cls, radius: float, plane: Vector) -> _CircularCompression:
        magnitude = hypot(plane[1], plane[2])
        if magnitude == 0:
            return cls(radius, 1, 0, pi if plane[0] >= 0 else 0)
        return cls(
            radius,
            -plane[2] / magnitude,
            -plane[1] / magnitude,
            acos(max(-1.0, min(1.0, -2 * plane[0] / magnitude))),
        )

    def point(self, u: float, v: float) -> Point:
        return (
            self.radius + self.nx * u - self.ny * v,
            self.radius + self.ny * u + self.nx * v,
        )

    def samples(self) -> Iterator[tuple[float, float, float]]:
        """Integrate projected circular chords in smooth polar coordinates."""
        half = self.limit / 2
        if half == 0:
            return
        for node, weight in _GAUSS:
            for t in (half * (1 - node), half * (1 + node)):
                u = self.radius * cos(t)
                half_chord = self.radius * sin(t)
                for v in (-half_chord / sqrt(3), half_chord / sqrt(3)):
                    x, y = self.point(u, v)
                    yield x, y, half_chord**2 * half * weight

    def boundary(self) -> tuple[Point, ...]:
        if self.limit == 0:
            return ()
        angles = (self.limit * (index / 32 - 1) for index in range(65))
        return tuple(
            self.point(self.radius * cos(t), self.radius * sin(t)) for t in angles
        )


@dataclass(frozen=True)
class _Stiffness:
    area: float
    y: float
    x: float
    yy: float
    xx: float
    yx: float

    @classmethod
    def from_points(cls, points: list[tuple[Vector, float]]) -> _Stiffness:
        return cls(
            fsum(weight for _, weight in points),
            fsum(weight * y for (_, y, _), weight in points),
            fsum(weight * x for (_, _, x), weight in points),
            fsum(weight * y**2 for (_, y, _), weight in points),
            fsum(weight * x**2 for (_, _, x), weight in points),
            fsum(weight * y * x for (_, y, x), weight in points),
        )

    def apply(self, plane: Vector) -> Vector:
        return (
            _dot((self.area, self.y, self.x), plane),
            _dot((self.y, self.yy, self.yx), plane),
            _dot((self.x, self.yx, self.xx), plane),
        )

    def solve(self, rhs: Vector) -> Vector | None:
        # Eliminate centroid strain. The remaining equations are about the
        # transformed centroid, with two dimensionless rotation coordinates.
        y, x = self.y / self.area, self.x / self.area
        yy, xx = self.yy - self.y * y, self.xx - self.x * x
        yx = self.yx - self.y * x
        determinant = yy * xx - yx**2
        if yy <= 0 or xx <= 0 or determinant <= 1e-12 * yy * xx:
            return None
        ry, rx = rhs[1] - y * rhs[0], rhs[2] - x * rhs[0]
        v = (xx * ry - yx * rx) / determinant
        u = (yy * rx - yx * ry) / determinant
        return rhs[0] / self.area - y * v - x * u, v, u

    def properties(self, width: float, depth: float) -> ColumnSectionProperties:
        return ColumnSectionProperties(
            self.area,
            width * (0.5 - self.x / self.area),
            depth * (0.5 - self.y / self.area),
            depth**2 * (self.yy - self.y**2 / self.area),
            width**2 * (self.xx - self.x**2 / self.area),
            depth * width * (self.yx - self.y * self.x / self.area),
        )


def equilibrate_service_section(
    *,
    width: float,
    depth: float,
    bars: tuple[PositionedColumnBar, ...],
    ec: float,
    es: float,
    p_kn: float,
    mx_knm: float,
    my_knm: float,
    circular: bool = False,
) -> ServiceSectionResponse | None:
    """Resolve compression-only concrete and discrete elastic bars at equilibrium.

    A circular section uses its diameter for both width and depth.
    """
    corners: tuple[Point, ...] = ((0, 0), (width, 0), (width, depth), (0, depth))

    def basis(x: float, y: float) -> Vector:
        return 1, 0.5 - y / depth, 0.5 - x / width

    radius = width / 2
    corner_basis = tuple(basis(x, y) for x, y in corners)
    bar_basis = tuple(basis(bar.x_from_left_mm, bar.y_from_top_mm) for bar in bars)
    target: Vector = (
        p_kn * 1000 / ec,
        mx_knm * 1e6 / depth / ec,
        my_knm * 1e6 / width / ec,
    )

    def section(
        plane: Vector,
    ) -> tuple[
        _Stiffness,
        Vector,
        tuple[Point, ...],
        tuple[float, ...],
        list[tuple[Vector, float]],
    ]:
        strains = tuple(_dot(row, plane) for row in corner_basis)
        if circular:
            polygon: tuple[Point, ...] = ()
            points = _CircularCompression.from_plane(radius, plane).samples()
        else:
            polygon = _clip_depth(corners, strains, 0, keep_shallow=False)
            points = _concrete_points(polygon)
        concrete = [(basis(x, y), area) for x, y, area in points]
        additions = [
            (row, bar.area_mm2 * (es / ec - (_dot(row, plane) >= 0)))
            for bar, row in zip(bars, bar_basis, strict=True)
        ]
        stiffness = _Stiffness.from_points(concrete + additions)
        axial, mx, my = stiffness.apply(plane)
        error: Vector = target[0] - axial, target[1] - mx, target[2] - my
        return stiffness, error, polygon, strains, concrete

    def actions(vector: Vector) -> Vector:
        return (
            vector[0] * ec / 1000,
            vector[1] * depth * ec / 1e6,
            vector[2] * width * ec / 1e6,
        )

    plane: Vector = (max(0.0, target[0] / (width * depth)), 0.0, 0.0)
    state = section(plane)
    for _ in range(40):
        stiffness, error, polygon, strains, concrete = state
        error_norm = hypot(*error)
        if error_norm <= 1e-6 / ec + 1e-12 * hypot(*target):
            break
        step = stiffness.solve(error)
        if step is None:
            return None
        scale = 1.0
        for _ in range(25):
            trial = (
                plane[0] + scale * step[0],
                plane[1] + scale * step[1],
                plane[2] + scale * step[2],
            )
            trial_state = section(trial)
            if hypot(*trial_state[1]) < error_norm:
                plane, state = trial, trial_state
                break
            scale /= 2
        else:
            return None
    else:
        return None

    gx, gy = -plane[2] / width, -plane[1] / depth
    axis_angle = None
    axis: tuple[Point, ...] = ()
    peak = max(strains)
    if circular:
        compression = _CircularCompression.from_plane(radius, plane)
        polygon = compression.boundary()
        peak = plane[0] + hypot(plane[1], plane[2]) / 2
        strains = ()
        if 0 < compression.limit < pi:
            axis = polygon[0], polygon[-1]
    elif min(strains) < 0 < peak:
        tolerance = 1e-12 * max(map(abs, strains))
        axis = tuple(
            dict.fromkeys(
                point
                for point in polygon
                if abs(_dot(basis(*point), plane)) <= tolerance
            )
        )
    if axis:
        axis_angle = degrees(atan2(gx, -gy)) % 180
    responses = []
    for bar, row in zip(bars, bar_basis, strict=True):
        strain = _dot(row, plane)
        steel, displaced = es * strain, ec * max(strain, 0)
        responses.append(
            ServiceBarResponse(
                bar, strain, steel, displaced, bar.area_mm2 * (steel - displaced) / 1000
            )
        )
    return ServiceSectionResponse(
        plane[0],
        gx,
        gy,
        ec * max(0, peak),
        axis_angle,
        axis,
        polygon if peak > 0 else (),
        strains,
        stiffness.properties(width, depth),
        tuple(responses),
        actions(_Stiffness.from_points(concrete).apply(plane)),
        actions(stiffness.apply(plane)),
        actions((-error[0], -error[1], -error[2])),
    )

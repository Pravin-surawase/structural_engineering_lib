"""Section equilibrium for mixed bars in a solid rectangular column."""

from __future__ import annotations

from dataclasses import dataclass
from math import cos, degrees, hypot, pi, sin

from structural_lib.codes.is456.section_materials import section_steel_stress

from ._common import _calculate_puz
from ._strain_compatibility import concrete_stress_at_strain, extreme_compression_strain
from .axial import min_eccentricity
from .biaxial import _calculate_alpha_n

Point = tuple[float, float]
_AngularPoint = tuple[float, float, float, float, float]
_ANGULAR_INTERVALS = 48
_RAY_TOLERANCE_KNM = 1e-8


@dataclass(frozen=True)
class PositionedColumnBar:
    """An identified longitudinal bar at its physical section position."""

    bar_id: str
    x_from_left_mm: float
    y_from_top_mm: float
    diameter_mm: float
    row: str

    @property
    def area_mm2(self) -> float:
        return pi * self.diameter_mm**2 / 4


@dataclass(frozen=True)
class CapacityRay:
    """Fixed-compression moment capacity and equilibrium on one signed ray."""

    normal_deg: float
    xu_mm: float
    p_kn: float
    mx_knm: float
    my_knm: float
    capacity_knm: float
    axial_residual_kn: float
    transverse_residual_knm: float


@dataclass(frozen=True)
class PositionedBiaxialStrength:
    """Signed capacities and independent strength dispositions."""

    steel_area_mm2: float
    puz_kn: float
    alpha_n: float
    axes: dict[str, CapacityRay]
    demand: CapacityRay | None
    contour_ratio: float
    direct_ratio: float
    minimum_eccentricity_ratios: dict[str, float]
    governing_ratio: float


def _clip_depth(
    polygon: tuple[Point, ...],
    depths: tuple[float, ...],
    limit: float,
    *,
    keep_shallow: bool,
) -> tuple[Point, ...]:
    """Clip a convex polygon to one side of a linear depth boundary."""
    clipped: list[Point] = []
    if not polygon:
        return ()
    previous, previous_depth = polygon[-1], depths[-1]
    for point, depth in zip(polygon, depths, strict=True):
        inside = depth <= limit if keep_shallow else depth >= limit
        previous_inside = (
            previous_depth <= limit if keep_shallow else previous_depth >= limit
        )
        if inside != previous_inside:
            fraction = (limit - previous_depth) / (depth - previous_depth)
            clipped.append(
                (
                    previous[0] + fraction * (point[0] - previous[0]),
                    previous[1] + fraction * (point[1] - previous[1]),
                )
            )
        if inside:
            clipped.append(point)
        previous, previous_depth = point, depth
    return tuple(clipped)


@dataclass(frozen=True)
class _ProjectedSection:
    corners: tuple[Point, ...]
    nx: float
    ny: float
    q_max: float
    span: float
    half_width: float
    half_depth: float
    bars: tuple[PositionedColumnBar, ...]
    fck: float
    fy: float

    def distance(self, point: Point) -> float:
        return self.q_max - self.nx * point[0] - self.ny * point[1]

    def resultants(self, xu: float) -> tuple[float, float, float]:
        top = extreme_compression_strain(xu, self.span)
        plateau_depth = xu * (1 - 0.002 / top)
        corner_depths = tuple(self.distance(point) for point in self.corners)
        compression = _clip_depth(self.corners, corner_depths, xu, keep_shallow=True)
        plateau = _clip_depth(
            self.corners, corner_depths, plateau_depth, keep_shallow=True
        )
        parabola = _clip_depth(
            compression,
            tuple(self.distance(point) for point in compression),
            plateau_depth,
            keep_shallow=False,
        )

        def strain(x: float, y: float) -> float:
            return top * (1 - self.distance((x, y)) / xu)

        force = mx = my = 0.0
        for polygon in (plateau, parabola):
            if len(polygon) < 3:
                continue
            ax, ay = polygon[0]
            for (bx, by), (cx, cy) in zip(polygon[1:-1], polygon[2:], strict=True):
                area = abs((bx - ax) * (cy - ay) - (by - ay) * (cx - ax)) / 2
                # Degree-three triangle rule: exact for the quadratic stress
                # and for its products with the linear moment arms.
                for x, y, weight in (
                    ((ax + bx + cx) / 3, (ay + by + cy) / 3, -27 / 48),
                    (0.6 * ax + 0.2 * (bx + cx), 0.6 * ay + 0.2 * (by + cy), 25 / 48),
                    (0.6 * bx + 0.2 * (ax + cx), 0.6 * by + 0.2 * (ay + cy), 25 / 48),
                    (0.6 * cx + 0.2 * (ax + bx), 0.6 * cy + 0.2 * (ay + by), 25 / 48),
                ):
                    df = (
                        concrete_stress_at_strain(strain(x, y), self.fck)
                        * area
                        * weight
                    )
                    force += df
                    mx += df * (self.half_depth - y)
                    my += df * (self.half_width - x)
        for bar in self.bars:
            x, y = bar.x_from_left_mm, bar.y_from_top_mm
            e = strain(x, y)
            net = bar.area_mm2 * (
                section_steel_stress(e, self.fy)
                - concrete_stress_at_strain(e, self.fck)
            )
            force += net
            mx += net * (self.half_depth - y)
            my += net * (self.half_width - x)
        return force / 1000, mx / 1e6, my / 1e6


@dataclass(frozen=True)
class _Section:
    width: float
    depth: float
    fck: float
    fy: float
    bars: tuple[PositionedColumnBar, ...]

    def equilibrate(self, angle: float, pu_kn: float) -> _AngularPoint | None:
        nx, ny = cos(angle), sin(angle)
        span = abs(nx * self.width) + abs(ny * self.depth)
        projected = _ProjectedSection(
            ((0, 0), (self.width, 0), (self.width, self.depth), (0, self.depth)),
            nx,
            ny,
            max(0, nx * self.width) + max(0, ny * self.depth),
            span,
            self.width / 2,
            self.depth / 2,
            self.bars,
            self.fck,
            self.fy,
        )
        low, high = 1e-6 * span, 256 * span
        if not projected.resultants(low)[0] < pu_kn < projected.resultants(high)[0]:
            return None
        for _ in range(42):
            middle = (low + high) / 2
            if projected.resultants(middle)[0] < pu_kn:
                low = middle
            else:
                high = middle
        xu = (low + high) / 2
        p, mx, my = projected.resultants(xu)
        if abs(p - pu_kn) > 0.01:
            return None
        return angle, xu, p, mx, my


def _signed_rays(
    section: _Section,
    samples: tuple[_AngularPoint, ...],
    pu_kn: float,
    dx: float,
    dy: float,
) -> tuple[CapacityRay, CapacityRay] | None:
    """Require one positive and one negative crossing of a line through zero."""

    def transverse(point: _AngularPoint) -> float:
        return -dy * point[3] + dx * point[4]

    roots = [
        point for point in samples[:-1] if abs(transverse(point)) <= _RAY_TOLERANCE_KNM
    ]
    for low, high in zip(samples[:-1], samples[1:], strict=True):
        low_value, high_value = transverse(low), transverse(high)
        if (
            min(abs(low_value), abs(high_value)) <= _RAY_TOLERANCE_KNM
            or low_value * high_value > 0
        ):
            continue
        left, right = low[0], high[0]
        for _ in range(36):
            angle = (left + right) / 2
            middle = section.equilibrate(angle, pu_kn)
            if middle is None:
                return None
            value = transverse(middle)
            if abs(value) <= _RAY_TOLERANCE_KNM:
                roots.append(middle)
                break
            if low_value * value < 0:
                right = angle
            else:
                left, low_value = angle, value
        else:
            return None

    hits: dict[bool, CapacityRay] = {}
    for angle, xu, p, mx, my in roots:
        projection = dx * mx + dy * my
        if abs(projection) <= _RAY_TOLERANCE_KNM or (projection > 0) in hits:
            return None
        hits[projection > 0] = CapacityRay(
            degrees(angle) % 360,
            xu,
            p,
            mx,
            my,
            abs(projection),
            p - pu_kn,
            (-dy * mx + dx * my) * (1 if projection > 0 else -1),
        )
    if len(hits) != 2:
        return None
    return hits[True], hits[False]


@dataclass(frozen=True)
class PositionedCapacitySlice:
    """Reuse one equilibrated section at fixed compression for concurrent actions."""

    section: _Section
    pu_kn: float
    steel_area_mm2: float
    puz_kn: float
    alpha_n: float
    scan: tuple[_AngularPoint, ...]
    axes: dict[str, CapacityRay]

    def check(
        self,
        mx_knm: float,
        my_knm: float,
        unsupported_x_mm: float,
        unsupported_y_mm: float,
    ) -> PositionedBiaxialStrength | None:
        """Compare one signed pair and the two separate minimum eccentricities."""
        cap_x = self.axes["x_negative" if mx_knm < 0 else "x_positive"].capacity_knm
        cap_y = self.axes["y_negative" if my_knm < 0 else "y_positive"].capacity_knm
        contour = (abs(mx_knm) / cap_x) ** self.alpha_n + (
            abs(my_knm) / cap_y
        ) ** self.alpha_n

        demand = None
        direct = 0.0
        magnitude = hypot(mx_knm, my_knm)
        if magnitude:
            rays = _signed_rays(
                self.section,
                self.scan,
                self.pu_kn,
                mx_knm / magnitude,
                my_knm / magnitude,
            )
            if rays is None:
                return None
            demand = rays[0]
            direct = magnitude / demand.capacity_knm

        minimum = {
            axis: self.pu_kn
            * min_eccentricity(length, depth)
            / 1000
            / min(
                self.axes[f"{axis}_{sign}"].capacity_knm
                for sign in ("positive", "negative")
            )
            for axis, depth, length in (
                ("x", self.section.depth, unsupported_x_mm),
                ("y", self.section.width, unsupported_y_mm),
            )
        }
        return PositionedBiaxialStrength(
            self.steel_area_mm2,
            self.puz_kn,
            self.alpha_n,
            self.axes.copy(),
            demand,
            contour,
            direct,
            minimum,
            max(contour, direct, *minimum.values()),
        )


def prepare_positioned_capacity(
    *,
    b_mm: float,
    D_mm: float,
    pu_kn: float,
    fck_nmm2: float,
    fy_nmm2: float,
    bars: tuple[PositionedColumnBar, ...],
) -> PositionedCapacitySlice | None:
    """Equilibrate the angular samples and the four signed pure-axis capacities."""
    steel = sum(bar.area_mm2 for bar in bars)
    puz = _calculate_puz(b_mm, D_mm, fck_nmm2, fy_nmm2, steel)
    if pu_kn >= puz:
        return None
    alpha = _calculate_alpha_n(pu_kn, puz)
    section = _Section(b_mm, D_mm, fck_nmm2, fy_nmm2, bars)
    samples = []
    for index in range(_ANGULAR_INTERVALS + 1):
        point = section.equilibrate(2 * pi * index / _ANGULAR_INTERVALS, pu_kn)
        if point is None:
            return None
        samples.append(point)
    scan = tuple(samples)
    x_rays = _signed_rays(section, scan, pu_kn, 1, 0)
    y_rays = _signed_rays(section, scan, pu_kn, 0, 1)
    if x_rays is None or y_rays is None:
        return None
    axes = dict(
        zip(
            ("x_positive", "x_negative", "y_positive", "y_negative"),
            (*x_rays, *y_rays),
            strict=True,
        )
    )
    return PositionedCapacitySlice(section, pu_kn, steel, puz, alpha, scan, axes)


def positioned_biaxial_strength(
    *,
    b_mm: float,
    D_mm: float,
    unsupported_length_mm: float,
    pu_kn: float,
    mx_knm: float,
    my_knm: float,
    fck_nmm2: float,
    fy_nmm2: float,
    bars: tuple[PositionedColumnBar, ...],
) -> PositionedBiaxialStrength | None:
    """Check Cl. 39.6 and a fixed-compression equilibrium ray for actual bars."""
    prepared = prepare_positioned_capacity(
        b_mm=b_mm,
        D_mm=D_mm,
        pu_kn=pu_kn,
        fck_nmm2=fck_nmm2,
        fy_nmm2=fy_nmm2,
        bars=bars,
    )
    if prepared is None:
        return None
    return prepared.check(mx_knm, my_knm, unsupported_length_mm, unsupported_length_mm)

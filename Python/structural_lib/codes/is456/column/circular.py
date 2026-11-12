"""Actual-bar circular section equilibrium using smooth chord quadrature."""

from __future__ import annotations

from dataclasses import dataclass
from math import acos, cos, pi, sin

from structural_lib.codes.is456.section_materials import section_steel_stress

from ._strain_compatibility import concrete_stress_at_strain, extreme_compression_strain
from .positioned_biaxial import PositionedColumnBar, equilibrate_section

# Positive nodes and weights of the symmetric 12-point Gauss-Legendre rule.
_GAUSS = (
    (0.1252334085114689, 0.2491470458134028),
    (0.3678314989981802, 0.2334925365383548),
    (0.5873179542866175, 0.2031674267230659),
    (0.7699026741943047, 0.1600783285433462),
    (0.9041172563704749, 0.1069393259953184),
    (0.9815606342467192, 0.04717533638651183),
)


@dataclass(frozen=True)
class CircularSection:
    """Solid circular concrete with discrete longitudinal bar centres."""

    diameter_mm: float
    fck: float
    fy: float
    bars: tuple[PositionedColumnBar, ...]

    @property
    def width(self) -> float:
        return self.diameter_mm

    @property
    def depth(self) -> float:
        return self.diameter_mm

    def equilibrate(
        self, angle: float, pu_kn: float
    ) -> tuple[float, float, float, float, float] | None:
        """Solve the axial root at one neutral-plane orientation."""
        radius = self.diameter_mm / 2
        nx, ny = cos(angle), sin(angle)
        positions = tuple(
            (bar, bar.x_from_left_mm - radius, bar.y_from_top_mm - radius)
            for bar in self.bars
        )

        def resultants(xu: float) -> tuple[float, float, float]:
            extreme = extreme_compression_strain(xu, self.diameter_mm)
            force, normal_moment = self._concrete(radius, xu, extreme)
            mx, my = -ny * normal_moment, -nx * normal_moment
            for bar, x, y in positions:
                strain = extreme * (1 - (radius - nx * x - ny * y) / xu)
                net = bar.area_mm2 * (
                    section_steel_stress(strain, self.fy)
                    - concrete_stress_at_strain(strain, self.fck)
                )
                force += net
                mx -= net * y
                my -= net * x
            return force / 1000, mx / 1e6, my / 1e6

        return equilibrate_section(angle, self.diameter_mm, pu_kn, resultants)

    def _concrete(
        self, radius: float, xu: float, extreme: float
    ) -> tuple[float, float]:
        # The normal coordinate u = R cos(t) gives a chord-area Jacobian
        # of 2 R² sin²(t), avoiding a square-root singularity at the rim.
        def limit(depth: float) -> float:
            return acos(max(-1.0, min(1.0, 1 - depth / radius)))

        plateau = limit(xu * (1 - 0.002 / extreme))
        compression = limit(xu)
        force = moment = 0.0
        for left, right in ((0.0, plateau), (plateau, compression)):
            if right <= left:
                continue
            middle, half = (right + left) / 2, (right - left) / 2
            for node, weight in _GAUSS:
                for theta in (middle - node * half, middle + node * half):
                    u = radius * cos(theta)
                    strain = extreme * (1 - (radius - u) / xu)
                    area = 2 * (radius * sin(theta)) ** 2 * half * weight
                    net = concrete_stress_at_strain(strain, self.fck) * area
                    force += net
                    moment += net * u
        return force, moment


def circular_bars(
    diameter_mm: float,
    count: int,
    bar_diameter_mm: float,
    ring_radius_mm: float,
    first_angle_deg: float,
) -> tuple[PositionedColumnBar, ...]:
    """Resolve equal bars clockwise from the right in top-left coordinates."""
    centre = diameter_mm / 2
    start = first_angle_deg * pi / 180
    return tuple(
        PositionedColumnBar(
            f"B{index + 1:02d}",
            centre + ring_radius_mm * cos(start + 2 * pi * index / count),
            centre + ring_radius_mm * sin(start + 2 * pi * index / count),
            bar_diameter_mm,
            "outer",
        )
        for index in range(count)
    )

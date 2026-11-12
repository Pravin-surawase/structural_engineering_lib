"""Geometry for straight contact partners restrained by transverse return links."""

from __future__ import annotations

from dataclasses import dataclass
from math import dist, pi
from typing import Literal

Point = tuple[float, float]


@dataclass(frozen=True)
class LinkSegment:
    """A straight line or a quarter circle in the transverse plane."""

    start_mm: Point
    end_mm: Point
    centre_mm: Point | None = None

    def distance_to(self, point: Point) -> float:
        """Exact distance from a longitudinal bar centre to the segment."""
        start, end, centre = self.start_mm, self.end_mm, self.centre_mm
        endpoint = min(dist(point, start), dist(point, end))
        if centre is not None:
            p = (point[0] - centre[0], point[1] - centre[1])
            radial_ends = tuple(
                (xy[0] - centre[0], xy[1] - centre[1]) for xy in (start, end)
            )
            if all(p[0] * xy[0] + p[1] * xy[1] >= 0 for xy in radial_ends):
                return abs(dist(point, centre) - dist(start, centre))
            return endpoint
        dx, dy = end[0] - start[0], end[1] - start[1]
        squared = dx * dx + dy * dy
        if squared == 0:
            return endpoint
        t = ((point[0] - start[0]) * dx + (point[1] - start[1]) * dy) / squared
        return (
            dist(point, (start[0] + t * dx, start[1] + t * dy))
            if 0 <= t <= 1
            else endpoint
        )

    @property
    def length_mm(self) -> float:
        if self.centre_mm is None:
            return dist(self.start_mm, self.end_mm)
        return pi / 2 * dist(self.start_mm, self.centre_mm)


@dataclass(frozen=True)
class ReturnLink:
    """Continuous spine with two anchored returns in one transverse plane."""

    axis: Literal["x", "y"]
    segments: tuple[LinkSegment, ...]
    tail_gap_mm: float

    @property
    def cut_length_mm(self) -> float:
        return sum(segment.length_mm for segment in self.segments)


def return_link(
    *,
    axis: Literal["x", "y"],
    left_mm: float,
    right_mm: float,
    near_mm: float,
    far_mm: float,
    radius_mm: float,
    tail_mm: float,
) -> ReturnLink:
    """Form each return with two 90° bends and an optional tangent between them."""
    r = radius_mm

    def xy(u: float, v: float) -> Point:
        return (u, v) if axis == "x" else (v, u)

    spine = LinkSegment(xy(left_mm, near_mm - r), xy(right_mm, near_mm - r))
    returns: list[LinkSegment] = []
    for u, side in ((left_mm, -1), (right_mm, 1)):
        returns.extend(
            (
                LinkSegment(
                    xy(u, near_mm - r), xy(u + side * r, near_mm), xy(u, near_mm)
                ),
                LinkSegment(xy(u + side * r, near_mm), xy(u + side * r, far_mm)),
                LinkSegment(xy(u + side * r, far_mm), xy(u, far_mm + r), xy(u, far_mm)),
                LinkSegment(xy(u, far_mm + r), xy(u - side * tail_mm, far_mm + r)),
            )
        )
    return ReturnLink(axis, (spine, *returns), right_mm - left_mm - 2 * tail_mm)

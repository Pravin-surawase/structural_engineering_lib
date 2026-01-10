"""Code-agnostic geometry definitions.

Cross-section geometry classes used by all design codes.
These are pure geometric calculations - no code-specific logic.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Literal


class Section(ABC):
    """Abstract base for cross-section geometry."""

    @property
    @abstractmethod
    def area(self) -> float:
        """Gross cross-sectional area (mm²)."""

    @property
    @abstractmethod
    def centroid_y(self) -> float:
        """Y-coordinate of centroid from bottom (mm)."""

    @property
    @abstractmethod
    def moment_of_inertia(self) -> float:
        """Second moment of area about centroidal axis (mm⁴)."""

    @property
    def section_modulus_bottom(self) -> float:
        """Section modulus for bottom fiber (mm³)."""
        return self.moment_of_inertia / self.centroid_y

    @property
    def section_modulus_top(self) -> float:
        """Section modulus for top fiber (mm³)."""
        return self.moment_of_inertia / (self.overall_depth - self.centroid_y)

    @property
    @abstractmethod
    def overall_depth(self) -> float:
        """Overall depth of section (mm)."""


@dataclass
class RectangularSection(Section):
    """Rectangular beam/column cross-section.

    Attributes:
        b: Width (mm)
        D: Overall depth (mm)
        d: Effective depth (mm), optional - calculated if not provided
        cover: Clear cover to reinforcement (mm)
    """

    b: float
    D: float
    d: float | None = None
    cover: float = 40.0

    def __post_init__(self) -> None:
        if self.d is None:
            # Assume single layer, 20mm bar, 8mm stirrup
            self.d = self.D - self.cover - 8 - 10

    @property
    def area(self) -> float:
        return self.b * self.D

    @property
    def centroid_y(self) -> float:
        return self.D / 2

    @property
    def moment_of_inertia(self) -> float:
        return self.b * self.D**3 / 12

    @property
    def overall_depth(self) -> float:
        return self.D


@dataclass
class TSection(Section):
    """T-beam cross-section.

    Attributes:
        bf: Flange width (mm)
        Df: Flange depth (mm)
        bw: Web width (mm)
        D: Overall depth (mm)
        d: Effective depth (mm)
    """

    bf: float  # Flange width
    Df: float  # Flange depth
    bw: float  # Web width
    D: float  # Overall depth
    d: float | None = None

    def __post_init__(self) -> None:
        if self.d is None:
            self.d = self.D - 50  # Default assumption

    @property
    def area(self) -> float:
        """Area = flange area + web area below flange."""
        flange_area = self.bf * self.Df
        web_area = self.bw * (self.D - self.Df)
        return flange_area + web_area

    @property
    def centroid_y(self) -> float:
        """Centroid from bottom."""
        flange_area = self.bf * self.Df
        web_area = self.bw * (self.D - self.Df)

        flange_y = self.D - self.Df / 2  # Flange centroid from bottom
        web_y = (self.D - self.Df) / 2  # Web centroid from bottom

        return (flange_area * flange_y + web_area * web_y) / self.area

    @property
    def moment_of_inertia(self) -> float:
        """I about centroidal axis using parallel axis theorem."""
        y_bar = self.centroid_y

        # Flange
        flange_area = self.bf * self.Df
        flange_y = self.D - self.Df / 2
        i_flange = self.bf * self.Df**3 / 12 + flange_area * (flange_y - y_bar) ** 2

        # Web
        web_h = self.D - self.Df
        web_area = self.bw * web_h
        web_y = web_h / 2
        i_web = self.bw * web_h**3 / 12 + web_area * (web_y - y_bar) ** 2

        return i_flange + i_web

    @property
    def overall_depth(self) -> float:
        return self.D


@dataclass
class LSection(Section):
    """L-beam (edge beam) cross-section.

    Similar to T-section but with flange on one side only.
    """

    bf: float  # Flange width (effective width on one side + bw)
    Df: float  # Flange depth
    bw: float  # Web width
    D: float  # Overall depth
    d: float | None = None

    def __post_init__(self) -> None:
        if self.d is None:
            self.d = self.D - 50

    @property
    def area(self) -> float:
        flange_area = self.bf * self.Df
        web_area = self.bw * (self.D - self.Df)
        return flange_area + web_area

    @property
    def centroid_y(self) -> float:
        flange_area = self.bf * self.Df
        web_area = self.bw * (self.D - self.Df)

        flange_y = self.D - self.Df / 2
        web_y = (self.D - self.Df) / 2

        return (flange_area * flange_y + web_area * web_y) / self.area

    @property
    def moment_of_inertia(self) -> float:
        y_bar = self.centroid_y

        flange_area = self.bf * self.Df
        flange_y = self.D - self.Df / 2
        i_flange = self.bf * self.Df**3 / 12 + flange_area * (flange_y - y_bar) ** 2

        web_h = self.D - self.Df
        web_area = self.bw * web_h
        web_y = web_h / 2
        i_web = self.bw * web_h**3 / 12 + web_area * (web_y - y_bar) ** 2

        return i_flange + i_web

    @property
    def overall_depth(self) -> float:
        return self.D


def effective_flange_width(
    span: float,
    bw: float,
    actual_flange: float,
    beam_type: Literal["T", "L"] = "T",
) -> float:
    """Calculate effective flange width per IS 456 Cl. 23.1.2.

    Args:
        span: Effective span (mm)
        bw: Web width (mm)
        actual_flange: Actual flange width available (mm)
        beam_type: "T" for T-beam, "L" for L-beam

    Returns:
        Effective flange width (mm)
    """
    if beam_type == "T":
        # bf = Lo/6 + bw + 6*Df (simplified, Df not passed)
        # Using Lo/6 + bw as conservative
        code_limit = span / 6 + bw
    else:  # L-beam
        code_limit = span / 12 + bw

    return min(actual_flange, code_limit)

"""Abstract base classes for design code implementations.

These classes define the interface that all code implementations must follow.
This enables:
- Consistent API across different design codes
- Easy addition of new codes (ACI, Eurocode)
- Polymorphic usage in application layer
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class DesignResult:
    """Standard result container for design calculations."""

    success: bool
    value: Any
    utilization_ratio: float | None = None
    warnings: list[str] | None = None
    code_reference: str | None = None

    def __post_init__(self) -> None:
        if self.warnings is None:
            self.warnings = []


class DesignCode(ABC):
    """Abstract base class for design codes.

    Each design code (IS 456, ACI 318, EC2) must implement:
    - code_id: Unique identifier (e.g., "IS456", "ACI318")
    - code_name: Human-readable name
    - code_version: Version/year (e.g., "2000", "19")
    """

    @property
    @abstractmethod
    def code_id(self) -> str:
        """Unique code identifier."""

    @property
    @abstractmethod
    def code_name(self) -> str:
        """Human-readable code name."""

    @property
    @abstractmethod
    def code_version(self) -> str:
        """Code version or year."""

    def __repr__(self) -> str:
        return f"{self.code_name} ({self.code_id}:{self.code_version})"


class FlexureDesigner(ABC):
    """Abstract base for flexural design calculations.

    Implementations must handle:
    - Area of steel calculation
    - Moment capacity calculation
    - Depth of neutral axis
    - Strain compatibility
    """

    @abstractmethod
    def required_steel_area(
        self,
        Mu: float,  # Design moment (kN·m)
        b: float,  # Width (mm)
        d: float,  # Effective depth (mm)
        fck: float,  # Concrete strength (N/mm²)
        fy: float,  # Steel yield strength (N/mm²)
    ) -> DesignResult:
        """Calculate required area of tension steel."""

    @abstractmethod
    def moment_capacity(
        self,
        Ast: float,  # Area of steel (mm²)
        b: float,  # Width (mm)
        d: float,  # Effective depth (mm)
        fck: float,  # Concrete strength (N/mm²)
        fy: float,  # Steel yield strength (N/mm²)
    ) -> DesignResult:
        """Calculate moment capacity of section."""


class ShearDesigner(ABC):
    """Abstract base for shear design calculations."""

    @abstractmethod
    def required_shear_reinforcement(
        self,
        Vu: float,  # Design shear (kN)
        b: float,  # Width (mm)
        d: float,  # Effective depth (mm)
        fck: float,  # Concrete strength (N/mm²)
        fy: float,  # Steel yield strength (N/mm²)
        Ast: float,  # Tension steel area (mm²)
    ) -> DesignResult:
        """Calculate required shear reinforcement."""

    @abstractmethod
    def shear_capacity(
        self,
        b: float,  # Width (mm)
        d: float,  # Effective depth (mm)
        fck: float,  # Concrete strength (N/mm²)
        Ast: float,  # Tension steel area (mm²)
        Asv: float,  # Shear reinforcement area (mm²)
        sv: float,  # Stirrup spacing (mm)
    ) -> DesignResult:
        """Calculate shear capacity of section."""


class DetailingRules(ABC):
    """Abstract base for reinforcement detailing rules."""

    @abstractmethod
    def min_steel_ratio(self, fck: float, fy: float) -> float:
        """Minimum steel ratio (As/bd)."""

    @abstractmethod
    def max_steel_ratio(self, fck: float, fy: float) -> float:
        """Maximum steel ratio (As/bd)."""

    @abstractmethod
    def min_cover(self, exposure: str) -> float:
        """Minimum concrete cover (mm)."""

    @abstractmethod
    def min_bar_spacing(self, bar_dia: float, agg_size: float) -> float:
        """Minimum clear spacing between bars (mm)."""

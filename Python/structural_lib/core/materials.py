"""Code-agnostic material models.

Provides universal material property definitions that work across all codes.
Code-specific adjustments (safety factors, stress-strain models) are handled
by the code implementations.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Concrete:
    """Concrete material properties.

    Attributes:
        fck: Characteristic compressive strength (N/mm²)
        Ec: Elastic modulus (N/mm²), auto-calculated if not provided
        density: Unit weight (kN/m³), default 25
        aggregate_size: Maximum aggregate size (mm), default 20
    """

    fck: float
    Ec: float | None = None
    density: float = 25.0
    aggregate_size: float = 20.0

    def __post_init__(self) -> None:
        if self.Ec is None:
            # IS 456 formula, can be overridden by code-specific factory
            self.Ec = 5000 * (self.fck**0.5)

    @property
    def fcm(self) -> float:
        """Mean compressive strength (approx fck + 8 for normal concrete)."""
        return self.fck + 8.0

    @property
    def fctm(self) -> float:
        """Mean tensile strength (approx 0.7 * sqrt(fck))."""
        return float(0.7 * (self.fck**0.5))


@dataclass
class Steel:
    """Reinforcement steel properties.

    Attributes:
        fy: Characteristic yield strength (N/mm²)
        Es: Elastic modulus (N/mm²), default 200000
        steel_type: Type of steel ("Fe415", "Fe500", "Fe550", etc.)
    """

    fy: float
    Es: float = 200000.0
    steel_type: str = "Fe500"

    @property
    def design_stress(self) -> float:
        """Design stress (fy/1.15 for IS 456, override for other codes)."""
        return self.fy / 1.15

    @property
    def strain_at_yield(self) -> float:
        """Strain at yield point."""
        return self.fy / self.Es + 0.002  # IS 456 approach


class MaterialFactory:
    """Factory for creating material objects with code-specific defaults.

    Usage:
        factory = MaterialFactory("IS456")
        concrete = factory.concrete(fck=30)
        steel = factory.steel(fy=500)
    """

    # Standard concrete grades by code
    CONCRETE_GRADES: dict[str, list[float]] = {
        "IS456": [20, 25, 30, 35, 40, 45, 50],
        "ACI318": [21, 28, 35, 42, 56],  # MPa equivalents
        "EC2": [20, 25, 30, 35, 40, 45, 50],
    }

    # Standard steel grades by code
    STEEL_GRADES: dict[str, dict[str, float]] = {
        "IS456": {"Fe415": 415, "Fe500": 500, "Fe550": 550},
        "ACI318": {"Grade60": 420, "Grade80": 550},
        "EC2": {"B500A": 500, "B500B": 500, "B500C": 500},
    }

    def __init__(self, code_id: str = "IS456"):
        """Initialize factory for specific code.

        Args:
            code_id: Design code identifier ("IS456", "ACI318", "EC2")
        """
        self.code_id = code_id

    def concrete(
        self,
        fck: float,
        aggregate_size: float = 20.0,
        density: float = 25.0,
    ) -> Concrete:
        """Create concrete with code-specific modulus calculation."""
        # Calculate Ec based on code
        if self.code_id == "IS456":
            ec_modulus = 5000 * (fck**0.5)
        elif self.code_id == "ACI318":
            ec_modulus = 4700 * (fck**0.5)  # ACI formula
        elif self.code_id == "EC2":
            fcm = fck + 8
            ec_modulus = 22000 * ((fcm / 10) ** 0.3)  # Eurocode formula
        else:
            ec_modulus = 5000 * (fck**0.5)  # Default to IS 456

        return Concrete(
            fck=fck,
            Ec=ec_modulus,
            aggregate_size=aggregate_size,
            density=density,
        )

    def steel(
        self,
        fy: float | None = None,
        grade: str | None = None,
        es_modulus: float = 200000.0,
    ) -> Steel:
        """Create steel from fy or grade name.

        Args:
            fy: Yield strength (N/mm²), overrides grade
            grade: Steel grade name (e.g., "Fe500")
            es_modulus: Elastic modulus (N/mm²)
        """
        steel_grade: str = ""
        if fy is None and grade is None:
            # Default to most common grade for code
            if self.code_id == "IS456":
                fy, steel_grade = 500.0, "Fe500"
            elif self.code_id == "ACI318":
                fy, steel_grade = 420.0, "Grade60"
            elif self.code_id == "EC2":
                fy, steel_grade = 500.0, "B500B"
            else:
                fy, steel_grade = 500.0, "Fe500"
        elif fy is None and grade is not None:
            # Look up grade
            grades = self.STEEL_GRADES.get(self.code_id, {})
            fy = grades.get(grade, 500.0)
            steel_grade = grade
        else:
            steel_grade = grade or f"fy{int(fy or 500)}"

        return Steel(fy=fy or 500.0, Es=es_modulus, steel_type=steel_grade)

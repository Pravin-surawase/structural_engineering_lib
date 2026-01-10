"""IS 456:2000 - Indian Standard for Plain and Reinforced Concrete.

This module provides IS 456-specific implementations of:
- Flexure design (Cl. 38.1)
- Shear design (Cl. 40)
- Detailing rules (Cl. 26)
- Material factors (Cl. 36)

All existing functionality from the main library is preserved.
This package acts as a namespace for IS 456-specific code.
"""

from __future__ import annotations

from structural_lib.core.base import DesignCode
from structural_lib.core.registry import register_code
from structural_lib.detailing import (
    calculate_bar_spacing,
    calculate_development_length,
    calculate_lap_length,
    check_min_spacing,
)

# Re-export existing implementations for backward compatibility
# These will be gradually migrated to this package
from structural_lib.flexure import (
    calculate_ast_required,
    calculate_mu_lim,
    design_doubly_reinforced,
    design_flanged_beam,
    design_singly_reinforced,
)
from structural_lib.shear import calculate_tv, design_shear


@register_code("IS456")
class IS456Code(DesignCode):
    """IS 456:2000 design code implementation."""

    @property
    def code_id(self) -> str:
        return "IS456"

    @property
    def code_name(self) -> str:
        return "Indian Standard IS 456:2000"

    @property
    def code_version(self) -> str:
        return "2000"

    # Material partial safety factors (Cl. 36.4.2)
    GAMMA_C = 1.5  # Concrete
    GAMMA_S = 1.15  # Steel

    # Stress block parameters (Cl. 38.1)
    STRESS_BLOCK_DEPTH = 0.42  # xu/d for balanced section
    STRESS_BLOCK_FACTOR = 0.36  # For rectangular stress block

    def get_design_strength_concrete(self, fck: float) -> float:
        """Design compressive strength of concrete (0.67*fck/γc)."""
        return 0.67 * fck / self.GAMMA_C

    def get_design_strength_steel(self, fy: float) -> float:
        """Design yield strength of steel (fy/γs)."""
        return fy / self.GAMMA_S


# Convenience exports
__all__ = [
    "IS456Code",
    # Flexure
    "calculate_ast_required",
    "calculate_mu_lim",
    "design_singly_reinforced",
    "design_doubly_reinforced",
    "design_flanged_beam",
    # Shear
    "calculate_tv",
    "design_shear",
    # Detailing
    "calculate_development_length",
    "calculate_lap_length",
    "calculate_bar_spacing",
    "check_min_spacing",
]

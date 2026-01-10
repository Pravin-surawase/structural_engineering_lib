"""IS 456:2000 - Indian Standard for Plain and Reinforced Concrete.

This module provides IS 456-specific implementations of:
- Flexure design (Cl. 38.1)
- Shear design (Cl. 40)
- Detailing rules (Cl. 26)
- Material factors (Cl. 36)

All existing functionality from the main library is preserved.
This package acts as a namespace for IS 456-specific code.

Migration Status:
- tables.py: ✅ Migrated (Session 5)
- shear.py: ⏳ Pending
- flexure.py: ⏳ Pending
- detailing.py: ⏳ Pending
- serviceability.py: ⏳ Pending
- compliance.py: ⏳ Pending
- ductile.py: ⏳ Pending
"""

from __future__ import annotations

# Import migrated modules - these are now in codes/is456/
from structural_lib.codes.is456 import tables
from structural_lib.core.base import DesignCode
from structural_lib.core.registry import register_code

# NOTE: Other modules (flexure, shear, detailing, etc.) will be imported here
# AFTER they are migrated. Importing them now would cause circular imports.
# See docs/research/is456-migration-research.md for migration plan.


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
    # Migrated modules
    "tables",
    # Note: flexure, shear, detailing exports will be added after migration
]

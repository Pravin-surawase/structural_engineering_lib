"""IS 456:2000 - Indian Standard for Plain and Reinforced Concrete.

This module provides IS 456-specific implementations of:
- Flexure design (Cl. 38.1)
- Shear design (Cl. 40)
- Detailing rules (Cl. 26)
- Serviceability checks (Cl. 42, 43)
- Compliance verification
- **Code traceability** (TASK-272: clause decorator and database)

All existing functionality from the main library is preserved.
This package acts as a namespace for IS 456-specific code.

Migration Status (Session 5-6):
- tables.py: ✅ Migrated
- shear.py: ✅ Migrated → beam/shear.py (Phase 1.5)
- flexure.py: ✅ Migrated → beam/flexure.py (Phase 1.5)
- detailing.py: ✅ Migrated → beam/detailing.py (Phase 1.5)
- serviceability.py: ✅ Migrated → beam/serviceability.py (Phase 1.5)
- torsion.py: ✅ Migrated → beam/torsion.py (Phase 1.5)
- compliance.py: ✅ Migrated
- ductile.py: ✅ Migrated
- traceability.py: ✅ Added (TASK-272)

Beam subpackage (Phase 1.5 — TASK-700):
- beam/flexure.py: Flexural design per Cl. 38.1
- beam/shear.py: Shear design per Cl. 40
- beam/detailing.py: Reinforcement detailing per Cl. 26
- beam/serviceability.py: Deflection/crack width per Cl. 42/43
- beam/torsion.py: Torsion design per Cl. 41
"""

from __future__ import annotations

# Import beam subpackage (canonical location)
# Import non-beam modules
from structural_lib.codes.is456 import (
    beam,  # noqa: F401
    column,  # noqa: F401
    compliance,
    ductile,
    footing,  # noqa: F401
    slenderness,
    tables,
    traceability,
)
from structural_lib.codes.is456.beam import (
    detailing,
    flexure,
    serviceability,
    shear,
    torsion,
)

# Import traceability API for convenience
from structural_lib.codes.is456.traceability import (
    clause,
    get_clause_info,
    get_clause_refs,
    list_clauses_by_category,
    search_clauses,
)

# Import base classes for IS456Code
from structural_lib.core.base import DesignCode
from structural_lib.core.registry import register_code


@register_code("IS456")
class IS456Code(DesignCode):
    """IS 456:2000 design code implementation.

    This class provides code-specific constants and methods.
    The actual design functions are in the submodules:
    - tables: Table 19/23 lookups
    - shear: Shear design per Cl. 40
    - flexure: Flexure design per Cl. 38.1
    - detailing: Reinforcement detailing per Cl. 26
    - serviceability: Deflection/crack width per Cl. 42/43
    - compliance: Compliance checking orchestration
    - ductile: Ductile detailing per IS 13920
    """

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

    # Convenience methods that delegate to submodules
    # These provide a unified interface through IS456Code instance

    def get_tau_c(self, fck: float, pt: float) -> float:
        """Get design shear strength τc from Table 19."""
        return tables.get_tc_value(fck, pt)

    def get_tau_c_max(self, fck: float) -> float:
        """Get maximum shear stress τc,max from Table 20."""
        return tables.get_tc_max_value(fck)


# Convenience exports
__all__ = [
    "IS456Code",
    # Subpackages
    "beam",
    "column",
    # Modules
    "tables",
    "shear",
    "flexure",
    "detailing",
    "serviceability",
    "compliance",
    "ductile",
    "slenderness",
    "torsion",
    "traceability",
    # Traceability API (TASK-272)
    "clause",
    "get_clause_refs",
    "get_clause_info",
    "list_clauses_by_category",
    "search_clauses",
]

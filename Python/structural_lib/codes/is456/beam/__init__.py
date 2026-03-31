"""IS 456:2000 — Beam design modules.

Subpackage grouping all beam-specific IS 456 calculations:
- flexure: Flexural design per Cl. 38.1
- shear: Shear design per Cl. 40
- detailing: Reinforcement detailing per Cl. 26
- serviceability: Deflection and crack width per Cl. 42/43
- torsion: Torsion design per Cl. 41

Created during Phase 1.5 restructure (TASK-700).
"""

from structural_lib.codes.is456.beam import (
    detailing,
    flexure,
    serviceability,
    shear,
    torsion,
)

__all__ = [
    "detailing",
    "flexure",
    "serviceability",
    "shear",
    "torsion",
]

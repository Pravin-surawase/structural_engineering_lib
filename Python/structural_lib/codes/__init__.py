"""Design codes implementations.

This package contains code-specific implementations:
- is456: Indian Standard IS 456:2000
- aci318: ACI 318 (placeholder for future)
- ec2: Eurocode 2 (placeholder for future)

Each code provides:
- Flexure design (required_steel_area, moment_capacity)
- Shear design (shear_reinforcement, shear_capacity)
- Detailing rules (min/max steel, cover, spacing)
- Material factors
- Tables and charts
"""

from __future__ import annotations

# Import to register codes on package load
from structural_lib.codes import is456

__all__ = ["is456"]

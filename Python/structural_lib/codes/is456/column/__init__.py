# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""IS 456:2000 — Column design modules.

Submodules:
    design: Axial load + uniaxial/biaxial bending (Cl. 39)
    slenderness: Short/long classification, effective length (Cl. 25.1.2, Table 28)

Backward compatibility:
    ``from structural_lib.codes.is456.column import X`` continues to work —
    all public names from ``design`` are re-exported here.
"""

from structural_lib.codes.is456.column.design import *  # noqa: F401,F403

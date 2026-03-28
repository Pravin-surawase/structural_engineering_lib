# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""IS 456:2000 — Shared helpers used by all element modules.

This subpackage contains code-specific constants, material properties,
lookup tables, and utility functions that are shared across beam, column,
slab, footing, and wall design modules.

Modules:
    materials: Material properties (fck, fy, Ec, xu_max/d)
    tables: IS 456 Table 19 (τc), Table 20 (τc_max), Table 28
    load_analysis: BMD/SFD computation for beam load cases
"""

from structural_lib.codes.is456.common.materials import (
    get_ec,
    get_fcr,
    get_xu_max_d,
)
from structural_lib.codes.is456.common.tables import (
    get_tc_max_value,
    get_tc_value,
    get_xu_max_ratio,
)

__all__ = [
    "get_ec",
    "get_fcr",
    "get_xu_max_d",
    "get_tc_value",
    "get_tc_max_value",
    "get_xu_max_ratio",
]

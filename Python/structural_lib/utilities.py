"""Backward compatibility stub.

This module has been migrated to: structural_lib.core.utilities
All functionality is re-exported here for backward compatibility.
Prefer importing directly from structural_lib.core.utilities."""

from __future__ import annotations

from structural_lib.core.utilities import (  # noqa: F401, E402
    deprecated,
    deprecated_field,
    linear_interp,
    m_to_mm,
    mm_to_m,
    round_to,
)

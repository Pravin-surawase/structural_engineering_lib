"""Backward compatibility stub.

This module has been migrated to: structural_lib.codes.is456.compliance

All functionality is re-exported here for backward compatibility.
Existing imports like `from structural_lib import compliance` continue to work.

Migration date: 2026-01-10 (Session 5)
"""

from __future__ import annotations

# Re-export private functions that tests depend on
# Re-export everything from the new location
from structural_lib.codes.is456.compliance import *  # noqa: F401, F403
from structural_lib.codes.is456.compliance import (  # noqa: F401
    _compute_crack_utilization,
    _compute_deflection_utilization,
    _compute_flexure_utilization,
    _compute_shear_utilization,
    _safe_crack_width_check,
    _safe_deflection_check,
    _utilization_safe,
)

# Re-export __all__ if defined
try:
    from structural_lib.codes.is456.compliance import __all__  # noqa: F401
except ImportError:
    pass  # Module may not define __all__

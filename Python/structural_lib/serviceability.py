"""Backward compatibility stub.

This module has been migrated to: structural_lib.codes.is456.serviceability

All functionality is re-exported here for backward compatibility.
Existing imports like `from structural_lib import serviceability` continue to work.

Migration date: 2026-01-10 (Session 5)
"""

from __future__ import annotations

# Re-export private functions that tests depend on
# Re-export everything from the new location
from structural_lib.codes.is456.serviceability import *  # noqa: F401, F403
from structural_lib.codes.is456.serviceability import (  # noqa: F401
    _as_dict,
    _normalize_exposure_class,
    _normalize_support_condition,
)

# Re-export data types that are expected to be accessible via this module
# These are needed for type annotations like `serviceability.DeflectionResult`
from structural_lib.data_types import (  # noqa: F401
    CrackWidthResult,
    DeflectionLevelBResult,
    DeflectionResult,
    ExposureClass,
    SupportCondition,
)

# Re-export __all__ if defined
try:
    from structural_lib.codes.is456.serviceability import __all__  # noqa: F401
except ImportError:
    pass  # Module may not define __all__

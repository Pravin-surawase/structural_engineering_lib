"""Backward compatibility shim — serviceability module moved to beam/ subpackage.

Migrated to: structural_lib.codes.is456.beam.serviceability
All existing imports like ``from structural_lib.codes.is456 import serviceability``
continue to work via this shim.

Migration: Phase 1.5 restructure (TASK-704).
"""

from __future__ import annotations

import warnings as _warnings

_warnings.warn(
    "structural_lib.codes.is456.serviceability has moved to "
    "structural_lib.codes.is456.beam.serviceability. "
    "Update imports to suppress this warning.",
    DeprecationWarning,
    stacklevel=2,
)

from structural_lib.codes.is456.beam.serviceability import *  # noqa: F401, F403, E402

# Re-export private names consumed by root-level shim
from structural_lib.codes.is456.beam.serviceability import (  # noqa: F401, E402
    _as_dict,
    _normalize_exposure_class,
    _normalize_support_condition,
)

try:
    from structural_lib.codes.is456.beam.serviceability import (
        __all__,
    )  # noqa: F401, E402
except ImportError:
    pass

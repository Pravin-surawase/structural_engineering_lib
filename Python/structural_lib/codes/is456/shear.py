"""Backward compatibility shim — shear module moved to beam/ subpackage.

Migrated to: structural_lib.codes.is456.beam.shear
All existing imports like ``from structural_lib.codes.is456 import shear``
continue to work via this shim.

Migration: Phase 1.5 restructure (TASK-702).
"""

from __future__ import annotations

import warnings as _warnings

_warnings.warn(
    "structural_lib.codes.is456.shear has moved to "
    "structural_lib.codes.is456.beam.shear. "
    "Update imports to suppress this warning.",
    DeprecationWarning,
    stacklevel=2,
)

from structural_lib.codes.is456.beam.shear import *  # noqa: F401, F403, E402

try:
    from structural_lib.codes.is456.beam.shear import __all__  # noqa: F401, E402
except ImportError:
    pass

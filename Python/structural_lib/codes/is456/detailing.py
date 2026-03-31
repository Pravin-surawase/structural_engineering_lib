"""Backward compatibility shim — detailing module moved to beam/ subpackage.

Migrated to: structural_lib.codes.is456.beam.detailing
All existing imports like ``from structural_lib.codes.is456 import detailing``
continue to work via this shim.

Migration: Phase 1.5 restructure (TASK-703).
"""

from __future__ import annotations

import warnings as _warnings

_warnings.warn(
    "structural_lib.codes.is456.detailing has moved to "
    "structural_lib.codes.is456.beam.detailing. "
    "Update imports to suppress this warning.",
    DeprecationWarning,
    stacklevel=2,
)

from structural_lib.codes.is456.beam.detailing import *  # noqa: F401, F403, E402

try:
    from structural_lib.codes.is456.beam.detailing import __all__  # noqa: F401, E402
except ImportError:
    pass

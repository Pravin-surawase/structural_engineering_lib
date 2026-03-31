"""Backward compatibility shim — flexure module moved to beam/ subpackage.

Migrated to: structural_lib.codes.is456.beam.flexure
All existing imports like ``from structural_lib.codes.is456 import flexure``
continue to work via this shim.

Migration: Phase 1.5 restructure (TASK-701).
"""

from __future__ import annotations

import warnings as _warnings

_warnings.warn(
    "structural_lib.codes.is456.flexure has moved to "
    "structural_lib.codes.is456.beam.flexure. "
    "Update imports to suppress this warning.",
    DeprecationWarning,
    stacklevel=2,
)

from structural_lib.codes.is456.beam.flexure import *  # noqa: F401, F403, E402

try:
    from structural_lib.codes.is456.beam.flexure import __all__  # noqa: F401, E402
except ImportError:
    pass

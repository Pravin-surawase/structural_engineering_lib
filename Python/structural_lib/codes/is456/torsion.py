"""Backward compatibility shim — torsion module moved to beam/ subpackage.

Migrated to: structural_lib.codes.is456.beam.torsion
All existing imports like ``from structural_lib.codes.is456 import torsion``
continue to work via this shim.

Migration: Phase 1.5 restructure (TASK-705).
"""

from __future__ import annotations

import warnings as _warnings


def __getattr__(name):
    from structural_lib.codes.is456.beam import torsion as _real

    attr = getattr(_real, name, None)
    if attr is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    _warnings.warn(
        f"{__name__} has moved to structural_lib.codes.is456.beam.torsion. "
        f"Update your import for '{name}'.",
        DeprecationWarning,
        stacklevel=2,
    )
    return attr

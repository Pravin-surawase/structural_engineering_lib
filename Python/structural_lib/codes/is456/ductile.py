# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Backward compatibility shim — ductile module moved to codes/is13920/.

Migrated to: structural_lib.codes.is13920.beam
IS 13920:2016 is a separate Indian Standard for ductile detailing.
All existing imports continue to work via this shim.

Migration: Phase 0 restructure (TASK-709).
"""

from __future__ import annotations

import warnings as _warnings

_warnings.warn(
    "structural_lib.codes.is456.ductile has moved to "
    "structural_lib.codes.is13920.beam. "
    "Update imports to suppress this warning.",
    DeprecationWarning,
    stacklevel=2,
)

from structural_lib.codes.is13920.beam import *  # noqa: F401, F403, E402

try:
    from structural_lib.codes.is13920.beam import __all__  # noqa: F401, E402
except ImportError:
    pass

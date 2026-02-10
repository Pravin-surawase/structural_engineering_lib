"""Backward compatibility stub.

This module has been migrated to: structural_lib.core.models
All functionality is re-exported here for backward compatibility.
Prefer importing directly from structural_lib.core.models."""

from __future__ import annotations

from structural_lib.core.models import (  # noqa: F401, E402
    BeamBatchInput,
    BeamBatchResult,
    BeamDesignResult,
    BeamForces,
    BeamGeometry,
    BuildingStatistics,
    DesignDefaults,
    DesignStatus,
    FrameType,
    Point3D,
    SectionProperties,
)

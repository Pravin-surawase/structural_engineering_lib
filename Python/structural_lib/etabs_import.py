"""Backward compatibility stub.

This module has been migrated to: structural_lib.services.etabs_import
All functionality is re-exported here for backward compatibility.
Prefer importing directly from structural_lib.services.etabs_import."""

from __future__ import annotations

from structural_lib.services.etabs_import import (  # noqa: F401, E402
    ETABSEnvelopeResult,
    ETABSForceRow,
    FrameGeometry,
    create_job_from_etabs,
    create_jobs_from_etabs_csv,
    envelopes_to_beam_forces,
    export_normalized_csv,
    frames_to_beam_geometries,
    load_etabs_csv,
    load_frames_geometry,
    merge_forces_and_geometry,
    normalize_etabs_forces,
    to_beam_forces,
    to_beam_geometry,
    validate_etabs_csv,
)

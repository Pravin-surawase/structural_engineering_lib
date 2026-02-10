"""Backward compatibility stub.

This module has been migrated to: structural_lib.core.inputs
All functionality is re-exported here for backward compatibility.
Prefer importing directly from structural_lib.core.inputs."""

from __future__ import annotations

from structural_lib.core.inputs import (  # noqa: F401, E402
    BeamGeometryInput,
    BeamInput,
    DetailingConfigInput,
    LoadCaseInput,
    LoadsInput,
    MaterialsInput,
    from_dict,
    from_json,
    from_json_file,
)

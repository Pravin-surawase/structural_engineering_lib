"""Backward compatibility stub.

This module has been migrated to: structural_lib.services.serialization
All functionality is re-exported here for backward compatibility.
Prefer importing directly from structural_lib.services.serialization."""

from __future__ import annotations

from structural_lib.services.serialization import (  # noqa: F401, E402
    generate_all_schemas,
    generate_schema,
    load_batch_input,
    load_batch_result,
    load_forces,
    load_geometry,
    save_batch_input,
    save_batch_result,
    save_forces,
    save_geometry,
)

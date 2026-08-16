"""Backward compatibility stub.

This module has been migrated to: structural_lib.services.imports
All functionality is re-exported here for backward compatibility.
Prefer importing directly from structural_lib.services.imports."""

from __future__ import annotations

from structural_lib.services.import_ledger import (  # noqa: F401, E402
    AdapterSelectionV1,
    ImportArtifactV1,
    ImportFieldAction,
    ImportFieldLedgerV1,
    ImportIssueCode,
    ImportIssueV1,
    ImportNormalizationLedgerV1,
    ImportRowLedgerV1,
    ImportStatus,
    ImportTotalsV1,
    LosslessImportResultV1,
)
from structural_lib.services.imports import (  # noqa: F401, E402
    ImportWarnings,
    LosslessImportBlockedError,
    merge_geometry_forces,
    parse_dual_csv,
    parse_dual_csv_lossless,
    parse_single_csv_lossless,
    validate_import,
)

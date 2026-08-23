"""Backward compatibility stub.

This module has been migrated to: structural_lib.services.imports
All functionality is re-exported here for backward compatibility.
Prefer importing directly from structural_lib.services.imports."""

from __future__ import annotations

from structural_lib.services.etabs_snapshot import (  # noqa: F401, E402
    ETABSApprovedExclusionV1,
    ETABSArchivedTableInputV1,
    ETABSBeamRequestBasisV1,
    ETABSCanonicalSnapshotV1,
    ETABSExportUnitsV1,
    ETABSLocalAxisMappingV1,
    ETABSMemberIdentityV1,
    ETABSProjectExportIdentityV1,
    ETABSResultIdentityV1,
    ETABSRowAccountingV1,
    ETABSRowDisposition,
    ETABSRowDispositionV1,
    ETABSSnapshotAmbiguityV1,
    ETABSSnapshotBuildResultV1,
    ETABSSnapshotIssueV1,
    ETABSSnapshotStatus,
    ETABSSourceArtifactV1,
    build_etabs_canonical_snapshot_v1,
    verify_etabs_canonical_snapshot_hash_v1,
)
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

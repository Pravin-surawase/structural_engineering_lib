"""Backward compatibility stub.

This module has been migrated to: structural_lib.services.audit
All functionality is re-exported here for backward compatibility.
Prefer importing directly from structural_lib.services.audit."""

from __future__ import annotations

from structural_lib.services.audit import (  # noqa: F401, E402
    AuditLogEntry,
    AuditTrail,
    CalculationHash,
    compute_hash,
    create_calculation_certificate,
    verify_calculation,
)

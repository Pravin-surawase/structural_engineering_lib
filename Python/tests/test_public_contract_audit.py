"""The S3 matrix must account for every actual OpenAPI operation/component."""

import importlib.util
from pathlib import Path

import pytest

pytestmark = pytest.mark.repo_only
_PATH = Path(__file__).resolve().parents[2] / "scripts/audit_public_contracts.py"
_SPEC = importlib.util.spec_from_file_location("audit_public_contracts", _PATH)
assert _SPEC and _SPEC.loader
audit = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(audit)


def test_contract_matrix_has_no_unowned_or_unresolved_components():
    matrix = audit.build_matrix()
    assert matrix["counts"] == {
        "surfaces": 14,
        "projections": 1308,
        "operations": 92,
        "paths": 91,
        "components": 488,
        "family_fields": 564,
    }
    assert all(item["operations"] and item["name"] for item in matrix["components"])
    assert all(
        op["owner"] and op["admission"] and op["evidence_boundary"]
        for op in matrix["operations"]
    )
    assert len(matrix["families"]) == 13
    assert matrix["signature_policy"]["reviewed_exception_count"] == 33

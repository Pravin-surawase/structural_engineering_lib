"""R0 advertised-field, adversarial-vector, and consumer acceptance."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.repo_only

_SCRIPT = (
    Path(__file__).resolve().parents[3]
    / "scripts"
    / "verify_lib_pro_012_r0_external_preview.py"
)
_SPEC = importlib.util.spec_from_file_location("r0_external_preview", _SCRIPT)
assert _SPEC is not None and _SPEC.loader is not None
r0 = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = r0
_SPEC.loader.exec_module(r0)


def test_all_advertised_family_fields_have_explicit_contract_decisions() -> None:
    receipt = r0.run_contract_audit()

    assert receipt["journey_count"] == 13
    assert receipt["unowned_field_count"] == 0
    assert all(
        workflow["compatibility_target_resolved"]
        and not workflow["unowned_field_paths"]
        for workflow in receipt["workflows"]
    )


def test_every_advertised_contract_class_has_adversarial_and_consumer_evidence() -> (
    None
):
    receipt = r0.run_contract_vectors()
    counts = receipt["vector_class_counts"]

    assert len(receipt["routes"]) == 13
    assert all(count > 0 for count in counts.values())
    assert counts["finite"] == 13
    assert counts["identity_or_provenance"] == 13
    assert counts["compatibility_target"] == 13
    assert counts["finite_json_consumer"] == 13
    assert counts["boolean"] == 11
    assert counts["cross_field_relation"] == 3
    assert counts["collection_cardinality"] == 1

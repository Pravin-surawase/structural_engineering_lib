"""Replay the independently frozen B01 direct service evidence."""

import hashlib
import json
from copy import deepcopy
from pathlib import Path

import pytest
from scripts._lib.release_slab_footing import (
    SLAB_DIRECT_SERVICE_CASES,
    SLAB_DIRECT_SERVICE_FIXTURE,
    input_paths,
    verify_slab_direct_service,
)

from structural_lib.design.is456 import slab

ROOT = Path(__file__).resolve().parents[3]
REFERENCE = ROOT / SLAB_DIRECT_SERVICE_FIXTURE
CASES = json.loads(REFERENCE.read_text(encoding="utf-8"))
SHA256 = "1f52e7e3616267bc6a0345fd775d6b08dcc472b4242f888c3fccfd356a2f7a7f"


def test_direct_slab_service_matches_frozen_reference():
    assert hashlib.sha256(REFERENCE.read_bytes()).hexdigest() == SHA256
    observed = {}
    for name, case in CASES["cases"].items():
        request = slab.load_direct_service(case["request"])
        result = slab.check_direct_service(request)
        observed[name] = {"case": name, "result": result.to_dict()}
    verify_slab_direct_service(observed, CASES)


def test_direct_slab_service_registered_for_030_artifacts():
    assert set(SLAB_DIRECT_SERVICE_CASES) == set(CASES["cases"])
    assert REFERENCE not in input_paths(ROOT, "0.29.2")
    assert REFERENCE in input_paths(ROOT, "0.30.0a1")


@pytest.mark.parametrize(
    ("group", "field", "value", "status", "code"),
    [
        (
            "section.distribution",
            "y_from_top_mm",
            117,
            "FAIL",
            "SLAB.SERVICE_LAYOUT_FAIL",
        ),
        (
            "service_loads.total",
            "support_shear_kn",
            11,
            "HOLD",
            "SLAB.SERVICE_ACTIONS_HELD",
        ),
        (
            "history",
            "axial_restraint",
            "restrained",
            "HOLD",
            "SLAB.SERVICE_HISTORY_HELD",
        ),
    ],
)
def test_direct_slab_service_checks_physical_evidence(
    group, field, value, status, code
):
    raw = deepcopy(CASES["cases"]["b01_service_history"]["request"])
    parent = raw
    for name in group.split("."):
        parent = parent[name]
    parent[field] = value
    result = slab.check_direct_service(slab.load_direct_service(raw))
    assert result.engineering_status.value == status
    assert {issue.code for issue in result.issues} == {code}
    assert result.calculation == {}


def test_invalid_lower_load_witness_keeps_deflection_on_hold():
    raw = deepcopy(CASES["cases"]["longer_span"]["request"])
    raw["elastic_witness_load_kn_per_m2"] = 6.75
    result = slab.check_direct_service(slab.load_direct_service(raw))
    assert result.engineering_status.value == "HOLD"
    assert result.calculation["deflection"]["final_deflection_mm"] is None
    assert result.calculation["crack"]["width_mm"] is None

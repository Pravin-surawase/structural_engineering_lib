"""One PASS/FAIL boundary vector across maintained Python and workflow surfaces."""

from __future__ import annotations

import json

import pytest

import structural_lib
from structural_lib import api as compatibility_api
from structural_lib.services import api as service_api
from structural_lib.services.project_beam import EffectiveDepthBasisV1
from structural_lib.services.serialization import to_transport_value
from structural_lib.services.workflow_runner import (
    WorkflowRunner,
    get_beam_workflow_template_document,
)

_BASIS = EffectiveDepthBasisV1(
    clear_cover_mm=40.0,
    stirrup_diameter_mm=8.0,
    tension_bar_diameter_mm=18.0,
)
_DIRECT_INPUTS = {
    "units": "IS456",
    "case_id": "CASE-1",
    "b_mm": 300.0,
    "D_mm": 500.0,
    "d_mm": None,
    "effective_depth_basis": _BASIS,
    "mu_knm": 150.0,
    "vu_kn": 420.0,
    "fck_nmm2": 25.0,
    "fy_nmm2": 500.0,
}


def test_python_facades_and_json_share_one_canonical_result() -> None:
    results = [
        service_api.design_beam_is456(**_DIRECT_INPUTS),
        structural_lib.design_beam_is456(**_DIRECT_INPUTS),
        compatibility_api.design_beam_is456(**_DIRECT_INPUTS),
    ]
    transports = [to_transport_value(result) for result in results]

    assert transports[0] == transports[1] == transports[2]
    assert json.loads(json.dumps(transports[0], allow_nan=False)) == transports[0]
    assert transports[0]["effective_depth_resolution"] == {
        "contract_version": "effective-depth-basis/v1",
        "source": "DERIVED",
        "D_mm": 500.0,
        "d_mm": 443.0,
        "effective_depth_basis": {
            "clear_cover_mm": 40.0,
            "stirrup_diameter_mm": 8.0,
            "tension_bar_diameter_mm": 18.0,
        },
    }
    assert transports[0]["is_ok"] is False
    assert transports[0]["governing_utilization"] == pytest.approx(1.01944, rel=1e-4)
    assert transports[0]["result_envelope"]["engineering_status"] == "FAIL"
    assert transports[0]["result_envelope"]["overall_status"] == "FAIL"


def test_canonical_service_requires_exactly_one_effective_depth_method() -> None:
    conflicting_depth = dict(_DIRECT_INPUTS)
    conflicting_depth["d_mm"] = 443.0
    with pytest.raises(ValueError, match="not both"):
        service_api.design_beam_is456(**conflicting_depth)

    missing_depth = dict(_DIRECT_INPUTS)
    missing_depth.pop("effective_depth_basis")
    with pytest.raises(ValueError, match="Supply d_mm"):
        service_api.design_beam_is456(**missing_depth)


def test_workflow_uses_the_same_depth_and_engineering_disposition() -> None:
    direct = service_api.design_beam_is456(**_DIRECT_INPUTS)
    workflow = WorkflowRunner().run(
        definition=get_beam_workflow_template_document(),
        inputs={
            "width": 300.0,
            "depth": 500.0,
            "clear_cover": 40.0,
            "stirrup_dia_mm": 8.0,
            "main_bar_dia_mm": 18.0,
            "moment": 150.0,
            "shear": 420.0,
            "fck": 25.0,
            "fy": 500.0,
        },
        run_id="depth-boundary",
        review_acknowledged=True,
    )
    design = workflow["steps"][2]["output"]

    assert workflow["status"] == "UNSAFE"
    assert design["effective_depth_used"] == 443.0
    assert design["governing_utilization"] == pytest.approx(
        direct.governing_utilization
    )
    assert design["is_ok"] is direct.is_ok is False
    assert design["result_envelope"] == direct.result_envelope

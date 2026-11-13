"""Column JSON projections exercised against source and installed archives."""

import json
import math
from dataclasses import replace

import pytest

from structural_lib.core.errors import CalculationError
from structural_lib.design.is456 import column
from structural_lib.services.column_api import design_column_axial_is456
from structural_lib.services.serialization import to_transport_value


@pytest.mark.parametrize(
    ("load", "length", "check_name", "field", "safe"),
    [
        (0, 2400, "uniaxial_x", "eccentricity_mm", True),
        (2500, 2400, "biaxial", "interaction_ratio", False),
        (2500, 5200, "long_column", "interaction_ratio", False),
    ],
)
def test_column_family_exports_unavailable_values_with_the_design_outcome(
    load, length, check_name, field, safe
):
    request = column.input(
        identity={"family_id": "column", "case_id": "transport"},
        geometry={
            "b_mm": 300,
            "D_mm": 400,
            "unsupported_length_mm": length,
            "minimum_eccentricity_length_mm": length,
            "end_condition": "HINGED_HINGED",
            "braced": True,
        },
        actions={
            "pu_kn": load,
            "mux_knm": 30,
            "muy_knm": 0,
            "m1x_signed_knm": 20,
            "m2x_signed_knm": 30,
            "m1y_signed_knm": 0,
            "m2y_signed_knm": 0,
        },
        materials={"fck_nmm2": 25, "fy_nmm2": 415},
        reinforcement={
            "supplied_steel_area_mm2": 1600,
            "reinforcement_centroid_depth_mm": 50,
        },
    )
    result = column.check(request)
    native = result.calculation["checks"][check_name]
    assert getattr(native, field) == math.inf
    assert native.is_safe is safe
    wire = result.to_dict()
    assert wire["envelope"]["engineering_status"] == ("PASS" if safe else "FAIL")
    projection = wire["calculation"]["checks"][check_name]
    assert projection == to_transport_value(native)
    assert projection[field] is None
    assert projection["unavailable_values"][field]["reason"]
    json.dumps(native.to_dict(), allow_nan=False)
    json.dumps(wire, allow_nan=False)
    for invalid in (math.nan, -math.inf):
        with pytest.raises(CalculationError, match="unexplained non-finite"):
            to_transport_value(replace(native, **{field: invalid}))


def test_short_axial_column_classification_is_json_serializable():
    result = design_column_axial_is456(
        fck_nmm2=25,
        fy_nmm2=415,
        Ag_mm2=120_000,
        Asc_mm2=1600,
    )
    payload = json.loads(json.dumps(result.to_dict(), allow_nan=False))
    assert payload["classification"] == result.classification.value == 1

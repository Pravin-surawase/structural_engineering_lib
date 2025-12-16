import json
from pathlib import Path

import pytest

from structural_lib import api


def _load_vectors() -> dict:
    path = Path(__file__).parent / "data" / "golden_vectors_is456.json"
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.mark.parametrize("vector", _load_vectors()["cases"], ids=lambda v: v["case_id"])
def test_is456_golden_vectors(vector: dict):
    vectors = _load_vectors()
    common = vectors["common_inputs"]

    res = api.design_beam_is456(
        units=vectors["units"]["system"],
        case_id=vector["case_id"],
        mu_knm=vector["mu_knm"],
        vu_kn=vector["vu_kn"],
        b_mm=common["b_mm"],
        D_mm=common["D_mm"],
        d_mm=common["d_mm"],
        fck_nmm2=common["fck_nmm2"],
        fy_nmm2=common["fy_nmm2"],
        d_dash_mm=common["d_dash_mm"],
        asv_mm2=common["asv_mm2"],
    )

    exp = vector["expected"]
    assert res.is_ok is exp["is_ok"]

    # Flexure key outputs
    assert res.flexure.is_safe is exp["flexure"]["is_safe"]
    assert res.flexure.mu_lim == pytest.approx(
        exp["flexure"]["mu_lim"], rel=1e-12, abs=1e-12
    )
    assert res.flexure.ast_required == pytest.approx(
        exp["flexure"]["ast_required"], rel=1e-12, abs=1e-9
    )
    assert res.flexure.asc_required == pytest.approx(
        exp["flexure"]["asc_required"], abs=1e-12
    )

    # Shear key outputs
    assert res.shear.is_safe is exp["shear"]["is_safe"]
    assert res.shear.tv == pytest.approx(exp["shear"]["tv"], rel=1e-12, abs=1e-12)
    assert res.shear.tc == pytest.approx(exp["shear"]["tc"], rel=1e-12, abs=1e-12)
    assert res.shear.tc_max == pytest.approx(
        exp["shear"]["tc_max"], rel=1e-12, abs=1e-12
    )
    assert res.shear.spacing == pytest.approx(
        exp["shear"]["spacing"], rel=1e-12, abs=1e-9
    )


def test_is456_golden_vectors_are_deterministic_on_repeat():
    vectors = _load_vectors()
    common = vectors["common_inputs"]
    v = vectors["cases"][0]

    res1 = api.design_beam_is456(
        units=vectors["units"]["system"],
        case_id=v["case_id"],
        mu_knm=v["mu_knm"],
        vu_kn=v["vu_kn"],
        b_mm=common["b_mm"],
        D_mm=common["D_mm"],
        d_mm=common["d_mm"],
        fck_nmm2=common["fck_nmm2"],
        fy_nmm2=common["fy_nmm2"],
        d_dash_mm=common["d_dash_mm"],
        asv_mm2=common["asv_mm2"],
    )

    res2 = api.design_beam_is456(
        units=vectors["units"]["system"],
        case_id=v["case_id"],
        mu_knm=v["mu_knm"],
        vu_kn=v["vu_kn"],
        b_mm=common["b_mm"],
        D_mm=common["D_mm"],
        d_mm=common["d_mm"],
        fck_nmm2=common["fck_nmm2"],
        fy_nmm2=common["fy_nmm2"],
        d_dash_mm=common["d_dash_mm"],
        asv_mm2=common["asv_mm2"],
    )

    assert res1.utilizations == res2.utilizations
    assert res1.flexure.ast_required == res2.flexure.ast_required
    assert res1.shear.spacing == res2.shear.spacing

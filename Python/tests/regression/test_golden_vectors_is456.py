import json
from pathlib import Path

import pytest

from structural_lib import api
from structural_lib.codes.is456.beam.flexure import design_flanged_beam


def _load_vectors() -> dict:
    # Path to tests/data/ (two levels up from tests/regression/)
    path = Path(__file__).parent.parent / "data" / "golden_vectors_is456.json"
    return json.loads(path.read_text(encoding="utf-8"))


_VECTORS = _load_vectors()


def _get_beam_flexure_inputs(vector: dict, common: dict) -> dict:
    """Build design_beam_is456 kwargs from a beam_flexure vector."""
    inputs = vector.get("inputs", common)
    return {
        "units": _VECTORS["units"]["system"],
        "case_id": vector["case_id"],
        "mu_knm": vector["mu_knm"],
        "vu_kn": vector["vu_kn"],
        "b_mm": inputs["b_mm"],
        "D_mm": inputs["D_mm"],
        "d_mm": inputs["d_mm"],
        "fck_nmm2": inputs["fck_nmm2"],
        "fy_nmm2": inputs["fy_nmm2"],
        "d_dash_mm": inputs["d_dash_mm"],
        "asv_mm2": inputs["asv_mm2"],
    }


# ─── Beam Flexure/Shear (G1–G5) ─────────────────────────────────────────────


@pytest.mark.golden
@pytest.mark.parametrize(
    "vector",
    _VECTORS["beam_flexure_cases"],
    ids=lambda v: v["case_id"],
)
def test_beam_flexure_golden(vector: dict):
    """Golden test: beam flexure/shear against SP:16 reference values."""
    common = _VECTORS["common_inputs"]
    kwargs = _get_beam_flexure_inputs(vector, common)
    tol = vector.get("tolerance", 1e-12)

    res = api.design_beam_is456(**kwargs)
    exp = vector["expected"]

    assert res.is_ok is exp["is_ok"]

    # Flexure
    assert res.flexure.is_safe is exp["flexure"]["is_safe"]
    assert res.flexure.Mu_lim == pytest.approx(exp["flexure"]["mu_lim"], rel=tol)
    assert res.flexure.Ast_required == pytest.approx(
        exp["flexure"]["ast_required"], rel=tol
    )
    assert res.flexure.Asc_required == pytest.approx(
        exp["flexure"]["asc_required"], abs=max(tol, 1e-9)
    )
    if "xu" in exp["flexure"]:
        assert res.flexure.xu == pytest.approx(exp["flexure"]["xu"], rel=tol)
    if "xu_max" in exp["flexure"]:
        assert res.flexure.xu_max == pytest.approx(exp["flexure"]["xu_max"], rel=tol)

    # Shear
    assert res.shear.is_safe is exp["shear"]["is_safe"]
    assert res.shear.tau_v == pytest.approx(exp["shear"]["tv"], rel=tol)
    assert res.shear.tau_c == pytest.approx(exp["shear"]["tc"], rel=tol)
    assert res.shear.tau_c_max == pytest.approx(exp["shear"]["tc_max"], rel=tol)
    assert res.shear.spacing == pytest.approx(exp["shear"]["spacing"], rel=tol)


# ─── Flanged Beam (G6) ──────────────────────────────────────────────────────


@pytest.mark.golden
@pytest.mark.parametrize(
    "vector",
    _VECTORS["beam_flanged_cases"],
    ids=lambda v: v["case_id"],
)
def test_beam_flanged_golden(vector: dict):
    """Golden test: flanged beam (T-beam) against SP:16 Annex G values."""
    inp = vector["inputs"]
    tol = vector.get("tolerance", 0.001)

    res = design_flanged_beam(
        bw=inp["bw_mm"],
        bf=inp["bf_mm"],
        d=inp["d_mm"],
        Df=inp["df_mm"],
        d_total=inp["D_mm"],
        mu_knm=vector["mu_knm"],
        fck=inp["fck_nmm2"],
        fy=inp["fy_nmm2"],
        d_dash=inp["d_dash_mm"],
    )

    exp = vector["expected"]["flexure"]
    assert res.is_safe is exp["is_safe"]
    assert res.Mu_lim == pytest.approx(exp["mu_lim"], rel=tol)
    assert res.Ast_required == pytest.approx(exp["ast_required"], rel=tol)
    assert res.Asc_required == pytest.approx(exp["asc_required"], abs=max(tol, 1e-9))
    assert res.xu == pytest.approx(exp["xu"], rel=tol)
    assert res.xu_max == pytest.approx(exp["xu_max"], rel=tol)


# ─── Beam Torsion (G7) ──────────────────────────────────────────────────────


@pytest.mark.golden
@pytest.mark.parametrize(
    "vector",
    _VECTORS["beam_torsion_cases"],
    ids=lambda v: v["case_id"],
)
def test_beam_torsion_golden(vector: dict):
    """Golden test: torsion design against IS 456 Cl 41 values."""
    inp = vector["inputs"]
    tol = vector.get("tolerance", 0.001)

    res = api.design_torsion(
        tu_knm=inp["tu_knm"],
        vu_kn=inp["vu_kn"],
        mu_knm=inp["mu_knm"],
        b=inp["b_mm"],
        D=inp["D_mm"],
        d=inp["d_mm"],
        fck=inp["fck_nmm2"],
        fy=inp["fy_nmm2"],
        cover=inp["cover_mm"],
        stirrup_dia=inp["stirrup_dia_mm"],
        pt=inp["pt_percent"],
    )

    exp = vector["expected"]
    assert res.is_safe is exp["is_safe"]
    assert res.Ve_kn == pytest.approx(exp["Ve_kn"], rel=tol)
    assert res.Me_knm == pytest.approx(exp["Me_knm"], rel=tol)
    assert res.tau_ve == pytest.approx(exp["tau_ve"], rel=tol)
    assert res.tau_c == pytest.approx(exp["tau_c"], rel=tol)
    assert res.tau_c_max == pytest.approx(exp["tau_c_max"], rel=tol)
    assert res.Asv_torsion == pytest.approx(exp["Asv_torsion"], rel=tol)
    assert res.Al_torsion == pytest.approx(exp["Al_torsion"], rel=tol)
    assert res.stirrup_spacing == exp["stirrup_spacing"]
    assert res.requires_closed_stirrups is exp["requires_closed_stirrups"]


# ─── Beam Serviceability / Deflection (G8) ───────────────────────────────────


@pytest.mark.golden
@pytest.mark.parametrize(
    "vector",
    _VECTORS["beam_serviceability_cases"],
    ids=lambda v: v["case_id"],
)
def test_beam_serviceability_golden(vector: dict):
    """Golden test: deflection span/depth ratio against IS 456 Cl 23.2.1."""
    inp = vector["inputs"]
    tol = vector.get("tolerance", 0.001)

    res = api.check_deflection_span_depth(
        span_mm=inp["span_mm"],
        d_mm=inp["d_mm"],
        support_condition=inp["support_condition"],
        mf_tension_steel=inp.get("mf_tension_steel"),
    )

    exp = vector["expected"]
    assert res.is_ok is exp["is_ok"]
    assert res.computed["ld_ratio"] == pytest.approx(exp["ld_ratio"], rel=tol)
    assert res.computed["allowable_ld"] == pytest.approx(exp["allowable_ld"], rel=tol)
    assert res.computed["base_allowable_ld"] == pytest.approx(
        exp["base_allowable_ld"], rel=tol
    )
    assert res.computed["mf_tension_steel"] == pytest.approx(
        exp["mf_tension_steel"], rel=tol
    )


# ─── Determinism check ──────────────────────────────────────────────────────


def test_is456_golden_vectors_are_deterministic_on_repeat():
    common = _VECTORS["common_inputs"]
    v = _VECTORS["beam_flexure_cases"][0]
    kwargs = _get_beam_flexure_inputs(v, common)

    res1 = api.design_beam_is456(**kwargs)
    res2 = api.design_beam_is456(**kwargs)

    assert res1.utilizations == res2.utilizations
    assert res1.flexure.Ast_required == res2.flexure.Ast_required
    assert res1.shear.spacing == res2.shear.spacing

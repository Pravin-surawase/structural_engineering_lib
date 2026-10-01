"""Independent source-defined SLS anchors using 60-digit Decimal mechanics.

No production imports. Service stress uses elastic transformed sections.
C2.1 is the prescribed empirical inertia expression; C3.1 is the prescribed
shrinkage approximation. C4.1 changes the permanent-load modulus and section.
Elastic deflection is derived separately by integrating actual and unit-load
bending moments. Inputs use mm, N/mm², mm² and unfactored kNm; outputs mm.
"""

from __future__ import annotations

import json
from decimal import Decimal, localcontext
from pathlib import Path


def d(value):
    return Decimal(str(value))


def integrate_polynomial(coefficients, upper):
    return sum(c * upper ** (i + 1) / d(i + 1) for i, c in enumerate(coefficients))


def elastic_deflection(moment, length, rigidity, support):
    if support == "simply_supported":
        # w=8*M/L²; M(x)=w*x*(L-x)/2, virtual m(x)=x/2 on left half.
        w = 8 * moment * d(1000000) / length**2
        product = [d(0), d(0), w * length / 4, -w / 4]
        return 2 * integrate_polynomial(product, length / 2) / rigidity
    # Actual M=P*(L-x), virtual m=L-x, P=Mroot/L.
    p = moment * d(1000000) / length
    return integrate_polynomial([p * length**2, -2 * p * length, p], length) / rigidity


def section(inputs, ec, moment):
    b, height, depth, area, es = (
        d(inputs[k]) for k in ("b_mm", "D_mm", "d_mm", "ast_mm2", "es_nmm2")
    )
    n = es / ec
    # Independent quadratic root and force equilibrium, not production helper.
    x = (-n * area + ((n * area) ** 2 + 2 * b * n * area * depth).sqrt()) / b
    icr = b * x**3 / 3 + n * area * (depth - x) ** 2
    ig = b * height**3 / 12
    mr = d(".7") * d(inputs["fck_nmm2"]).sqrt() * ig / (height / 2) / d(1000000)
    z = depth - x / 3
    ieff = (
        ig
        if moment <= mr
        else min(
            ig,
            max(icr, icr / (d("1.2") - (mr / moment) * (z / depth) * (1 - x / depth))),
        )
    )
    return {
        "ec_nmm2": ec,
        "x_mm": x,
        "z_mm": z,
        "icr_mm4": icr,
        "igross_mm4": ig,
        "mcr_knm": mr,
        "ieff_mm4": ieff,
        "force_residual_n": b * x * x / 2 - n * area * (depth - x),
    }


def response(inputs):
    ec = d(5000) * d(inputs["fck_nmm2"]).sqrt()
    permanent, variable = abs(d(inputs["ma_sustained_knm"])), abs(
        d(inputs["ma_live_knm"])
    )
    support, span = inputs["support_condition"], d(inputs["span_mm"])
    theta = (
        {7: d("2.2"), 28: d("1.6"), 365: d("1.1")}[inputs["age_at_loading_days"]]
        if permanent
        else d(0)
    )
    initial = section(inputs, ec, permanent + variable)
    original_permanent = section(inputs, ec, permanent)
    long_permanent = section(inputs, ec / (1 + theta), permanent)
    immediate = elastic_deflection(
        permanent + variable, span, ec * initial["ieff_mm4"], support
    )
    initial_sustained = elastic_deflection(
        permanent, span, ec * original_permanent["ieff_mm4"], support
    )
    long_sustained = elastic_deflection(
        permanent, span, long_permanent["ec_nmm2"] * long_permanent["ieff_mm4"], support
    )
    pt = 100 * d(inputs["ast_mm2"]) / (d(inputs["b_mm"]) * d(inputs["d_mm"]))
    k4 = min(d(1), (d(".72") if pt < 1 else d(".65")) * pt / pt.sqrt())
    phi = k4 * d(inputs["shrinkage_strain"]) / d(inputs["D_mm"])
    shrink = (d(".125") if support == "simply_supported" else d(".5")) * phi * span**2
    creep = long_sustained - initial_sustained
    total = immediate + creep + shrink
    stress = (
        permanent
        * d(1000000)
        * (
            d(inputs["D_mm"]) / 2 / original_permanent["igross_mm4"]
            if permanent <= initial["mcr_knm"]
            else original_permanent["x_mm"] / original_permanent["icr_mm4"]
        )
    )
    assert stress <= d(inputs["fck_nmm2"]) / 3
    return {
        **initial,
        "permanent_initial_section": original_permanent,
        "permanent_long_term_section": long_permanent,
        "delta_permanent_initial_mm": initial_sustained,
        "delta_permanent_long_term_mm": long_sustained,
        "delta_immediate_mm": immediate,
        "delta_creep_mm": creep,
        "delta_shrinkage_mm": shrink,
        "delta_total_mm": total,
        "delta_limit_mm": span / d(inputs["deflection_limit_ratio"]),
        "creep_coefficient": theta,
        "shrinkage_curvature": phi,
        "k4": k4,
        "permanent_concrete_stress_nmm2": stress,
        "is_ok": total <= span / d(inputs["deflection_limit_ratio"]),
    }


def encode(value, exact=False):
    if isinstance(value, Decimal):
        return str(value) if exact else float(value)
    if isinstance(value, dict):
        return {k: encode(v, exact) for k, v in value.items()}
    if isinstance(value, list):
        return [encode(v, exact) for v in value]
    return value


def references():
    base = {
        "b_mm": 300,
        "D_mm": 500,
        "d_mm": 450,
        "span_mm": 6000,
        "ast_mm2": 1200,
        "fck_nmm2": 25,
        "asc_mm2": 0,
        "age_at_loading_days": 28,
        "relative_humidity_percent": 50,
        "shrinkage_strain": 0.0003,
        "deflection_limit_ratio": 250,
        "es_nmm2": 200000,
        "support_condition": "simply_supported",
        "ma_sustained_knm": 0,
        "ma_live_knm": 0,
    }
    mr = section(base, d(25000), d(0))["mcr_knm"]
    states = []
    for support in ("simply_supported", "cantilever"):
        for age in (7, 28, 365):
            for ratio in (".8", "1.05", "1.5", "2", "3"):
                for sign in (1, -1):
                    inputs = {
                        **base,
                        "support_condition": support,
                        "span_mm": 6000 if support == "simply_supported" else 3000,
                        "age_at_loading_days": age,
                        "ma_sustained_knm": float(sign * d(".4") * d(ratio) * mr),
                        "ma_live_knm": float(sign * d(".6") * d(ratio) * mr),
                    }
                    expected = response(inputs)
                    states.append(
                        {
                            "id": f"{support}-{age}-Mratio{ratio}-sign{sign}",
                            "inputs": inputs,
                            "expected": encode(expected),
                            "exact_expected": encode(expected, True),
                        }
                    )
        inputs = {
            **base,
            "support_condition": support,
            "span_mm": 6000 if support == "simply_supported" else 3000,
        }
        expected = response(inputs)
        states.append(
            {
                "id": f"{support}-zero-load-shrinkage",
                "inputs": inputs,
                "expected": encode(expected),
                "exact_expected": encode(expected, True),
            }
        )
    holds = []
    supported = {**base, "ma_sustained_knm": 17.5, "ma_live_knm": 26.25}
    for name, changes, basis in (
        (
            "continuous",
            {"support_condition": "continuous"},
            "C2.1/Table25 support averaging; C3.1 distinct support cases",
        ),
        (
            "compression-bars",
            {"asc_mm2": 300},
            "transformed-section mechanics require compression-bar coordinate",
        ),
        (
            "age14",
            {"age_at_loading_days": 14},
            "6.2.5.1 lists ages7/28/365 only; no selected interpolation",
        ),
        (
            "age90",
            {"age_at_loading_days": 90},
            "6.2.5.1 lists ages7/28/365 only; no selected interpolation",
        ),
        (
            "opposing-loads",
            {"ma_live_knm": -17.5},
            "cracking/loading-history cannot be inferred from cancellation",
        ),
        (
            "low-shrinkage-imbalance",
            {"ast_mm2": 300},
            "C3.1 stated k4 domain pt-pc>=.25 percent",
        ),
        (
            "nonlinear-creep-stress",
            {"ma_sustained_knm": 90},
            "6.2.5 proportional creep stress limited to fck/3",
        ),
        (
            "high-grade-default",
            {"fck_nmm2": 60},
            "6.1 note beyond M55 needs additional material/design data",
        ),
    ):
        holds.append(
            {
                "id": name,
                "inputs": {**supported, **changes},
                "expected_status": "HOLD_UNSUPPORTED",
                "basis": basis,
            }
        )
    return {
        "source": {
            "method": "IS456_ANNEX_C_RECT_SINGLE_V1",
            "primary": "IS456:2000 Cl6.2.3.1/6.2.4.1/6.2.5/6.2.5.1; AnnexC2.1/C3.1/C4.1",
            "primary_url": "https://law.resource.org/pub/in/bis/S03/is.456.2000.pdf#page=101",
            "controlled_sha256": "964e270593392a0dea28b8c7c9ff1e0e730bbea912f8a903e8a86c7bb34d9264",
            "printed_pages": [15, 16, 88, 89],
            "arithmetic": "60-digit Decimal; independent virtual-work polynomial integration",
            "scope": "singly reinforced rectangles; SS UDL or cantilever end point; same-direction unfactored actions; default ultimate estimates",
            "source_limit": "controlled Amd5 consolidation and Amd6 targeted check; latest complete amendment set not certified",
        },
        "states": states,
        "unsupported": holds,
    }


if __name__ == "__main__":
    with localcontext() as context:
        context.prec = 60
        result = references()
    path = Path(__file__).with_name("sls_annexc_reference.json")
    path.write_text(
        json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "states": len(result["states"]),
                "unsupported": len(result["unsupported"]),
                "fixture": str(path),
            }
        )
    )

"""Independent Decimal anchors for representative Fig23 and Annex G bar forces.

No production imports. Source figures define families, Es, partial factors and
plastic offsets. Exact design-curve values remain separate from rounded Table A
and the prescribed .36/.42/.87 design-force equations.
"""

from __future__ import annotations

import json
from decimal import Decimal, localcontext
from pathlib import Path


def decimal(value):
    return Decimal(str(value))


def stress(strain, fy):
    es = decimal(200000)
    strength = decimal(fy) / decimal("1.15")
    magnitude = abs(strain)
    if fy == 250:
        value = min(es * magnitude, strength)
    else:
        vertices = [(decimal(0), decimal(0))]
        vertices.extend(
            (decimal(p) + decimal(r) * strength / es, decimal(r) * strength)
            for r, p in (
                (0.8, 0),
                (0.85, 0.0001),
                (0.9, 0.0003),
                (0.95, 0.0007),
                (0.975, 0.001),
                (1, 0.002),
            )
        )
        value = strength
        for (e0, s0), (e1, s1) in zip(vertices, vertices[1:], strict=False):
            if magnitude <= e1:
                value = ((e1 - magnitude) * s0 + (magnitude - e0) * s1) / (e1 - e0)
                break
    return -value if strain < 0 else value


def references():
    rows = []
    for fy in (250, 415, 500, 550):
        fyd = decimal(fy) / decimal("1.15")
        if fy == 250:
            positive = [
                decimal(0),
                decimal(".0005"),
                decimal(".001"),
                fyd / decimal(200000),
                decimal(".003"),
                decimal(".01"),
            ]
        else:
            knots = [
                decimal(p) + decimal(r) * fyd / decimal(200000)
                for r, p in (
                    (0.8, 0),
                    (0.85, 0.0001),
                    (0.9, 0.0003),
                    (0.95, 0.0007),
                    (0.975, 0.001),
                    (1, 0.002),
                )
            ]
            positive = [
                decimal(0),
                decimal(".0005"),
                decimal(".001"),
                decimal(".0025"),
                decimal(".003"),
                decimal(".01"),
            ] + knots
            positive += [(a + b) / 2 for a, b in zip(knots, knots[1:], strict=False)]
        for i, strain in enumerate(sorted(set(positive + [-x for x in positive]))):
            value = stress(strain, fy)
            rows.append(
                {
                    "id": f"Fe{fy}-state{i}",
                    "fy": fy,
                    "strain": float(strain),
                    "stress_nmm2": float(value),
                    "exact_strain": str(strain),
                    "exact_stress_nmm2": str(value),
                    "family": (
                        "Fig23B definite-yield"
                        if fy == 250
                        else "Fig23A representative cold-worked"
                    ),
                }
            )
    beam = []
    for fy in (250, 415, 500, 550):
        ratio = {250: decimal(".53"), 415: decimal(".48"), 500: decimal(".46")}.get(fy)
        if ratio is None:
            ratio = decimal(700) / (decimal(1100) + decimal(".87") * decimal(fy))
        xu = ratio * decimal(450)
        concrete = decimal(".36") * decimal(25) * decimal(300) * xu
        capacity = concrete * (decimal(450) - decimal(".42") * xu)
        for cover in (50, 100, 175):
            eps = decimal(".0035") * (1 - decimal(cover) / xu)
            fsc = stress(eps, fy)
            u = min(decimal(1), max(decimal(0), eps / decimal(".002")))
            fcc = decimal(".67") / decimal("1.5") * decimal(25) * (2 * u - u * u)
            excess = decimal(40000000)
            asc = excess / ((fsc - fcc) * (decimal(450) - decimal(cover)))
            ast = concrete / (decimal(".87") * decimal(fy))
            ast += asc * (fsc - fcc) / (decimal(".87") * decimal(fy))
            beam.append(
                {
                    "id": f"Fe{fy}-cover{cover}",
                    "inputs": {
                        "b": 300,
                        "d": 450,
                        "d_dash": cover,
                        "d_total": 500,
                        "mu_knm": float((capacity + excess) / decimal(1000000)),
                        "fck": 25,
                        "fy": fy,
                    },
                    "expected": {
                        "Mu_lim": float(capacity / decimal(1000000)),
                        "xu": float(xu),
                        "strain_sc": float(eps),
                        "fsc": float(fsc),
                        "fcc": float(fcc),
                        "Ast_required": float(ast),
                        "Asc_required": float(asc),
                        "Ast_max": 6000,
                        "is_safe": max(ast, asc) <= 6000,
                    },
                    "exact_Asc": str(asc),
                    "exact_Ast": str(ast),
                }
            )
    supplemental = supplemental_consumers()
    beam.append(supplemental[0])
    return {
        "source": {
            "standard": "IS456:2000 Cl38.1(e), Fig23A/B; Fig21; AnnexG1.2",
            "primary_url": "https://law.resource.org/pub/in/bis/S03/is.456.2000.pdf#page=83",
            "controlled_source_sha256": "964e270593392a0dea28b8c7c9ff1e0e730bbea912f8a903e8a86c7bb34d9264",
            "controlled_printed_pages": [69, 70, 96],
            "original_SP16_url": "https://law.resource.org/pub/in/bis/S03/is.sp.16.1980.pdf#page=29",
            "original_SP16_sha256": "d2a6246a5dc7504568f4e55f310dd4be9d925fb1a8b04b6d7f5132c93f66c76e",
            "SP16_TableA": "printed6 six rounded points; corroboration, not exact engine",
            "method": "IS456_FIG23_REP_GS115_V1",
            "arithmetic": "60-digit Decimal",
            "family_scope": "existing Fe250 definite-yield convention; other supported fy use parameterized representative Fig23A. Not a manufacturer-tested law for arbitrary steel types; no nearest-grade table extrapolation.",
            "source_limit": "Amd5 consolidation and Amd6 inspected; latest complete amendment set not certified",
            "separate_code_design_coefficients": [0.36, 0.42, 0.87],
        },
        "steel_states": rows,
        "doubly_reinforced": beam,
        "flanged_compression": supplemental[1:],
    }


def supplemental_consumers():
    """Existing G5 and three inherited flange compression branches, not new features."""
    rows = []
    cases = [
        (
            "G5",
            {
                "b": 300,
                "d": 500,
                "d_dash": 50,
                "d_total": 550,
                "mu_knm": 350,
                "fck": 25,
                "fy": 500,
            },
        ),
        (
            "web-full-flange-block",
            {
                "bw": 300,
                "bf": 1000,
                "d": 500,
                "Df": 100,
                "d_total": 550,
                "mu_knm": 1000,
                "fck": 25,
                "fy": 500,
                "d_dash": 50,
            },
        ),
        (
            "web-split-flange-block",
            {
                "bw": 230,
                "bf": 1000,
                "d": 450,
                "Df": 120,
                "d_total": 500,
                "mu_knm": 800,
                "fck": 25,
                "fy": 415,
                "d_dash": 100,
            },
        ),
        (
            "full-flange-rectangle",
            {
                "bw": 300,
                "bf": 1000,
                "d": 500,
                "Df": 300,
                "d_total": 550,
                "mu_knm": 1000,
                "fck": 25,
                "fy": 500,
                "d_dash": 50,
            },
        ),
    ]
    for name, inputs in cases:
        fy = inputs["fy"]
        dpth = decimal(inputs["d"])
        fck = decimal(inputs["fck"])
        xu = {415: decimal(".48"), 500: decimal(".46")}[fy] * dpth
        flange = decimal(0)
        flange_moment = decimal(0)
        if "bw" in inputs and decimal(inputs["Df"]) < xu:
            width = decimal(inputs["bw"])
            df = decimal(inputs["Df"])
            yf = (
                df
                if df <= decimal(".2") * dpth
                else min(df, decimal(".15") * xu + decimal(".65") * df)
            )
            flange = decimal(".45") * fck * (decimal(inputs["bf"]) - width) * yf
            flange_moment = flange * (dpth - yf / 2)
        else:
            width = decimal(inputs.get("bf", inputs.get("b")))
        force = decimal(".36") * fck * width * xu
        capacity = force * (dpth - decimal(".42") * xu) + flange_moment
        cover = decimal(inputs["d_dash"])
        eps = decimal(".0035") * (1 - cover / xu)
        fs = stress(eps, fy)
        u = min(decimal(1), eps / decimal(".002"))
        fc = decimal(".67") / decimal("1.5") * fck * (2 * u - u * u)
        excess = decimal(inputs["mu_knm"]) * decimal(1000000) - capacity
        asc = excess / ((fs - fc) * (dpth - cover))
        ast = (force + flange + excess / (dpth - cover)) / (
            decimal(".87") * decimal(fy)
        )
        maximum = (
            decimal(".04")
            * decimal(inputs.get("bw", inputs.get("b")))
            * decimal(inputs["d_total"])
        )
        rows.append(
            {
                "id": name,
                "inputs": inputs,
                "expected": {
                    "Mu_lim": float(capacity / decimal(1000000)),
                    "xu": float(xu),
                    "strain_sc": float(eps),
                    "fsc": float(fs),
                    "fcc": float(fc),
                    "Ast_required": float(ast),
                    "Asc_required": float(asc),
                    "Ast_max": float(maximum),
                    "is_safe": max(ast, asc) <= maximum,
                    "base_compression_force_n": float(force + flange),
                    "excess_moment_nmm": float(excess),
                },
                "exact_Asc": str(asc),
                "exact_Ast": str(ast),
                "source": "Independent Decimal G1.2 bar equilibrium and G2.2 limiting flange block; added after legacy expectation failures, no production imports.",
            }
        )
    return rows


if __name__ == "__main__":
    with localcontext() as context:
        context.prec = 60
        result = references()
    path = Path(__file__).with_name("material_profile_reference.json")
    path.write_text(
        json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "steel_states": len(result["steel_states"]),
                "doubly_reinforced_states": len(result["doubly_reinforced"]),
                "fixture": str(path),
            }
        )
    )

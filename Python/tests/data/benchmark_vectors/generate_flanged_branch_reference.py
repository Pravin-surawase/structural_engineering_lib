"""Independent Decimal mechanics for the existing Annex G flange-design route.

No structural_lib imports. Known neutral-axis states define demands directly;
rounded branch gaps and the separate limiting state are retained explicitly.
"""

from __future__ import annotations

import json
from decimal import Decimal, localcontext
from pathlib import Path


def number(value):
    return Decimal(str(value))


def limit_ratio(fy):
    listed = {250: "0.53", 415: "0.48", 500: "0.46"}
    return (
        number(listed[fy])
        if fy in listed
        else number(700) / (number(1100) + number("0.87") * number(fy))
    )


def resultants(section, xu, branch):
    bw, bf, d, df, fck = (number(section[k]) for k in ("bw", "bf", "d", "Df", "fck"))
    if branch == "rectangular":
        force = number("0.36") * fck * bf * xu
        moment = force * (d - number("0.42") * xu)
        return force, moment, None
    if branch == "limiting":
        yf = (
            df
            if df / d <= number("0.2")
            else min(number("0.15") * xu + number("0.65") * df, df)
        )
    else:
        yf = (
            df
            if df / xu <= number("0.43")
            else min(number("0.15") * xu + number("0.65") * df, df)
        )
    web = number("0.36") * fck * bw * xu
    flange = number("0.45") * fck * (bf - bw) * yf
    return web + flange, web * (d - number("0.42") * xu) + flange * (d - yf / 2), yf


def freeze_case(name, section, xu, branch):
    force, moment, yf = resultants(section, xu, branch)
    ratio = limit_ratio(section["fy"])
    xmax = ratio * number(section["d"])
    _, capacity, _ = resultants(
        section, xmax, "rectangular" if xmax <= number(section["Df"]) else "limiting"
    )
    return {
        "id": name,
        "inputs": section,
        "mu_knm": float(moment / number(1000000)),
        "branch": branch,
        "expected": {
            "xu": float(xu),
            "yf": None if yf is None else float(yf),
            "Ast_required": float(force / (number("0.87") * number(section["fy"]))),
            "force_n": float(force),
            "moment_nmm": float(moment),
            "Mu_lim": float(capacity / number(1000000)),
            "xu_max": float(xmax),
        },
        "exact_decimal": {
            "xu": str(xu),
            "moment_nmm": str(moment),
            "force_n": str(force),
        },
    }


def generate():
    section = {
        "bw": 230,
        "bf": 1000,
        "d": 450,
        "Df": 60,
        "d_total": 500,
        "fck": 25,
        "fy": 415,
    }
    cases = [
        freeze_case(f"anchor-xu-{x}", section, number(x), "web") for x in (80, 120)
    ]
    for fy in (250, 415, 500, 550):
        xmax = limit_ratio(fy) * number(450)
        for df in (30, 60, 90, 120):
            s = dict(section, fy=fy, Df=df)
            boundary = number(df) / number("0.43")
            candidate_depths = (
                number(df) * number("1.01"),
                (number(df) + xmax) / 2,
                xmax * number("0.999"),
                boundary * number("0.999"),
                boundary,
                boundary * number("1.001"),
            )
            _, capacity, _ = resultants(s, xmax, "limiting")
            for i, xu in enumerate(candidate_depths):
                if not number(df) < xu < xmax:
                    continue
                case = freeze_case(f"Fe{fy}-Df{df}-state{i}", s, xu, "web")
                if number(case["exact_decimal"]["moment_nmm"]) < capacity:
                    cases.append(case)
            cases.append(freeze_case(f"Fe{fy}-Df{df}-limiting", s, xmax, "limiting"))
    cases.append(
        freeze_case("no-overhang-web", dict(section, bf=230), number(80), "web")
    )
    for df in (216, 225, 280):
        s = dict(section, bw=300, bf=600, Df=df)
        cases.append(
            freeze_case(f"flange-contains-limit-Df{df}", s, number(80), "rectangular")
        )

    unsupported = []
    df = number(section["Df"])
    _, rectangular_edge, _ = resultants(section, df, "rectangular")
    _, web_edge, _ = resultants(section, df, "web")
    unsupported.append(
        {
            "id": "flange-web-rounded-gap",
            "inputs": section,
            "mu_knm": float((rectangular_edge + web_edge) / number(2000000)),
            "lower_moment_nmm": float(rectangular_edge),
            "upper_moment_nmm": float(web_edge),
            "gap_knm": float((web_edge - rectangular_edge) / number(1000000)),
        }
    )
    boundary = df / number("0.43")
    # At the threshold the full-flange equation applies; retain the other
    # polynomial's left limit separately without assigning it that endpoint.
    bw, bf, d, fck = (number(section[k]) for k in ("bw", "bf", "d", "fck"))
    yf_left = number("0.15") * boundary + number("0.65") * df
    web = number("0.36") * fck * bw * boundary * (d - number("0.42") * boundary)
    left_m = web + number("0.45") * fck * (bf - bw) * yf_left * (d - yf_left / 2)
    _, right_m, _ = resultants(section, boundary, "web")
    unsupported.append(
        {
            "id": "Df-xu-043-rounded-gap",
            "inputs": section,
            "mu_knm": float((left_m + right_m) / number(2000000)),
            "lower_moment_nmm": float(left_m),
            "upper_moment_nmm": float(right_m),
            "gap_knm": float((right_m - left_m) / number(1000000)),
        }
    )
    s = dict(section, Df=90, fy=500)
    xmax = limit_ratio(500) * number(450)
    _, ordinary_cap, _ = resultants(s, xmax, "web")
    _, limiting_cap, _ = resultants(s, xmax, "limiting")
    unsupported.append(
        {
            "id": "ordinary-limiting-rounded-gap",
            "inputs": s,
            "mu_knm": float((ordinary_cap + limiting_cap) / number(2000000)),
            "lower_moment_nmm": float(ordinary_cap),
            "upper_moment_nmm": float(limiting_cap),
            "gap_knm": float((limiting_cap - ordinary_cap) / number(1000000)),
        }
    )
    return {
        "source": {
            "standard": "IS 456:2000 Annex G-2.1/2.2/2.2.1/2.3, Cl38.1",
            "primary_url": "https://law.resource.org/pub/in/bis/S03/is.456.2000.pdf#page=109",
            "controlled_source": "private_sources/is456_library_first/source_pdfs/is456_2000_amd5_reff2021.pdf",
            "controlled_source_sha256": "964e270593392a0dea28b8c7c9ff1e0e730bbea912f8a903e8a86c7bb34d9264",
            "controlled_printed_pages": [96, 97],
            "source_limit": "Amd5 consolidation checked; latest complete amendment qualification remains separate",
            "method": "IS456_ANNEX_G_PIECEWISE_BRANCH_ROOT_V1",
            "profile": "code-design rounded Annex G coefficients, not integrated Fig21 analysis",
            "mechanics": "known xu with independently evaluated forces and lever arms; 60-digit Decimal arithmetic; no production imports",
            "units": "mm, N/mm2, N, Nmm; supplied/report moment kNm and steel mm2",
            "ordinary_criterion": "Df/xu <= .43",
            "limiting_criterion": "Df/d <= .2",
            "boundary_policy": "rounded equation gaps remain unsupported; no interpolation or endpoint fallback",
        },
        "cases": cases,
        "unsupported": unsupported,
    }


if __name__ == "__main__":
    with localcontext() as context:
        context.prec = 60
        data = generate()
    output = Path(__file__).with_name("flanged_branch_reference.json")
    output.write_text(
        json.dumps(data, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "path": str(output),
                "supported_states": len(data["cases"]),
                "unsupported_gaps": len(data["unsupported"]),
            }
        )
    )

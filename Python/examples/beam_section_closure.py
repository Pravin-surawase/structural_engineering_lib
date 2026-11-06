"""Run supplied shear and sagging flange calculations with an installed package."""

from __future__ import annotations

import json
from math import pi

from structural_lib import beam


def sagging_section(
    flange_thickness_mm: float,
    *,
    web_width_mm: float = 300,
    flange_width_mm: float = 800,
    depth_mm: float = 475,
    fck_nmm2: float = 25,
    fy_nmm2: float = 415,
    tension_layers: tuple[tuple[float, tuple[int, ...]], ...] = (
        (405, (18, 18)),
        (440, (20, 20, 20)),
    ),
) -> beam.OperationResult:
    bars = tuple(
        beam.BarPosition(
            bar_id=f"L{layer}-{i}",
            diameter_mm=diameter,
            x_from_left_mm=web_width_mm * i / (len(diameters) + 1),
            y_from_top_mm=depth,
            face=beam.Face.BOTTOM,
            layer=layer,
        )
        for layer, (depth, diameters) in enumerate(tension_layers, 1)
        for i, diameter in enumerate(diameters, 1)
    )
    return beam.flexural_capacity(
        beam.FlexuralCapacityRequest(
            profile_id="sagging-flanged-section",
            section_kind=beam.SectionKind.T_BEAM,
            web_width_mm=web_width_mm,
            depth_mm=depth_mm,
            concrete_strength_n_per_mm2=fck_nmm2,
            steel_yield_strength_n_per_mm2=fy_nmm2,
            bars=bars,
            tension_face=beam.Face.BOTTOM,
            flange_width_mm=flange_width_mm,
            flange_thickness_mm=flange_thickness_mm,
        )
    )


def main() -> None:
    vertical = beam.SectionShearReinforcement(
        "vertical", 2 * pi * 8**2 / 4, 415, 90, 150
    )
    inclined = beam.SectionShearReinforcement(
        "inclined", 2 * pi * 8**2 / 4, 415, 45, 150
    )
    single = beam.SectionShearReinforcement("single", 2 * pi * 16**2 / 4, 415, 45, None)
    repeated = beam.SectionShearReinforcement(
        "repeated", 2 * pi * 16**2 / 4, 415, 45, 150
    )
    shear = {}
    for case_id, stirrups, bent_up in (
        ("inclined", inclined, None),
        ("vertical_and_single", vertical, single),
        ("inclined_and_over_limit_repeated", inclined, repeated),
    ):
        result = beam.supplied_section_shear_capacity(
            beam.SuppliedSectionShearRequest(
                profile_id=case_id,
                web_width_mm=300,
                effective_depth_mm=450,
                fck_nmm2=25,
                longitudinal_tension_area_mm2=1350,
                stirrups=stirrups,
                bent_up_bars=bent_up,
            )
        )
        shear[case_id] = result.to_dict()

    flexure = {
        case_id: sagging_section(thickness).to_dict()
        for case_id, thickness in (
            ("within_flange", 150),
            ("web_reduced_flange", 50),
            ("web_full_flange", 30),
        )
    }
    print(json.dumps({"shear": shear, "flexure": flexure}, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()

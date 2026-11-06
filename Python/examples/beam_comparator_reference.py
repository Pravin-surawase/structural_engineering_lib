"""Compare three supplied beam sections using an installed StructLib package.

Run with python beam_comparator_reference.py. The JSON contains section
capacities and their method identifiers. Coordinates are in millimetres
from the left and top faces. All three examples put the tension face at
the bottom and use vertical links on the V2 axis.
"""

from __future__ import annotations

import json

from structural_lib import beam


def section_capacities(
    case_id: str,
    width_mm: float,
    depth_mm: float,
    fck_nmm2: float,
    layers: tuple[tuple[beam.Face, float, tuple[int, ...]], ...],
    *,
    flange_width_mm: float | None = None,
    flange_thickness_mm: float | None = None,
) -> dict:
    # Symmetric x coordinates preserve each layer's bar diameters and depth.
    # The quickstart specifies depths only. Treat the x coordinates as
    # illustrative section inputs.
    bars = tuple(
        beam.BarPosition(
            bar_id=f"L{layer_number}-{bar_number}",
            diameter_mm=diameter,
            x_from_left_mm=width_mm * bar_number / (len(diameters) + 1),
            y_from_top_mm=y_mm,
            face=face,
            layer=layer_number,
        )
        for layer_number, (face, y_mm, diameters) in enumerate(layers, start=1)
        for bar_number, diameter in enumerate(diameters, start=1)
    )
    flexure = beam.flexural_capacity(
        beam.FlexuralCapacityRequest(
            profile_id=case_id,
            section_kind=(
                beam.SectionKind.RECTANGULAR
                if flange_width_mm is None
                else beam.SectionKind.T_BEAM
            ),
            web_width_mm=width_mm,
            depth_mm=depth_mm,
            concrete_strength_n_per_mm2=fck_nmm2,
            steel_yield_strength_n_per_mm2=415,
            bars=bars,
            tension_face=beam.Face.BOTTOM,
            flange_width_mm=flange_width_mm,
            flange_thickness_mm=flange_thickness_mm,
        )
    )
    if flexure.execution != "completed":
        raise RuntimeError(f"{case_id} flexure: {flexure.diagnostics}")

    # The link envelope uses the nominal 25 mm cover from the comparator.
    # Preserve the longitudinal bar depths supplied for the calculation.
    cover_to_link_centre_mm = 25 + 8 / 2
    link = beam.TransverseLink(
        link_id="2-leg-8-at-150",
        diameter_mm=8,
        legs_v2=2,
        legs_v3=2,
        spacing_mm=150,
        steel_yield_strength_n_per_mm2=415,
        closed=True,
        centre_width_mm=width_mm - 2 * cover_to_link_centre_mm,
        centre_depth_mm=depth_mm - 2 * cover_to_link_centre_mm,
    )
    flexural_outputs = flexure.outputs
    shear = beam.shear_capacity(
        beam.ShearCapacityRequest(
            profile_id=case_id,
            axis=beam.ShearAxis.V2,
            resisting_width_mm=width_mm,  # The web also resists shear in the T section.
            effective_depth_mm=flexural_outputs["effective_depth_mm"],
            concrete_strength_n_per_mm2=fck_nmm2,
            longitudinal_tension_area_mm2=flexural_outputs["tension_steel_area_mm2"],
            link=link,
        )
    )
    if shear.execution != "completed":
        raise RuntimeError(f"{case_id} shear: {shear.diagnostics}")

    return {
        "xu_mm": flexural_outputs["equilibrium_neutral_axis_depth_mm"],
        "d_mm": flexural_outputs["effective_depth_mm"],
        "pt_percent": shear.outputs["longitudinal_percentage_actual"],
        "mu_knm": flexural_outputs["capacity_knm"],
        "vuc_kn": shear.outputs["concrete_capacity_kn"],
        "vus_kn": shear.outputs["link_capacity_kn"],
        "shear_total_kn": shear.outputs["provided_capacity_kn"],
        "method_revision_ids": {
            "flexure": flexure.provenance.method_revision_id,
            "shear": shear.provenance.method_revision_id,
        },
    }


def main() -> None:
    bottom, top = beam.Face.BOTTOM, beam.Face.TOP
    results = {
        "singly_reinforced_rectangular": section_capacities(
            "singly_reinforced_rectangular",
            230,
            450,
            20,
            ((bottom, 415, (20, 16, 20)),),
        ),
        "doubly_reinforced_rectangular": section_capacities(
            "doubly_reinforced_rectangular",
            230,
            450,
            20,
            ((top, 35, (16, 16)), (bottom, 415, (16, 16, 16))),
        ),
        "flanged_two_tension_layers": section_capacities(
            "flanged_two_tension_layers",
            300,
            475,
            25,
            ((bottom, 405, (18, 18)), (bottom, 440, (20, 20, 20))),
            flange_width_mm=800,
            flange_thickness_mm=150,
        ),
    }
    print(json.dumps(results, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()

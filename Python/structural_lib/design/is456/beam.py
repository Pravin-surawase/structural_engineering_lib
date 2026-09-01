"""Small public facade for the canonical rectangular-beam workflow."""

from __future__ import annotations

from typing import Any, Literal

from structural_lib.core.errors import InputContractError, InputIssueV1
from structural_lib.services.canonical_beam import (
    BeamBBSResultV1,
    BeamDesignAndDetailResultV1,
    BeamDesignResultV1,
    BeamDetailingResultV1,
    check,
    design,
    design_and_detail,
    detail,
    generate_bbs,
)
from structural_lib.services.contracts.beam import (
    BEAM_FIELD_CONTRACTS,
    BeamActionsV1,
    BeamCalculationBasisV1,
    BeamDesignInputV1,
    BeamDetailingOptionsV1,
    BeamServiceabilityV1,
    CentroidCoverDepthRequestV1,
    DetailingStandard,
    EffectiveDepthBasisRequestV1,
    IS456MaterialsV1,
    IS456ReinforcementMaterialsV1,
    MemberIdentityV1,
    RectangularBeamSectionV1,
)
from structural_lib.services.contracts.beam_serviceability import (
    BeamAnnexFCrackCheckV1,
    BeamServiceabilityBasisV1,
    BeamServiceabilityChecksV1,
    BeamSpanDepthCheckV1,
)
from structural_lib.services.contracts.common import model_validate_or_error

__all__ = [
    "BeamActionsV1",
    "BEAM_FIELD_CONTRACTS",
    "BeamBBSResultV1",
    "BeamCalculationBasisV1",
    "BeamDesignAndDetailResultV1",
    "BeamDesignInputV1",
    "BeamDesignResultV1",
    "BeamDetailingOptionsV1",
    "BeamDetailingResultV1",
    "BeamServiceabilityV1",
    "BeamServiceabilityChecksV1",
    "BeamServiceabilityBasisV1",
    "BeamSpanDepthCheckV1",
    "BeamAnnexFCrackCheckV1",
    "DetailingStandard",
    "EffectiveDepthBasisRequestV1",
    "CentroidCoverDepthRequestV1",
    "IS456MaterialsV1",
    "IS456ReinforcementMaterialsV1",
    "InputContractError",
    "InputIssueV1",
    "MemberIdentityV1",
    "RectangularBeamSectionV1",
    "bbs",
    "check",
    "design",
    "design_and_detail",
    "detail",
    "input",
    "load",
]


def input(  # noqa: A001 - frozen public facade spelling
    *,
    member_id: str,
    story: str,
    case_id: str,
    span_mm: float,
    b_mm: float,
    D_mm: float,
    fck_nmm2: float,
    fy_nmm2: float,
    fy_transverse_nmm2: float | None = None,
    mu_knm: float,
    vu_kn: float,
    d_dash_mm: float,
    asv_mm2: float,
    d_mm: float | None = None,
    effective_depth_basis: (
        EffectiveDepthBasisRequestV1 | CentroidCoverDepthRequestV1 | None
    ) = None,
    tu_knm: float = 0.0,
    primary_tension_face: Literal["TOP", "BOTTOM"] | None = None,
    pt_percent: float | None = None,
    ast_mm2_for_shear: float | None = None,
    detailing: BeamDetailingOptionsV1 | None = None,
    serviceability: BeamServiceabilityV1 | BeamServiceabilityChecksV1 | None = None,
    source_provenance: str | None = None,
) -> BeamDesignInputV1:
    """Build the strict nested request without exposing Pydantic exceptions."""

    return model_validate_or_error(
        BeamDesignInputV1,
        {
            "identity": {
                "member_id": member_id,
                "story": story,
                "case_id": case_id,
            },
            "section": {
                "span_mm": span_mm,
                "b_mm": b_mm,
                "D_mm": D_mm,
                "d_mm": d_mm,
                "effective_depth_basis": effective_depth_basis,
            },
            "materials": {
                "fck_nmm2": fck_nmm2,
                "fy_nmm2": fy_nmm2,
                **(
                    {"fy_transverse_nmm2": fy_transverse_nmm2}
                    if fy_transverse_nmm2 is not None
                    else {}
                ),
            },
            "actions": {
                "mu_knm": mu_knm,
                "vu_kn": vu_kn,
                "tu_knm": tu_knm,
                **(
                    {"primary_tension_face": primary_tension_face}
                    if primary_tension_face is not None
                    else {}
                ),
            },
            "calculation_basis": {
                "d_dash_mm": d_dash_mm,
                "asv_mm2": asv_mm2,
                "pt_percent": pt_percent,
                "ast_mm2_for_shear": ast_mm2_for_shear,
            },
            "detailing": detailing,
            "serviceability": serviceability,
            "source_provenance": source_provenance,
        },
    )


def load(value: Any) -> BeamDesignInputV1:
    """Validate nested Python/JSON data into the canonical request."""

    return model_validate_or_error(BeamDesignInputV1, value)


def bbs(
    result: (
        BeamDesignAndDetailResultV1
        | BeamDetailingResultV1
        | list[BeamDetailingResultV1]
    ),
) -> BeamBBSResultV1:
    """Generate a canonical BBS from exact accepted result types."""

    return generate_bbs(result)

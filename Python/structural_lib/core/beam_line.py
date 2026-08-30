# SPDX-License-Identifier: MIT
"""Immutable W3G beam-line contracts; no solver, vendor API or code-design math.

Signs: x right; translation/load up; rotation/nodal couple counterclockwise.
Member diagrams use sagging-positive moment and shear dM/dx. Offsets are
unloaded rigid horizontal arms; all member loads act on flexible length only.
"""

from __future__ import annotations

from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from structural_lib.core.analysis_contracts import EvidenceValueV1

__all__ = [
    "BeamLineNodeV1",
    "BeamLineSpanV1",
    "BeamLineSupportV1",
    "BeamLineSupportSpringV1",
    "BeamLineUniformLoadV1",
    "BeamLinePointLoadV1",
    "BeamLineNodalLoadV1",
    "BeamLineLoadCaseV1",
    "BeamLineFactorV1",
    "BeamLineCombinationV1",
    "BeamLineScenarioV1",
    "BeamLineNumericsV1",
    "BeamLineAnalysisRequestV1",
    "BeamLineNodeResultV1",
    "BeamLineStationV1",
    "BeamLineSpanResultV1",
    "BeamLineEquilibriumV1",
    "BeamLineAnalysisResultV1",
    "BeamLineIssueV1",
    "BeamLineAnalysisBuildResultV1",
]

_Id = Annotated[str, Field(min_length=1, max_length=160)]
_Hash = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]


class _BeamLineModel(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        allow_inf_nan=False,
        validate_default=True,
        str_strip_whitespace=True,
    )


class BeamLineNodeV1(_BeamLineModel):
    node_id: _Id
    x_m: float


class BeamLineSpanV1(_BeamLineModel):
    span_id: _Id
    start_node_id: _Id
    end_node_id: _Id
    elastic_modulus_nmm2: float = Field(gt=0)
    second_moment_mm4: float = Field(gt=0)
    stiffness_modifier: float = Field(gt=0)
    area_mm2: float = Field(gt=0)
    density_kg_m3: float = Field(ge=0)
    release_start_rotation: bool
    release_end_rotation: bool
    rigid_offset_start_m: float = Field(ge=0)
    rigid_offset_end_m: float = Field(ge=0)
    load_domain: Literal["FLEXIBLE_LENGTH_ONLY"]


class BeamLineSupportSpringV1(_BeamLineModel):
    rotational_stiffness_knm_per_rad: float = Field(ge=0)


class BeamLineSupportV1(_BeamLineModel):
    node_id: _Id
    vertical: Literal["FIXED", "FREE"]
    rotation: Literal["FIXED", "FREE", "SPRING"]
    spring: EvidenceValueV1[BeamLineSupportSpringV1]


class BeamLineUniformLoadV1(_BeamLineModel):
    span_id: _Id
    vertical_kn_per_m: float


class BeamLinePointLoadV1(_BeamLineModel):
    span_id: _Id
    distance_from_flexible_start_m: float = Field(ge=0)
    vertical_kn: float


class BeamLineNodalLoadV1(_BeamLineModel):
    node_id: _Id
    vertical_kn: float
    moment_knm: float


class BeamLineLoadCaseV1(_BeamLineModel):
    case_id: _Id
    uniform_loads: tuple[BeamLineUniformLoadV1, ...] = Field(max_length=128)
    point_loads: tuple[BeamLinePointLoadV1, ...] = Field(max_length=128)
    nodal_loads: tuple[BeamLineNodalLoadV1, ...] = Field(max_length=128)
    self_weight_factor: float


class BeamLineFactorV1(_BeamLineModel):
    source_kind: Literal["CASE", "COMBINATION"]
    source_id: _Id
    factor: float


class BeamLineCombinationV1(_BeamLineModel):
    combination_id: _Id
    factors: tuple[BeamLineFactorV1, ...] = Field(min_length=1, max_length=128)


class BeamLineScenarioV1(_BeamLineModel):
    scenario_id: _Id
    purpose: Literal["STRENGTH", "SERVICE", "COMPARISON"]
    result_kind: Literal["CASE", "COMBINATION"]
    result_id: _Id
    assumptions: tuple[_Id, ...] = Field(min_length=1, max_length=64)


class BeamLineNumericsV1(_BeamLineModel):
    """Numerical acceptance, not engineering/calibration tolerances."""

    equilibrium_relative: float = Field(default=1e-8, gt=0, le=1e-8)
    absolute_force_kn: float = Field(default=1e-9, gt=0, le=1e-6)
    absolute_moment_knm: float = Field(default=1e-9, gt=0, le=1e-6)
    scaled_pivot_floor: float = Field(default=1e-12, gt=0, le=1e-8)


class BeamLineAnalysisRequestV1(_BeamLineModel):
    schema_version: Literal["beam-line-analysis-request/v1"] = (
        "beam-line-analysis-request/v1"
    )
    model_definition_sha256: _Hash
    catalogue_sha256: _Hash
    scenario_definition_sha256: _Hash
    source_basis: Literal["SYNTHETIC_REFERENCE", "CALLER_SUPPLIED_UNCALIBRATED"]
    nodes: tuple[BeamLineNodeV1, ...] = Field(min_length=2, max_length=6)
    spans: tuple[BeamLineSpanV1, ...] = Field(min_length=1, max_length=5)
    supports: tuple[BeamLineSupportV1, ...] = Field(min_length=2, max_length=6)
    load_cases: tuple[BeamLineLoadCaseV1, ...] = Field(min_length=1, max_length=64)
    combinations: tuple[BeamLineCombinationV1, ...] = Field(max_length=64)
    scenario: BeamLineScenarioV1
    gravity_m_per_s2: float = Field(gt=0)
    station_intervals_per_span: int = Field(ge=2, le=200)
    max_station_rows: int = Field(default=2000, ge=1, le=2000)
    numerics: BeamLineNumericsV1
    unit_basis: Literal["M_KN_KNM_RAD_E_NMM2_I_MM4"]


class BeamLineNodeResultV1(_BeamLineModel):
    node_id: _Id
    vertical_displacement_m: float
    rotation_rad: EvidenceValueV1[float]
    vertical_reaction_kn: float
    reaction_moment_knm: float


class BeamLineStationV1(_BeamLineModel):
    span_id: _Id
    distance_from_flexible_start_m: float
    x_m: float
    side: Literal["LEFT", "RIGHT", "CONTINUOUS"]
    vertical_displacement_m: float
    rotation_rad: float
    shear_kn: float
    moment_knm: float


class BeamLineSpanResultV1(_BeamLineModel):
    span_id: _Id
    flexible_length_m: float = Field(gt=0)
    effective_ei_knm2: float = Field(gt=0)
    # Node-on-element actions in [vertical_i, couple_i, vertical_j, couple_j].
    end_actions_kn_knm: tuple[float, float, float, float]
    end_displacements_m_rad: tuple[float, float, float, float]
    uniform_vertical_kn_per_m: float
    point_loads: tuple[BeamLinePointLoadV1, ...]
    stations: tuple[BeamLineStationV1, ...] = Field(min_length=3, max_length=2000)


class BeamLineEquilibriumV1(_BeamLineModel):
    force_residual_kn: float
    moment_residual_knm: float
    max_free_force_residual_kn: float
    max_free_moment_residual_knm: float
    applied_force_norm_kn: float = Field(ge=0)
    applied_moment_norm_knm: float = Field(ge=0)
    force_tolerance_kn: float = Field(gt=0)
    moment_tolerance_knm: float = Field(gt=0)


class BeamLineAnalysisResultV1(_BeamLineModel):
    schema_version: Literal["beam-line-analysis/v1"] = "beam-line-analysis/v1"
    solver_identity: Literal["EULER_BERNOULLI_DIRECT_STIFFNESS_V1"] = (
        "EULER_BERNOULLI_DIRECT_STIFFNESS_V1"
    )
    capability: Literal["SURROGATE_ONLY"] = "SURROGATE_ONLY"
    independent_frame_analysis: Literal["HELD_NOT_SUPPORTED"] = "HELD_NOT_SUPPORTED"
    torsion: Literal["HELD_NOT_DERIVED"] = "HELD_NOT_DERIVED"
    calibration: Literal["NOT_CALIBRATED_W3H_REQUIRED"] = "NOT_CALIBRATED_W3H_REQUIRED"
    request: BeamLineAnalysisRequestV1
    request_sha256: _Hash
    result_sha256: _Hash
    nodes: tuple[BeamLineNodeResultV1, ...]
    spans: tuple[BeamLineSpanResultV1, ...]
    equilibrium: BeamLineEquilibriumV1
    station_row_count: int = Field(ge=3, le=2000)


class BeamLineIssueV1(_BeamLineModel):
    reason_code: _Id
    message: str = Field(min_length=1)


class BeamLineAnalysisBuildResultV1(_BeamLineModel):
    status: Literal["ACCEPTED", "BLOCKED"]
    result: BeamLineAnalysisResultV1 | None = None
    issues: tuple[BeamLineIssueV1, ...] = ()

    @model_validator(mode="after")
    def _complete_or_blocked(self) -> Self:
        if self.status == "ACCEPTED" and (self.result is None or self.issues):
            raise ValueError(
                "accepted build requires one complete result and no issues"
            )
        if self.status == "BLOCKED" and (self.result is not None or not self.issues):
            raise ValueError("blocked build requires issues and no partial result")
        return self

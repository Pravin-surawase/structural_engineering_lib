"""Input contract for the regular, centred four-beam interior joint."""

from __future__ import annotations

from typing import Annotated, Literal, Self

from pydantic import Field, field_validator, model_validator

from structural_lib.services.contracts.common import StrictPublicModel

JointDirection = Literal["X+", "X-", "Y+", "Y-"]
JOINT_DIRECTIONS: tuple[JointDirection, ...] = ("X+", "X-", "Y+", "Y-")
_Plane = Literal["X", "Y"]
_BeamSide = Literal["minus", "plus"]
_ColumnEnd = Literal["upper", "lower"]
_Id = Annotated[str, Field(min_length=1, max_length=120, pattern=r"\S")]
_Reference = Annotated[str, Field(min_length=1, max_length=500, pattern=r"\S")]
_Dimension = Annotated[float, Field(gt=0, le=20000)]
_SmallDimension = Annotated[float, Field(gt=0, le=500)]
_Station = Annotated[float, Field(ge=0, le=3000)]
_Tolerance = Annotated[float, Field(ge=0, le=20)]
_Load = Annotated[float, Field(ge=-10000, le=10000)]
_PositiveLoad = Annotated[float, Field(gt=0, le=10000)]


class JointActionRowV1(StrictPublicModel):
    """Concurrent elastic actions with compression and downward reaction positive."""

    combination_id: _Id
    upper_axial_compression_kn: _PositiveLoad
    beam_on_joint_downward_shear_kn: dict[_BeamSide, _Load]
    analysis_column_shear_magnitude_kn: Annotated[float, Field(ge=0, le=10000)]

    @model_validator(mode="after")
    def check_vertical_balance_inputs(self) -> Self:
        vertical = self.beam_on_joint_downward_shear_kn
        if set(vertical) != {"minus", "plus"}:
            raise ValueError("Supply both opposed beam reactions in every action row.")
        return self


_DirectionRows = Annotated[tuple[JointActionRowV1, ...], Field(max_length=32)]


class DuctileJointRequestV1(StrictPublicModel):
    """IS 13920 regular non-roof joint with opposed symmetric rectangular beams.

    All dimensions are mm, strengths MPa, and actions kN or kN/m unless named
    otherwise. Each direction supplies the complete factored combination set
    used for this specimen. The open-frame section contains no slab bars.
    """

    schema_version: Literal["ductile-interior-joint/v1"] = "ductile-interior-joint/v1"
    joint_id: _Id
    continuity: _Reference
    applicability_reference: _Reference | None = None
    action_revision: _Id | None = None
    cage_action_revision: _Id | None = None
    beam_width_mm: _Dimension
    column_width_mm: _Dimension
    joint_depth_mm: _Dimension
    column_clear_heights_mm: dict[_ColumnEnd, _Dimension]
    beam_clear_spans_mm: dict[_Plane, dict[_BeamSide, _Dimension]]
    beam_dead_plus_live_kn_m: dict[
        _Plane, dict[_BeamSide, Annotated[float, Field(ge=0, le=2000)]]
    ]
    mechanism_inflection_offsets_mm: dict[_ColumnEnd, _Dimension] | None = None
    column_fck_mpa: Literal[30]
    beam_fck_mpa: Literal[30]
    joint_fck_mpa: Literal[20, 25, 30, 35, 40, 45, 50]
    longitudinal_fy_mpa: Literal[500]
    link_fy_mpa: Literal[415]
    longitudinal_grade: Literal["Fe500D"]
    transverse_grade: Literal["Fe415D"]
    column_bar_mm: Literal[20, 25, 32]
    column_bar_edge_mm: _SmallDimension
    beam_bar_mm: Literal[20, 25, 32]
    beam_axis_across_column_mm: tuple[_Dimension, _Dimension, _Dimension, _Dimension]
    beam_row_depth_from_top_mm: dict[_Plane, _SmallDimension]
    beam_uninterrupted_development_mm: Annotated[float, Field(ge=0, le=20000)]
    beam_link_mm: Literal[8, 10, 12]
    beam_link_centre_radius_mm: _SmallDimension
    beam_link_seat_inset_mm: _SmallDimension
    beam_first_link_mm: _SmallDimension
    beam_inner_link_offset_mm: _SmallDimension
    beam_pitch_mm: _SmallDimension
    column_cover_mm: _SmallDimension
    column_link_mm: Literal[8, 10, 12, 16]
    column_link_centre_radius_mm: _SmallDimension
    column_hook_tail_mm: _SmallDimension
    column_hook_rise_mm: _SmallDimension
    column_hook_ramp_length_mm: _SmallDimension
    cross_tie_station_offset_mm: _SmallDimension
    joint_hoop_centres_mm: Annotated[
        tuple[_Station, ...], Field(min_length=2, max_length=40)
    ]
    column_first_end_hoop_mm: _SmallDimension
    column_end_pitch_mm: Annotated[float, Field(ge=20, le=500)]
    column_end_confinement_length_mm: _Dimension
    required_beam_cover_mm: Annotated[float, Field(ge=20, le=200)]
    required_column_cover_mm: Annotated[float, Field(ge=40, le=200)]
    aggregate_max_mm: _SmallDimension
    axis_tolerance_mm: _Tolerance
    tie_station_tolerance_mm: _Tolerance
    diameter_overage_mm: _Tolerance
    compaction_head_mm: _SmallDimension | None = None
    assembly: _Reference | None = None
    directions: dict[JointDirection, _DirectionRows] = Field(default_factory=dict)

    @field_validator(
        "beam_axis_across_column_mm", "joint_hoop_centres_mm", mode="before"
    )
    @classmethod
    def json_sequences(cls, value: object) -> object:
        return tuple(value) if isinstance(value, list) else value

    @field_validator("directions", mode="before")
    @classmethod
    def json_action_rows(cls, value: object) -> object:
        if isinstance(value, dict):
            return {
                key: tuple(rows) if isinstance(rows, list) else rows
                for key, rows in value.items()
            }
        return value

    @model_validator(mode="after")
    def admit_regular_geometry(self) -> Self:
        if set(self.column_clear_heights_mm) != {"upper", "lower"} or (
            self.mechanism_inflection_offsets_mm is not None
            and set(self.mechanism_inflection_offsets_mm) != {"upper", "lower"}
        ):
            raise ValueError(
                "Supply both column end heights and any inflection offsets."
            )
        for beam_map in (self.beam_clear_spans_mm, self.beam_dead_plus_live_kn_m):
            if set(beam_map) != {"X", "Y"} or any(
                set(spans) != {"minus", "plus"} for spans in beam_map.values()
            ):
                raise ValueError(
                    "Supply both opposed beam faces in each principal plane."
                )
        across = self.beam_axis_across_column_mm
        levels = self.beam_row_depth_from_top_mm
        if (
            self.beam_width_mm > self.column_width_mm
            or not 5 < self.column_bar_edge_mm < self.column_width_mm / 2 - 5
            or set(levels) != {"X", "Y"}
            or any(level >= self.joint_depth_mm / 2 for level in levels.values())
            or across != tuple(sorted(set(across)))
            or across[-1] >= self.column_width_mm
            or abs(across[0] + across[-1] - self.column_width_mm) > 1e-6
            or abs(across[1] + across[-2] - self.column_width_mm) > 1e-6
        ):
            raise ValueError(
                "Supply the centred, symmetric four-bar beam and eight-bar column geometry."
            )
        stations = self.joint_hoop_centres_mm
        if (
            stations != tuple(sorted(set(stations)))
            or stations[-1] > self.joint_depth_mm
        ):
            raise ValueError(
                "Supply distinct increasing hoop stations within the joint."
            )
        combos = [
            row.combination_id for rows in self.directions.values() for row in rows
        ]
        if len(combos) != len(set(combos)):
            raise ValueError(
                "Joint action combinations must have distinct identifiers."
            )
        return self

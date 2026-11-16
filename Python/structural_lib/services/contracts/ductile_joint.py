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


class ExteriorJointActionRowV1(StrictPublicModel):
    """One concurrent signed row for an exterior-joint principal plane."""

    combination_id: _Id
    upper_axial_compression_kn: _PositiveLoad
    beam_on_joint_downward_shear_kn: dict[_BeamSide, _Load]
    analysis_column_shear_magnitude_kn: Annotated[float, Field(ge=0, le=10000)]
    beam_axial_kn: Literal[0]
    sway: Literal["+", "-"]


class JointHookV1(StrictPublicModel):
    """90-degree hook with a vertical tail measured after the bend tangent."""

    tip_x_mm: _Dimension
    tail_mm: _Dimension


class DuctileExteriorJointRequestV1(StrictPublicModel):
    """Regular exterior open-frame joint with one terminating X-minus beam."""

    schema_version: Literal["ductile-exterior-joint/v1"] = "ductile-exterior-joint/v1"
    topology: Literal["exterior_x_minus"]
    joint_id: _Id
    applicability_reference: _Reference | None = None
    action_revision: _Id | None = None
    cage_action_revision: _Id | None = None
    column_width_mm: _Dimension
    joint_depth_mm: Annotated[float, Field(gt=0, le=750)]
    beam_width_mm: dict[_Plane, _Dimension]
    column_bar_mm: Literal[25, 32]
    column_bar_edge_mm: _SmallDimension
    beam_bar_mm: dict[_Plane, Literal[20, 25, 32]]
    beam_axes_mm: dict[_Plane, tuple[_Dimension, _Dimension, _Dimension, _Dimension]]
    beam_top_z_mm: dict[_Plane, _SmallDimension]
    x_hooks: dict[Literal["TOP", "BOTTOM"], JointHookV1] | None = None
    x_hook_radius_mm: _SmallDimension
    y_straight_each_side_mm: _Dimension
    column_cover_mm: _SmallDimension
    column_link_mm: Literal[16]
    column_link_radius_mm: _SmallDimension
    column_link_overlap_half_mm: _SmallDimension
    column_cross_tie_axis_y_mm: _Dimension
    column_link_tail_mm: _SmallDimension
    column_link_ramp_run_mm: _SmallDimension
    link_group_offset_mm: _SmallDimension
    joint_hoop_centres_mm: Annotated[
        tuple[_Station, ...], Field(min_length=2, max_length=40)
    ]
    column_end_link_first_mm: _SmallDimension
    column_end_pitch_mm: Annotated[float, Field(ge=20, le=500)]
    column_end_confinement_length_mm: _Dimension
    column_clear_heights_mm: dict[_ColumnEnd, _Dimension]
    mechanism_inflection_offsets_mm: dict[_ColumnEnd, _Dimension] | None = None
    beam_clear_spans_mm: dict[_Plane, dict[_BeamSide, _Dimension]]
    beam_dead_plus_live_kn_m: dict[
        _Plane, dict[_BeamSide, Annotated[float, Field(ge=0, le=2000)]]
    ]
    beam_link_mm: Literal[10, 12]
    beam_pitch_mm: _SmallDimension
    beam_first_link_mm: _SmallDimension
    beam_inner_link_offset_mm: _SmallDimension
    beam_link_centre_radius_mm: dict[_Plane, _SmallDimension]
    beam_link_seat_inset_mm: dict[_Plane, _SmallDimension]
    beam_link_hook_tail_mm: _SmallDimension
    column_fck_mpa: Literal[30]
    beam_fck_mpa: Literal[30]
    joint_fck_mpa: Literal[20, 25, 30, 35, 40, 45, 50]
    longitudinal_fy_mpa: Literal[500]
    link_fy_mpa: Literal[415]
    longitudinal_grade: Literal["Fe500D"]
    transverse_grade: Literal["Fe415D"]
    required_beam_cover_mm: Annotated[float, Field(ge=20, le=200)]
    required_column_cover_mm: Annotated[float, Field(ge=40, le=200)]
    aggregate_max_mm: _SmallDimension
    axis_tolerance_mm: _Tolerance
    diameter_overage_mm: _Tolerance
    tie_station_tolerance_mm: _Tolerance
    anchor_cut_length_tolerance_mm: _Tolerance
    compaction_head_mm: _SmallDimension | None = None
    assembly: _Reference | None = None
    directions: dict[
        JointDirection,
        Annotated[tuple[ExteriorJointActionRowV1, ...], Field(max_length=32)],
    ] = Field(default_factory=dict)

    @field_validator("beam_axes_mm", "directions", mode="before")
    @classmethod
    def json_sequences_by_name(cls, value: object) -> object:
        if isinstance(value, dict):
            return {
                name: tuple(rows) if isinstance(rows, list) else rows
                for name, rows in value.items()
            }
        return value

    @field_validator("joint_hoop_centres_mm", mode="before")
    @classmethod
    def json_stations(cls, value: object) -> object:
        return tuple(value) if isinstance(value, list) else value

    @model_validator(mode="after")
    def admit_exterior_geometry_and_actions(self) -> Self:
        width = self.column_width_mm
        if set(self.column_clear_heights_mm) != {"upper", "lower"} or (
            self.mechanism_inflection_offsets_mm is not None
            and set(self.mechanism_inflection_offsets_mm) != {"upper", "lower"}
        ):
            raise ValueError(
                "Supply both column end heights and any inflection offsets."
            )
        expected_sides = {"X": {"minus"}, "Y": {"minus", "plus"}}
        for beam_map in (self.beam_clear_spans_mm, self.beam_dead_plus_live_kn_m):
            if {
                plane: set(sides) for plane, sides in beam_map.items()
            } != expected_sides:
                raise ValueError("Supply the X-minus beam and both Y beams.")
        plane_inputs = (
            self.beam_width_mm,
            self.beam_bar_mm,
            self.beam_axes_mm,
            self.beam_top_z_mm,
            self.beam_link_centre_radius_mm,
            self.beam_link_seat_inset_mm,
        )
        if any(set(values) != {"X", "Y"} for values in plane_inputs):
            raise ValueError("Supply the beam and bar geometry in both planes.")
        for plane, axes in self.beam_axes_mm.items():
            if (
                self.beam_width_mm[plane] > width
                or self.beam_top_z_mm[plane] >= self.joint_depth_mm / 2
                or axes != tuple(sorted(set(axes)))
                or axes[-1] >= width
                or abs(axes[0] + axes[-1] - width) > 1e-6
                or abs(axes[1] + axes[-2] - width) > 1e-6
            ):
                raise ValueError(
                    "Supply centred four-bar symmetric beam rows within the joint."
                )
        inset = self.column_cover_mm + self.column_link_mm / 2
        radius = self.column_link_radius_mm
        overlap = self.column_link_overlap_half_mm
        jog_run = self.column_link_ramp_run_mm
        half = width / 2
        if (
            not 5 < self.column_bar_edge_mm < half - 5
            or not inset < half - overlap
            or not inset < self.column_cross_tie_axis_y_mm - radius < width - inset
            or width - 2 * inset <= 2 * radius
            or half + overlap - inset <= 2 * radius + jog_run
        ):
            raise ValueError(
                "Supply distinct closed hoop, cross-tie and column bar axes."
            )
        if self.x_hooks is not None and any(
            hook.tip_x_mm <= self.x_hook_radius_mm for hook in self.x_hooks.values()
        ):
            raise ValueError("A terminating bar needs a positive horizontal tangent.")
        stations = self.joint_hoop_centres_mm
        if (
            stations != tuple(sorted(set(stations)))
            or stations[-1] > self.joint_depth_mm
        ):
            raise ValueError(
                "Supply distinct increasing hoop stations within the joint."
            )
        ids: list[str] = []
        for direction, rows in self.directions.items():
            for row in rows:
                if (
                    set(row.beam_on_joint_downward_shear_kn)
                    != expected_sides[direction[0]]
                    or row.sway != direction[1]
                ):
                    raise ValueError(
                        "Supply the signed reactions for the beams present in each direction."
                    )
                ids.append(row.combination_id)
        if len(ids) != len(set(ids)):
            raise ValueError(
                "Joint action combinations must have distinct identifiers."
            )
        return self

"""Strict supplied-action contract for the ordinary two-span beam check."""

from __future__ import annotations

from typing import Annotated, Literal, Self

from pydantic import Field, field_validator, model_validator

from structural_lib.services.contracts.common import StrictPublicModel

BEAM_CONTINUOUS_CHECK_SCHEMA_VERSION: Literal["is456-continuous-beam-check/v1"] = (
    "is456-continuous-beam-check/v1"
)

Identifier = Annotated[str, Field(min_length=1, max_length=120)]
Reference = Annotated[str, Field(min_length=1, max_length=500)]


def _as_tuple(value: object) -> object:
    return tuple(value) if isinstance(value, list) else value


class BeamContinuousSupportV1(StrictPublicModel):
    """Support centre and full width in the beam's longitudinal coordinate."""

    support_id: Identifier
    centre_mm: float = Field(ge=0, le=30000)
    width_mm: float = Field(gt=0, le=3000)

    @property
    def left_face_mm(self) -> float:
        return self.centre_mm - self.width_mm / 2

    @property
    def right_face_mm(self) -> float:
        return self.centre_mm + self.width_mm / 2


class BeamContinuousBarV1(StrictPublicModel):
    """An actual longitudinal bar in one of two single-layer physical faces."""

    bar_id: Identifier
    face: Literal["top", "bottom"]
    diameter_mm: float = Field(ge=8, le=40)
    x_from_left_mm: float = Field(gt=0)
    y_from_top_mm: float = Field(gt=0)


class BeamContinuousStraightBarsV1(StrictPublicModel):
    """Shared, uninterrupted straight extent of the declared bars."""

    start_mm: float
    end_mm: float
    source_reference: Reference


class BeamContinuousStationV1(StrictPublicModel):
    """Named physical coordinate with an explicit side at a discontinuity."""

    station_id: Identifier
    x_mm: float = Field(ge=0, le=30000)
    side: Literal["LEFT", "RIGHT", "CONTINUOUS"]


class BeamContinuousCombinationV1(StrictPublicModel):
    """Caller-declared combination and its required station inventory."""

    combination_id: Identifier
    kind: Literal["ULS", "SLS", "SUSTAINED_SLS"]
    required_station_ids: tuple[Identifier, ...] = Field(min_length=1, max_length=300)

    @field_validator("required_station_ids", mode="before")
    @classmethod
    def accept_json_array(cls, value: object) -> object:
        return _as_tuple(value)


class BeamContinuousActionV1(StrictPublicModel):
    """One supplied concurrent row in kN and kN·m."""

    row_id: Identifier
    combination_id: Identifier
    station_id: Identifier
    mu_knm: float = Field(ge=-100000, le=100000)
    vu_kn: float = Field(ge=-100000, le=100000)
    tu_knm: float = Field(default=0, ge=-100000, le=100000)


class BeamContinuousCheckRequestV1(StrictPublicModel):
    """Two-span rectangular section, actual bars and revision-bound actions."""

    schema_version: Literal["is456-continuous-beam-check/v1"] = (
        BEAM_CONTINUOUS_CHECK_SCHEMA_VERSION
    )
    member_id: Identifier
    analysis_revision: Identifier
    current_analysis_revision: Identifier
    reinforcement_revision: Identifier
    source_reference: Reference
    width_mm: float = Field(ge=150, le=1500)
    depth_mm: float = Field(ge=200, le=2000)
    fck_nmm2: float = Field(ge=20, le=40)
    fy_nmm2: Literal[415, 500]
    clear_cover_mm: float = Field(ge=20, le=75)
    aggregate_size_mm: float = Field(gt=0, le=40)
    link_diameter_mm: float = Field(ge=6, le=16)
    link_spacing_mm: float = Field(gt=0, le=600)
    link_fy_nmm2: Literal[250, 415, 500]
    supports: tuple[
        BeamContinuousSupportV1, BeamContinuousSupportV1, BeamContinuousSupportV1
    ]
    bars: tuple[BeamContinuousBarV1, ...] = Field(min_length=4, max_length=40)
    straight_bars: BeamContinuousStraightBarsV1 | None = None
    stations: tuple[BeamContinuousStationV1, ...] = Field(max_length=300)
    combinations: tuple[BeamContinuousCombinationV1, ...] = Field(
        min_length=1, max_length=100
    )
    actions: tuple[BeamContinuousActionV1, ...] = Field(max_length=10000)

    @field_validator(
        "supports", "bars", "stations", "combinations", "actions", mode="before"
    )
    @classmethod
    def accept_json_arrays(cls, value: object) -> object:
        return _as_tuple(value)

    @model_validator(mode="after")
    def check_geometry_and_inventory(self) -> Self:
        supports = self.supports
        if len({support.support_id for support in supports}) != len(supports):
            raise ValueError("Support IDs must be unique.")
        if any(
            right.left_face_mm - left.right_face_mm < 2.5 * self.depth_mm
            for left, right in zip(supports[:-1], supports[1:], strict=True)
        ):
            raise ValueError(
                "Supports must bound two ordered clear spans of at least 2.5 times the section depth."
            )
        for face in ("top", "bottom"):
            bars = [bar for bar in self.bars if bar.face == face]
            if len(bars) < 2 or len({bar.y_from_top_mm for bar in bars}) != 1:
                raise ValueError(
                    "Provide at least two bars in exactly one layer at each physical face."
                )
        if any(
            bar.x_from_left_mm >= self.width_mm
            or bar.y_from_top_mm >= self.depth_mm
            or ((bar.face == "top") != (bar.y_from_top_mm < self.depth_mm / 2))
            for bar in self.bars
        ):
            raise ValueError(
                "Bar coordinates must be inside the section and agree with their physical face."
            )
        if len({bar.bar_id for bar in self.bars}) != len(self.bars):
            raise ValueError("Bar IDs must be unique.")
        extent = self.straight_bars
        if extent is not None and not (
            supports[0].left_face_mm + self.clear_cover_mm
            <= extent.start_mm
            <= supports[0].centre_mm
            < supports[2].centre_mm
            <= extent.end_mm
            <= supports[2].right_face_mm - self.clear_cover_mm
        ):
            raise ValueError(
                "Straight bar extents must cross both spans and fit within the end faces and cover."
            )

        station_ids = {station.station_id for station in self.stations}
        station_keys = {(station.x_mm, station.side) for station in self.stations}
        if len(station_ids) != len(self.stations) or len(station_keys) != len(
            self.stations
        ):
            raise ValueError("Station IDs and coordinate-side pairs must be unique.")
        for station in self.stations:
            if not supports[0].centre_mm <= station.x_mm <= supports[2].centre_mm:
                raise ValueError(
                    "A station lies outside the declared support centrelines."
                )
            if (
                station.side != "CONTINUOUS"
                and (station.x_mm, "CONTINUOUS") in station_keys
            ):
                raise ValueError(
                    "Use continuous or left/right station sides at a coordinate."
                )
            allowed_centre_sides = {
                supports[0].centre_mm: ("RIGHT",),
                supports[1].centre_mm: ("LEFT", "RIGHT"),
                supports[2].centre_mm: ("LEFT",),
            }
            if (
                station.x_mm in allowed_centre_sides
                and station.side not in allowed_centre_sides[station.x_mm]
            ):
                raise ValueError(
                    "Support centreline stations must identify their physical approach side."
                )
        for x_mm in (
            supports[0].right_face_mm,
            supports[1].left_face_mm,
            supports[1].right_face_mm,
            supports[2].left_face_mm,
        ):
            if (x_mm, "LEFT") in station_keys or (x_mm, "RIGHT") in station_keys:
                raise ValueError(
                    "This profile requires a continuous action station at each support face."
                )
        if any(
            (left.centre_mm < station.x_mm < left.right_face_mm)
            or (right.left_face_mm < station.x_mm < right.centre_mm)
            for left, right in zip(supports[:-1], supports[1:], strict=True)
            for station in self.stations
        ):
            raise ValueError(
                "Use a physical support face or centreline, with no intermediate stations inside the support."
            )
        combinations = {
            item.combination_id: set(item.required_station_ids)
            for item in self.combinations
        }
        if len(combinations) != len(self.combinations):
            raise ValueError("Combination IDs must be unique.")
        if any(
            len(combinations[item.combination_id]) != len(item.required_station_ids)
            or not combinations[item.combination_id] <= station_ids
            for item in self.combinations
        ):
            raise ValueError("Required station IDs must be unique and declared.")
        action_keys = {
            (action.combination_id, action.station_id) for action in self.actions
        }
        if len(action_keys) != len(self.actions) or len(
            {action.row_id for action in self.actions}
        ) != len(self.actions):
            raise ValueError(
                "Source row IDs and combination-station keys must be unique."
            )
        if any(
            station not in combinations.get(case, ()) for case, station in action_keys
        ):
            raise ValueError(
                "Each supplied action must belong to a declared combination and station."
            )
        return self

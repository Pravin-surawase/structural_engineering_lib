"""Strict supplied-action contracts for ordinary rectangular beam checks."""

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


class _BeamStationCheckRequest(StrictPublicModel):
    """Shared physical section, revisions and supplied station actions."""

    schema_version: str
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
    bars: tuple[BeamContinuousBarV1, ...] = Field(min_length=4, max_length=40)
    straight_bars: BeamContinuousStraightBarsV1 | None = None
    stations: tuple[BeamContinuousStationV1, ...] = Field(max_length=300)
    combinations: tuple[BeamContinuousCombinationV1, ...] = Field(
        min_length=1, max_length=100
    )
    actions: tuple[BeamContinuousActionV1, ...] = Field(max_length=10000)

    @field_validator("bars", "stations", "combinations", "actions", mode="before")
    @classmethod
    def accept_json_arrays(cls, value: object) -> object:
        return _as_tuple(value)

    def _check_bar_geometry(self) -> None:
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

    def _check_action_inventory(self, station_ids: set[str]) -> None:
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

    def _check_station_inventory(self) -> tuple[set[str], set[tuple[float, str]]]:
        ids = {station.station_id for station in self.stations}
        keys: set[tuple[float, str]] = {
            (station.x_mm, station.side) for station in self.stations
        }
        if len(ids) != len(self.stations) or len(keys) != len(self.stations):
            raise ValueError("Station IDs and coordinate-side pairs must be unique.")
        if any(
            side != "CONTINUOUS" and (x_mm, "CONTINUOUS") in keys for x_mm, side in keys
        ):
            raise ValueError(
                "Use continuous or left/right station sides at a coordinate."
            )
        return ids, keys


class BeamContinuousCheckRequestV1(_BeamStationCheckRequest):
    """Two-span rectangular section, actual bars and revision-bound actions."""

    schema_version: Literal["is456-continuous-beam-check/v1"] = (
        BEAM_CONTINUOUS_CHECK_SCHEMA_VERSION
    )
    supports: tuple[
        BeamContinuousSupportV1, BeamContinuousSupportV1, BeamContinuousSupportV1
    ]

    @field_validator("supports", mode="before")
    @classmethod
    def accept_support_array(cls, value: object) -> object:
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
        self._check_bar_geometry()
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

        station_ids, station_keys = self._check_station_inventory()
        for station in self.stations:
            if not supports[0].centre_mm <= station.x_mm <= supports[2].centre_mm:
                raise ValueError(
                    "A station lies outside the declared support centrelines."
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
        self._check_action_inventory(station_ids)
        return self


class BeamCantileverCheckRequestV1(_BeamStationCheckRequest):
    """Ordinary rectangular cantilever, measured outward from its fixed face."""

    schema_version: Literal["is456-cantilever-beam-check/v1"] = (
        "is456-cantilever-beam-check/v1"
    )
    fixed_support_id: Identifier
    fixed_support_width_mm: float = Field(gt=0, le=3000)
    free_end_mm: float = Field(gt=0, le=30000)

    @model_validator(mode="after")
    def check_geometry_and_inventory(self) -> Self:
        self._check_bar_geometry()
        if self.free_end_mm < 2.5 * self.depth_mm:
            raise ValueError(
                "Clear cantilever span must be at least 2.5 section depths."
            )
        extent = self.straight_bars
        if extent is not None and not (
            -self.fixed_support_width_mm + self.clear_cover_mm <= extent.start_mm < 0
            and abs(extent.end_mm - (self.free_end_mm - self.clear_cover_mm)) <= 1e-9
        ):
            raise ValueError(
                "Straight bars must extend into the fixed support and to the free-end cover."
            )
        station_ids, _ = self._check_station_inventory()
        for station in self.stations:
            if station.x_mm > self.free_end_mm:
                raise ValueError("A station lies past the declared free end.")
            if station.x_mm in (0, self.free_end_mm) and station.side != "CONTINUOUS":
                raise ValueError("Fixed and free ends require a continuous station.")
        self._check_action_inventory(station_ids)
        return self

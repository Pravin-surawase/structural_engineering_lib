"""Typed, supplied-action contract for the PROJECT03 two-joint frame cut."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import Field

from structural_lib.services.contracts.common import StrictPublicModel
from structural_lib.services.contracts.ductile_joint import (
    DuctileExteriorJointRequestV1,
    DuctileJointRequestV1,
    JointDirection,
)

JointID = Literal["J1", "J2"]
FrameBeamID = Literal["BX12", "BX1W", "BY1S", "BY1N", "BY2S", "BY2N"]
FrameColumnID = Literal["C-J1-upper", "C-J1-lower", "C-J2-upper", "C-J2-lower"]
_Id = Annotated[str, Field(min_length=1, max_length=120, pattern=r"\S")]
_Dimension = Annotated[float, Field(gt=0, le=20000)]
_Reference = Annotated[str, Field(min_length=1, max_length=500, pattern=r"\S")]
_Number = Annotated[float, Field(ge=-100000, le=100000)]
_Vector = Annotated[list[_Number], Field(min_length=3, max_length=3)]
_Pair = Annotated[list[_Number], Field(min_length=2, max_length=2)]
_StationGrid = Annotated[list[_Dimension], Field(max_length=12)]


class FrameFaceActionV1(StrictPublicModel):
    """One force and free couple applied to a member at a global point."""

    point_m: _Vector
    force_kn: _Vector
    couple_knm: _Vector


class FrameBeamActionsV1(StrictPublicModel):
    """Signed beam section actions, end wrenches and their UDL resultant."""

    start_joint: JointID | None
    end_joint: JointID | None
    plane: Literal["X", "Y"]
    clear_span_m: Annotated[float, Field(gt=0, le=20)]
    nominal_dead_plus_live_kn_m: Annotated[float, Field(ge=0, le=2000)]
    factored_udl_kn_m: Annotated[float, Field(gt=0, le=2000)]
    start_face: FrameFaceActionV1
    end_face: FrameFaceActionV1
    distributed_resultant: FrameFaceActionV1
    sectional_end_moments_knm: _Pair
    vertical_reactions_kn: _Pair


class FrameColumnActionsV1(StrictPublicModel):
    """One continuous column leg with both cut-face wrenches and body weight."""

    joint: JointID
    position: Literal["upper", "lower"]
    near_face: FrameFaceActionV1
    boundary_face: FrameFaceActionV1
    self_weight_resultant: FrameFaceActionV1


class FrameCombinationV1(StrictPublicModel):
    """Concurrent actions from the stated source revision."""

    action_revision: _Id
    direction: JointDirection
    beams: dict[FrameBeamID, FrameBeamActionsV1]
    columns: dict[FrameColumnID, FrameColumnActionsV1]


class FrameJointGeometryV1(StrictPublicModel):
    """Local geometry of the interior west and exterior east joints."""

    J1: DuctileJointRequestV1
    J2: DuctileExteriorJointRequestV1


class FrameReinforcementV1(StrictPublicModel):
    """Physical link jogs, central stations and the declared west embedment."""

    center_fill_mm: dict[Literal["BX12-O", "BX12-M"], _StationGrid]
    beam_closure_run_mm: Annotated[float, Field(gt=0, le=300)]
    beam_closure_rise_mm: Annotated[float, Field(gt=0, le=100)]
    beam_link_hook_tail_mm: _Dimension
    west_clear_span_mm: _Dimension
    west_development_mm: _Dimension
    west_support_depth_mm: _Dimension
    stock_length_mm: _Dimension


class DuctileFrameRequestV1(StrictPublicModel):
    """One regular open two-joint frame cut with explicit signed end actions."""

    schema_version: Literal["ductile-frame-cut/v1"] = "ductile-frame-cut/v1"
    project_id: _Id
    applicability_reference: _Reference | None = None
    action_revision: _Id
    current_action_revision: _Id
    required_combinations: dict[
        JointDirection, Annotated[list[_Id], Field(max_length=32)]
    ]
    joint_geometry: FrameJointGeometryV1
    detailing: FrameReinforcementV1
    actions: Annotated[dict[_Id, FrameCombinationV1], Field(max_length=128)]

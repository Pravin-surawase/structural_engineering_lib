"""Finite two-layer reinforcement selection using the supplied section checks."""

from __future__ import annotations

import hashlib
import html
import json
import math
from dataclasses import replace
from itertools import product
from typing import Any, Literal, Self

from pydantic import Field, field_validator, model_validator

from structural_lib.beam.reinforcement import Face
from structural_lib.core.result_contract import (
    EngineeringStatus,
    FreshnessStatus,
    StructuralIssueV1,
)
from structural_lib.services.beam_continuous import check_section_beam
from structural_lib.services.canonical_family import (
    CanonicalFamilyResultV1,
    FamilyIdentityV1,
    canonical_family_result,
    require_request_type,
)
from structural_lib.services.contracts.beam_continuous import (
    BeamSectionBarV1,
    BeamSectionCheckRequestV1,
    Identifier,
    _as_tuple,
)
from structural_lib.services.contracts.common import StrictPublicModel

WORKFLOW = "is456.beam.section-catalogue/v1"


class BeamLayerOptionV1(StrictPublicModel):
    """An explicit diameter and bar centres for one bottom layer."""

    option_id: Identifier
    diameter_mm: float = Field(ge=8, le=40)
    x_from_left_mm: tuple[float, ...] = Field(min_length=2, max_length=12)

    @field_validator("x_from_left_mm", mode="before")
    @classmethod
    def accept_array(cls, value: object) -> object:
        return _as_tuple(value)

    @model_validator(mode="after")
    def validate_positions(self) -> Self:
        if min(self.x_from_left_mm) <= 0 or any(
            x >= y
            for x, y in zip(
                self.x_from_left_mm[:-1], self.x_from_left_mm[1:], strict=True
            )
        ):
            raise ValueError("Bar centres must be positive and strictly ordered.")
        return self


class BeamLayerCatalogueV1(StrictPublicModel):
    """Finite options for one of the two actual bottom layer depths."""

    layer: Literal[1, 2]
    options: tuple[BeamLayerOptionV1, ...] = Field(min_length=1, max_length=12)

    @field_validator("options", mode="before")
    @classmethod
    def accept_array(cls, value: object) -> object:
        return _as_tuple(value)

    @model_validator(mode="after")
    def validate_ids(self) -> Self:
        if any("/" in option.option_id for option in self.options):
            raise ValueError("Option IDs cannot contain a slash.")
        if len({option.option_id for option in self.options}) != len(self.options):
            raise ValueError("Each layer requires unique option IDs.")
        return self


class BeamSectionCatalogueInputV1(StrictPublicModel):
    """Check every combination of a bounded two-layer bottom steel catalogue."""

    schema_version: Literal["is456-beam-section-catalogue-input/v1"] = (
        "is456-beam-section-catalogue-input/v1"
    )
    identity: FamilyIdentityV1
    member: BeamSectionCheckRequestV1
    layers: tuple[BeamLayerCatalogueV1, BeamLayerCatalogueV1]
    evaluation_limit: int = Field(ge=1, le=144)
    analysis_basis: Literal[
        "fixed_supplied_actions", "reinforcement_dependent_stiffness"
    ]

    @field_validator("layers", mode="before")
    @classmethod
    def accept_array(cls, value: object) -> object:
        return _as_tuple(value)

    @model_validator(mode="after")
    def validate_layers(self) -> Self:
        if (
            self.identity.member_id != self.member.member_id
            or self.member.flange is not None
        ):
            raise ValueError(
                "Catalogue selection requires the same solid rectangular member identity."
            )
        if {layer.layer for layer in self.layers} != {1, 2} or {
            bar.layer for bar in self.member.bars if bar.face == "bottom"
        } != {1, 2}:
            raise ValueError(
                "Declare exactly two existing and two catalogue bottom layers."
            )
        if any(
            option.x_from_left_mm[-1] >= self.member.width_mm
            for layer in self.layers
            for option in layer.options
        ):
            raise ValueError(
                "All candidate bar centres must be within the section width."
            )
        top_count = sum(bar.face == "top" for bar in self.member.bars)
        if (
            top_count
            + sum(
                max(len(option.x_from_left_mm) for option in layer.options)
                for layer in self.layers
            )
            > 40
        ):
            raise ValueError(
                "A catalogue candidate cannot exceed the section's 40-bar limit."
            )
        return self


def _rank(pair: tuple[BeamLayerOptionV1, BeamLayerOptionV1]) -> tuple[float, int, str]:
    areas = [
        math.pi * option.diameter_mm**2 / 4
        for option in pair
        for _ in option.x_from_left_mm
    ]
    return sum(areas), len(areas), f"{pair[0].option_id}/{pair[1].option_id}"


def select_section_catalogue(
    request: BeamSectionCatalogueInputV1,
) -> CanonicalFamilyResultV1[dict[str, Any]]:
    """Enumerate and rank finite bottom reinforcement candidates.

    Parameters
    ----------
    request : BeamSectionCatalogueInputV1
        A rectangular section, supplied action rows and bottom bar options.

    Returns
    -------
    CanonicalFamilyResultV1
        Every checked candidate, eligible order and the selected checked section.

    Raises
    ------
    InputContractError
        The supplied request is not a validated catalogue input.

    Examples
    --------
    >>> callable(select_section_catalogue)
    True

    Limitations
    -----------
    Fixed top bars and depths, two bottom layers and one physical section.

    Provenance
    ----------
    Reuses the signed section flexure, shear and reinforcement geometry checks.
    """
    require_request_type(request, BeamSectionCatalogueInputV1)
    member = request.member
    left, right = sorted(request.layers, key=lambda item: item.layer)
    pairs = sorted(product(left.options, right.options), key=_rank)
    depths = {
        bar.layer: bar.y_from_top_mm for bar in member.bars if bar.face == "bottom"
    }
    top = tuple(bar for bar in member.bars if bar.face == "top")
    fixed_ids = {bar.bar_id for bar in top}
    prefix = "B"
    while any(bar_id.startswith(prefix) for bar_id in fixed_ids):
        prefix += "B"
    evaluated: dict[str, dict[str, Any]] = {}
    eligible = []
    selected = None
    for pair in pairs[: request.evaluation_limit]:
        area, count, candidate_id = _rank(pair)
        bars = top + tuple(
            BeamSectionBarV1(
                bar_id=f"{prefix}{layer}-{index}",
                face="bottom",
                layer=layer,
                diameter_mm=option.diameter_mm,
                x_from_left_mm=x,
                y_from_top_mm=depths[layer],
            )
            for layer, option in enumerate(pair, 1)
            for index, x in enumerate(option.x_from_left_mm, 1)
        )
        revision_data = json.dumps(
            [
                member.reinforcement_revision,
                [bar.model_dump(mode="json") for bar in bars],
            ],
            sort_keys=True,
            separators=(",", ":"),
        )
        revision = "catalogue-" + hashlib.sha256(revision_data.encode()).hexdigest()
        candidate = member.model_copy(
            update={"bars": bars, "reinforcement_revision": revision}
        )
        checked = check_section_beam(candidate)
        row_scores = [
            (
                max(row.flexure_utilization or 0, row.shear_utilization or 0),
                row.action.row_id,
            )
            for row in checked.rows
            if row.flexure_utilization is not None or row.shear_utilization is not None
        ]
        evaluated[candidate_id] = {
            "status": checked.ultimate_status,
            "bottom_area_mm2": area,
            "rank": [area, count, candidate_id],
            "governing_row_id": (
                min(row_scores, key=lambda row: (-row[0], row[1]))[1]
                if row_scores
                else None
            ),
            "capacities_knm": {
                face.value: checked.flexural_sections[face].outputs["capacity_knm"]
                for face in Face
                if face in checked.flexural_sections
            },
            "steel_by_face": {
                face.value: {
                    "provided_mm2": leaf.outputs["tension_steel_area_mm2"],
                    "code_minimum_mm2": leaf.outputs["minimum_tension_steel_area_mm2"],
                }
                for face, leaf in checked.flexural_sections.items()
                if "minimum_tension_steel_area_mm2" in leaf.outputs
            },
            "issue_codes": [issue.code for issue in checked.result_envelope.issues],
        }
        if checked.ultimate_status == "PASS":
            eligible.append(candidate_id)
            if selected is None:
                selected = checked.to_dict()

    complete = len(evaluated) == len(pairs)
    terminal = "COMPLETE_FEASIBLE"
    status = EngineeringStatus.PASS
    if not complete:
        terminal, status = "INCOMPLETE_BUDGET", EngineeringStatus.HOLD
    elif any(item["status"] == "HOLD" for item in evaluated.values()):
        terminal, status = "BLOCKED_MANDATORY_CHECK", EngineeringStatus.HOLD
    elif not eligible:
        terminal, status = "COMPLETE_INFEASIBLE", EngineeringStatus.FAIL
    elif request.analysis_basis != "fixed_supplied_actions":
        terminal, status = "REANALYSIS_REQUIRED", EngineeringStatus.HOLD
    result = canonical_family_result(
        request,
        {
            "terminal_state": terminal,
            "catalogue_count": len(pairs),
            "evaluated_count": len(evaluated),
            "enumeration_complete": complete,
            "evaluated": evaluated,
            "eligible_ids": eligible,
            "selected_id": eligible[0] if status is EngineeringStatus.PASS else None,
            "selected": selected if status is EngineeringStatus.PASS else None,
            "member_acceptance": "NOT_EVALUATED",
        },
        workflow_id=WORKFLOW,
        engineering_status=status,
        limitations=(
            "Selection ranks total bottom steel area, bar count and option IDs in that order.",
            "The result covers the supplied section and action rows.",
            "Member stability, serviceability, construction schedules and completeness of combinations require separate checks.",
        ),
        provenance=(
            "IS 456 signed section workflow and exhaustive Cartesian enumeration.",
        ),
    )
    if status is EngineeringStatus.PASS:
        return result
    messages = {
        "INCOMPLETE_BUDGET": "The evaluation budget stopped the catalogue replay.",
        "BLOCKED_MANDATORY_CHECK": "At least one candidate has an unresolved mandatory section check.",
        "COMPLETE_INFEASIBLE": "Every candidate failed at least one supplied section check.",
        "REANALYSIS_REQUIRED": "The source analysis depends on reinforcement stiffness. Refresh actions for the selected cage.",
    }
    issue = StructuralIssueV1(
        f"BEAM.CATALOGUE_{terminal}", "layers", messages[terminal]
    )
    return replace(
        result,
        envelope=replace(
            result.envelope,
            issues=(issue,),
            freshness_status=(
                FreshnessStatus.CURRENT
                if member.analysis_revision == member.current_analysis_revision
                else FreshnessStatus.STALE
            ),
        ),
    )


def render_section_catalogue_html(
    result: CanonicalFamilyResultV1[dict[str, Any]],
) -> str:
    """Render the checked candidate ranking and selection.

    Parameters
    ----------
    result : CanonicalFamilyResultV1
        A checked beam section catalogue result.

    Returns
    -------
    str
        HTML report with evaluation rows and the same input identity.

    Raises
    ------
    TypeError
        The supplied result belongs to a different workflow.

    Examples
    --------
    >>> callable(render_section_catalogue_html)
    True

    Limitations
    -----------
    Renders the recorded section checks without recalculation.

    Provenance
    ----------
    Uses the same candidate and source row identities as the JSON.
    """
    if (
        not isinstance(result, CanonicalFamilyResultV1)
        or result.workflow_id != WORKFLOW
    ):
        raise TypeError("result must be a beam section catalogue result")
    data = result.calculation
    identity = result.envelope.result_identity
    rows = "".join(
        f"<tr><th>{html.escape(key)}</th><td>{row['status']}</td>"
        f"<td>{row['bottom_area_mm2']:.2f}</td>"
        f"<td>{html.escape(row['governing_row_id'] or 'HOLD')}</td></tr>"
        for key, row in data["evaluated"].items()
    )
    limits = "".join(f"<li>{html.escape(limit)}</li>" for limit in result.limitations)
    issues = "".join(
        f"<li>{html.escape(issue.message)}</li>" for issue in result.issues
    )
    return f"""<!doctype html>
<html lang="en"><meta charset="utf-8"><title>Beam section catalogue</title>
<h1>Beam section catalogue · {html.escape(result.identity.case_id)}</h1>
<p>{result.engineering_status.value} · Qualified review required</p>
<p>Input identity <code>{identity.input_hash if identity else ''}</code></p>
<p>Checked {data['evaluated_count']} of {data['catalogue_count']}. Selected
{html.escape(data['selected_id'] or 'none')}.</p>
<table><thead><tr><th>Candidate</th><th>Status</th><th>Bottom steel (mm²)</th>
<th>Governing supplied row</th></tr></thead><tbody>{rows}</tbody></table>
<ul>{issues}{limits}</ul></html>"""

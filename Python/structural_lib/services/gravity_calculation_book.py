# SPDX-License-Identifier: MIT
"""Deterministic review dossier for Building Gravity Workflow V1."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict

from structural_lib.core.gravity_workflow import (
    ComponentApplicabilityMatrixV1,
    GravityComponentResultV1,
    GravityMemberActionV1,
    GravityWorkflowRequestV1,
    GravityWorkflowResultV1,
)
from structural_lib.services.gravity_builder import (
    get_gravity_workflow_example_document_v1,
)
from structural_lib.services.gravity_loads import build_gravity_load_ledger_v1
from structural_lib.services.gravity_workflow import run_gravity_workflow_v1
from structural_lib.services.serialization import to_transport_value

__all__ = [
    "GravityCalculationBookV1",
    "GravityWorkflowDefinitionV1",
    "GravityWorkflowRunBundleV1",
    "build_gravity_calculation_book_v1",
    "get_gravity_workflow_definition_v1",
    "render_gravity_calculation_book_markdown_v1",
    "run_gravity_workflow_with_book_v1",
]


class _FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", allow_inf_nan=False)


class GravityCalculationBookV1(_FrozenModel):
    """Complete machine-readable review record; not professional approval."""

    schema_version: Literal["gravity-calculation-book/v1"] = (
        "gravity-calculation-book/v1"
    )
    workflow_version: Literal["building-gravity-workflow/v1"] = (
        "building-gravity-workflow/v1"
    )
    formula_version: Literal["gravity-load-path/v1"] = "gravity-load-path/v1"
    model_hash: str
    load_model_hash: str
    ledger_hash: str
    workflow_result_hash: str
    model_snapshot: dict[str, Any]
    load_snapshot: dict[str, Any]
    ledger_snapshot: dict[str, Any]
    reconciliation: dict[str, Any]
    applicability: ComponentApplicabilityMatrixV1
    actions: tuple[GravityMemberActionV1, ...]
    components: tuple[GravityComponentResultV1, ...]
    result_envelope: dict[str, Any]
    approved_exclusions: tuple[dict[str, Any], ...]
    limitations: tuple[str, ...]
    issues: tuple[dict[str, Any], ...]
    review_disposition: Literal["QUALIFIED_REVIEW_REQUIRED"] = (
        "QUALIFIED_REVIEW_REQUIRED"
    )


class GravityWorkflowRunBundleV1(_FrozenModel):
    schema_version: Literal["gravity-workflow-run-bundle/v1"] = (
        "gravity-workflow-run-bundle/v1"
    )
    workflow_result: GravityWorkflowResultV1
    calculation_book: GravityCalculationBookV1


class GravityWorkflowDefinitionV1(_FrozenModel):
    """Discoverable, non-executable capability definition for product surfaces."""

    schema_version: Literal["gravity-workflow-definition/v1"] = (
        "gravity-workflow-definition/v1"
    )
    capability_id: Literal["building.gravity.dead-live.v1"] = (
        "building.gravity.dead-live.v1"
    )
    workflow_version: Literal["building-gravity-workflow/v1"] = (
        "building-gravity-workflow/v1"
    )
    title: str
    summary: str
    accepted_topology: tuple[str, ...]
    component_adapters: dict[str, str]
    product_surfaces: dict[str, str]
    example_request: dict[str, Any]
    exclusions: tuple[str, ...]
    status_contract: Literal["structural-result-envelope/v2"] = (
        "structural-result-envelope/v2"
    )
    qualified_review_required: Literal[True] = True


def get_gravity_workflow_definition_v1() -> GravityWorkflowDefinitionV1:
    """Return the single canonical discovery record for Gravity Workflow V1."""

    return GravityWorkflowDefinitionV1(
        title="Building Gravity Workflow V1",
        summary=(
            "One rectangular, one-storey dead/live gravity load path with exact "
            "ledger reconciliation and conditional component design adapters."
        ),
        accepted_topology=(
            "one rectangular slab panel",
            "two simply supported beams in the declared X direction",
            "four braced axial-only columns",
            "four concentric footing action destinations",
        ),
        component_adapters={
            "SLAB": "design_complete_one_way_slab_is456",
            "BEAM": "design_beam_is456",
            "COLUMN": "design_column_is456",
            "FOOTING": "design_concentric_isolated_footing_is456",
        },
        product_surfaces={
            "python": "structural_lib.run_gravity_workflow_with_book_v1",
            "python_builder": (
                "structural_lib.build_rectangular_gravity_workflow_request_v1"
            ),
            "python_example": (
                "structural_lib.get_gravity_workflow_example_request_v1"
            ),
            "cli_example": "python -m structural_lib gravity-v1 example",
            "cli_run": "python -m structural_lib gravity-v1 REQUEST.json",
            "rest": "POST /api/v1/building-gravity/v1/run",
            "review_ui": "/workbench/building-gravity/v1",
        },
        example_request=get_gravity_workflow_example_document_v1(),
        exclusions=(
            "wind, seismic, wall, equipment, stair, tank, and special roof actions",
            "global frame, stiffness, finite-element, nonlinear, and spatial analysis",
            "live-load reduction and automatic engineering-assumption inference",
            "footing design without complete external service, soil, and detailing basis",
        ),
    )


def build_gravity_calculation_book_v1(
    request: GravityWorkflowRequestV1,
    result: GravityWorkflowResultV1,
) -> GravityCalculationBookV1:
    """Bind accepted inputs, ledger, actions, results, and holds in one dossier."""

    ledger = build_gravity_load_ledger_v1(request.building, request.loads)
    if ledger.ledger_hash != result.ledger_hash:
        raise ValueError("workflow result ledger identity does not match replay")
    issues = tuple(
        issue
        for component in result.components
        for issue in component.result_envelope.get("issues", [])
        if isinstance(issue, dict)
    )
    max_residual = max((abs(item.residual_kn) for item in ledger.balances), default=0.0)
    return GravityCalculationBookV1(
        model_hash=result.model_hash,
        load_model_hash=result.load_model_hash,
        ledger_hash=result.ledger_hash,
        workflow_result_hash=result.workflow_result_hash,
        model_snapshot=to_transport_value(request.building),
        load_snapshot=to_transport_value(request.loads),
        ledger_snapshot=to_transport_value(ledger),
        reconciliation={
            "all_balanced": ledger.all_balanced,
            "boundary_count": len(ledger.balances),
            "maximum_absolute_residual_kn": max_residual,
            "balance_tolerance_kn": request.loads.balance_tolerance_kn,
            "accepted_entry_count": ledger.accepted_entry_count,
            "blocked_entry_count": ledger.blocked_entry_count,
        },
        applicability=result.applicability,
        actions=result.actions,
        components=result.components,
        result_envelope=result.result_envelope,
        approved_exclusions=tuple(
            to_transport_value(item) for item in request.loads.approved_exclusions
        ),
        limitations=result.limitations,
        issues=issues,
    )


def run_gravity_workflow_with_book_v1(
    request: GravityWorkflowRequestV1,
) -> GravityWorkflowRunBundleV1:
    """Run the workflow and create its bound calculation book."""

    result = run_gravity_workflow_v1(request)
    return GravityWorkflowRunBundleV1(
        workflow_result=result,
        calculation_book=build_gravity_calculation_book_v1(request, result),
    )


def render_gravity_calculation_book_markdown_v1(
    book: GravityCalculationBookV1,
) -> str:
    """Render a compact human review view without changing calculation truth."""

    envelope_issues = book.result_envelope.get("issues", [])
    governing_issue = (
        envelope_issues[0]
        if isinstance(envelope_issues, list)
        and envelope_issues
        and isinstance(envelope_issues[0], dict)
        else None
    )
    lines = [
        "# Building Gravity Workflow V1 Calculation Book",
        "",
        f"- Overall status: `{book.result_envelope['overall_status']}`",
        *(
            [
                "- Governing reason: "
                f"`{governing_issue.get('code', 'UNSPECIFIED')}` — "
                f"{governing_issue.get('message', '')}"
            ]
            if governing_issue is not None
            else []
        ),
        f"- Model hash: `{book.model_hash}`",
        f"- Load-model hash: `{book.load_model_hash}`",
        f"- Ledger hash: `{book.ledger_hash}`",
        f"- Workflow-result hash: `{book.workflow_result_hash}`",
        f"- Formula identity: `{book.formula_version}`",
        f"- Review: `{book.review_disposition}`",
        "",
        "## Reconciliation",
        "",
        f"- All boundaries balanced: `{book.reconciliation['all_balanced']}`",
        f"- Boundaries checked: `{book.reconciliation['boundary_count']}`",
        "- Maximum absolute residual: "
        f"`{book.reconciliation['maximum_absolute_residual_kn']} kN`",
        "",
        "## Component dispositions",
        "",
        "| Component | Kind | Status | Canonical function |",
        "|---|---|---|---|",
    ]
    lines.extend(
        "| {id} | {kind} | {status} | `{function}` |".format(
            id=item.component_id,
            kind=item.kind.value,
            status=item.result_envelope["overall_status"],
            function=item.canonical_function,
        )
        for item in book.components
    )
    lines.extend(["", "## Explicit limitations", ""])
    lines.extend(f"- {item}" for item in book.limitations)
    lines.extend(["", "## Approved exclusions", ""])
    lines.extend(
        f"- `{item['category']}` — {item['reason']}"
        for item in book.approved_exclusions
    )
    lines.extend(["", "## Issues and holds", ""])
    if book.issues:
        lines.extend(
            f"- `{item.get('code', 'UNSPECIFIED')}` at "
            f"`{item.get('path', '$')}` — {item.get('message', '')}"
            for item in book.issues
        )
    else:
        lines.append("- None recorded.")
    lines.extend(
        [
            "",
            "> This calculation book records bounded software output. "
            "Qualified structural-engineering review remains required.",
            "",
        ]
    )
    return "\n".join(lines)

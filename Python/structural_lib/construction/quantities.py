"""AO04: reconciled steel, concrete, formwork, and waste quantities."""

from __future__ import annotations

import math

from structural_lib.beam.semantics import (
    Diagnostic,
    OperationResult,
    Provenance,
    completed_result,
    effective_inputs,
    rejected_result,
    semantic_hash,
)

from .contracts import (
    ConcreteQuantity,
    ConstructionQuantityOutput,
    ConstructionQuantityRequest,
    FormworkMeasurementState,
    FormworkQuantity,
    QuantitySteelItem,
    WasteLedger,
)

CALCULATE_QUANTITIES_OPERATION = "structural.construction_quantities.calculate/v1"
QUANTITY_METHOD_REVISION = "structural-construction-quantities-wp07-v1"


def _text(value: str | None) -> bool:
    return bool(value and value.strip())


def _provenance() -> Provenance:
    return Provenance(
        "construction-data-wp07-v1",
        QUANTITY_METHOD_REVISION,
        (
            "PF7 AR04 independent mass, volume, and contact-area arithmetic",
            "PF7 AR20 explicit net segments and formwork contact faces",
        ),
    )


def _error(code: str, message: str, field: str, remediation: str) -> Diagnostic:
    return Diagnostic(
        code,
        "error",
        message,
        CALCULATE_QUANTITIES_OPERATION,
        field,
        "construction-quantities",
        remediation,
    )


def _reject(
    inputs: dict[str, dict[str, object]],
    code: str,
    message: str,
    field: str,
    remediation: str,
) -> OperationResult:
    return rejected_result(
        CALCULATE_QUANTITIES_OPERATION,
        inputs,
        (_error(code, message, field, remediation),),
        provenance=_provenance(),
    )


def calculate_construction_quantities(
    request: ConstructionQuantityRequest,
) -> OperationResult:
    """Calculate quantities without applying regional or commercial rates."""

    inputs = effective_inputs(request=request)
    bbs = request.bbs
    if not all(
        _text(value)
        for value in (
            request.profile_id,
            request.project_basis_id,
            request.member_id,
            request.detail_revision_id,
            request.bbs_result_id,
            request.bbs_output_payload_id,
            request.concrete_overlap_policy_id,
            request.formwork_measurement_policy_id,
        )
    ):
        return _reject(
            inputs,
            "QUANTITY.IDENTITY",
            "Complete quantity, detail, and measurement policy identities are required.",
            "request",
            "Supply all current identities and named policies.",
        )
    if (
        bbs.profile_id != request.profile_id
        or bbs.project_basis_id != request.project_basis_id
        or bbs.member_id != request.member_id
        or bbs.detail_revision_id != request.detail_revision_id
        or not bbs.passed
    ):
        return _reject(
            inputs,
            "QUANTITY.BBS_STALE",
            "Quantities must bind the current passing BBS for the same detail.",
            "bbs",
            "Recreate the BBS from the active resolved schedule.",
        )
    if request.bbs_output_payload_id != semantic_hash("output_payload_id", bbs):
        return _reject(
            inputs,
            "QUANTITY.BBS_BINDING",
            "The BBS payload does not match its canonical output identity.",
            "bbs_output_payload_id",
            "Bind the unchanged AO19 output payload.",
        )

    segment_ids = [item.segment_id for item in request.concrete_segments]
    segment_owners = [item.ownership_id for item in request.concrete_segments]
    deduction_ids = [
        item.deduction_id
        for segment in request.concrete_segments
        for item in segment.deductions
    ]
    deduction_owners = [
        item.ownership_id
        for segment in request.concrete_segments
        for item in segment.deductions
    ]
    if (
        not request.concrete_segments
        or len(segment_ids) != len(set(segment_ids))
        or len(segment_owners) != len(set(segment_owners))
        or len(deduction_ids) != len(set(deduction_ids))
        or len(deduction_owners) != len(set(deduction_owners))
        or set(segment_owners) & set(deduction_owners)
        or any(
            not all(
                _text(value)
                for value in (
                    item.segment_id,
                    item.member_id,
                    item.material_id,
                    item.ownership_id,
                )
            )
            or item.member_id != request.member_id
            or not math.isfinite(item.cross_section_area_mm2)
            or item.cross_section_area_mm2 <= 0
            or not math.isfinite(item.physical_length_mm)
            or item.physical_length_mm <= 0
            or any(
                not all(
                    _text(value)
                    for value in (
                        deduction.deduction_id,
                        deduction.ownership_id,
                        deduction.reason,
                    )
                )
                or not math.isfinite(deduction.volume_m3)
                or deduction.volume_m3 < 0
                for deduction in item.deductions
            )
            for item in request.concrete_segments
        )
    ):
        return _reject(
            inputs,
            "QUANTITY.CONCRETE_OWNERSHIP",
            "Concrete segments and deductions require unique, explicit physical ownership.",
            "concrete_segments",
            "Remove duplicate or unbound segment and deduction ownership.",
        )

    concrete_items: list[ConcreteQuantity] = []
    for segment in request.concrete_segments:
        gross = segment.cross_section_area_mm2 * segment.physical_length_mm / 1e9
        deductions = math.fsum(item.volume_m3 for item in segment.deductions)
        if deductions > gross + 1e-12:
            return _reject(
                inputs,
                "QUANTITY.CONCRETE_DEDUCTION",
                "Concrete deductions cannot exceed the owned gross segment volume.",
                f"concrete_segments[{segment.segment_id}]",
                "Correct the explicit overlap or opening deduction.",
            )
        concrete_items.append(
            ConcreteQuantity(
                segment.segment_id,
                segment.material_id,
                segment.ownership_id,
                gross,
                deductions,
                gross - deductions,
                segment.owns_monolithic_interface,
            )
        )

    face_ids = [item.face_id for item in request.formwork_faces]
    face_owners = [item.ownership_id for item in request.formwork_faces]
    area_deduction_ids = [
        item.deduction_id for face in request.formwork_faces for item in face.deductions
    ]
    area_deduction_owners = [
        item.ownership_id for face in request.formwork_faces for item in face.deductions
    ]
    if (
        not request.formwork_faces
        or len(face_ids) != len(set(face_ids))
        or len(face_owners) != len(set(face_owners))
        or len(area_deduction_ids) != len(set(area_deduction_ids))
        or len(area_deduction_owners) != len(set(area_deduction_owners))
        or set(face_owners) & set(area_deduction_owners)
        or any(
            not all(
                _text(value)
                for value in (item.face_id, item.member_id, item.ownership_id)
            )
            or item.member_id != request.member_id
            or not math.isfinite(item.gross_area_mm2)
            or item.gross_area_mm2 < 0
            or not isinstance(item.measurement_state, FormworkMeasurementState)
            or (
                item.measurement_state is FormworkMeasurementState.EXCLUDED
                and not _text(item.exclusion_reason)
            )
            or (
                item.measurement_state is FormworkMeasurementState.INCLUDED
                and item.exclusion_reason is not None
            )
            or any(
                not all(
                    _text(value)
                    for value in (
                        deduction.deduction_id,
                        deduction.ownership_id,
                        deduction.reason,
                    )
                )
                or not math.isfinite(deduction.area_mm2)
                or deduction.area_mm2 < 0
                for deduction in item.deductions
            )
            for item in request.formwork_faces
        )
    ):
        return _reject(
            inputs,
            "QUANTITY.FORMWORK_OWNERSHIP",
            "Formwork faces and deductions require unique physical ownership and explicit inclusion state.",
            "formwork_faces",
            "Itemize each contact or interface face exactly once.",
        )

    formwork_items: list[FormworkQuantity] = []
    for face in request.formwork_faces:
        gross = face.gross_area_mm2 / 1e6
        deductions = math.fsum(item.area_mm2 for item in face.deductions) / 1e6
        if deductions > gross + 1e-12:
            return _reject(
                inputs,
                "QUANTITY.FORMWORK_DEDUCTION",
                "Formwork deductions cannot exceed the owned gross contact face.",
                f"formwork_faces[{face.face_id}]",
                "Correct the explicit contact-area deduction.",
            )
        net = (
            gross - deductions
            if face.measurement_state is FormworkMeasurementState.INCLUDED
            else 0.0
        )
        formwork_items.append(
            FormworkQuantity(
                face.face_id,
                face.category,
                face.ownership_id,
                face.measurement_state,
                gross,
                deductions,
                net,
                face.exclusion_reason,
            )
        )

    steel_items = tuple(
        QuantitySteelItem(
            row.bar_mark,
            row.diameter_mm,
            row.steel_grade_n_per_mm2,
            row.scheduled_bar_count,
            row.scheduled_cut_length_mm,
            row.theoretical_mass_kg,
        )
        for row in bbs.rows
    )
    output = ConstructionQuantityOutput(
        request.profile_id,
        request.project_basis_id,
        request.member_id,
        request.detail_revision_id,
        request.bbs_result_id,
        request.concrete_overlap_policy_id,
        request.formwork_measurement_policy_id,
        steel_items,
        tuple(concrete_items),
        tuple(formwork_items),
        WasteLedger(
            bbs.kerf_length_mm, bbs.reusable_offcut_length_mm, bbs.waste_length_mm
        ),
        bbs.scheduled_steel_mass_kg,
        bbs.purchased_stock_mass_kg,
        math.fsum(item.net_volume_m3 for item in concrete_items),
        math.fsum(item.net_area_m2 for item in formwork_items),
        sum(item.count for item in bbs.couplers),
    )
    return completed_result(
        CALCULATE_QUANTITIES_OPERATION,
        inputs,
        {"quantities": output},
        provenance=_provenance(),
    )

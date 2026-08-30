#!/usr/bin/env python3
"""Export a validated, formula-free W3J review carrier; never call ETABS/Excel.

The input is an existing CalculationDossierV1 whose required canonical artifacts
contain a catalogue, a beam-demand-review/v1 (request + snapshot), and a W3E
evaluation or explicit blocked input-build result. Output must not already exist.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from structural_lib.core.calculation_dossier import CalculationDossierV1
from structural_lib.services.beam_audit import (
    BeamAuditEvaluationResultV1,
    BeamAuditInputBuildResultV1,
)
from structural_lib.services.calculation_dossier import (
    build_calculation_dossier_v1,
    record_review_attestation_v1,
)
from structural_lib.services.contracts.etabs_w3 import (
    BeamDemandDerivationRequestV1,
    ETABSResultCatalogueBuildRequestV1,
    ETABSResultCatalogueV1,
    build_etabs_result_catalogue_v1,
    derive_beam_demand_snapshot_v1,
)

MAX_BYTES = 64 * 1024 * 1024


def canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def export_review(dossier: CalculationDossierV1) -> dict[str, object]:
    """Validate through existing owners, then carry their exact bytes to Office.js."""
    built = build_calculation_dossier_v1(dossier.request)
    if built.dossier is None:
        raise ValueError(f"Dossier blocked: {built.issues}")
    rebuilt = built.dossier
    for attestation in dossier.attestations:
        rebuilt = record_review_attestation_v1(rebuilt, attestation)
    observed = dossier.model_dump(mode="json")
    expected = rebuilt.model_dump(mode="json")
    expected.pop("attested_sha256", None)
    if observed != expected:
        raise ValueError("Dossier hash, scope, revision or attestation state is stale")
    artifacts = {}
    for item in dossier.request.artifacts:
        if item.canonical_json.state.value == "PRESENT":
            artifacts[item.kind] = json.loads(item.canonical_json.value or "")
    if not {"CATALOGUE", "DEMAND", "CALCULATION"} <= artifacts.keys():
        raise ValueError(
            "Review requires complete canonical catalogue/demand/calculation artifacts"
        )
    catalogue = ETABSResultCatalogueV1.model_validate_json(
        canonical(artifacts["CATALOGUE"]), strict=False
    )
    if catalogue.model_dump(mode="json") != artifacts["CATALOGUE"]:
        raise ValueError("Catalogue parsing changed its canonical values")
    rebuilt_catalogue = build_etabs_result_catalogue_v1(
        ETABSResultCatalogueBuildRequestV1(
            model_identity_sha256=catalogue.model_identity_sha256,
            runtime_identity_sha256=catalogue.runtime_identity_sha256,
            getter_matrix_sha256=catalogue.getter_matrix_sha256,
            load_patterns=catalogue.load_patterns,
            load_cases=catalogue.load_cases,
            analysis_statuses=catalogue.analysis_statuses,
            response_combinations=catalogue.response_combinations,
            result_selections=catalogue.result_selections,
            capacity_limit=catalogue.capacity.accepted_capacity_limit,
        )
    )
    if rebuilt_catalogue.catalogue != catalogue:
        raise ValueError("Catalogue replay did not reconcile")
    demand = artifacts["DEMAND"]
    if (
        set(demand) != {"schema_version", "request", "snapshot"}
        or demand["schema_version"] != "beam-demand-review/v1"
    ):
        raise ValueError("Expected the complete beam-demand-review/v1 carrier")
    request = BeamDemandDerivationRequestV1.model_validate_json(
        canonical(demand["request"]), strict=False
    )
    if request.model_dump(mode="json") != demand["request"]:
        raise ValueError("Demand parsing changed its canonical values")
    if request.catalogue != catalogue:
        raise ValueError("Demand catalogue differs from the dossier catalogue")
    derived = derive_beam_demand_snapshot_v1(request)
    if (
        derived.snapshot is None
        or derived.snapshot.model_dump(mode="json") != demand["snapshot"]
    ):
        raise ValueError("Demand replay did not reconcile")
    if (
        catalogue.model_identity_sha256
        != dossier.request.identity.model_identity_sha256
    ):
        raise ValueError("Dossier model identity differs from the demand catalogue")
    calculation = artifacts["CALCULATION"]
    if calculation.get("schema_version") == "beam-audit-evaluation/v1":
        evaluated = BeamAuditEvaluationResultV1.model_validate_json(
            canonical(calculation), strict=False
        )
        if evaluated.status.value != "ACCEPTED":
            raise ValueError(
                "Use an explicit blocked input-build carrier for unavailable calculations"
            )
        for row in evaluated.rows:
            if (
                row.input.action.baseline_sha256 != request.baseline.baseline_sha256
                or row.input.action.catalogue_sha256 != catalogue.catalogue_sha256
            ):
                raise ValueError("Calculation row belongs to another source")
            if (
                hashlib.sha256(row.canonical_result_json.encode()).hexdigest()
                != row.canonical_result_sha256
            ):
                raise ValueError("Calculation result bytes changed")
    else:
        blocked = BeamAuditInputBuildResultV1.model_validate_json(
            canonical(calculation), strict=False
        )
        if (
            blocked.status.value != "BLOCKED"
            or dossier.request.software_status != "HOLD"
        ):
            raise ValueError(
                "Missing calculations must remain an explicit software HOLD"
            )
    text = canonical(observed)
    encoded = text.encode("utf-8")
    if len(encoded) > MAX_BYTES:
        raise ValueError("Dossier exceeds the 64 MiB review limit; nothing exported")
    return {
        "schema_version": "calculation-review-transport/v1",
        "dossier_json": text,
        "dossier_content_sha256": hashlib.sha256(encoded).hexdigest(),
        "dossier_utf8_bytes": len(encoded),
        "request_json": canonical(observed["request"]),
        "scope_json": canonical(observed["request"]["scope"]),
        "professional_approval": "NOT_PROVIDED",
        "signature_verification": "NOT_PROVIDED",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dossier", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Output already exists; no overwrite is permitted")
    if args.dossier.stat().st_size > MAX_BYTES:
        parser.error("Input exceeds the bounded 64 MiB limit")
    dossier = CalculationDossierV1.model_validate_json(
        args.dossier.read_text(encoding="utf-8")
    )
    transport = export_review(dossier)
    with args.output.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(canonical(transport) + "\n")
    print(
        json.dumps(
            {
                "output": str(args.output),
                "dossier_content_sha256": transport["dossier_content_sha256"],
                "dossier_utf8_bytes": transport["dossier_utf8_bytes"],
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

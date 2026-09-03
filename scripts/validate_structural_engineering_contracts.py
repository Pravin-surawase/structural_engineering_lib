#!/usr/bin/env python3
"""Validate language-neutral structural-engineering contract artifacts."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_ROOT = ROOT / "contracts" / "structural-engineering"
EXPECTED_WP01 = {
    "FO01": "structural.reinforcement.bar_area/v1",
    "FO02": "structural.reinforcement.mass_per_length/v1",
    "FO03": "structural.reinforcement.effective_depth/v1",
    "FO04": "is456.beam.flexural_capacity/v1",
    "AO03": "structural.reinforcement_geometry.evaluate/v1",
    "AO06": "is456.beam.flexure.check/v1",
}
EXPECTED_MANIFESTS = {
    "wp01": EXPECTED_WP01,
    "wp02": {
        "FO05": "is456.beam.shear_capacity/v1",
        "AO07": "is456.beam.shear.check/v1",
        "AO08": "is456.beam.torsion.check/v1",
    },
    "wp03": {
        "AO01": "structural.action_snapshot.normalize/v1",
        "AO02": "structural.beam_line.solve/v1",
        "AO15": "structural.beam_topology.define/v1",
    },
    "wp04": {
        "FO07": "is456.beam.deflection_limit/v1",
        "FO08": "is456.beam.crack_width_limit/v1",
        "AO09": "is456.beam.deflection.check/v1",
        "AO10": "is456.beam.crack_width.check/v1",
    },
}


def load(path: Path) -> object:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def fail(message: str) -> None:
    raise ValueError(message)


def validate() -> None:
    paths = tuple(CONTRACT_ROOT.rglob("*.json"))
    if not paths:
        fail("no structural-engineering contract JSON files found")
    for path in paths:
        load(path)

    result_schema = load(CONTRACT_ROOT / "schemas" / "operation-result.schema.json")
    Draft202012Validator.check_schema(result_schema)
    for packet in EXPECTED_MANIFESTS:
        request_schema = load(CONTRACT_ROOT / "schemas" / f"{packet}.schema.json")
        Draft202012Validator.check_schema(request_schema)

    for packet, expected in EXPECTED_MANIFESTS.items():
        manifest = load(CONTRACT_ROOT / "operations" / f"{packet}.json")
        operations = manifest["operations"]
        actual = {
            item["catalogue_id"]: item["semantic_id"] for item in operations
        }
        if actual != expected:
            fail(f"{packet.upper()} semantic catalogue mismatch: {actual!r}")
        for item in operations:
            if not item["python_projection"].startswith("structural_lib."):
                fail(f"invalid Python projection for {item['catalogue_id']}")
            if not item["dotnet_projection"].startswith("StructuralEngineering."):
                fail(f"invalid .NET projection for {item['catalogue_id']}")
            if not item["required_inputs"] or not item["outputs"]:
                fail(f"incomplete signature for {item['catalogue_id']}")

    code_data = load(CONTRACT_ROOT / "code-data" / "is456" / "flexure-v1.json")
    if code_data["code_data_revision_id"] != "is456-wp01-v1":
        fail("WP01 code-data revision mismatch")
    if code_data["limiting_neutral_axis_ratios"] != {
        "250": 0.53,
        "415": 0.48,
        "500": 0.46,
    }:
        fail("WP01 limiting neutral-axis ratios changed")

    shear_data = load(
        CONTRACT_ROOT / "code-data" / "is456" / "shear-torsion-v1.json"
    )
    if shear_data["code_data_revision_id"] != "is456-wp02-v1":
        fail("WP02 code-data revision mismatch")
    if len(shear_data["table_19"]["longitudinal_percentage_rows"]) != 13:
        fail("WP02 Table 19 row domain is incomplete")
    if set(shear_data["table_19"]["columns"]) != {
        "15",
        "20",
        "25",
        "30",
        "35",
        "40",
    }:
        fail("WP02 Table 19 grade columns are incomplete")

    analysis_data = load(
        CONTRACT_ROOT / "code-data" / "analysis" / "beam-line-v1.json"
    )
    if analysis_data["method_revision_id"] != "structural-analysis-wp03-v1":
        fail("WP03 analysis-method revision mismatch")
    if analysis_data["degrees_of_freedom_per_node"] != [
        "v2_displacement_mm",
        "rotation_m3_rad",
    ]:
        fail("WP03 bounded beam degrees of freedom changed")
    if analysis_data["limits"] != {
        "minimum_nodes": 2,
        "maximum_nodes": 20,
        "minimum_station_intervals": 2,
        "maximum_station_intervals": 100,
    }:
        fail("WP03 bounded analysis limits changed")

    serviceability_data = load(
        CONTRACT_ROOT / "code-data" / "is456" / "serviceability-v1.json"
    )
    if serviceability_data["code_data_revision_id"] != "is456-wp04-v1":
        fail("WP04 code-data revision mismatch")
    if serviceability_data["deflection"]["basic_span_depth_ratios"] != {
        "cantilever": 7,
        "simply_supported": 20,
        "continuous": 26,
    }:
        fail("WP04 basic span-depth ratios changed")
    if serviceability_data["crack_width"]["ceilings_mm"] != {
        "non_harmful_mild": 0.3,
        "harmful_or_weather_or_moderate_severe": 0.2,
        "very_severe_extreme": 0.1,
    }:
        fail("WP04 crack-width ceilings changed")

    all_vectors = []
    for packet in EXPECTED_MANIFESTS:
        conformance = load(
            CONTRACT_ROOT / "conformance" / f"{packet}-vectors.json"
        )
        all_vectors.extend(conformance["vectors"])
    vector_ids = [item["id"] for item in all_vectors]
    if len(vector_ids) != len(set(vector_ids)):
        fail("duplicate structural-engineering conformance vector id")
    canonical = next(
        item for item in all_vectors if item["id"] == "wp01-canonical-object"
    )
    expected_bytes = canonical["expected_canonical_utf8"].encode("utf-8")
    digest = hashlib.sha256(expected_bytes).hexdigest()
    expected_id = f"normalized_input_id:pf4-canonical-json-v1:{digest}"
    if canonical["expected_normalized_input_id"] != expected_id:
        fail("canonical fixture digest does not match its bytes")
    action_vector = next(
        item for item in all_vectors if item["id"] == "wp03-action-six-components"
    )
    if action_vector["expected"]["row_id"] != (
        "action_row_id:pf4-canonical-json-v1:"
        "2667bdfe26231eea46cf6f1ad5bfaf585b42470997ef6a2427a76e29c6f14c38"
    ):
        fail("WP03 action-row canonical identity changed")
    crack_vector = next(
        item for item in all_vectors if item["id"] == "wp04-annex-f-actual-bars"
    )
    if abs(
        crack_vector["expected"]["calculated_crack_width_mm"]
        - 0.11379830508373975
    ) > 1e-15:
        fail("WP04 Annex F reference result changed")
    operations_with_vectors = {
        item["operation_semantic_id"]
        for item in all_vectors
        if item["operation_semantic_id"] != "canonicalization"
    }
    expected_operations = {
        semantic_id
        for manifest in EXPECTED_MANIFESTS.values()
        for semantic_id in manifest.values()
    }
    missing = expected_operations - operations_with_vectors
    if missing:
        fail(f"operations without a conformance vector: {sorted(missing)}")


def main() -> int:
    try:
        validate()
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    packets = ", ".join(packet.upper() for packet in EXPECTED_MANIFESTS)
    print(f"OK: {packets} semantic manifests, schemas, code data, and conformance vectors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

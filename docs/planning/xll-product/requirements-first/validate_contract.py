"""Audit the draft specification and fixtures; does not run structural calculations."""

from __future__ import annotations

import copy
import csv
import json
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parent


def read(name: str):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def semantic_errors(data: dict) -> list[str]:
    """Only the narrow cross-field constraints supplied in this draft."""
    errors = []
    request = data.get("effective_input", data)
    section = request.get("section", {})
    if section and section["effective_depth_mm"] >= section["overall_depth_mm"]:
        errors.append("EFFECTIVE_DEPTH_NOT_INSIDE_SECTION")
    if "effective_input" in data and data["operation"] != request["operation"]:
        errors.append("RESULT_OPERATION_MISMATCH")
    return errors


def source_identity_resolved(data: dict, resolved_sources: dict[str, str]) -> bool:
    """Source-identity prerequisite only; not permission or readiness to execute."""
    source = data["code_basis"]
    digest = source["dataset_digest"]
    return (
        not semantic_errors(data)
        and digest != "sha256:" + "0" * 64
        and resolved_sources.get(source["ruleset_id"]) == digest
    )


def result_source_errors(data: dict, check_sources: dict[str, tuple[str, str]]) -> list[str]:
    """Resolve emitted check references against a trusted, content-bound registry."""
    basis = data['effective_input']['code_basis']
    expected = (basis['ruleset_id'], basis['dataset_digest'])
    return [source for check in data['checks'] for source in check['source_ids']
            if check_sources.get(source) != expected]


def main() -> None:
    schemas = {p.name: read(p.name) for p in ROOT.glob("*.schema.json")}
    registry = Registry()
    for name, schema in schemas.items():
        Draft202012Validator.check_schema(schema)
        registry = registry.with_resource(name, Resource.from_contents(schema))
    validators = {
        name: Draft202012Validator(schema, registry=registry)
        for name, schema in schemas.items()
    }
    counts = {"schema_fixtures": 0, "semantic_fixtures": 0, "admission_fixtures": 0}
    for case in read("validation-cases.json"):
        data = read(case["file"])
        errors = list(validators[case["schema"]].iter_errors(data))
        assert (not errors) == case["schema_valid"], (case["file"], errors)
        counts["schema_fixtures"] += 1
        if "semantic_valid" in case:
            assert (not semantic_errors(data)) == case["semantic_valid"], case["file"]
            counts["semantic_fixtures"] += 1
        if "source_identity_resolved" in case:
            assert source_identity_resolved(data, {}) == case["source_identity_resolved"], case["file"]
            counts["admission_fixtures"] += 1

    # These counterexamples verify actual contract hazards, not numerical formulas.
    base = read("examples/check-section.json")
    for field, value in [("unknown", 1), ("provided_tension_steel_mm2", None)]:
        bad = copy.deepcopy(base)
        bad[field] = value
        assert not validators["section-request.schema.json"].is_valid(bad)
    bad = copy.deepcopy(base)
    bad["action"]["torsion_knm"] = 5
    assert not validators["section-request.schema.json"].is_valid(bad)
    bad = copy.deepcopy(base)
    bad["operation"] = "design_section"
    assert not validators["section-request.schema.json"].is_valid(bad)
    bad = read("examples/not-run-result.json")
    bad["engineering"] = "pass"
    assert not validators["section-result.schema.json"].is_valid(bad)
    bad = read("examples/not-run-result.json")
    bad["operation"] = "design_section"
    assert semantic_errors(bad) == ["RESULT_OPERATION_MISMATCH"]
    counts["counterexamples"] = 6

    # Synthetic provenance mechanics only: these are not real code datasets/results.
    synthetic = copy.deepcopy(base)
    synthetic['code_basis']['ruleset_id'] = 'synthetic-registry-fixture'
    digest = 'sha256:' + '1' * 64
    synthetic['code_basis']['dataset_digest'] = digest
    assert source_identity_resolved(synthetic, {'synthetic-registry-fixture': digest})
    assert not source_identity_resolved(synthetic, {'synthetic-registry-fixture': 'sha256:' + '2' * 64})
    assert not source_identity_resolved(synthetic, {})
    synthetic_result = {'effective_input': synthetic, 'checks': [{'source_ids': ['fixture-source']} ]}
    assert result_source_errors(synthetic_result, {}) == ['fixture-source']
    assert result_source_errors(synthetic_result, {'fixture-source': ('synthetic-registry-fixture', digest)}) == []
    assert result_source_errors(synthetic_result, {'fixture-source': ('wrong-ruleset', digest)}) == ['fixture-source']
    rejected = read('examples/not-run-result.json')
    del rejected['effective_input']
    rejected.update(execution='rejected', submitted_input_digest='sha256:' + '3' * 64)
    assert validators['section-result.schema.json'].is_valid(rejected)
    bad = read('examples/not-run-result.json')
    bad.update(execution='completed', completeness='complete_for_declared_scope',
               freshness='current', engine_version='synthetic-fixture',
               calculation_digest=digest, quantities={},
               checks=[{'check_id':'flexure','outcome':'not_evaluated','source_ids':['fixture-source'],'explanation':'Synthetic schema counterexample'}])
    assert not validators['section-result.schema.json'].is_valid(bad)
    counts['provenance_and_state_checks'] = 8

    def indexed(name: str) -> dict:
        items = read(name)
        result = {item["id"]: item for item in items}
        assert len(result) == len(items), f"Duplicate ID in {name}"
        return result

    sources = indexed("sources.json")
    requirements = indexed("requirements.json")
    failures = indexed("failure-register.json")
    operations = indexed("operations.json")
    examples = indexed("example-index.json")
    for item in [*requirements.values(), *failures.values()]:
        assert set(item["source_ids"]) <= sources.keys(), item["id"]
    for item in failures.values():
        assert set(item["prevention_requirements"]) <= requirements.keys(), item["id"]
    for op in operations.values():
        assert op["example_ids"], op["id"]
        assert set(op['requirement_ids']) <= requirements.keys(), op['id']
        for example_id in op["example_ids"]:
            assert op["id"] in examples[example_id]["operation_ids"]
        if op["contract_state"] == "specified-wire":
            assert op["request_schema"] in schemas and op["result_schema"] in schemas
        else:
            assert op["request_schema"] is None and op["result_schema"] is None
    for example in examples.values():
        assert example["source_id"] in sources
        assert set(example["operation_ids"]) <= operations.keys()
        assert example["numerical_execution"] == "not_run"
        if example["file"]:
            assert (ROOT / example["file"]).is_file()
    with (ROOT/'requirements.csv').open(encoding='utf-8-sig', newline='') as handle:
        projected = list(csv.DictReader(handle))
    for row in projected:
        row['source_ids'] = row['source_ids'].split(';')
    assert projected == list(requirements.values()), 'CSV projection drift'
    print(json.dumps({"status": "PASS", "schemas": len(schemas), **counts,
                      "requirements": len(requirements), "failure_families": len(failures),
                      "operations": len(operations), "examples": len(examples),
                      "engineering_executions": 0, "installed_executions": 0}, indent=2))


if __name__ == "__main__":
    main()

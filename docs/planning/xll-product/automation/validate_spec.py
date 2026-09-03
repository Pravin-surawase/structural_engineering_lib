"""Validate operation/example/source links and the actual request schemas."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[3]


def load(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def ids(items):
    values = [x["id"] for x in items]
    assert len(values) == len(set(values)), "duplicate IDs"
    return set(values)


def main():
    req, ops, ex, src = map(
        load,
        [
            "requirements.json",
            "operations.json",
            "examples.json",
            "source-crosswalk.json",
        ],
    )
    req_ids, op_ids, ex_ids, src_ids = ids(req), ids(ops), ids(ex), ids(src)
    op_map = {o["id"]: o for o in ops}
    req_map = {r["id"]: r for r in req}
    for r in req:
        assert r["acceptance"], r["id"]
        assert set(r["operations"]) <= op_ids, r["id"]
        assert set(r["examples"]) <= ex_ids, r["id"]
        assert set(r["sources"]) <= src_ids, r["id"]
    for example in ex:
        assert example["operation"] in op_ids, example["id"]
        assert example["assertions"], example["id"]
        assert example["id"] in op_map[example["operation"]]["examples"]
        if example.get("test_path"):
            assert (REPO / example["test_path"]).is_file()
    for op in ops:
        assert op["request_type"] and op["result_type"] and op["signature"]
        assert (
            set(op["requirements"]) <= req_ids
            and set(op["examples"]) <= ex_ids
            and set(op["sources"]) <= src_ids
        )
        for rid in op["requirements"]:
            assert op["id"] in req_map[rid]["operations"]
        names = [f["name"] for f in op["inputs"]]
        assert len(names) == len(set(names))
        for field in op["inputs"]:
            assert {
                "name",
                "type",
                "unit",
                "required",
                "default",
                "condition",
                "validation",
            } <= field.keys()
            assert isinstance(field["required"], bool) and field["validation"]
        if op.get("request_schema"):
            filename, _, fragment = op["request_schema"].partition("#")
            schema = load(filename)
            Draft202012Validator.check_schema(schema)
            selected = schema
            for part in fragment.strip("/").split("/") if fragment else []:
                selected = selected[part]
            if op["implementation"]:
                assert set(names) == set(schema["properties"]), op["id"]
                assert (REPO / op["implementation"]["source"]).is_file()
    for source in src:
        if source.get("path"):
            assert (REPO / source["path"]).is_file(), source["path"]
    member = load("member-inputs.schema.json")

    def refs(node):
        if isinstance(node, dict):
            if "$ref" in node and node["$ref"].startswith("#/$defs/"):
                assert node["$ref"][8:] in member["$defs"], node["$ref"]
            for value in node.values():
                refs(value)
        elif isinstance(node, list):
            for value in node:
                refs(value)

    refs(member)
    for name, typename in [
        ("beam-line", "BeamLineRequest"),
        ("reinforcement", "ReinforcementGeometryRequest"),
        ("quantities", "QuantityRequest"),
    ]:
        schema = json.loads(
            (REPO / f"CSharp/schemas/{typename}.schema.json").read_text()
        )
        example = json.loads((REPO / f"CSharp/examples/{name}.json").read_text())
        Draft202012Validator(schema).validate(example)
    print(
        f"PASS: {len(req)} requirements; {len(ops)} operations; {len(ex)} examples; {len(src)} sources; {len(member['$defs'])} member/check types; compiled request fixtures"
    )


if __name__ == "__main__":
    main()

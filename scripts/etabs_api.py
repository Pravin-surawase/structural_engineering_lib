#!/usr/bin/env python3
"""Discover ETABS methods and workflows without loading or invoking ETABS.

When to use: Search the pinned API, inspect exact signatures/defaults/navigation,
read one installed help topic, or rebuild the portable metadata catalogue.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import re
import sys
from collections import deque
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "docs/reference/etabs-api-catalog.json.gz"
WORKFLOWS = ROOT / "docs/reference/etabs-api-workflows.json"
SCHEMA = "structural.etabs_api_guide/v1"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class HelpPage(HTMLParser):
    """Read help metadata/text only; never execute its scripts or examples."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.metadata: dict[str, str] = {}
        self.parts: list[str] = []
        self.skip = False

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "meta" and "name" in attributes:
            self.metadata[attributes["name"]] = attributes.get("content", "")
        if tag in {"script", "style", "head"}:
            self.skip = True
        if tag in {"br", "p", "dt", "dd", "div", "h4", "pre", "tr"}:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in {"script", "style", "head"}:
            self.skip = False
        if tag in {"p", "dt", "dd", "div", "h4", "pre", "tr"}:
            self.parts.append("\n")

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)

    def text(self) -> str:
        return "\n".join(
            line
            for raw in "".join(self.parts).splitlines()
            if (line := re.sub(r"\s+", " ", raw).strip())
        )


def method_id(member: dict) -> str:
    cap = member["Capability"]
    return f"{cap['InterfaceType']}.{cap['Member']}"


def load_catalog(path: Path = CATALOG) -> dict:
    value = json.loads(gzip.decompress(path.read_bytes()))
    if value["schema"] != SCHEMA:
        raise ValueError("Unsupported guide schema; rebuild with the maintained tool.")
    return value


def load_workflows() -> dict:
    return json.loads(WORKFLOWS.read_text(encoding="utf-8"))["workflows"]


def navigation(catalog: dict) -> dict[str, str]:
    paths = {
        "ETABSv1.cSapModel": "SapModel",
        "ETABSv1.cOAPI": "EtabsObject",
        "ETABSv1.cHelper": "Helper",
    }
    pending = deque(paths)
    while pending:
        owner = pending.popleft()
        for prop in catalog["inventory"]["Properties"]:
            if (
                prop["InterfaceType"] == owner
                and prop["CanRead"]
                and prop["Type"] not in paths
            ):
                paths[prop["Type"]] = f"{paths[owner]}.{prop['Name']}"
                pending.append(prop["Type"])
    return paths


def select_member(catalog: dict, query: str) -> dict:
    matches = [
        m
        for m in catalog["inventory"]["Members"]
        if method_id(m).lower() == query.lower()
        or method_id(m).removeprefix("ETABSv1.").lower() == query.lower()
        or m["Capability"]["Member"].lower() == query.lower()
    ]
    if len(matches) != 1:
        names = ", ".join(method_id(m) for m in matches[:12])
        raise ValueError(
            f"Expected one exact method, found {len(matches)}. Use interface.member. {names}"
        )
    return matches[0]


def search(catalog: dict, query: str, workflows: dict) -> list[dict]:
    words = re.findall(r"[a-z0-9]+", query.lower())
    if not words:
        raise ValueError("Use a method, interface, or task keyword.")
    results = []
    for member in catalog["inventory"]["Members"]:
        name = method_id(member)
        linked = [key for key, flow in workflows.items() if name in flow["methods"]]
        tasks = " ".join(
            key
            + " "
            + workflows[key]["purpose"]
            + " "
            + " ".join(workflows[key]["keywords"])
            for key in linked
        )
        haystack = f"{name} {member['Capability']['Area']} {tasks}".lower()
        if all(word in haystack for word in words):
            score = sum(4 for word in words if word in name.lower())
            results.append(
                {
                    "method": name,
                    "status": member["Status"],
                    "effect": member["Capability"]["Effect"],
                    "workflows": linked,
                    "score": score,
                }
            )
    return sorted(results, key=lambda item: (-item["score"], item["method"]))


def card(catalog: dict, member: dict, workflows: dict) -> dict:
    name = method_id(member)
    cap = member["Capability"]
    owner = navigation(catalog).get(cap["InterfaceType"])
    referenced = {
        p["Type"].rstrip("&[]") for m in member["Methods"] for p in m["Parameters"]
    }
    referenced.update(m["ReturnType"] for m in member["Methods"])
    return {
        "method": name,
        "object_path": f"{owner}.{cap['Member']}" if owner else None,
        "effect": cap["Effect"],
        "status": member["Status"],
        "signatures": member["Methods"],
        "enums": [e for e in catalog["inventory"]["Enums"] if e["Type"] in referenced],
        "help_topics": catalog["topics"].get("M:" + name, []),
        "registered_getters": member["RegisteredGetters"],
        "workflows": [
            key for key, flow in workflows.items() if name in flow["methods"]
        ],
        "evidence": "Static metadata only. Registered signatures and documentation do not prove live behavior or authorize invocation.",
        "source": catalog["source"],
    }


def coverage(catalog: dict, workflows: dict) -> dict:
    inv = catalog["inventory"]
    present = [m for m in inv["Members"] if m["Methods"]]
    return {
        "interfaces": len(inv["Interfaces"]),
        "method_names_present": len(present),
        "method_declarations": sum(len(m["Methods"]) for m in present),
        "missing_candidates": [
            method_id(m) for m in inv["Members"] if not m["Methods"]
        ],
        "properties": len(inv["Properties"]),
        "enums": len(inv["Enums"]),
        "methods_with_help": sum(
            bool(catalog["topics"].get("M:" + method_id(m))) for m in present
        ),
        "methods_without_help": [
            method_id(m)
            for m in present
            if not catalog["topics"].get("M:" + method_id(m))
        ],
        "registered_method_names": sum(bool(m["RegisteredGetters"]) for m in present),
        "unclassified_effects": sum(
            m["Capability"]["Effect"] == "unclassified" for m in present
        ),
        "workflows": list(workflows),
        "target_methods_invoked": inv["TargetMethodsInvoked"],
        "scope": inv["EvidenceScope"],
        "source": catalog["source"],
    }


def build_catalog(
    inventory_path: Path, assembly: Path, chm: Path, help_root: Path
) -> dict:
    raw = json.loads(inventory_path.read_text(encoding="utf-8-sig"))
    inv = raw["inventory"]
    if (
        inv["SchemaVersion"] != "structural.etabs_api_inventory/v2"
        or inv["TargetMethodsInvoked"] != 0
    ):
        raise ValueError(
            "Require current v2 static-only inventory from --api-inventory-all."
        )
    if digest(assembly) != raw["sourceAssemblySha256"]:
        raise ValueError(
            "Assembly differs from the inventory source; regenerate first."
        )
    topics: dict[str, list] = {}
    version = raw["sourceAssemblyFileVersion"]
    for path in sorted(help_root.glob("html/*.htm")):
        html = path.read_text(encoding="utf-8-sig")
        page = HelpPage()
        page.feed(html.split("</head>", 1)[0] + "</head>")
        identity = page.metadata.get("Microsoft.Help.Id", "")
        if not identity.startswith(("M:ETABSv1.", "P:ETABSv1.", "T:ETABSv1.")):
            continue
        if identity.startswith(("M:", "P:")) and f"({version})" not in html:
            raise ValueError(f"Help/assembly file-version mismatch: {path.name}")
        topics.setdefault(identity.split("(", 1)[0], []).append(
            {
                "path": path.relative_to(help_root).as_posix(),
                "id": identity,
                "sha256": digest(path),
            }
        )
    if not topics:
        raise ValueError(
            "No API help topics found; extract the matching CHM into a fresh directory."
        )
    return {
        "schema": SCHEMA,
        "source": {
            "assembly_file_version": version,
            "assembly_sha256": raw["sourceAssemblySha256"],
            "assembly_identity": inv["AssemblyIdentity"],
            "help_file_name": chm.name,
            "help_sha256": digest(chm),
            "help_binding": "Operator-extracted matching CHM; per-topic bytes and assembly file versions checked.",
        },
        "inventory": inv,
        "topics": topics,
    }


def validate(catalog: dict, workflows: dict) -> list[str]:
    inv = catalog["inventory"]
    errors = []
    names = [method_id(m) for m in inv["Members"]]
    if len(names) != len(set(names)) or inv["TargetMethodsInvoked"] != 0:
        errors.append("Duplicate methods or non-static inventory.")
    for key, flow in workflows.items():
        for name in flow["methods"]:
            if name not in names:
                errors.append(f"{key}: unknown method {name}")
        for path in flow["owners"]:
            if not (ROOT / path).is_file():
                errors.append(f"{key}: missing owner {path}")
    for name, topics in catalog["topics"].items():
        for topic in topics:
            if not re.fullmatch(r"html/[a-zA-Z0-9_-]+\.htm", topic["path"]):
                errors.append(f"Unsafe topic path for {name}")
    return errors


def read_help(catalog: dict, member: dict, root: Path, section: str) -> str:
    topics = catalog["topics"].get("M:" + method_id(member), [])
    if len(topics) != 1:
        raise ValueError(
            "Help is missing or overloaded; use the exact topic path from show."
        )
    topic = topics[0]
    path = root / topic["path"]
    if digest(path) != topic["sha256"]:
        raise ValueError(
            "Help topic differs from the pinned catalogue; refresh or use the matching extraction."
        )
    html = path.read_text(encoding="utf-8-sig")
    if section in {"parameters", "returns"}:
        label = "Parameters" if section == "parameters" else "Return Value"
        match = re.search(
            rf"<h4[^>]*>{label}</h4>(.*?)(?=<h4|<div class=\"collapsibleAreaRegion\"|$)",
            html,
            re.DOTALL,
        )
        if not match:
            raise ValueError(f"No {label} section; inspect --section all.")
        html = match.group(1)
    parser = HelpPage()
    parser.feed(html)
    return parser.text()


def positive(value: str) -> int:
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("Must be positive.")
    return number


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=CATALOG)
    subs = parser.add_subparsers(dest="command", required=True)
    subs.add_parser("summary")
    subs.add_parser("workflows")
    find = subs.add_parser("search")
    find.add_argument("query")
    find.add_argument("--limit", type=positive, default=12)
    find.add_argument("--offset", type=int, default=0)
    for command in ("show", "interface", "enum", "workflow"):
        subs.add_parser(command).add_argument("name")
    help_cmd = subs.add_parser("help")
    help_cmd.add_argument("name")
    help_cmd.add_argument("--root", type=Path, required=True)
    help_cmd.add_argument(
        "--section", choices=["parameters", "returns", "all"], default="parameters"
    )
    help_cmd.add_argument("--offset", type=int, default=0)
    help_cmd.add_argument("--limit", type=positive, default=6000)
    check = subs.add_parser("check")
    check.add_argument("--assembly", type=Path)
    check.add_argument("--chm", type=Path)
    build = subs.add_parser("build")
    for option in ("inventory", "assembly", "chm", "help-root"):
        build.add_argument("--" + option, type=Path, required=True)
    build.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        flows = load_workflows()
        if args.command == "build":
            catalog = build_catalog(
                args.inventory, args.assembly, args.chm, args.help_root
            )
            errors = validate(catalog, flows)
            if errors:
                raise ValueError("; ".join(errors))
            args.output.write_bytes(
                gzip.compress(
                    json.dumps(catalog, sort_keys=True, separators=(",", ":")).encode(),
                    mtime=0,
                )
            )
            result = coverage(catalog, flows)
        else:
            catalog = load_catalog(args.catalog)
            if args.command == "summary":
                result = coverage(catalog, flows)
            elif args.command == "search":
                results = search(catalog, args.query, flows)
                start = max(0, args.offset)
                result = {
                    "total": len(results),
                    "offset": start,
                    "results": results[start : start + args.limit],
                }
            elif args.command == "show":
                result = card(catalog, select_member(catalog, args.name), flows)
            elif args.command == "interface":
                name = (
                    args.name
                    if args.name.startswith("ETABSv1.")
                    else "ETABSv1." + args.name
                )
                if name not in catalog["inventory"]["Interfaces"]:
                    raise ValueError("Unknown interface; use summary/search first.")
                result = {
                    "interface": name,
                    "object_path": navigation(catalog).get(name),
                    "properties": [
                        p
                        for p in catalog["inventory"]["Properties"]
                        if p["InterfaceType"] == name
                    ],
                    "methods": [
                        method_id(m)
                        for m in catalog["inventory"]["Members"]
                        if m["Capability"]["InterfaceType"] == name
                    ],
                }
            elif args.command == "enum":
                result = [
                    e
                    for e in catalog["inventory"]["Enums"]
                    if e["Type"] in {args.name, "ETABSv1." + args.name}
                ]
                if not result:
                    raise ValueError("Unknown enum.")
            elif args.command == "workflows":
                result = {
                    key: {"purpose": flow["purpose"], "status": flow["status"]}
                    for key, flow in flows.items()
                }
            elif args.command == "workflow":
                if args.name not in flows:
                    raise ValueError("Unknown workflow; run workflows first.")
                result = flows[args.name]
            elif args.command == "help":
                content = read_help(
                    catalog, select_member(catalog, args.name), args.root, args.section
                )
                start = max(0, args.offset)
                result = {
                    "section": args.section,
                    "total_characters": len(content),
                    "offset": start,
                    "text": content[start : start + args.limit],
                }
            else:
                errors = validate(catalog, flows)
                for label, path in (("assembly", args.assembly), ("help", args.chm)):
                    if path and digest(path) != catalog["source"][label + "_sha256"]:
                        errors.append(
                            f"{label} drift: regenerate and review before use."
                        )
                result = {
                    "status": "FAIL" if errors else "PASS",
                    "errors": errors,
                    "installed_identity_checked": bool(args.assembly and args.chm),
                }
                if errors:
                    print(json.dumps(result, indent=2))
                    return 1
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except (OSError, ValueError, KeyError) as exc:
        print(f"ETABS API discovery failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
